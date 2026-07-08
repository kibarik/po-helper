# Research Lens Arsenal — Implementation Plan · Итерация 3 (PP-4: шаги 3–8)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Оснастить оставшиеся 6 шагов Product Discovery (Market/Value/BizModel/GTM/Solution/Acquisition) их командами-плейлистами линз, чтобы весь 8-шаговый discovery был исполним end-to-end.

**Architecture:** Каждый шаг = команда `/prd-<step>.md` (адаптивный плейлист линз, как эталон `/prd-customer`), исполняющая линзы через единый Wrap (`lens_runtime.md`) с харвестом в Нексусы по Node schema. Harvest-карты определяются в командах (авторитетно) + добавляются в `lenses.yaml` для single-host линз. Разрешаются два ledger-Minor: коллизия `channel`→`dist-channel` и per-host_step harvest у `odi`.

**Tech Stack:** Markdown command files; YAML frontmatter (Node schema §2.3/§3.1) + `lenses.yaml`; Bash + python3(yaml) для структурных проверок.

## Global Constraints

- **Промты дословны и read-only:** тела `resources/lenses/*.md` не редактируются; команды добавляют только вход (PULSE) и персист (HARVEST).
- **Методология read-only:** `docs/AI-PROCESSES|TRADITIONAL|RL|AI-TRANSFORMATION` не редактировать. Редактируемы: `.claude/`, `sa_documentation/`.
- **Оценка ≠ факт:** числа (TAM/SAM/SOM, unit-эк, RICE, P×I, скоринги) → `hyp_status: hypothesis`, `cp_policy: estimate` (CP ≤ 0.4), пометка `[estimate]`; суждения → `judgment` (0.2–0.4); web-якорь → `desk` (0.5–0.7); реальные интервью/эксперименты → `evidence` (0.6–1.0). Уважать `[Assumption]` промта. Узел без `sources` не создавать.
- **Node schema контракт:** обяз. ключи frontmatter + hyp_status/depends_on; node_type только из §3.1 (`dist-channel` добавляется в Task 1).
- **RACI owners:** market → Portfolio Manager; product → Product Engineer; growth → Growth Engineer; customer → Product Engineer.
- **Fit-гейты (мягкие):** Value→Need/Value Fit, BizModel→Biz-model, Solution→PMF, Acquisition→PCF (пороги — `resources/fit_gates.md`; не блокировать, помечать долг).
- **Язык:** русский. Англ. промты исполняются с инструкцией «отвечай по-русски».
- **STOP-паузы** после каждой линзы и в конце шага (human-in-the-loop).
- **Регистрация:** новые команды → `install.sh` массив `COMMANDS`.

## Verification approach (нет автотест-харнесса)

Структурные shell-чек (`test -f`, grep, `python3 -c` yaml) + сценарные static-trace (интерактив deferred). Тест-vault: `/private/tmp/.../scratchpad/prd-test` (узлы Step 1+2 из прошлых прогонов).

---

## File Structure

**Создаём (6 команд):**
- `.claude/commands/prd-market.md` — Step 3 (lens: tam-sam-som)
- `.claude/commands/prd-value.md` — Step 4 (nsm, odi, rory-interrogation) ▸ гейт Need/Value Fit
- `.claude/commands/prd-bizmodel.md` — Step 5 (unit-economics, aarrr) ▸ гейт Biz-model
- `.claude/commands/prd-gtm.md` — Step 6 (positioning-4p, distribution-channels, rory-interrogation)
- `.claude/commands/prd-solution.md` — Step 7 (ost, ab-design, rat) ▸ гейт PMF
- `.claude/commands/prd-acquisition.md` — Step 8 (aarrr, distribution-channels) ▸ гейт PCF

