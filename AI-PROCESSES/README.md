---
nexus: product
node_id: aip-readme
node_type: spine
paf_step: null
sprint_phase: null
kind: normative
owner: Product Ops
confidence: 1.0
sources: ["[S1]", "[S2]", "[S3]", "[S4]"]
updated: 2026-06-20
ttl_days: 365
ripeness: fresh
tags: []
---

# 🧭 AI-PROCESSES — AI-Native продуктовый фреймворк: от Идеи к полному Product Discovery

> **Исполняемый StepByStep-фреймворк продуктовой команды нового поколения.** Объединяет классический Product Discovery (веха за вехой) с AI-Native операционной моделью **PAF** (Тихомиров С., [S1]–[S4]) и AI-трансформацией (`AI-TRANSFORMATION/`).
> Цель: пройти от **большой идеи** до подтверждённого **Product-Channel Fit** через 9 шагов, в каждом из которых крутится цикл **Product Sprint**.
> Принцип: **ноль галлюцинаций** — каждый факт трассируется до источника ([S1]–[S4], `RB-STEP-*`, `AI-TRANSFORMATION/*`).

---

## 🎯 Что это и зачем

**AI-PROCESSES** — это канонический исполняемый фреймворк: пошаговая модель работы продуктового пода (pod) нового поколения. В отличие от разрозненных раннбуков, это **единая сквозная последовательность** с явными гейтами (fit-точками), единым движком (цикл Product Sprint) и единой операционной моделью (Нексус + Кортекс + Банч + Confidence Point).

**Три слоя фреймворка:**
1. **Хребет (spine):** 9 вех Product Discovery — `Step 0 … Step 8`.
2. **Движок (engine):** цикл **Product Sprint** крутится внутри каждого шага: `PULSE → SCOUT → BUNCH → PITCH → EXECUTE → HARVEST`.
3. **Опер.модель:** [[operating-model]] — правила игры (Нексус, Кортекс, Банч, CP, роли, гвардраилы).

---

## 🗺️ Хребет — 9 шагов

| Step | Веха | Что насыщаем/валидируем | RB-источник (методы) | Fit-точка (гейт) |
|---|---|---|---|---|
| **0** | [Foundation](STEP-0-FOUNDATION/overview) | Бутстрап AI-native опер.модели (Нексус+Кортекс+роли+Progress Pulse) | новое | — |
| **1** | [Idea & Context](STEP-1-IDEA/overview) | BIG Idea, 3 Линзы, первые Нексусы (рынок/продукт/рост) | RB-STEP-1 | — |
| **2** | [Customer](STEP-2-CUSTOMER/overview) | Нексус потребителя, сегменты, гипотеза mNSM | RB-STEP-2 | — |
| **3** | [Market](STEP-3-MARKET/overview) | Нексус рынка, TAM/SAM/SOM→mNSM, Ставки (Bets); 7 типов Узлов (Force/Trend/Constant/TAM-SAM-SOM/Competitor/Gap/Bet) | RB-STEP-3 | — |
| **4** | [Value](STEP-4-VALUE/overview) | Ценностное предложение, need/value fit | RB-STEP-4 | **🟧 Need/Value Fit** |
| **5** | [Business Model](STEP-5-BUSINESS-MODEL/overview) | Нексус системы роста, NPV, рычаги, AI-COGS | RB-STEP-5 | 🟥 Biz-model fit |
| **6** | [Go-to-Market](STEP-6-GO-TO-MARKET/overview) | Bale + Germination, позиционирование, каналы | RB-STEP-6 | — |
| **7** | [Solution & PMF](STEP-7-SOLUTION-PMF/overview) | Product Sprint до PMF, прототип/MVP/Harvesting | RB-STEP-7 | **🟫 PMF** |
| **8** | [Acquisition & PCF](STEP-8-ACQUISITION-PCF/overview) | Harvesting модели роста, дистрибуция | RB-STEP-8 | **⬛ PCF (Discovery завершён)** |

> Каждая fit-точка — это **Stage-Gate по Confidence Point**: пройти дальше можно только при достаточном доверии (насыщенном Нексусе). См. [[fit-points]].

