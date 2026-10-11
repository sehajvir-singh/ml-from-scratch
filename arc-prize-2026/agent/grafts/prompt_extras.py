# ---- ours/prompt_extras: truthful scoring rule, time pacing and click candidates.
# Wraps ToolAgent._build_user_prompt (appends a few short lines) and ToolAgent._compact_action_result
# (remembers the per-game time budget the solver reports). Expects `_tool_agent` in scope and an
# optional OURS_PROMPT_FLAGS dict {"scoring": bool, "pacing": bool, "clicks": bool}.
# Fail-open: any exception returns the unmodified prompt.
#
# Why: a Kaggle participant measured "click candidates + the true scoring rule + time_remaining
# pacing" at 1.12 -> 1.43 on the hidden set (discussion 743060). Extra prompt text is re-sent every
# turn (prefill is ~94% of GPU work on this chassis), so every line here is kept short.
import re as _px_re
import time as _px_time

_PX_CLS = _tool_agent.ToolAgent
_PX_FLAGS = {"scoring": True, "pacing": True, "clicks": True}
_PX_FLAGS.update(globals().get("OURS_PROMPT_FLAGS") or {})
_PX_COLORS = "WwgGcBMPRbSYOrNp"  # inference.utils.grid_utils.ARC_COLOR_CHARS
_PX_MOUSE_RE = _px_re.compile(r"MOUSE\(row=(\d+),\s*col=(\d+)\)")
_PX_MAX_CANDIDATES = 8
_PX_STALL_ACTIONS = 150
OURS_PROMPT_COUNTS = {"prompts": 0, "with_clicks": 0, "dead_classes": 0, "errors": 0}

_PX_SCORING_LINE = (
    "Scoring (exact): a cleared level scores min(1.15, (human_actions / your_actions)^2), level k has weight k, "
    "and an uncleared level scores 0. Every executed action counts, including clicks that change nothing and RESET. "
    "Clearing levels matters most; once a plan is verified, execute it as one batch."
)

assert _PX_CLS._build_user_prompt.__code__.co_varnames[:2] == ("self", "action_num"), "prompt_extras: signature moved"
_px_orig_build = _PX_CLS._build_user_prompt
_px_orig_compact = _PX_CLS._compact_action_result


def _px_components(grid):
    """4-connected same-color components: list of dicts with color, cells, bbox, centroid."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    seen = [[False] * cols for _ in range(rows)]
    comps = []
    for r0 in range(rows):
        for c0 in range(cols):
            if seen[r0][c0]:
                continue
            color = grid[r0][c0]
            stack = [(r0, c0)]
            seen[r0][c0] = True
            cells = []
            while stack:
                r, c = stack.pop()
                cells.append((r, c))
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            rs = [p[0] for p in cells]
            cs = [p[1] for p in cells]
            comps.append({
                "color": color,
                "cells": cells,
                "size": len(cells),
                "bbox": (min(rs), min(cs), max(rs), max(cs)),
            })
    return comps


def _px_component_at(grid, r, c):
    """Color and size of the component containing (r, c), or None when out of range."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if not (0 <= r < rows and 0 <= c < cols):
        return None
    color = grid[r][c]
    seen = {(r, c)}
    stack = [(r, c)]
    while stack:
        cr, cc = stack.pop()
        for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
            if (nr, nc) not in seen and 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == color:
                seen.add((nr, nc))
                stack.append((nr, nc))
    return (color, len(seen))


def _px_is_hud(comp, rows, cols):
    """Thin lines or bars hugging the border: timers, step bars. Square-ish edge objects stay (they are often buttons)."""
    r0, c0, r1, c1 = comp["bbox"]
    h, w = r1 - r0 + 1, c1 - c0 + 1
    edge = r0 <= 1 or c0 <= 1 or r1 >= rows - 2 or c1 >= cols - 2
    if not edge:
        return False
    thick, length = min(h, w), max(h, w)
    return thick <= 1 or (thick <= 3 and length >= 3 * thick + 5)


def _px_dead_classes(history_entries, level):
    """(color, size) classes clicked on this level >=2 times with no visible board change and never with one."""
    dead, live = {}, set()
    prev = None
    for entry in history_entries:
        frame = entry.frame
        if prev is not None and frame is not None and frame.level == level and prev.level == level:
            m = _PX_MOUSE_RE.search(entry.action or "")
            if m:
                key = _px_component_at(prev.grid, int(m.group(1)), int(m.group(2)))
                if key is not None:
                    if frame.grid == prev.grid:
                        dead[key] = dead.get(key, 0) + 1
                    else:
                        live.add(key)
        prev = frame
    return {k for k, n in dead.items() if n >= 2 and k not in live}


