# Compliance Gap — PAF Team OS ↔ AI-PROCESSES

> **Вопрос:** что нужно коробке для **полного соответствия** системе и процессам, описанным в `AI-PROCESSES/`.
> **Метод:** канон `AI-PROCESSES` (хребет + движок + опер.модель + гейты) накладывается на текущее состояние сборки; каждый гэп трассируется до источника (wiki-link на ноту AI-PROCESSES + `[S1]`–`[S4]`).
> **Дата:** 2026-06-21. **Снимок:** после коммита `61d28b9` (`/paf-init` skill shipped).
> **Спека:** [[2026-06-21-paf-team-os-design]] (scope §11 — что создавать).

---

## 0. Compliance bar — что считается «полным соответствием»

`AI-PROCESSES` = три слоя + гейты. Коробка должна позволить клиенту **исполнить** все три, не выходимая в ручной режим мимо Кортекса.

| Слой | Канон требует | Источник |
|---|---|---|
| **Хребет** | 9 шагов `Step 0 … Step 8`, каждый — `overview` + 6 фаз Sprint | [[AI-PROCESSES/README]] |
| **Движок** | цикл Product Sprint `PULSE→SCOUT→BUNCH→PITCH→EXECUTE→HARVEST` крутится в каждом шаге 1–8 | [[AI-PROCESSES/operating-model]] столп 5 |
| **Опер.модель** | Нексус + Кортекс + Банч + CP + 3PL + роли + гвардраилы | [[AI-PROCESSES/operating-model]] 5 столпов |
| **Гейты** | 4 fit-точки (Need/Value, Biz-model, PMF, PCF) = Stage-Gate по Confidence Point | [[AI-PROCESSES/fit-points]] |
| **Step 0** | бутстрап (4 подшага) обязателен до всего — без него «остальные шаги усиливают мусор» | [[AI-PROCESSES/STEP-0-FOUNDATION/overview]] · [S1] IX |

**Инварианты процесса** (нарушение = workslop, не соответствие):
- Инженер работает **только через Кортекс** [S1] III.1.
- **Сначала Нексус, потом Кортекс** [S1] IX — без спелого контекста Кортекс усиливает мусор.
- Каждое утверждение → `sources[]`; Узел без источников = workslop [[sa_documentation/nexus_schema]].
- Онбординг цифровизует, **не валидирует**; low-CP допущения не выдавать за факты.

---

## 1. Текущее состояние сборки (что уже соответствует)

| Scope-item (§11) | Статус | Артефакт |
|---|---|---|
| 1. Мастер-каталог Nexus-типов | ✅ | [[sa_documentation/nexus_catalog]] |
| 2. Node schema (open `nexus` + кастом + empirical) | ✅ | [[sa_documentation/nexus_schema]] v1.1 |
| 3. `/paf-init` (config + GROUND + дефолтный минимум) | ✅ | `.claude/skills/paf-init/SKILL.md` |
| 6. GROUND skeleton | ✅ | `GROUND/` |
| 7. `config.yaml` + `_registry.yaml` schema + TDD-валидатор | ✅ | [[sa_documentation/ground_schema]], `validate_ground.py` |
| Кортекс: 6 агентов PULSE/SCOUT/BUNCH/PITCH | ✅ | `.claude/agents/*`, [[.claude/CORTEX]] |
| Context Ripeness = `completeness × freshness`, гейт 0.6 | ✅ (в агенте) | `wilting-detector.md` по [[sa_documentation/nexus_schema]] §4 |

---

## 2. Гэп-матрица

### Слой A — Step 0 Bootstrap (вход во весь процесс)

