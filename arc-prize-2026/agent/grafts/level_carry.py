# ---- ours/level_carry: carry what cleared a level into the next one (Depth Engine, part 2).
# On a level transition the harness wipes the six working-note slots, so every level is re-learned from scratch.
# Clearing a level is the strongest evidence the agent gets: the world, goal and action models it held at that
# moment worked. This graft snapshots those slots just before the wipe and writes them into the harness's own
# `cross_level_notes` slot, which the wipe keeps and every prompt already shows as "Cross-level notes". It also
# records how many actions the level took and the last few actions that finished it.
# Only the latest two cleared levels are kept, capped at _LC_MAX_CHARS, so the prompt stays short.
# Game over and run completion are left to the original method. Expects `_tool_agent` in scope. Fail-open.
import inspect as _lc_inspect

_LC_CLS = _tool_agent.ToolAgent
_lc_src = _lc_inspect.getsource(_LC_CLS._update_summarized_knowledge_from_step_summary)
assert 'summary.get("level_transition")' in _lc_src and '"cross_level_notes"' not in _lc_src.split("for key in")[1], \
    "level_carry: wipe logic moved"
_lc_orig = _LC_CLS._update_summarized_knowledge_from_step_summary
_LC_SLOTS = (("world_model", "World"), ("goal_model", "Goal"), ("action_model", "Actions"))
_LC_SLOT_CHARS = 220
_LC_MAX_CHARS = 900
OURS_LEVEL_CARRY_COUNTS = {"carried": 0, "empty": 0, "errors": 0}


def _lc_clip(text, limit):
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _lc_update(self):
    snapshot = None
    try:
        summary = self._last_step_summary
        if summary and summary.get("level_transition") and not summary.get("run_complete"):
            knowledge = self._summarized_knowledge
            parts = [f"{label}: {_lc_clip(knowledge.get(key), _LC_SLOT_CHARS)}" for key, label in _LC_SLOTS if knowledge.get(key)]
            finishing = [a for a in (summary.get("executed_actions") or []) if a][-6:]
            # no level number: the engine's level index base differs between places, and a wrong number misleads
            head = "The previous level was cleared"
            if finishing:
                head += " (it ended with " + ", ".join(finishing) + ")"
            if parts:
                snapshot = head + " using this understanding. " + "; ".join(parts) + \
                    ". Mechanics often carry over to the next level but layouts change: test it cheaply before relying on it."
            else:
                OURS_LEVEL_CARRY_COUNTS["empty"] += 1
                snapshot = head + "."
    except Exception:
        OURS_LEVEL_CARRY_COUNTS["errors"] += 1
        snapshot = None
    result = _lc_orig(self)
    if snapshot:
        try:
            previous = [p for p in str(self._summarized_knowledge.get("cross_level_notes") or "").split(" || ") if p.strip()]
            kept = (previous + [snapshot])[-2:]
            notes = " || ".join(kept)
            while len(notes) > _LC_MAX_CHARS and len(kept) > 1:
                kept = kept[1:]
                notes = " || ".join(kept)
            self._summarized_knowledge["cross_level_notes"] = _lc_clip(notes, _LC_MAX_CHARS)
            OURS_LEVEL_CARRY_COUNTS["carried"] += 1
            print(f"OURS_LEVEL_CARRY {OURS_LEVEL_CARRY_COUNTS}", flush=True)
        except Exception:
            OURS_LEVEL_CARRY_COUNTS["errors"] += 1
    return result


_lc_update.__wrapped__ = _lc_orig
_LC_CLS._update_summarized_knowledge_from_step_summary = _lc_update
print("OURS_LEVEL_CARRY ok", flush=True)
