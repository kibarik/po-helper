---
nexus: product
node_id: pulse-s14
node_type: sprint-phase
sprint_phase: pulse
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.5
sources: ["sprint-sync:S14", "GROUND/NEXUS/product/_index.md"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
tags: [pulse]
level: sprint
cycle_ref: S14
nexus_snapshot:
  product: {ripeness: 0.72, gaps: ["mNSM-гипотеза фичи X не валидирована"]}
  growth: {ripeness: 0.30, gaps: ["каналы активации не заполнены"]}
gap_vs_vision: "нет валидированной ценности фичи X относительно Vision продукта"
intent: "в S14 закрыть гэп по ценностной гипотезе фичи X (пилот на SMB)"
cp_start: "CP гипотезы X = 0.3"
lens: product
---

# Progress Pulse — Sprint 14

> Снимок состояния Нексуса на входе в цикл. Не генерирует решения (это Scout) — честно фиксирует «где мы».

Ripeness вычислен `validate_ground.py` (полнота × актуальность), не вписан руками. Гэп признан без приукрашивания.