| Подшаг Step 0 | Канон-артефакт | Есть | Гэп | Источник |
|---|---|---|---|---|
| 0.1 Nexus setup | граф 4 Нексусов + Node schema + RACI | ✅ `/paf-init` | — (пусто до онбординга) | [[AI-PROCESSES/STEP-0-FOUNDATION/1.nexus-setup]] |
| 0.2 Cortex setup | Кортекс фазы 1–2; работа **только через проводника** | ⚠️ агенты + `phase_target` | ❌ **агенты хардкодят `namespace="ai-kortex"` + фикс. 4 Нексуса** → не читают `config.yaml`/`_registry.yaml`. Чужой клиент/кастом-Нексус = не работает | [[AI-PROCESSES/STEP-0-FOUNDATION/2.cortex-setup]] · scope §11.8 |
| 0.3 Roles | roster Comb-shaped + маппинг Skill Map/профстандарт | ✅ roster в `config.yaml` | ⚠️ нет артефакта-документа RACI в GROUND | [[AI-PROCESSES/STEP-0-FOUNDATION/3.roles]] |
| 0.4 Pulse + Goal Map | **шаблон Progress Pulse + Goal Map v0** (связь 3PL) | ⚠️ init-pulse создан | ❌ **Goal Map v0 НЕ создаётся** — 3PL-синхронизация отсутствует | [[AI-PROCESSES/STEP-0-FOUNDATION/4.progress-pulse]] · overview §артефакт |

### Слой B — Движок Product Sprint (6 фаз × каждый шаг)

| Фаза | Агент/скилл | Гэп | Источник |
|---|---|---|---|
| PULSE | ✅ wilting-detector | — | [S1] VI.4 |
| SCOUT | ✅ scouting (3 Линзы) | — | [S1] Принцип 5, VI.5 |
| BUNCH | ✅ bunch-former | ⚠️ нет **шаблона артефакта Банча** (`GROUND/BUNCH/` пуст) | [S1] VI.6 |
| PITCH | ✅ cp-scorer + pitching-opponent | — | [S1] VI.4, VI.7 |
| **EXECUTE** | ❌ **нет** | discovery (1–5)=валидация гипотез; build (6–8)=Build+Bale+Germination. «Агентизация — Phase 3» (CORTEX.md). **2 из 6 фаз без драйвера** | [S1] VI.5 |
| **HARVEST** | ⚠️ reuse nexus-builder | ❌ нет скилла HARVEST (фиксация NPV/mNSM, инкремент контекста) + нет шаблона `GROUND/RESULTS/` | [S1] VI.4 |
| **Оркестрация цикла** | ❌ **нет драйвера** | клиент вручную инвочит агенты + сам читает `STEP-N/*.md`. Нет `/paf-sprint`/фазных скиллов, ведущих PULSE→…→HARVEST для текущего шага | README §«Движок» |

### Слой C — Онбординг (насыщение Нексуса)

| Канон | Есть | Гэп | Источник |
|---|---|---|---|
| Цифровизация контекста → насыщенный Нексус (low-CP) перед Steps 1–8 | ❌ **`/paf-onboard` НЕ построен** | **критич.** — без него Нексус пустой, CR≈0, Step 1 не открывается (критерий Step 0) | spec §5 · scope §11.5 |
| Кастомные Нексусы под решение клиента | ❌ `/paf-nexus-create` НЕ построен | каталог расширяемый по schema, но скилл-генератор отсутствует | spec §2.3 · scope §11.4 |

### Слой D — Гейты / CP-дисциплина

| Канон | Есть | Гэп | Источник |
|---|---|---|---|
| CP-скоринг (колесо Гилада, ICE/RICE) | ✅ cp-scorer | — | [S1] VI.7, Принцип 4 |
| 4 fit-точки (Stage-Gate по CP) | ✅ доки | ⚠️ **advisory только** — нет readiness-check, блокирующего переход Step N→N+1 при CP/CR < порога. Veto за человеком, но чек-механика = нет | [[AI-PROCESSES/fit-points]] |
| Context Ripeness ≥ 0.6 порог перехода | ✅ формула в wilting-detector | — | [[sa_documentation/nexus_schema]] §4 |

### Слой E — Дистрибуция / целостность

| Scope-item | Есть | Гэп | Источник |
|---|---|---|---|
| README quickstart (clone→init→nexus-create→onboard→Steps) | ❌ | scope §11.9 | README §«Как пользоваться» |
| INSTALL.md (prerequisites, ruflo quirk) | ❌ | scope §11.10 | spec §9 graceful degradation |
| LICENSE (dual CC BY-SA + MIT) | ❌ | scope §11.10 | spec §10 |

