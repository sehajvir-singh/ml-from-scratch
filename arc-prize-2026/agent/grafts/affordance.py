# ---- ours/affordance: an action-effect model learned during play (Depth Engine, part 1).
# A small CNN, trained on CPU on this game's own transitions, predicts whether an action changes the board in a
# given state (StochasticGoose, the ARC-AGI-3 preview winner, used the same signal on its own). Here it only
# advises the LLM: one or two short prompt lines listing the clicks most likely to do something and the moves
# likely to do nothing. It never blocks an action.
#
# Data: the harness's NoopGuard observes every executed action with its board-before signature. We keep the grid
# behind each signature; the next signature the same thread computes is the board after the action. The label is
# a REAL change: many games tick a one-cell step counter on the border on every action (vc33, tn36), so the
# harness's board_changed flag is almost always true. A diff of at most 3 collinear cells within 2 cells of the
# border counts as a timer tick, not an effect. Animated actions always count as an effect.
# The model is kept across levels of the same game, so what it learned on level 1 carries into level 2.
# Honesty gate: a hint is shown only when the model's predict-then-learn accuracy on its last 30 samples is at
# least 80% and beats always guessing the majority label.
# Fail-open: without torch, or on any exception, the prompt is unchanged. CPU only; never touches CUDA.
import collections as _af_collections
import re as _af_re
import threading as _af_threading
import time as _af_time

try:
    import numpy as _af_np
    import torch as _af_torch
    import torch.nn as _af_nn

    _af_torch.set_num_threads(4)
    _AF_TORCH = _af_torch.__version__
except Exception:  # pragma: no cover - Kaggle images ship torch; stay inert without it
    _af_np = _af_torch = _af_nn = None
    _AF_TORCH = None

_AF_KEYS = ("UP", "DOWN", "LEFT", "RIGHT", "SPACE", "ACTION7")
_AF_MOUSE_RE = _af_re.compile(r"MOUSE\(row=(\d+),\s*col=(\d+)\)")
_AF_COLORS = "WwgGcBMPRbSYOrNp"  # inference.utils.grid_utils.ARC_COLOR_CHARS
_AF_MIN_SAMPLES = 24
_AF_TRAIN_EVERY = 8
_AF_TRAIN_SECONDS = 1.0
_AF_MAX_SAMPLES = 3000
_AF_WINDOW = 30
_AF_MIN_ACC = 0.8
_AF_TOP_CLICKS = 6
_AF_TRAIN_LOCK = _af_threading.Lock()
_AF_GRIDS = _af_collections.OrderedDict()
_AF_LOCAL = _af_threading.local()
OURS_AFFORDANCE_COUNTS = {"observed": 0, "effects": 0, "trains": 0, "prompts": 0, "hints": 0, "errors": 0}

_af_orig_sig = _tool_agent.board_signature
_af_orig_observe = _tool_agent.NoopGuard.observe
_af_orig_build = _tool_agent.ToolAgent._build_user_prompt


def _af_real_change(before, after):
    diff = [(r, c) for r, (rb, ra) in enumerate(zip(before, after)) for c, (xb, xa) in enumerate(zip(rb, ra)) if xb != xa]
    if len(before) != len(after):
        return True
    if not diff:
        return False
    rows = {r for r, _ in diff}
    cols = {c for _, c in diff}
    n = len(before)
    near_border = all(r <= 2 or r >= n - 3 or c <= 2 or c >= n - 3 for r, c in diff)
    return not (len(diff) <= 3 and near_border and (len(rows) == 1 or len(cols) == 1))


def _af_finish(pending, after):
    learner, before, parsed, animated, key = pending
    label = bool(animated) or _af_real_change(before, after)
    OURS_AFFORDANCE_COUNTS["observed"] += 1
    OURS_AFFORDANCE_COUNTS["effects"] += int(label)
    learner.add(before, parsed[0], parsed[1], label, key)
    learner.maybe_train()
    if OURS_AFFORDANCE_COUNTS["observed"] in (50, 150, 300) or OURS_AFFORDANCE_COUNTS["observed"] % 500 == 0:
        print(f"OURS_AFFORDANCE {OURS_AFFORDANCE_COUNTS}", flush=True)


def _af_board_signature(grid):
    sig = _af_orig_sig(grid)
    try:
        if grid:
            _AF_GRIDS[sig] = grid
            while len(_AF_GRIDS) > 4096:
                _AF_GRIDS.popitem(last=False)
            pending = getattr(_AF_LOCAL, "pending", None)
            if pending is not None:
                _AF_LOCAL.pending = None
                _af_finish(pending, grid)
    except Exception:
        OURS_AFFORDANCE_COUNTS["errors"] += 1
    return sig