**Модифицируем:**
- `sa_documentation/nexus_schema.md` — §3.1: `channel` (distribution) → `dist-channel` (устранить коллизию с инфо-`channel`).
- `.claude/skills/prd-research/resources/lenses.yaml` — harvest-блоки для tam-sam-som/unit-economics/positioning-4p; `odi` harvest — комментарий про per-host override.
- `.claude/skills/prd-research/resources/lens_runtime.md` — правило «harvest host-команды приоритетен над реестром для мультихост-линз».
- `.claude/skills/prd-research/resources/pipeline.md` — плейлисты шагов 3–8.
- `install.sh` — регистрация 6 команд.

**Harvest-карты (референс для всех задач):**
| Шаг | Линза | Выход → node_type (nexus, cp_policy) |
|---|---|---|
| Market | tam-sam-som | TAM/SAM/SOM+sensitivity → `tam-sam-som` (market, estimate); конкуренты → `competitor` (market, judgment) |
| Value | nsm | NSM → `nsm-metric` (product, judgment); input-метрики → `input-metric` (growth, judgment) |
| Value | odi | desired outcomes → `outcome` (**product**, judgment); opp-scores → `opportunity` (product, estimate) |
| Value | rory-interrogation | рефрейм ценности → `value-prop` (product, judgment); позиционирование → `positioning` (product, judgment) |
| BizModel | unit-economics | LTV/CAC/cohort → `unit-econ` (growth, estimate) + `cohort` (growth, estimate) |
| BizModel | aarrr | воронка revenue → `funnel-stage` (growth, judgment); метрики → `input-metric` (growth, estimate) |
| GTM | positioning-4p | 4P → `four-p` (growth, judgment); позиционирование → `positioning` (product, judgment) |
| GTM | distribution-channels | каналы(+RICE) → `dist-channel` (growth, estimate) |
| GTM | rory-interrogation | позиционирование → `positioning` (product, judgment) |
| Solution | ost | opportunity/solution/experiment → одноим. (product, judgment) |
| Solution | ab-design | эксперимент → `ab-test` (product, judgment) |
| Solution | rat | риск-карты(P×I) → `risk-card` (product, estimate) |
| Acquisition | aarrr | воронка acq → `funnel-stage` (growth, judgment) + `input-metric` (growth, estimate) |
| Acquisition | distribution-channels | конфиг каналов → `dist-channel` (growth, judgment) |

---

## Task 1: Схема + реестр — `dist-channel`, harvest-блоки, per-host правило

**Files:**
- Modify: `sa_documentation/nexus_schema.md` (§3.1: `channel`→`dist-channel`)
- Modify: `.claude/skills/prd-research/resources/lenses.yaml` (harvest tam-sam-som/unit-economics/positioning-4p; odi comment)
- Modify: `.claude/skills/prd-research/resources/lens_runtime.md` (per-host override note)

**Interfaces:**
- Produces: node_type `dist-channel` (заменяет distribution-`channel`); harvest-дефолты для 3 single-host линз; правило приоритета команды.

- [ ] **Step 1: Проверка (ожидаемо провалится)**

Run:
```bash
cd "$(git rev-parse --show-toplevel)"
grep -q 'dist-channel' sa_documentation/nexus_schema.md && echo OK || echo FAIL
```
Expected: `FAIL`

- [ ] **Step 2: §3.1 — переименовать distribution `channel` → `dist-channel`**

В `sa_documentation/nexus_schema.md` §3.1 в строке таблицы, где `node_type` = `channel` с источником `distribution-channels`, заменить значение первого столбца `channel` на `dist-channel` (источник/нексус не менять: `distribution-channels | growth`). Это устраняет коллизию с базовым §3 `channel` (инфо-канал `channels`-Нексуса).

- [ ] **Step 3: lenses.yaml — harvest-блоки для single-host линз**

Добавить `harvest:` к записям (после их `lang: ru`):

