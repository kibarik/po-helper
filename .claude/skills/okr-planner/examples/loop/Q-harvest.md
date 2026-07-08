---
nexus: growth
node_id: harvest-q3
node_type: sprint-phase
sprint_phase: harvest
paf_step: null
kind: empirical
owner: Portfolio Manager
confidence: 0.55
sources: ["okr-harvest-quarter:Q3", "RESULTS/S14-harvest.md"]
updated: 2026-07-08
ttl_days: 90
ripeness: fresh
tags: [harvest]
level: quarter
cycle_ref: Q3
bunch_ref: bunch-q3
outcomes:
  cp_change: "+0.15 (ставка на SMB частично подтверждена спринтами S12–S14)"
  mNSM_delta: "[УТОЧНИТЬ: growth тонкий]"
  npv_actual: "[УТОЧНИТЬ: L2 не разблокирован]"
insights:
  - "онбординг-рычаг подтверждён на уровне спринтов, требует масштабирования в Q4"
  - "рычаг автоинвойса заблокирован интеграцией БАЗИС"
nexus_writeback:
  - {nexus: growth, node: activation, change: "confidence 0.3->0.45, добавлен рычаг онбординга", source: harvest-q3}
  - {nexus: market, node: segment-smb, change: "ставка частично подтверждена", source: harvest-q3}
next_intent: "вход в Q4-pulse: масштабировать онбординг-рычаг, разблокировать автоинвойс"
---

# Harvest квартала — Q3

> Rollup спринтовых урожаев (`RESULTS/S*-harvest.md`, у которых `rolls_up_to: harvest-q3`). Writeback в `market`/`growth`. Квартальный уровень — без `rolls_up_to`.
