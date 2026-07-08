---
nexus: precedents
node_id: precedents-vybor-sinhronnogo-platezhnogo-potoka
node_type: decision
paf_step: null
kind: empirical
owner: Cortex
confidence: 0.3
sources: ["confluence:https://wiki/131074"]
updated: 2026-07-04
ttl_days: 180
ripeness: fresh
tags: [confluence-indexed]
---

# Выбор синхронного платёжного потока

⚠️ **допущение клиента (онбординг)**, оцифровано из Confluence, требует
валидации — CP отражает уровень доверия к допущению, не подтверждённый факт.

ADR-страница «Платёжный шлюз» фиксирует решение: критичные B2B-транзакции
проводятся через **синхронный** платёжный поток, а не через асинхронную
очередь. Причина — заказчику нужно немедленное подтверждение оплаты в момент
оформления заказа, чтобы не плодить зависшие заказы при таймауте
процессингового партнёра.

Решение затрагивает компонент платёжного шлюза — см. [[system-landscape-payment-gateway]].