`tam-sam-som`:
```yaml
    harvest:
      - output: "TAM/SAM/SOM + sensitivity (Stage 9)"
        nexus: market
        node_type: tam-sam-som
        cp_policy: estimate
```
`unit-economics`:
```yaml
    harvest:
      - output: "LTV/CAC/ratio + cohorts"
        nexus: growth
        node_type: unit-econ
        cp_policy: estimate
      - output: "CohortsTable"
        nexus: growth
        node_type: cohort
        cp_policy: estimate
```
`positioning-4p`:
```yaml
    harvest:
      - output: "four_p итог"
        nexus: growth
        node_type: four-p
        cp_policy: judgment
      - output: "рекомендованное позиционирование"
        nexus: product
        node_type: positioning
        cp_policy: judgment
```
В запись `odi` (у неё уже есть harvest на customer) добавить строку-комментарий над блоком `harvest:`:
```yaml
    # harvest ниже — дефолт для host customer; на host value команда /prd-value направляет outcome → product (см. lens_runtime).
```

- [ ] **Step 4: lens_runtime.md — правило приоритета команды**

В `resources/lens_runtime.md` в разделе HARVEST (после шага 8) добавить пункт:
```markdown
8a. **Мультихост-линзы** (`host_steps` из ≥2 шагов, напр. odi/rory-interrogation/aarrr/distribution-channels): harvest-нексус/тип задаёт **host-команда** текущего шага; блок `harvest` в реестре — дефолт первого хоста. Команда приоритетна.
```

- [ ] **Step 5: Проверка**

Run:
```bash
cd "$(git rev-parse --show-toplevel)"
grep -q 'dist-channel' sa_documentation/nexus_schema.md && \
python3 -c "import yaml; L={l['id']:l for l in yaml.safe_load(open('.claude/skills/prd-research/resources/lenses.yaml'))['lenses']}; assert 'harvest' in L['tam-sam-som'] and 'harvest' in L['unit-economics'] and 'harvest' in L['positioning-4p']; print('OK')" && \
grep -q 'Мультихост' .claude/skills/prd-research/resources/lens_runtime.md && echo ALLOK || echo FAIL
```
Expected: `OK` then `ALLOK`

- [ ] **Step 6: Commit**

```bash
git add sa_documentation/nexus_schema.md .claude/skills/prd-research/resources/lenses.yaml .claude/skills/prd-research/resources/lens_runtime.md
git commit -m "feat(prd-research): dist-channel node_type + harvest-блоки шагов 3-8 + правило мультихост-харвеста"
```

---

## Task 2: `/prd-market` (Step 3)

**Files:** Create: `.claude/commands/prd-market.md`
**Interfaces:** Consumes lens_runtime, lenses.yaml (tam-sam-som), Step1/2 узлы. Produces market-узлы (tam-sam-som/competitor).

- [ ] **Step 1: Создать `.claude/commands/prd-market.md`**

```markdown
---
description: 'Discovery Step 3 (Market) — линза TAM/SAM/SOM; наполняет market-Нексус (роль: Discovery Facilitator + рыночный аналитик)'
---

## Использование

```
/prd-market
```
Вход: узлы Step 1/2 (сегменты, канал). Выход: market-узлы + state.yaml(market).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md` (CP-политики), `resources/lenses.yaml` (линза `tam-sam-som`).
2. Прочитай `docs/AI-PROCESSES/STEP-3-MARKET/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы market/customer (сегменты `cust-seg-*`, `idea-lens-market-*`) — вход и `depends_on`.

### Этап 2: Линза tam-sam-som (Wrap)
4. Исполни линзу `tam-sam-som` по `lens_runtime.md` (PULSE→промт дословно, 9 стадий, top-down+bottom-up→HARVEST).
   HARVEST: TAM/SAM/SOM + sensitivity → `tam-sam-som` (market, **estimate**, `[estimate]` в теле); выявленные конкуренты/альтернативы → `competitor` (market, judgment). `depends_on` = сегменты Step 2.

### Этап 3: Состояние
5. Обнови `{discovery_workspace(market)}/state.yaml` (nodes/cp/status/open_questions/last_touched) + `journal.md`.

### Этап 4: СТОП
```
Step 3 (Market): узлов N (market). Средний CP: X. [estimate]-узлов: k.
── СТОП ── PO: проверь узлы. Дальше → /prd-value, либо /prd-lens rat.
```

## Запреты
1. Тело линзы НЕ редактировать. 2. Числа рынка → `estimate` CP ≤ 0.4, не факт; узел без `sources` не создавать. 3. «Не знаю» → `parked`. 4. RACI market → Portfolio Manager. `docs/` read-only.
```

