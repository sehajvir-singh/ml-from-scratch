# ---- ours/progress_notice_fz: factual progress counter for a level that is not moving (Franzen harness) ----
# Evidence, not advice: write-ups found that added advice text costs points while recorded facts help, and Tufa named
# wrong-goal loops as a main failure. Franzen's opener reports deaths in detail but never says how long the current
# level has been going nowhere. This graft counts, per level: actions, analysis turns, deaths, distinct boards seen at
# turn starts, and turns since the board last showed a new state. It adds ONE line of counts to the turn opener when
# the action count crosses a doubling threshold (40, 80, 160, ...) or when the board has shown nothing new for
# OURS_PN_STALE_TURNS turns. The line states counts only: no suggestion of what to do.
# Hook: ToolAgent._prepare_auto_diff(self, current_frame, previous_step_summary), as solved_memory_fz; both can be
# loaded (each wraps whatever is installed). Expects `_tool_agent` in scope. Fail-open.
import hashlib as _pn_hashlib
import os as _pn_os

_PN_CLS = _tool_agent.ToolAgent
assert _PN_CLS._prepare_auto_diff.__code__.co_varnames[:3] == ("self", "current_frame", "previous_step_summary") \
    or hasattr(_PN_CLS._prepare_auto_diff, "__wrapped__"), "progress_notice_fz: _prepare_auto_diff signature moved"
_pn_orig_prepare = _PN_CLS._prepare_auto_diff
_PN_FIRST = max(5, int(_pn_os.environ.get("OURS_PN_ACTIONS", "40")))
_PN_STALE = max(2, int(_pn_os.environ.get("OURS_PN_STALE_TURNS", "4")))
OURS_PN_COUNTS = {"turns": 0, "notices": 0, "stale_notices": 0, "errors": 0}


def _pn_board_key(frame):
    grid = getattr(frame, "grid", None)
    if grid is None:
        return None
    return _pn_hashlib.blake2b(repr(grid).encode(), digest_size=8).digest()


def _pn_reset(self, level):
    self._ours_pn = {"level": level, "actions": 0, "turns": 0, "deaths": 0, "boards": set(), "since_new": 0,
                     "next": _PN_FIRST, "stale_said": False}


def _pn_line(st, reason):
    return (f"Progress count (harness, level {st['level']}): {st['actions']} actions over {st['turns']} analysis turns "
            f"since this level began; {st['deaths']} game over(s) on this level; {len(st['boards'])} distinct boards "
            f"seen at turn starts; the board at turn start has not changed to a new state for {st['since_new']} "
            f"turn(s). [{reason}]")


def _pn_prepare(self, current_frame, previous_step_summary, *args, **kwargs):
    extra = None
    try:
        OURS_PN_COUNTS["turns"] += 1
        level = getattr(current_frame, "level", None)
        st = getattr(self, "_ours_pn", None)
        if st is None or (level is not None and level != st["level"]):
            _pn_reset(self, level)
            st = self._ours_pn
        s = previous_step_summary or {}
        key = (s.get("start_action_num"), s.get("end_action_num"), s.get("executed_count")) if s else None
        if key is not None and key[1] is None:
            key = ("id", id(s))
        fresh = key is None or key != getattr(self, "_ours_pn_last_key", None)
        if key is not None:
            self._ours_pn_last_key = key
        if fresh:   # a resumed (yielded) turn repeats its summary: count it once
            st["turns"] += 1
            if s and not s.get("stale") and not s.get("level_transition"):
                acts = s.get("executed_actions")
                if isinstance(acts, list):
                    st["actions"] += len(acts)
                if s.get("game_over"):
                    st["deaths"] += 1
            b = _pn_board_key(current_frame)
            if b is not None:
                if b in st["boards"]:
                    st["since_new"] += 1
                else:
                    st["boards"].add(b)
                    st["since_new"] = 0
                    st["stale_said"] = False
            if st["actions"] >= st["next"]:
                while st["next"] <= st["actions"]:
                    st["next"] *= 2
                extra = _pn_line(st, f"shown at {_PN_FIRST}, {2 * _PN_FIRST}, {4 * _PN_FIRST}, ... actions")
                OURS_PN_COUNTS["notices"] += 1
            elif st["since_new"] >= _PN_STALE and not st["stale_said"]:
                st["stale_said"] = True
                extra = _pn_line(st, f"shown once when no new board for {_PN_STALE} turns")
                OURS_PN_COUNTS["stale_notices"] += 1
            n = OURS_PN_COUNTS["notices"] + OURS_PN_COUNTS["stale_notices"]
            if extra and (n in (1, 10) or n % 100 == 0):
                print(f"OURS_PROGRESS_NOTICE {OURS_PN_COUNTS}", flush=True)
    except Exception:
        OURS_PN_COUNTS["errors"] += 1
        extra = None
    lines = _pn_orig_prepare(self, current_frame, previous_step_summary, *args, **kwargs)
    if extra:
        try:
            lines = list(lines) + [extra]
        except Exception:
            OURS_PN_COUNTS["errors"] += 1
    return lines


_pn_prepare.__wrapped__ = _pn_orig_prepare
_PN_CLS._prepare_auto_diff = _pn_prepare
print(f"OURS_PROGRESS_NOTICE ok first={_PN_FIRST} stale={_PN_STALE}", flush=True)