def _af_tensor(grids):
    """list of 2D int grids -> float tensor [N, 16, 64, 64] one-hot (cropped/padded to 64x64)."""
    arr = _af_np.zeros((len(grids), 64, 64), dtype=_af_np.int64)
    for i, g in enumerate(grids):
        a = _af_np.asarray(g, dtype=_af_np.int64)[:64, :64]
        arr[i, : a.shape[0], : a.shape[1]] = _af_np.clip(a, 0, 15)
    t = _af_torch.from_numpy(arr)
    return _af_torch.nn.functional.one_hot(t, 16).permute(0, 3, 1, 2).float()


if _AF_TORCH:
    class _AfNet(_af_nn.Module):
        def __init__(self):
            super().__init__()
            self.body = _af_nn.Sequential(
                _af_nn.Conv2d(16, 32, 3, padding=1), _af_nn.ReLU(),
                _af_nn.Conv2d(32, 64, 3, padding=1), _af_nn.ReLU(),
                _af_nn.Conv2d(64, 64, 3, padding=1), _af_nn.ReLU(),
            )
            self.click = _af_nn.Conv2d(64, 1, 1)
            self.keys = _af_nn.Linear(64, len(_AF_KEYS))

        def forward(self, x):
            h = self.body(x)
            click = self.click(h)[:, 0]                       # [N, 64, 64] logits
            keys = self.keys(_af_torch.amax(h, dim=(2, 3)))   # [N, 6] logits
            return click, keys


def _af_parse(action_sig):
    """action signature -> ('key', index) or ('click', (row, col)) or None."""
    m = _AF_MOUSE_RE.search(action_sig or "")
    if m:
        return ("click", (min(63, int(m.group(1))), min(63, int(m.group(2)))))
    name = (action_sig or "").strip().upper()
    if name in _AF_KEYS:
        return ("key", _AF_KEYS.index(name))
    return None


class _AfLearner:
    def __init__(self):
        self.net = _AfNet()
        self.opt = _af_torch.optim.Adam(self.net.parameters(), lr=1e-3)
        self.samples = []            # (grid, kind, target, label)
        self.seen = set()
        self.recent = _af_collections.deque(maxlen=_AF_WINDOW)   # (correct, label)
        self.pending = 0
        self.trained = False

    def _logit(self, grid, kind, target):
        with _af_torch.no_grad():
            click, keys = self.net(_af_tensor([grid]))
        return float(click[0, target[0], target[1]]) if kind == "click" else float(keys[0, target])

    def add(self, grid, kind, target, label, key):
        if self.trained:   # predict-then-learn: an honest running accuracy on data the model has not seen
            self.recent.append(((self._logit(grid, kind, target) > 0) == bool(label), bool(label)))
        if key in self.seen:
            return
        self.seen.add(key)
        self.samples.append((grid, kind, target, 1.0 if label else 0.0))
        if len(self.samples) > _AF_MAX_SAMPLES:
            self.samples.pop(0)
        self.pending += 1

    def maybe_train(self):
        if len(self.samples) < _AF_MIN_SAMPLES or self.pending < _AF_TRAIN_EVERY:
            return
        labels = {s[3] for s in self.samples}
        if len(labels) < 2 or not _AF_TRAIN_LOCK.acquire(blocking=False):
            return
        try:
            self.pending = 0
            deadline = _af_time.monotonic() + _AF_TRAIN_SECONDS
            n = len(self.samples)
            steps = 0
            while _af_time.monotonic() < deadline and steps < 60:
                idx = _af_np.random.randint(0, n, size=min(32, n))
                batch = [self.samples[i] for i in idx]
                click, keys = self.net(_af_tensor([b[0] for b in batch]))
                logits = []
                for j, (_, kind, target, _) in enumerate(batch):
                    logits.append(click[j, target[0], target[1]] if kind == "click" else keys[j, target])
                y = _af_torch.tensor([b[3] for b in batch])
                loss = _af_torch.nn.functional.binary_cross_entropy_with_logits(_af_torch.stack(logits), y)
                self.opt.zero_grad()
                loss.backward()
                self.opt.step()
                steps += 1
            self.trained = True
            OURS_AFFORDANCE_COUNTS["trains"] += 1
        finally:
            _AF_TRAIN_LOCK.release()

    def trusted(self):
        if not self.trained or len(self.recent) < _AF_WINDOW:
            return None
        acc = sum(c for c, _ in self.recent) / len(self.recent)
        pos = sum(l for _, l in self.recent) / len(self.recent)
        return acc if acc >= _AF_MIN_ACC and acc > max(pos, 1 - pos) else None