- [ ] **Step 2: Проверка**
```bash
test -f .claude/commands/prd-market.md && grep -q 'tam-sam-som' .claude/commands/prd-market.md && grep -q 'lens_runtime' .claude/commands/prd-market.md && grep -q 'Portfolio Manager' .claude/commands/prd-market.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Commit**
```bash
git add .claude/commands/prd-market.md
git commit -m "feat(prd-research): стадия /prd-market (Step 3) — линза TAM/SAM/SOM"
```

---

## Task 3: `/prd-value` (Step 4, гейт Need/Value Fit)

**Files:** Create: `.claude/commands/prd-value.md`
**Interfaces:** Consumes lens_runtime, lenses (nsm/odi/rory-interrogation), fit_gates. Produces product/growth-узлы (nsm-metric/input-metric/outcome/opportunity/value-prop/positioning).

- [ ] **Step 1: Создать `.claude/commands/prd-value.md`**

```markdown
---
description: 'Discovery Step 4 (Value) — плейлист: NSM → ODI(outcomes) → Rory; ценностное предложение + гейт Need/Value Fit (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-value
/prd-value <lens_id>   # nsm | odi | rory-interrogation
```
Вход: узлы Step 2/3. Выход: product/growth-узлы + state.yaml(value).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-4-VALUE/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer (сегменты/jtbd/persona/value-prop) + market — вход и `depends_on`.

### Этап 2: Плейлист (адаптивно; PO может пропустить/переставить), каждый — через lens_runtime:
- **nsm** (cross-cutting) → `nsm-metric` (product, judgment) + `input-metric` (growth, judgment).
- **odi** → desired outcomes → `outcome` (**product**, judgment) [override customer→product на этом шаге]; opp-scores → `opportunity` (product, estimate).
- **rory-interrogation** → рефрейм ценности → `value-prop` (product, judgment); позиционирование-намёк → `positioning` (product, judgment).
После каждой линзы — мини-STOP.

### Этап 3: Гейт Need/Value Fit (мягкий)
4. По `fit_gates.md`: Context Ripeness(product) ≥ 0.6? Нет → 🟡 не блокировать, пометить долг в open_questions.

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(value)` (+ гейт-пометка) + `journal.md`.
```
Step 4 (Value): линз L/3. Узлов N (product a / growth b). CP: X. Гейт Need/Value Fit: <🟢/🟡>.
── СТОП ── PO. Дальше → /prd-bizmodel, либо /prd-lens rat.
```

## Запреты
1. Тела линз не редактировать. 2. Оценки/скоринги → `estimate`; узел без `sources` не создавать; «не знаю» → `parked`. 3. Не выдавать 🟡 за пройденный гейт. 4. RACI product → Product Engineer. `docs/` read-only.
```

- [ ] **Step 2: Проверка**
```bash
test -f .claude/commands/prd-value.md && grep -q 'nsm' .claude/commands/prd-value.md && grep -q 'odi' .claude/commands/prd-value.md && grep -q 'Need/Value Fit' .claude/commands/prd-value.md && grep -q 'outcome' .claude/commands/prd-value.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Commit**
```bash
git add .claude/commands/prd-value.md
git commit -m "feat(prd-research): стадия /prd-value (Step 4) — NSM/ODI/Rory + гейт Need/Value Fit"
```

---

## Task 4: `/prd-bizmodel` (Step 5, гейт Biz-model)

