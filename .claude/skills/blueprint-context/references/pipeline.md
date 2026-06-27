# Blueprint Pipeline — обзор

```
/blueprint-context  → выбор режима (ENRICH|SCRATCH)
   ├─ [enrich]  /blueprint-extract   (Scope Model из БФТ)
   └─ [scratch] /blueprint-discover  (Scope Model исследованием: context-gen, scouting, problem-analyst, Nexus)
/blueprint-model    → нормализация + валидация (точка слияния)
/blueprint-render   → Grid + Mermaid + render-гейт → GROUND/BLUEPRINT/<task>/blueprint.md
```

- Каноническая модель: `GROUND/BLUEPRINT/<task>/scope-model.yaml` (схема `sa_documentation/blueprint_schema.md`).
- Валидатор: `sa_documentation/validate_scope_model.py`.
- Render-гейт: `sa_documentation/blueprint_render.py` (mmdc → npx → блок).
- Связь с экосистемой: после `bft-writer`; верхнеуровневый мост к `/arch-gen` (C4) и `/data-trace` (dataflow).
- Spec: `docs/superpowers/specs/2026-06-25-blueprint-pipeline-design.md`.
