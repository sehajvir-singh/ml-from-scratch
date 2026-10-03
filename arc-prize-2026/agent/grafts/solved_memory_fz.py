# ---- ours/solved_memory_fz: pin each solved level's winning action sequence (Franzen harness) ----
# Evidence, not advice: sirikilohit's Milestone 2 write-up found that pinning what was learned on cleared levels was
# "the only text addition that helped" (+2.8), while every advice line hurt. Franzen keeps the history across levels
# but trims it in large blocks (~118k -> ~59k tokens), so on long games the winning moves of early levels fall out of
# context. This graft records, per level, the actions of the attempt that cleared it (deaths reset the record) and
# shows them, run-length compressed, to the model.
# Cache: by default (OURS_SM_MODE=append) the system prompt is left untouched - rewriting it changes the first tokens of
# every request and forces a full prefill of the ~60-120k-token history. The block is instead added to the turn opener
# once when a level is pinned, and again only when the history trim has evicted it. OURS_SM_MODE=system keeps the old
# behaviour (rewrite the system prompt), for A/B runs.
# Hook: ToolAgent._prepare_auto_diff(self, current_frame, previous_step_summary), called once per analyzer turn with
# the previous turn's summary (executed_actions, game_over, level_transition). Expects `_tool_agent` in scope.
# Fail-open: any error leaves the original behaviour.
_SM_CLS = _tool_agent.ToolAgent
assert _SM_CLS._prepare_auto_diff.__code__.co_varnames[:3] == ("self", "current_frame", "previous_step_summary"), \
    "solved_memory_fz: _prepare_auto_diff signature moved"
_sm_orig_prepare = _SM_CLS._prepare_auto_diff
_SM_MAX_ACTIONS = 60      # per level, most recent kept
_SM_MAX_CHARS = 1800      # whole pinned block
_SM_MARK = "Solved levels in this game (recorded by the harness"
_SM_MODE = __import__("os").environ.get("OURS_SM_MODE", "append").strip().lower()
OURS_SM_COUNTS = {"turns": 0, "levels_pinned": 0, "deaths": 0, "shown": 0, "reshown": 0, "errors": 0}


def _sm_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
    return ""


def _sm_in_history(agent):
    for m in getattr(agent, "_history_messages", None) or []:
        if isinstance(m, dict) and _SM_MARK in _sm_text(m.get("content")):
            return True
    return False


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
    lines = [_SM_MARK + ": the exact actions of the attempt that cleared each level, oldest first). "
             "Later levels often reuse these mechanics."]
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
    extra = None
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
                    self._ours_sm_new = True
                    if _SM_MODE == "system":
                        self._system_prompt = self._ours_sm_base_prompt + "\n\n" + _sm_block(self._ours_sm_solved)
                    OURS_SM_COUNTS["levels_pinned"] += 1
                    if OURS_SM_COUNTS["levels_pinned"] in (1, 10) or OURS_SM_COUNTS["levels_pinned"] % 50 == 0:
                        print(f"OURS_SOLVED_MEMORY {OURS_SM_COUNTS}", flush=True)
                self._ours_sm_attempt = []
        cur = getattr(current_frame, "level", None)
        if cur is not None:
            self._ours_sm_level = cur
        if _SM_MODE != "system" and self._ours_sm_solved:
            if getattr(self, "_ours_sm_new", False):
                extra = _sm_block(self._ours_sm_solved)
                OURS_SM_COUNTS["shown"] += 1
            elif not _sm_in_history(self):   # evicted by the history trim: show it again
                extra = _sm_block(self._ours_sm_solved)
                OURS_SM_COUNTS["reshown"] += 1
            self._ours_sm_new = False
    except Exception:
        OURS_SM_COUNTS["errors"] += 1
        extra = None
    lines = _sm_orig_prepare(self, current_frame, previous_step_summary, *args, **kwargs)
    if extra:
        try:
            lines = list(lines) + [extra]
        except Exception:
            OURS_SM_COUNTS["errors"] += 1
    return lines


_sm_prepare.__wrapped__ = _sm_orig_prepare
_SM_CLS._prepare_auto_diff = _sm_prepare
print(f"OURS_SOLVED_MEMORY ok mode={_SM_MODE}", flush=True)