**Files:** Create: `.claude/commands/prd-bizmodel.md`
**Interfaces:** lenses (unit-economics, aarrr). Produces growth-узлы (unit-econ/cohort/funnel-stage/input-metric).

- [ ] **Step 1: Создать `.claude/commands/prd-bizmodel.md`**

```markdown
---
description: 'Discovery Step 5 (Business Model) — плейлист: UNIT-экономика → AARRR(revenue); гейт Biz-model (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-bizmodel
/prd-bizmodel <lens_id>   # unit-economics | aarrr
```
Вход: узлы Step 2–4. Выход: growth-узлы + state.yaml(bizmodel).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-5-BUSINESS-MODEL/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer/product/market (сегменты, value-prop, размеры) — вход и `depends_on`.

### Этап 2: Плейлист (через lens_runtime):
- **unit-economics** → LTV/CAC/ratio + cohorts → `unit-econ` (growth, **estimate**) + `cohort` (growth, estimate). Все числа — `[estimate]`.
- **aarrr** (revenue-фокус) → воронка → `funnel-stage` (growth, judgment); revenue-метрики → `input-metric` (growth, estimate).
Мини-STOP после каждой.

### Этап 3: Гейт Biz-model (мягкий)
4. По `fit_gates.md`: Context Ripeness(growth) ≥ 0.6? Нет → 🟡, долг в open_questions.

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(bizmodel)` + `journal.md`.
```
Step 5 (BizModel): линз L/2. Узлов N (growth). CP: X. Гейт Biz-model: <🟢/🟡>. [estimate]: k.
── СТОП ── PO. Дальше → /prd-gtm.
```

## Запреты
1. Тела линз не редактировать. 2. Финансовые числа → `estimate` CP ≤ 0.4 (нет данных = не факт); узел без `sources` не создавать. 3. Не выдавать 🟡 за гейт. 4. RACI growth → Growth Engineer. `docs/` read-only.
```

- [ ] **Step 2: Проверка**
```bash
test -f .claude/commands/prd-bizmodel.md && grep -q 'unit-economics' .claude/commands/prd-bizmodel.md && grep -q 'aarrr' .claude/commands/prd-bizmodel.md && grep -q 'Biz-model' .claude/commands/prd-bizmodel.md && grep -q 'Growth Engineer' .claude/commands/prd-bizmodel.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Commit**
```bash
git add .claude/commands/prd-bizmodel.md
git commit -m "feat(prd-research): стадия /prd-bizmodel (Step 5) — UNIT-эк/AARRR + гейт Biz-model"
```

---

## Task 5: `/prd-gtm` (Step 6)

**Files:** Create: `.claude/commands/prd-gtm.md`
**Interfaces:** lenses (positioning-4p, distribution-channels, rory-interrogation). Produces growth/product-узлы (four-p/positioning/dist-channel).

- [ ] **Step 1: Создать `.claude/commands/prd-gtm.md`**

```markdown
---
description: 'Discovery Step 6 (Go-To-Market) — плейлист: 4P → каналы → Rory; позиционирование и каналы (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-gtm
/prd-gtm <lens_id>   # positioning-4p | distribution-channels | rory-interrogation
```
Вход: узлы Step 2–5. Выход: growth/product-узлы + state.yaml(gtm).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`.
2. Прочитай `docs/AI-PROCESSES/STEP-6-GO-TO-MARKET/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer/product/growth (сегменты, value-prop, unit-эк) — вход и `depends_on`.

### Этап 2: Плейлист (через lens_runtime):
- **positioning-4p** → `four-p` (growth, judgment) + рекоменд. позиционирование → `positioning` (product, judgment).
- **distribution-channels** → каналы (+RICE-скор) → `dist-channel` (growth, estimate).
- **rory-interrogation** → усиление позиционирования → `positioning` (product, judgment).
Мини-STOP после каждой.

### Этап 3: Состояние + СТОП
4. Обнови `state.yaml(gtm)` + `journal.md`.
```
Step 6 (GTM): линз L/3. Узлов N (growth a / product b). CP: X.
── СТОП ── PO. Дальше → /prd-solution.
```

## Запреты
1. Тела линз не редактировать. 2. RICE/оценки → `estimate`; узел без `sources` не создавать; «не знаю» → `parked`. 3. RACI growth → Growth Engineer, product → Product Engineer. `docs/` read-only.
```

