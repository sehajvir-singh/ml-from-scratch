# ---- ours/note_fill: world-model slots also filled from the model's reasoning.
# Adapted from Thuitanium's thui-a10 graft (MIT-0, github.com/Sahasawatt/arc-agi-3-agent).
# The harness refreshes its "working world model" note only from VISIBLE assistant text, but
# Qwen3.8-Flash-Next usually thinks and then calls the tool with no prose, so the note stays
# empty for whole games. After each response, parse the reasoning with the harness's own
# extractor and fill any slot the visible text left empty, capped at _NF_CAP chars.
# Expects `_tool_agent` (inference.agent.tool_agent) in scope. Fail-open: never costs a response.
import inspect as _nf_inspect
import sys as _nf_sys

_NF_CAP = 488
_NF_CLS = _tool_agent.ToolAgent
_nf_src = _nf_inspect.getsource(_NF_CLS.analyze)
assert _nf_src.count("response_meta = _format_model_response_meta(") == 1, "note_fill: meta call site moved"
assert _nf_src.count("reasoning=reasoning,") == 1 and _nf_src.count("content=content,") == 1, \
    "note_fill: meta call no longer passes reasoning/content by keyword"
_nf_orig = _tool_agent._format_model_response_meta
OURS_NOTE_FILL_COUNTS = {"calls": 0, "responses_filled": 0, "slots_filled": 0, "no_self": 0, "errors": 0}


def _nf_meta(*args, **kwargs):
    out = _nf_orig(*args, **kwargs)
    try:
        OURS_NOTE_FILL_COUNTS["calls"] += 1
        agent = _nf_sys._getframe(1).f_locals.get("self")
        if not isinstance(agent, _NF_CLS):
            OURS_NOTE_FILL_COUNTS["no_self"] += 1
            return out
        reasoning = kwargs.get("reasoning") or ""
        if not reasoning.strip():
            return out
        content = kwargs.get("content") or ""
        seen = _tool_agent._extract_scientist_note(content) if content.strip() else {}
        got = _tool_agent._extract_scientist_note(reasoning)
        n = 0
        for key, value in got.items():
            if value and not seen.get(key):
                agent._summarized_knowledge[key] = _tool_agent._normalize_summary_text(value, max_chars=_NF_CAP)
                n += 1
        if n:
            OURS_NOTE_FILL_COUNTS["slots_filled"] += n
            OURS_NOTE_FILL_COUNTS["responses_filled"] += 1
            if OURS_NOTE_FILL_COUNTS["responses_filled"] in (1, 10) or OURS_NOTE_FILL_COUNTS["responses_filled"] % 200 == 0:
                print(f"OURS_NOTE_FILL {OURS_NOTE_FILL_COUNTS}", flush=True)
    except Exception as exc:
        OURS_NOTE_FILL_COUNTS["errors"] += 1
        if OURS_NOTE_FILL_COUNTS["errors"] == 1:
            print(f"OURS_NOTE_FILL_ERROR first {type(exc).__name__}: {exc}", flush=True)
    return out


_nf_meta.__wrapped__ = _nf_orig
_tool_agent._format_model_response_meta = _nf_meta
assert _tool_agent._format_model_response_meta is _nf_meta, "note_fill: wrapper not installed"
print(f"OURS_NOTE_FILL ok cap={_NF_CAP}", flush=True)
