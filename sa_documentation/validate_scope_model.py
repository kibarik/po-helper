"""Валидатор Blueprint Scope Model (scope-model.yaml).

См. sa_documentation/blueprint_schema.md и spec
docs/superpowers/specs/2026-06-25-blueprint-pipeline-design.md (§4).
"""
import pathlib
import re
import yaml

_SCOPE = {"changed", "affected", "context"}
_KINDS = {"bft", "nexus", "web", "interview"}


def validate_scope_model(path):
    """Проверить scope-model.yaml. Возвращает список строк-ошибок (пустой = OK)."""
    errs = []
    path = pathlib.Path(path)
    if not path.exists():
        return [f"missing {path}"]

    m = yaml.safe_load(path.read_text()) or {}

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(m.get("task", ""))):
        errs.append(f"task invalid ascii-slug: {m.get('task')!r}")
    if m.get("mode") not in ("enrich", "scratch"):
        errs.append(f"mode must be enrich|scratch: {m.get('mode')!r}")

    # sources
    sources = m.get("sources") or []
    if not sources:
        errs.append("sources is required and non-empty")
    src_ids = set()
    for s in sources:
        sid = s.get("id")
        if sid in src_ids:
            errs.append(f"duplicate source id: {sid!r}")
        src_ids.add(sid)
        if s.get("kind") not in _KINDS:
            errs.append(f"source {sid!r} kind invalid: {s.get('kind')!r}")

    def _check_src(holder, where):
        ref = (holder or {}).get("source")
        if ref not in src_ids:
            errs.append(f"{where} source unknown: {ref!r}")

    _check_src(m.get("trigger"), "trigger")
    _check_src(m.get("end_state"), "end_state")

    # journey
    journey = m.get("journey") or []
    if not journey:
        errs.append("journey is required and non-empty")
    steps = set()
    for j in journey:
        st = j.get("step")
        if st in steps:
            errs.append(f"duplicate journey step: {st!r}")
        steps.add(st)
        _check_src(j, f"journey step {st}")

    # layers
    layers = m.get("layers") or []
    if not layers:
        errs.append("layers is required and non-empty")
    layer_ids = set()
    for l in layers:
        lid = l.get("id")
        if lid in layer_ids:
            errs.append(f"duplicate layer id: {lid!r}")
        layer_ids.add(lid)

    # cells
    for c in m.get("cells") or []:
        if c.get("scope") not in _SCOPE:
            errs.append(f"cell scope invalid: {c.get('scope')!r}")
        if c.get("step") not in steps:
            errs.append(f"cell step unknown: {c.get('step')!r}")
        if c.get("layer") not in layer_ids:
            errs.append(f"cell layer unknown: {c.get('layer')!r}")
        _check_src(c, f"cell step={c.get('step')} layer={c.get('layer')}")

    return errs


if __name__ == "__main__":
    import sys
    e = validate_scope_model(sys.argv[1])
    print("\n".join(e) or "OK")
