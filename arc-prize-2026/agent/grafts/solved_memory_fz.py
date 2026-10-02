# ---- ours/solved_memory_fz: pin each solved level's winning action sequence (Franzen harness) ----
# Evidence, not advice: sirikilohit's Milestone 2 write-up found that pinning what was learned on cleared levels was
# "the only text addition that helped" (+2.8), while every advice line hurt. Franzen keeps the history across levels
# but trims it in large blocks (~118k -> ~59k tokens), so on long games the winning moves of early levels fall out of
# context. This graft records, per level, the actions of the attempt that cleared it (deaths reset the record) and
# pins them, run-length compressed, at the end of the system prompt. One system-prompt change per cleared level costs
# one prefix re-read, which Franzen's trims already pay for.
# Hook: ToolAgent._prepare_auto_diff(self, current_frame, previous_step_summary), called once per analyzer turn with
# the previous turn's summary (executed_actions, game_over, level_transition). Expects `_tool_agent` in scope.
# Fail-open: any error leaves the original behaviour.
_SM_CLS = _tool_agent.ToolAgent
assert _SM_CLS._prepare_auto_diff.__code__.co_varnames[:3] == ("self", "current_frame", "previous_step_summary"), \
    "solved_memory_fz: _prepare_auto_diff signature moved"
_sm_orig_prepare = _SM_CLS._prepare_auto_diff
_SM_MAX_ACTIONS = 60      # per level, most recent kept
_SM_MAX_CHARS = 1800      # whole pinned block
OURS_SM_COUNTS = {"turns": 0, "levels_pinned": 0, "deaths": 0, "errors": 0}


def _sm_compress(actions):
    """['UP','UP','UP','MOUSE(row=3, col=4)'] -> 'UP x3, MOUSE(row=3, col=4)'."""
    out, prev, n = [], None, 0
    for a in actions:
        a = " ".join(str(a).split())
        if a == prev:
            n += 1
            continue
        if prev is not None:
            out.append(prev if n == 1 else f"{prev} x{n}")
        prev, n = a, 1
    if prev is not None:
        out.append(prev if n == 1 else f"{prev} x{n}")
    return ", ".join(out)


def _sm_block(solved):
    lines = ["", "Solved levels in this game (recorded by the harness: the exact actions of the attempt that "
             "cleared each level, oldest first). Later levels often reuse these mechanics."]
    for lvl in sorted(solved):
        acts = solved[lvl]
        shown = acts[-_SM_MAX_ACTIONS:]
        head = f"- Level {lvl} ({len(acts)} actions{', last ' + str(len(shown)) + ' shown' if len(shown) < len(acts) else ''}): "
        lines.append(head + _sm_compress(shown))
    text = "\n".join(lines)
    if len(text) > _SM_MAX_CHARS:   # keep the most recent levels
        text = text[:120] + "\n...\n" + text[-(_SM_MAX_CHARS - 130):]
    return text


def _sm_prepare(self, current_frame, previous_step_summary, *args, **kwargs):
    try:
        OURS_SM_COUNTS["turns"] += 1
        if not hasattr(self, "_ours_sm_base_prompt"):
            self._ours_sm_base_prompt = self._system_prompt
            self._ours_sm_attempt = []
            self._ours_sm_solved = {}
            self._ours_sm_level = getattr(current_frame, "level", None)
        s = previous_step_summary or {}
        # A resumed (yielded) turn can rebuild its opener from the same summary: count each summary once.
        key = (s.get("start_action_num"), s.get("end_action_num"), s.get("executed_count")) if s else None
        if key is not None and key[1] is None:
            key = ("id", id(s))
        if key is not None and key == getattr(self, "_ours_sm_last_key", None):
            s = {}
        elif key is not None:
            self._ours_sm_last_key = key
        if s and not s.get("stale"):
            acts = s.get("executed_actions")
            if isinstance(acts, list):
                self._ours_sm_attempt.extend(str(a) for a in acts)
            if s.get("game_over"):
                OURS_SM_COUNTS["deaths"] += 1
                self._ours_sm_attempt = []
            elif s.get("level_transition") and not s.get("run_complete"):
                lvl = self._ours_sm_level
                if lvl is not None and self._ours_sm_attempt:
                    self._ours_sm_solved[lvl] = list(self._ours_sm_attempt)
                    self._system_prompt = self._ours_sm_base_prompt + _sm_block(self._ours_sm_solved)
                    OURS_SM_COUNTS["levels_pinned"] += 1
                    if OURS_SM_COUNTS["levels_pinned"] in (1, 10) or OURS_SM_COUNTS["levels_pinned"] % 50 == 0:
                        print(f"OURS_SOLVED_MEMORY {OURS_SM_COUNTS}", flush=True)
                self._ours_sm_attempt = []
        cur = getattr(current_frame, "level", None)
        if cur is not None:
            self._ours_sm_level = cur
    except Exception:
        OURS_SM_COUNTS["errors"] += 1
    return _sm_orig_prepare(self, current_frame, previous_step_summary, *args, **kwargs)


_sm_prepare.__wrapped__ = _sm_orig_prepare
_SM_CLS._prepare_auto_diff = _sm_prepare
print("OURS_SOLVED_MEMORY ok", flush=True)