- [ ] **Step 2: Проверка**
```bash
test -f .claude/commands/prd-gtm.md && grep -q 'positioning-4p' .claude/commands/prd-gtm.md && grep -q 'distribution-channels' .claude/commands/prd-gtm.md && grep -q 'dist-channel' .claude/commands/prd-gtm.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Commit**
```bash
git add .claude/commands/prd-gtm.md
git commit -m "feat(prd-research): стадия /prd-gtm (Step 6) — 4P/каналы/Rory"
```

---

## Task 6: `/prd-solution` (Step 7, гейт PMF)

**Files:** Create: `.claude/commands/prd-solution.md`
**Interfaces:** cross-cutting линзы ost/ab-design/rat, sequenced. Produces product-узлы (opportunity/solution/experiment/ab-test/risk-card).

- [ ] **Step 1: Создать `.claude/commands/prd-solution.md`**

```markdown
---
description: 'Discovery Step 7 (Solution) — плейлист: OST → A/B → RAT; решение, эксперименты, риски + гейт PMF (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-solution
/prd-solution <lens_id>   # ost | ab-design | rat
```
Вход: узлы Step 2–6. Выход: product-узлы + state.yaml(solution).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-7-SOLUTION-PMF/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы customer/product (jtbd/outcome/value-prop) — вход и `depends_on`.

### Этап 2: Плейлист (эти линзы cross-cutting; здесь — рекомендуемая последовательность шага; каждая через lens_runtime):
- **ost** → outcome→opportunity→solution→experiment → узлы `opportunity`/`solution`/`experiment` (product, judgment), связанные `depends_on`.
- **ab-design** → дизайн эксперимента → `ab-test` (product, judgment).
- **rat** → топ-5 рисковых допущений (P×I) → `risk-card` (product, estimate; скоры `[estimate]`).
Мини-STOP после каждой.

### Этап 3: Гейт PMF (мягкий)
4. По `fit_gates.md`: Context Ripeness(product) ≥ 0.6 + PMF-критерии. Нет → 🟡, долг в open_questions. Напомни PO: PMF требует **evidence** (реальные эксперименты), не гипотез.

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(solution)` + `journal.md`.
```
Step 7 (Solution): линз L/3. Узлов N (product). CP: X. Гейт PMF: <🟢/🟡>. Риск-карт: r.
── СТОП ── PO. Дальше → /prd-acquisition.
```

## Запреты
1. Тела линз не редактировать. 2. Гипотезы решений → `judgment`, риск-скоры → `estimate`; узел без `sources` не создавать. 3. PMF ✅ только при `evidence`-узлах — не выдавать гипотезу за PMF. 4. RACI product → Product Engineer. `docs/` read-only.
```

- [ ] **Step 2: Проверка**
```bash
test -f .claude/commands/prd-solution.md && grep -q 'ost' .claude/commands/prd-solution.md && grep -q 'ab-design' .claude/commands/prd-solution.md && grep -q 'rat' .claude/commands/prd-solution.md && grep -q 'PMF' .claude/commands/prd-solution.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Commit**
```bash
git add .claude/commands/prd-solution.md
git commit -m "feat(prd-research): стадия /prd-solution (Step 7) — OST/A-B/RAT + гейт PMF"
```

---

## Task 7: `/prd-acquisition` (Step 8, гейт PCF)

**Files:** Create: `.claude/commands/prd-acquisition.md`
**Interfaces:** lenses (aarrr, distribution-channels). Produces growth-узлы (funnel-stage/input-metric/dist-channel).

