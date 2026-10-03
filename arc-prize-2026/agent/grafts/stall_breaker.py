# ---- ours/stall_breaker: concrete untried interactions when a level stalls (Depth Engine, part 3).
# The 25-game census showed thrashing: when the clock ran out, the level in progress had often taken several times
# a human's whole-level action count (vc33 264 vs 61, sc25 254 vs 32, s5i5 218 vs 89). Generic "try something
# else" text did not help (m2 carried such a line and scored lower). So once a level passes _SB_THRESHOLD actions,
# this adds ONE line naming what has not been tried on this level: object classes (color x size) never clicked, and
# valid keys never pressed. Nothing is blocked or forced. Expects `_tool_agent` in scope. Fail-open.
import re as _sb_re

_SB_CLS = _tool_agent.ToolAgent
assert _SB_CLS._build_user_prompt.__code__.co_varnames[:2] == ("self", "action_num"), "stall_breaker: signature moved"
_sb_orig_build = _SB_CLS._build_user_prompt
_SB_THRESHOLD = 80
_SB_MAX_ITEMS = 6
_SB_COLORS = "WwgGcBMPRbSYOrNp"  # inference.utils.grid_utils.ARC_COLOR_CHARS
_SB_MOUSE_RE = _sb_re.compile(r"MOUSE\(row=(\d+),\s*col=(\d+)\)")
_SB_KEYS = ("UP", "DOWN", "LEFT", "RIGHT", "SPACE", "ACTION7")
OURS_STALL_COUNTS = {"prompts": 0, "stalled": 0, "lines": 0, "errors": 0}


def _sb_objects(grid):
    """{(color, size): (row, col)} for same-color 4-connected components up to 5% of the board, minus border strips."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    seen = [[False] * cols for _ in range(rows)]
    out = {}
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
            band = all(r <= 2 or r >= rows - 3 or c <= 2 or c >= cols - 3 for r, c in cells)   # HUD bars, counters
            if len(cells) <= rows * cols * 0.05 and not band:
                out.setdefault((color, len(cells)), cells[len(cells) // 2])
    return out


def _sb_class_at(grid, r, c):
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


def _sb_level_start(history_entries, level):
    """Index of the first entry of the current run on this level (the level's entries are a suffix of the history)."""
    i = len(history_entries)
    while i > 0:
        entry = history_entries[i - 1]
        if entry.frame is None or entry.frame.level != level:
            break
        i -= 1
    return i


def _sb_line(frame, history_entries, valid):
    start = _sb_level_start(history_entries, frame.level)
    spent = sum(1 for entry in history_entries[start:] if entry.action)
    if spent < _SB_THRESHOLD:
        return None
    OURS_STALL_COUNTS["stalled"] += 1
    tried_keys, tried_classes = set(), set()
    for i in range(start, len(history_entries)):
        entry = history_entries[i]
        m = _SB_MOUSE_RE.search(entry.action or "")
        if m:
            before = history_entries[i - 1].frame if i > 0 else None   # the board the click was made on
            if before is not None:
                cls = _sb_class_at(before.grid, int(m.group(1)), int(m.group(2)))
                if cls:
                    tried_classes.add(cls)
        elif entry.action:
            tried_keys.add(entry.action.strip().upper().split("(")[0])
    parts = []
    if "MOUSE" in valid:
        untried = [(cls, pos) for cls, pos in _sb_objects(frame.grid).items() if cls not in tried_classes]
        untried.sort(key=lambda item: item[0][1])        # small objects first: buttons and tokens
        if untried:
            parts.append("clicks on " + ", ".join(
                f"{_SB_COLORS[max(0, min(15, int(color)))]}x{size} at (row={pos[0]}, col={pos[1]})"
                for (color, size), pos in untried[:_SB_MAX_ITEMS]))
    keys = [k for k in _SB_KEYS if k in valid and k not in tried_keys]
    if keys:
        parts.append("keys " + ", ".join(keys))
    if not parts:
        return None
    return (f"Stall check: {spent} actions on this level without clearing it. Not tried on this level yet: "
            + "; ".join(parts) + ". Test one of these once before repeating earlier moves.")


def _sb_build(self, action_num, *args, **kwargs):
    prompt = _sb_orig_build(self, action_num, *args, **kwargs)
    try:
        OURS_STALL_COUNTS["prompts"] += 1
        frame = kwargs.get("current_frame")
        if frame is None or not frame.grid:
            return prompt
        valid = _tool_agent._normalize_valid_actions(kwargs.get("valid_actions") or [])
        line = _sb_line(frame, kwargs.get("history_entries") or [], valid)
        if not line:
            return prompt
        OURS_STALL_COUNTS["lines"] += 1
        if OURS_STALL_COUNTS["lines"] in (1, 20) or OURS_STALL_COUNTS["lines"] % 200 == 0:
            print(f"OURS_STALL {OURS_STALL_COUNTS}", flush=True)
        return prompt + "\n" + line
    except Exception:
        OURS_STALL_COUNTS["errors"] += 1
        return prompt


_sb_build.__wrapped__ = _sb_orig_build
_SB_CLS._build_user_prompt = _sb_build
print("OURS_STALL_BREAKER ok", flush=True)
