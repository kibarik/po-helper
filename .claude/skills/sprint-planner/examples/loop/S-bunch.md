---
nexus: product
node_id: bunch-s14
node_type: sprint-phase
sprint_phase: bunch
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.4
sources: ["OKR-Q3", "sprint-deliver:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
tags: [bunch]
level: sprint
cycle_ref: S14
parent_bunch: bunch-q3
goal_map_ref: OKR-Q3
bunch_size: 5
bunch_window: sprint-14
items:
  - {ref: PROJ-123, kind: hypothesis, vp_offer: "быстрый онбординг SMB за 5 минут", trace: "GROUND/NEXUS/product/feature-x.md", initial_cp: 3}
  - {ref: PROJ-124, kind: feature, vp_offer: "автоинвойс по расписанию", trace: "GROUND/NEXUS/product/invoicing.md", initial_cp: 4}
gate:
  final_cp: 0.5
  cost_of_risk: "риск переоценки объёма X на ~3 SP"
  decision: commit
selection_rationale: "① max mNSM (онбординг двигает активацию) ② min риск (CP выше у PROJ-124) ③ эффект в окне S14"
npv_estimate: "[УТОЧНИТЬ: growth тонкий]"
---

# Bunch — Sprint 14

> Связка в моменте под Карту Целей OKR-Q3. Не беклог: сформирована из текущего состояния Нексуса, `items` — ссылки на JIRA, не копии.