- [ ] **Step 1: Создать `.claude/commands/prd-acquisition.md`**

```markdown
---
description: 'Discovery Step 8 (Acquisition) — плейлист: AARRR(acq) → каналы; конфиг привлечения + гейт PCF (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-acquisition
/prd-acquisition <lens_id>   # aarrr | distribution-channels
```
Вход: узлы Step 5–7. Выход: growth-узлы + state.yaml(acquisition).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md`, `resources/node_conventions.md`, `resources/lenses.yaml`, `resources/fit_gates.md`.
2. Прочитай `docs/AI-PROCESSES/STEP-8-ACQUISITION-PCF/overview.md`.

### Этап 1: PULSE
3. Прочитай узлы growth/product (unit-эк, каналы, воронка) — вход и `depends_on`.

### Этап 2: Плейлист (через lens_runtime):
- **aarrr** (acquisition-фокус) → воронка привлечения → `funnel-stage` (growth, judgment) + метрики → `input-metric` (growth, estimate).
- **distribution-channels** → конфиг «сегмент-канал-оффер» → `dist-channel` (growth, judgment).
Мини-STOP после каждой.

### Этап 3: Гейт PCF (мягкий)
4. По `fit_gates.md`: конфиг привлечения окупается (LTV/CAC). Нет данных → 🟡, долг в open_questions. Напомни: PCF требует **evidence** (реальная окупаемость).

### Этап 4: Состояние + СТОП
5. Обнови `state.yaml(acquisition)` + `journal.md`.
```
Step 8 (Acquisition): линз L/2. Узлов N (growth). CP: X. Гейт PCF: <🟢/🟡>.
── СТОП ── PO. Discovery-цикл пройден по всем 8 шагам → /prd-assemble (витрина), /prd-research (доска).
```

## Запреты
1. Тела линз не редактировать. 2. CAC/LTV/оценки → `estimate`; узел без `sources` не создавать. 3. PCF ✅ только при `evidence`. 4. RACI growth → Growth Engineer. `docs/` read-only.
```

- [ ] **Step 2: Проверка**
```bash
test -f .claude/commands/prd-acquisition.md && grep -q 'aarrr' .claude/commands/prd-acquisition.md && grep -q 'distribution-channels' .claude/commands/prd-acquisition.md && grep -q 'PCF' .claude/commands/prd-acquisition.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Commit**
```bash
git add .claude/commands/prd-acquisition.md
git commit -m "feat(prd-research): стадия /prd-acquisition (Step 8) — AARRR/каналы + гейт PCF"
```

---

## Task 8: pipeline.md плейлисты + регистрация в install.sh

**Files:**
- Modify: `.claude/skills/prd-research/resources/pipeline.md`
- Modify: `install.sh`

- [ ] **Step 1: pipeline.md — плейлисты шагов 3–8**

В `resources/pipeline.md` после существующей строки про линзы добавить:
```markdown
> **Плейлисты шагов 3–8:** Market → tam-sam-som · Value → nsm/odi/rory-interrogation (гейт Need/Value Fit) · BizModel → unit-economics/aarrr (гейт Biz-model) · GTM → positioning-4p/distribution-channels/rory-interrogation · Solution → ost/ab-design/rat (гейт PMF) · Acquisition → aarrr/distribution-channels (гейт PCF).
```

- [ ] **Step 2: install.sh — регистрация 6 команд**

В массиве `COMMANDS=( ... )` в строке с prd-командами дополнить до:
```bash
  prd-research prd-idea prd-assemble prd-customer prd-lens prd-market prd-value prd-bizmodel prd-gtm prd-solution prd-acquisition