---

## 3. Build backlog (приоритезировано)

### P0 — без этого коробка НЕ соответствует процессу (нельзя войти в Sprint)

| # | Задача | Снимает гэп | Слой |
|---|---|---|---|
| 1 | **`/paf-onboard`** — цифровизация контекста (Phase A ингестия доков + B интервью + C verify/low-CP + D readiness) | C · критерий Step 0 | C |
| 2 | **`/paf-nexus-create`** — кастомные Нексусы (интервью → `NEXUS/<slug>/` + `_registry.yaml`) | C · §2.3 | C |
| 3 | **Cortex-адаптация** — агенты читают `config.yaml` (`namespace=product.slug`) + `_registry.yaml` (все Нексусы); убрать хардкод `ai-kortex`/фикс.4 | A.0.2 · §11.8 | A |

### P1 — движок / оркестрация («цикл Sprint крутится»)

| # | Задача | Снимает гэп | Слой |
|---|---|---|---|
| 4 | **Goal Map v0** в `/paf-init` (связь 3PL, черновые цели под Steps 1–3) | A.0.4 | A |
| 5 | **EXECUTE + HARVEST** — скиллы/агенты для 2 фаз без драйвера (или явный скилл «инженер + nexus-builder») | B · 2/6 фаз | B |
| 6 | **Артефакт-шаблоны** — Банч (`GROUND/BUNCH/_template.md`), Pulse, Harvest (`GROUND/RESULTS/`) | B (BUNCH/HARVEST) | B |
| 7 | **`/paf-sprint`** (или фазные скиллы) — драйвер цикла для текущего `config.paf_step` (читает `STEP-N/overview` → ведёт 6 фаз) | B · оркестрация | B |

### P2 — гейты + дистрибуция

| # | Задача | Снимает гэп | Слой |
|---|---|---|---|
| 8 | **Readiness/gate-check** — CP/CR-порог перед переходом шага (soft-block + карта пробелов) | D · enforcement | D |
| 9 | **README + INSTALL + LICENSE** | E · scope §11.9–11 | E |

---

## 4. Зависимости

```
P0:
  [1 /paf-onboard] ─┐
  [2 /paf-nexus-create] ─┤  → разблокируют насыщение Нексуса (вход в Steps 1–8)
  [3 Cortex-адаптация] ──┘  → разблокирует мульти-клиента/кастом-Нексус

P1:
  [6 шаблоны] → [5 EXECUTE/HARVEST] → [7 /paf-sprint]   (движок собирается снизу)
  [4 Goal Map] независимо (доработка /paf-init)

P2:
  [8 gate-check] после [1]+[3] (нужны насыщенный Нексус + параметризованные агенты)
  [9 docs] в любой момент
```

---

## 5. Критерий «полное соответствие» достигнуто

- ✅ Новый клиент: clone → `/paf-init` (4 Нексуса + Goal Map + roster + Cortex phase) → `/paf-nexus-create`? → `/paf-onboard` (насыщение, CR↑) → **`/paf-sprint`** ведёт цикл PULSE→…→HARVEST над насыщенным GROUND Nexus → **gate-check** на fit-точках → Step 0…8 — всё через Кортекс, мимо ручного режима не выходим.
- ✅ Агенты параметризованы клиентом (`config.yaml` + `_registry.yaml`), хардкод устранён.
- ✅ Все 6 фаз Sprint имеют драйвер; EXECUTE/HARVEST не «Phase 3»-заглушка.
- ✅ Гейты — enforcement (soft-block), а не advisory.

Соответствует spec §13 («done»): новый клиент за ≤1 рабочий день доходит до Product Sprint над насыщенным GROUND Nexus.

---

**Связанные:** [[2026-06-21-paf-team-os-design]] (spec) · [[AI-PROCESSES/README]] · [[AI-PROCESSES/operating-model]] · [[AI-PROCESSES/fit-points]] · [[.claude/CORTEX]] · [[sa_documentation/nexus_schema]] · [[sa_documentation/nexus_catalog]] · [[sa_documentation/ground_schema]]