def _px_click_lines(frame, history_entries):
    grid = frame.grid
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if not rows or not cols:
        return []
    comps = _px_components(grid)
    total = rows * cols
    color_area = {}
    for comp in comps:
        color_area[comp["color"]] = color_area.get(comp["color"], 0) + comp["size"]
    dead = _px_dead_classes(history_entries, frame.level)
    scored = []
    per_signature = {}
    for comp in comps:
        if comp["size"] > total * 0.15 or _px_is_hud(comp, rows, cols):
            continue
        key = (comp["color"], comp["size"])
        if key in dead:
            continue
        per_signature[key] = per_signature.get(key, 0) + 1
        if per_signature[key] > 2:
            continue
        rarity = 1.0 - color_area[comp["color"]] / total
        size_score = 1.0 if 4 <= comp["size"] <= 64 else (0.5 if comp["size"] < 4 else 0.3)
        # click the member cell nearest the bbox center, so concave shapes still get a real cell
        r0, c0, r1, c1 = comp["bbox"]
        cr, cc = (r0 + r1) / 2.0, (c0 + c1) / 2.0
        tr, tc = min(comp["cells"], key=lambda p: (p[0] - cr) ** 2 + (p[1] - cc) ** 2)
        scored.append((0.5 * rarity + 0.5 * size_score, tr, tc, comp["color"], comp["size"]))
    scored.sort(key=lambda item: -item[0])
    top = scored[:_PX_MAX_CANDIDATES]
    lines = []
    if top:
        rendered = ", ".join(f"(row={r}, col={c}) {_PX_COLORS[max(0, min(15, int(color)))]}x{size}" for _, r, c, color, size in top)
        lines.append(f"Click candidates (salient non-HUD objects, a hint not a rule): {rendered}.")
    if dead:
        OURS_PROMPT_COUNTS["dead_classes"] += 1
        rendered_dead = ", ".join(f"{_PX_COLORS[max(0, min(15, int(color)))]}x{size}" for color, size in sorted(dead)[:6])
        lines.append(f"Clicked on this level 2+ times with no visible board change (omitted above): {rendered_dead}.")
    return lines


def _px_level_actions(history_entries, level):
    n = 0
    for entry in reversed(history_entries):
        if entry.frame is None or entry.frame.level != level or not entry.action:
            break
        n += 1
    return n


def _px_build(self, action_num, *args, **kwargs):
    prompt = _px_orig_build(self, action_num, *args, **kwargs)
    try:
        OURS_PROMPT_COUNTS["prompts"] += 1
        frame = kwargs.get("current_frame")
        history_entries = kwargs.get("history_entries") or []
        valid_actions = kwargs.get("valid_actions") or []
        extra = []
        if _PX_FLAGS.get("scoring"):
            extra.append(_PX_SCORING_LINE)
        if _PX_FLAGS.get("pacing"):
            pacing = []
            budget = getattr(self, "_ours_time_remaining", None)
            if budget is not None:
                remaining = max(0.0, budget[0] - (_px_time.monotonic() - budget[1]))
                pacing.append(f"Time left for this game: about {int(round(remaining / 60.0))} min.")
            if frame is not None:
                spent = _px_level_actions(history_entries, frame.level)
                pacing.append(f"Actions spent on this level: {spent}.")
                if spent >= _PX_STALL_ACTIONS:
                    pacing.append("That is a lot without clearing it: test a different hypothesis about the goal or the controls instead of repeating the current approach.")
            if pacing:
                extra.append(" ".join(pacing))
        # the solver passes engine names (ACTION6); the harness's own normalizer maps them to MOUSE
        if _PX_FLAGS.get("clicks") and frame is not None and "MOUSE" in _tool_agent._normalize_valid_actions(valid_actions):
            click_lines = _px_click_lines(frame, history_entries)
            if click_lines:
                OURS_PROMPT_COUNTS["with_clicks"] += 1
                extra.extend(click_lines)
        if not extra:
            return prompt
        if OURS_PROMPT_COUNTS["prompts"] == 1:
            print(f"OURS_PROMPT_EXTRAS first lines={len(extra)}", flush=True)
        return prompt + "\n" + "\n".join(extra)
    except Exception as exc:
        OURS_PROMPT_COUNTS["errors"] += 1
        if OURS_PROMPT_COUNTS["errors"] == 1:
            print(f"OURS_PROMPT_EXTRAS_ERROR first {type(exc).__name__}: {exc}", flush=True)
        return prompt


def _px_compact(self, payload):
    out = _px_orig_compact(self, payload)
    try:
        remaining = payload.get("time_remaining_seconds") if isinstance(payload, dict) else None
        if remaining is not None:
            self._ours_time_remaining = (float(remaining), _px_time.monotonic())
    except Exception:
        pass
    return out


_px_build.__wrapped__ = _px_orig_build
_px_compact.__wrapped__ = _px_orig_compact
_PX_CLS._build_user_prompt = _px_build
_PX_CLS._compact_action_result = _px_compact
print(f"OURS_PROMPT_EXTRAS ok flags={_PX_FLAGS}", flush=True)
