---
nexus: market
node_id: bunch-q3
node_type: sprint-phase
sprint_phase: bunch
paf_step: null
kind: empirical
owner: Portfolio Manager
confidence: 0.4
sources: ["okr-deliver:Q3"]
updated: 2026-07-08
ttl_days: 90
ripeness: fresh
tags: [bunch]
level: quarter
cycle_ref: Q3
goal_map_ref: OKR-Q3
bunch_size: 3
bunch_window: Q3
items:
  - {ref: OBJ-1, kind: bet, trace: "GROUND/NEXUS/market/segment-smb.md", initial_cp: 3}
  - {ref: OBJ-2, kind: lever, trace: "GROUND/NEXUS/growth/activation.md", initial_cp: 2}
gate:
  final_cp: 0.45
  cost_of_risk: "ставка на SMB не окупится при CAC выше плана"
  decision: commit
selection_rationale: "① max mNSM портфеля ② min каннибализация ③ эффект в окне квартала → композитный NPV"
npv_estimate: "[УТОЧНИТЬ: growth тонкий, L2 не разблокирован]"
---

# Bunch квартала — Q3 (Ставки/Рычаги)

> Крупный Банч под Goal Map. Квартальный уровень (без `parent_bunch`). Спринтовые Банчи ссылаются сюда через `parent_bunch: bunch-q3`.
