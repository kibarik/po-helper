# Blueprint Scope Model — schema

Каноническая промежуточная модель pipeline `/blueprint-*`. Общая для режимов
ENRICH (из БФТ) и SCRATCH (исследование). Хранится в
`GROUND/BLUEPRINT/<task>/scope-model.yaml`. Валидатор: `validate_scope_model.py`.

## Правила (валидатор требует)

1. `task` — ascii-slug `[a-z0-9][a-z0-9-]*`.
2. `mode` — `enrich` | `scratch`.
3. `sources` — непустой список; каждый: `{id, kind, ref}`; `kind ∈ {bft,nexus,web,interview}`; `id` уникален.
4. `trigger`, `end_state` — обязательны, у каждого `source`, ссылающийся на существующий `sources[].id`.
5. `journey` — непустой список шагов `{step:int, name, actor?, source}`; `step` уникален; каждый `source` существует.
6. `layers` — непустой список `{id, name}`; `id` уникален.
7. `cells` — список `{step, layer, action, scope, source}`; `scope ∈ {changed,affected,context}`;
   `step` существует в `journey`; `layer` существует в `layers`; `source` существует.
8. **Zero-hallucination:** любой ссылочный `source` ОБЯЗАН существовать в `sources`. Узел без источника недопустим — он уходит в `gaps`.
9. `gaps` — список `{about, note}` (может быть пустым).

## YAML-структура

```yaml
task: <slug>
title: <строка>
mode: enrich | scratch
created: <YYYY-MM-DD>
confidence: <0..1>
sources:
  - {id: S1, kind: bft, ref: "БФТ §2.1"}
trigger: {actor: <строка>, event: <строка>, source: S1}
end_state: {outcome: <строка>, source: S1}
actors:
  - {id: A1, name: <строка>, source: S1}
journey:
  - {step: 1, name: <строка>, actor: A1, source: S1}
layers:
  - {id: L_actor, name: "Actor / Customer"}
  - {id: L_frontstage, name: "Frontstage / UX-UI"}
  - {id: L_backstage, name: "Backstage / App-logic"}
  - {id: L_integration, name: "Integrations / Services"}
  - {id: L_data, name: "Data"}
  - {id: L_external, name: "External / Support"}
cells:
  - {step: 1, layer: L_frontstage, action: <строка>, scope: changed, source: S1}
scope_of_change:
  - {layer: L_backstage, summary: <строка>, marker: changed, source: S1}
gaps:
  - {about: <строка>, note: <строка>}
```

## Frontmatter `blueprint.md` (облегчённый, blueprint-специфичный)

```yaml
---
artifact: blueprint
task: <slug>
mode: enrich | scratch
confidence: <0..1>
sources: [<ref>, ...]   # человекочитаемые refs из scope-model.sources
created: <YYYY-MM-DD>
tags: [blueprint, scope]
---
```
