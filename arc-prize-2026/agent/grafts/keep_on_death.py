# ---- ours/keep_on_death: keep the world-model note across a GAME_OVER (death) on the same level.
# The harness wipes all six summarized-knowledge slots on level_transition, run_complete AND game_over.
# A death is not a new level: the rules, goal and what the agent learned still apply, but the wipe makes it
# re-derive the level from scratch. This keeps the slots on game_over (adding one line saying the last attempt
# died) and still wipes on a real level transition or run completion. Idea: Thuitanium's B101 (never run).
# Expects `_tool_agent` in scope. Fail-open: on any error the original method runs.
import inspect as _kd_inspect

_KD_CLS = _tool_agent.ToolAgent
_kd_src = _kd_inspect.getsource(_KD_CLS._update_summarized_knowledge_from_step_summary)
assert 'summary.get("game_over")' in _kd_src and 'summary.get("level_transition")' in _kd_src, \
    "keep_on_death: wipe condition moved"
_kd_orig = _KD_CLS._update_summarized_knowledge_from_step_summary
OURS_KEEP_ON_DEATH_COUNTS = {"kept": 0, "wiped": 0, "errors": 0}


def _kd_update(self):
    try:
        summary = self._last_step_summary
        if summary and summary.get("game_over") and not summary.get("level_transition") and not summary.get("run_complete"):
            OURS_KEEP_ON_DEATH_COUNTS["kept"] += 1
            findings = self._summarized_knowledge.get("recent_findings", "")
            note = "The previous attempt at this level ended in GAME_OVER; avoid repeating what caused it."
            if note not in findings:
                self._summarized_knowledge["recent_findings"] = (findings + " " + note).strip()
            if OURS_KEEP_ON_DEATH_COUNTS["kept"] in (1, 10) or OURS_KEEP_ON_DEATH_COUNTS["kept"] % 100 == 0:
                print(f"OURS_KEEP_ON_DEATH {OURS_KEEP_ON_DEATH_COUNTS}", flush=True)
            return None
        if summary and (summary.get("level_transition") or summary.get("run_complete")):
            OURS_KEEP_ON_DEATH_COUNTS["wiped"] += 1
    except Exception as exc:
        OURS_KEEP_ON_DEATH_COUNTS["errors"] += 1
        if OURS_KEEP_ON_DEATH_COUNTS["errors"] == 1:
            print(f"OURS_KEEP_ON_DEATH_ERROR first {type(exc).__name__}: {exc}", flush=True)
    return _kd_orig(self)


_kd_update.__wrapped__ = _kd_orig
_KD_CLS._update_summarized_knowledge_from_step_summary = _kd_update
print("OURS_KEEP_ON_DEATH ok", flush=True)
