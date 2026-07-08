---
nexus: product
node_id: harvest-s14
node_type: sprint-phase
sprint_phase: harvest
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.6
sources: ["sprint-fact:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
tags: [harvest]
level: sprint
cycle_ref: S14
bunch_ref: bunch-s14
rolls_up_to: harvest-q3
outcomes:
  cp_change: "+0.2 (гипотеза X валидирована пилотом на 8 SMB)"
  mNSM_delta: "[УТОЧНИТЬ: growth тонкий]"
  npv_actual: "[УТОЧНИТЬ: growth тонкий]"
insights:
  - "пилот подтвердил ценность быстрого онбординга для сегмента SMB"
  - "автоинвойс требует интеграции с БАЗИС — вынесено в S15"
nexus_writeback:
  - {nexus: product, node: feature-x, change: "confidence 0.4->0.6, статус: пилот-подтверждён", source: harvest-s14}
next_intent: "вход в S15-pulse: масштабировать онбординг X, начать интеграцию автоинвойса"
---

# Harvest — Sprint 14

> Урожай цикла. `nexus_writeback` замыкает петлю: инкремент возвращается в узел Нексуса `product` (поднять confidence, обновить updated, добавить source).