```
Не удалять/переставлять существующие записи — только дополнить 6 новыми.

- [ ] **Step 3: Проверка**
```bash
cd "$(git rev-parse --show-toplevel)"
for c in prd-market prd-value prd-bizmodel prd-gtm prd-solution prd-acquisition; do grep -q "$c" install.sh || echo "MISS $c"; done
grep -q 'Плейлисты шагов 3–8' .claude/skills/prd-research/resources/pipeline.md && bash -n install.sh && echo OK || echo FAIL
```
Expected: no `MISS`, then `OK`.

- [ ] **Step 4: Commit**
```bash
git add .claude/skills/prd-research/resources/pipeline.md install.sh
git commit -m "feat(prd-research): pipeline плейлисты 3-8 + регистрация 6 команд в install.sh"
```

---

## Task 9: Сквозная проверка + статус спеки

**Files:** —

- [ ] **Step 1: Структурная целостность 8 шагов**
```bash
cd "$(git rev-parse --show-toplevel)"
for s in idea customer market value bizmodel gtm solution acquisition; do
  test -f ".claude/commands/prd-$s.md" && echo "ok  prd-$s" || echo "MISSING prd-$s"
done
grep -q 'dist-channel' sa_documentation/nexus_schema.md && echo "ok dist-channel"
python3 -c "import yaml; L={l['id']:l for l in yaml.safe_load(open('.claude/skills/prd-research/resources/lenses.yaml'))['lenses']}; print('harvest ok' if all('harvest' in L[i] for i in ['tam-sam-som','unit-economics','positioning-4p','segmentation','consumer-context','odi']) else 'harvest FAIL')"
```
Expected: 8 × `ok prd-*`, `ok dist-channel`, `harvest ok`.

- [ ] **Step 2: Сквозной dry-run (все 8 шагов)**
В тест-vault (узлы Step 1+2 есть): статически трассировать `/prd-market` → `/prd-value` → … → `/prd-acquisition` → `/prd-assemble`. Ожидаемо: каждый шаг создаёт валидные узлы своих node_type с корректным cp_policy (числа=estimate), `depends_on` связывает шаги; витрина показывает больше 🟡-разделов; ни один гейт (Value/BizModel/Solution/Acquisition) не отмечен ✅ без `evidence`-узлов.

- [ ] **Step 3: Обновить статус спеки**
В `docs/superpowers/specs/2026-07-06-research-lens-arsenal-design.md` шапку `Статус:` → `дизайн утверждён; итерации 2–3 реализованы (арсенал + все 8 шагов исполнимы)`.

- [ ] **Step 4: Commit**
```bash
git add docs/superpowers/specs/2026-07-06-research-lens-arsenal-design.md
git commit -m "docs(prd-research): все 8 шагов discovery исполнимы (итерация 3, PP-4)"
```

---

## Self-Review (план против спеки)

**Spec coverage:**
- §3.1 step-bound маппинг (Market/Value/BizModel/GTM/Solution/Acquisition) → Tasks 2–7 ✓
- §3.2 cross-cutting (ost/ab/rat/nsm) используются в плейлистах Value/Solution → Tasks 3,6 ✓
- §3.3 node_type — все используемые типы уже в §3.1; `channel`→`dist-channel` (ledger-Minor) → Task 1 ✓
- §4 CP-политики (estimate для чисел) → все команды ✓
- §6 PP-4..N порядок → эта итерация закрывает шаги 3–8 ✓
- §8 open-Q: odi per-host (Task 3 override + Task 1 note) ✓; OST-граф (узлы opportunity/solution/experiment со связями, Task 6) ✓
- fit-гейты Value/BizModel/Solution/Acquisition → Tasks 3,4,6,7 ✓

**Placeholder scan:** содержимое всех 6 команд приведено полностью; harvest-карты явные. Нет TBD. ✓

**Type consistency:** node_type (tam-sam-som/nsm-metric/input-metric/outcome/opportunity/value-prop/positioning/unit-econ/cohort/funnel-stage/four-p/dist-channel/solution/experiment/ab-test/risk-card/competitor), cp_policy (judgment/estimate), команды (/prd-market…/prd-acquisition) — согласованы между Task 1 и Tasks 2–8. ✓