---

## 🔁 Движок — цикл Product Sprint (внутри каждого шага 1–8)

```
PULSE → SCOUT → BUNCH → PITCH → EXECUTE → HARVEST → (след. шаг)
```

| Фаза | Суть | PAF-источник |
|---|---|---|
| **PULSE** | Progress Pulse: фиксация состояния Нексуса (как пилоты у приборов), гэп → intent шага | [S1] VI.4 |
| **SCOUT** | Скаутинг возможностей/угроз через 3 Линзы; насыщение Нексуса (Understand, Und-Id-Ex) | [S1] Принцип 5, VI.5 |
| **BUNCH** | Формирование Банча из текущего состояния (Identify); Bunch Size/Window | [S1] VI.5, VI.6 |
| **PITCH** | Pitching of Trust: защита Банча, рост CP, гейт; слабое — в отказ | [S1] VI.4, VI.7 |
| **EXECUTE** | Discovery-шаги: валидация гипотез; build-шаги (6–8): Build+Bale+Germination | [S1] VI.5 |
| **HARVEST** | Harvesting: фиксация NPV/mNSM, инкремент контекста в Нексус → цикл | [S1] VI.4 |

> Фазы активируются **контекстно**: не во всех шагах все 6 фаз тяжёлые (например, в discovery-шагах 1–5 EXECUTE = валидация; в build-шагах 6–8 EXECUTE = разработка+дистрибуция). Какие фазы активны — см. `overview.md` каждого шага.

---

## 📖 Как пользоваться фреймворком

1. **Сначала прочитай [[operating-model]]** — правила игры (Нексус, Кортекс, Банч, CP, роли, анти-workslop). Без неё шаги не поймёшь.
2. **Пройди по порядку Step 0 → Step 8.** Step 0 обязателен — без Нексуса и Кортекса остальные шаги усиливают мусор [S1] IX.
3. **В каждом шаге** читай `overview.md` → проходи фазы Sprint по порядку → на выходе гейт (CP / fit-точка).
4. **Гейт не пройден** → осознанный отказ или возврат (PAF: «рост контекста = рост скорости процессов, в т.ч. отказа» [S1] VI.3).
5. **Глубина методов** → wiki-link на `RB-STEP-N/*` (JTBD, TAM/SAM/SOM, VPC, BMC, SPIN, MVP…).
6. **«Почему так»** → wiki-link на `AI-TRANSFORMATION/reformation` и инструкции.

---

## 🔗 Связь с остальным хранилищем (канон + ссылки)

- **AI-PROCESSES (этот)** = исполняемый канон — что и как делать шаг за шагом.
- **`RB-STEP-*`** = справочник методов (классический Product Discovery в деталях).
- **`AI-TRANSFORMATION/`** = обоснование трансформации (`reformation.md` — что/где/почему меняется; 67 инструкций).
- **`sa_documentation/naming_conventions`** = глоссарий PAF + запрещённые синонимы.

Ничего не удаляется. Три слоя互补: методы → трансформация → исполнение.

---

## 📚 Источники (ground truth)

| Код | Источник | Статус |
|---|---|---|
| **[S1]** | [productframework.ru/ops/main](https://productframework.ru/ops/main) — каркас PAF | ✅ |
| **[S2]** | [productframework.ru/ai_product_roles](https://productframework.ru/ai_product_roles) — роли в эпоху ИИ | ✅ |
| **[S3]** | [productframework.ru/skill_map](https://productframework.ru/skill_map) — карта навыков | ✅ |
| **[S4]** | Профстандарт 06.012 (приказ Минтруда № 636н) | ✅ |

**Связанные артефакты:** [[operating-model]] · [[fit-points]] · [[AI-TRANSFORMATION/reformation|reformation]] · [[AI-TRANSFORMATION/index|index]] · [[sa_documentation/naming_conventions|naming_conventions]] · [[0 КАРТА ПРОЦЕССА — Product Discovery]]

---
**Version:** 1.0 · **Last updated:** 2026-06-20 · **Maintained by:** AI-KORTEX
