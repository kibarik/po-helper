# prd-research — как писать discovery-узел

Каждый узел = markdown-нота в `GROUND/NEXUS/<slug>/<node_id>.md` с YAML-frontmatter по Node schema (§2 + §2.3 `sa_documentation/nexus_schema.md`).

## Обязательный frontmatter discovery-узла

```yaml
---
nexus: market            # slug из GROUND/NEXUS/_registry.yaml
node_id: idea-lens-market-1   # ascii, стабильный
node_type: bet                # см. §3.1 nexus_schema — discovery artifact-тип
paf_step: 1
sprint_phase: scout
kind: empirical
owner: Portfolio Manager      # роль из roster (RACI market → Portfolio Manager)
confidence: 0.3               # CP по источнику (см. шкалу §2.3)
sources: ["onboarding:interview", "https://... (2026-07-06)"]
updated: 2026-07-06
ttl_days: 90                  # market/customer/product=90, growth=60
ripeness: fresh
hyp_status: hypothesis        # §2.3 lifecycle
depends_on: []                # node_id первопричин из других шагов
tags: [discovery]
---
```

## Правила
- Пустой источник → не создавать узел (workslop). PO-суждение — валидный источник `["onboarding:interview"]`, но CP низкий (0.2–0.4).
- В тело узла-допущения ставить пометку: `> ⚠️ гипотеза discovery, CP отражает доверие к допущению, не факт.`
- `depends_on` заполнять при кросс-шаговой причинности → включает контур рассогласования.
- `ttl_days`: продуктовые Нексусы market/customer/product = 90, growth = 60 (product явно = 90).
- Для узла `hyp_status: parked` — `confidence` отражает доверие к последней сформулированной гипотезе (обычно 0.2), не 0.

## CP-политики (харвест линз)

Линзы порождают гипотезы и оценки — не факты. Каждый харвест-выход несёт `cp_policy`:

| cp_policy | Когда | hyp_status | CP | Пометка |
|---|---|---|---|---|
| `judgment` | генерация из ввода PO без внешних данных | hypothesis | 0.2–0.4 | — |
| `estimate` | числовая оценка (TAM/SAM/SOM, unit-эк, размер сегмента, K-factor) | hypothesis | 0.3–0.4 | `[estimate]` в теле |
| `desk` | подкреплено web/desk-research (URL+дата) | validating | 0.5–0.7 | якорь-URL |
| `evidence` | реальное интервью / эксперимент / аналитика | validated/refuted | 0.6–1.0 | источник-факт |

Правила:
- Если промт сам метит допущение (`[Assumption]`, sensitivity, «never guess») — харвест уважает: помеченное → `estimate`/`judgment`, не `validated`.
- Числовые оценки без данных → всегда `estimate` (CP ≤ 0.4).
- `evidence` — только когда линза реально прогнала интервью/эксперимент/аналитику.
- Узел без `sources` не создаётся (workslop).