def _af_candidates(grid):
    """One representative cell per same-color 4-connected component (at most 2 per (color, size)), skipping huge ones."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    seen = [[False] * cols for _ in range(rows)]
    out, per = [], {}
    for r0 in range(rows):
        for c0 in range(cols):
            if seen[r0][c0]:
                continue
            color = grid[r0][c0]
            stack, cells = [(r0, c0)], []
            seen[r0][c0] = True
            while stack:
                r, c = stack.pop()
                cells.append((r, c))
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            if len(cells) > rows * cols * 0.15:
                continue
            key = (color, len(cells))
            per[key] = per.get(key, 0) + 1
            if per[key] > 2:
                continue
            cr = sum(p[0] for p in cells) / len(cells)
            cc = sum(p[1] for p in cells) / len(cells)
            r, c = min(cells, key=lambda p: (p[0] - cr) ** 2 + (p[1] - cc) ** 2)
            out.append((r, c, color, len(cells)))
    return out


def _af_hint_lines(learner, frame, valid):
    acc = learner.trusted()
    if acc is None or frame is None or not frame.grid:
        return []
    grid = frame.grid
    with _af_torch.no_grad():
        click, keys = learner.net(_af_tensor([grid]))
    lines = []
    head = f"Learned effect model (trained on this game's {len(learner.samples)} tried actions, recent accuracy {acc:.0%}; advice, not a rule):"
    if "MOUSE" in valid:
        probs = _af_torch.sigmoid(click[0])
        scored = sorted(((float(probs[r, c]), r, c, color, size) for r, c, color, size in _af_candidates(grid)), reverse=True)
        top = [s for s in scored[:_AF_TOP_CLICKS] if s[0] >= 0.5]
        if top:
            rendered = ", ".join(f"(row={r}, col={c}) {_AF_COLORS[max(0, min(15, int(color)))]}x{size} {p:.0%}" for p, r, c, color, size in top)
            lines.append(f"{head} clicks most likely to change the board: {rendered}.")
    kprobs = _af_torch.sigmoid(keys[0])
    dead = [f"{name} {float(kprobs[i]):.0%}" for i, name in enumerate(_AF_KEYS) if name in valid and float(kprobs[i]) < 0.1]
    if dead:
        lines.append((head + " " if not lines else "") + "Likely no effect in this exact state: " + ", ".join(dead) + ".")
    return lines


def _af_observe(self, *, level, board_before_sig, action_sig, board_changed, animated=False):
    _af_orig_observe(self, level=level, board_before_sig=board_before_sig, action_sig=action_sig,
                     board_changed=board_changed, animated=animated)
    try:
        grid = _AF_GRIDS.get(board_before_sig)
        parsed = _af_parse(action_sig)
        if grid is None or parsed is None:
            return
        learner = self.__dict__.get("_ours_affordance")
        if learner is None:
            learner = self.__dict__["_ours_affordance"] = _AfLearner()
        if not board_changed and not animated:   # no diff at all: label now, no need to wait for the next board
            _AF_LOCAL.pending = None
            _af_finish((learner, grid, parsed, False, (board_before_sig, action_sig)), grid)
        else:                                    # the next board_signature on this thread is the board after
            _AF_LOCAL.pending = (learner, grid, parsed, animated, (board_before_sig, action_sig))
    except Exception:
        OURS_AFFORDANCE_COUNTS["errors"] += 1


def _af_build(self, action_num, *args, **kwargs):
    prompt = _af_orig_build(self, action_num, *args, **kwargs)
    try:
        OURS_AFFORDANCE_COUNTS["prompts"] += 1
        guard = getattr(self, "_noop_guard", None)
        learner = guard.__dict__.get("_ours_affordance") if guard is not None else None
        if learner is None:
            return prompt
        valid = _tool_agent._normalize_valid_actions(kwargs.get("valid_actions") or [])
        lines = _af_hint_lines(learner, kwargs.get("current_frame"), valid)
        if not lines:
            return prompt
        OURS_AFFORDANCE_COUNTS["hints"] += 1
        return prompt + "\n" + "\n".join(lines)
    except Exception:
        OURS_AFFORDANCE_COUNTS["errors"] += 1
        return prompt


if _AF_TORCH:
    _tool_agent.board_signature = _af_board_signature
    _tool_agent.NoopGuard.observe = _af_observe
    _tool_agent.ToolAgent._build_user_prompt = _af_build
    print(f"OURS_AFFORDANCE ok torch={_AF_TORCH}", flush=True)
else:
    print("OURS_AFFORDANCE disabled (no torch)", flush=True)
