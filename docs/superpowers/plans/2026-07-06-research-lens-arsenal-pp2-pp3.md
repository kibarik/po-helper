# Research Lens Arsenal — Implementation Plan · Итерация 2 (PP-2 + PP-3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Собрать инфраструктуру сменных Research-линз (реестр 14 промтов + единый Wrap-исполнитель + `/prd-lens` диспетчер + расширение схемы) и эталонный хост-шаг `/prd-customer`, прогоняющий плейлист из 3 линз (segmentation → consumer-context → odi) с харвестом в customer-Нексус.

**Architecture:** Промты PO копируются дословно в `resources/lenses/*.md`; `lenses.yaml` — реестр (id, prompt_file, host_steps, harvest-map). Единый Wrap (`lens_runtime.md`) исполняет любую линзу: PULSE (вход из узлов) → запуск промта дословно → HARVEST (выход → узлы по Node schema). Шаг-команда `/prd-customer` = адаптивный плейлист линз; `/prd-lens <id>` = cross-cutting диспетчер.

**Tech Stack:** Markdown skill/command files; YAML frontmatter (Node schema §2.3/§3.1) + `lenses.yaml`; Obsidian vault (`GROUND/NEXUS/`); Bash + python3(yaml) для структурных проверок.

## Global Constraints

- **Промты дословны и read-only:** тело промта в `resources/lenses/*.md` не редактируется; Wrap добавляет только вход (PULSE) и персист (HARVEST). Источник — файлы PO в `/Users/aleksishmanov/Downloads/`.
- **Методология read-only:** `docs/AI-PROCESSES/`, `docs/TRADITIONAL/`, `docs/RL/`, `docs/AI-TRANSFORMATION/` не редактировать. Редактируемы: `.claude/`, `sa_documentation/`.
- **Оценка ≠ факт:** числа/гипотезы линз → `hyp_status: hypothesis`, CP по политике (`judgment` 0.2–0.4 / `estimate` 0.3–0.4 / `desk` 0.5–0.7 / `evidence` 0.6–1.0). Уважать собственную разметку `[Assumption]` промта. Узел без `sources` не создавать (workslop).
- **Node schema — единый контракт:** узлы линз пишутся во frontmatter с обяз. ключами (nexus, node_id, node_type, paf_step, kind, owner, confidence, sources, updated, ttl_days, ripeness, hyp_status, depends_on). node_type — из §3.1 (расширяется в Task 1).
- **RACI owners:** customer → Product Engineer; product → Product Engineer; market → Portfolio Manager; growth → Growth Engineer.
- **Язык артефактов:** русский. Промты (англ. по умолчанию) исполняются с инструкцией Wrap «отвечай по-русски».
- **STOP-паузы:** каждая линза/шаг завершается блоком СТОП (human-in-the-loop).
- **Регистрация:** новые команды → `install.sh` массив `COMMANDS`.

## Verification approach (нет автотест-харнесса)

Проверка — структурные shell-чек (`test -f`, grep ключей, `python3 -c` yaml-парс) + сценарные static-trace (интерактивные слэш-команды субагент не исполняет — трассирует статически и помечает deferred). Тест-фикстура для трейсов — vault из итерации 1: `/private/tmp/.../scratchpad/prd-test` (если удалён — пересоздать минимально).

---

## File Structure

**Создаём:**
- `.claude/skills/prd-research/resources/lenses/` — 14 файлов промтов (дословные копии).
- `.claude/skills/prd-research/resources/lenses.yaml` — реестр линз.
- `.claude/skills/prd-research/resources/lens_runtime.md` — контракт Wrap (PULSE/SCOUT/HARVEST/STOP + нормализация гейт-языка + input-pack).
- `.claude/commands/prd-lens.md` — cross-cutting диспетчер `/prd-lens <id>`.
- `.claude/commands/prd-customer.md` — Step 2 хост (плейлист 3 линз).

**Модифицируем:**
- `sa_documentation/nexus_schema.md` — §3.1: добавить discovery node_type арсенала.
- `.claude/skills/prd-research/resources/node_conventions.md` — CP-политики (judgment/estimate/desk/evidence).
- `.claude/skills/prd-research/resources/pipeline.md` — привязать линзы Step 2, ссылка на lenses.yaml.
- `.claude/skills/prd-research/SKILL.md` — раздел про Lens Registry + Wrap + /prd-lens.
- `install.sh` — `COMMANDS += prd-customer prd-lens`.

**Маппинг 14 источников → lenses/ (id):**
| Источник (`/Users/aleksishmanov/Downloads/…`) | dest `resources/lenses/<id>.md` | host_steps |
|---|---|---|
| `Анализ нишевых возможностей.txt` | `niche-opportunities.md` | [idea] |
| `Сегментация ЦА.txt` | `segmentation.md` | [customer] |
| `Единый контекст потребителя.txt` | `consumer-context.md` | [customer] |
| `Outcome-Driven Innovation.txt` | `odi.md` | [customer, value] |
| `TAM _ SAM _ SOM.txt` | `tam-sam-som.md` | [market] |
| `NSM - консультант.txt` | `nsm.md` | [] cross |
| `Маркетинговый допрос (Rory Sutherland).txt` | `rory-interrogation.md` | [value, gtm] |
| `Проектирование UNIT-экономики.txt` | `unit-economics.md` | [bizmodel] |
| `Проектирование AARRR воронки.txt` | `aarrr.md` | [bizmodel, acquisition] |
| `4P распаковка позиционирования.txt` | `positioning-4p.md` | [gtm] |
| `Выбор каналов дистрибуции.txt` | `distribution-channels.md` | [gtm, acquisition] |
| `OST (Opportunity Solution Tree).txt` | `ost.md` | [] cross |
| `Проектирование A_B.txt` | `ab-design.md` | [] cross |
| `RAT -  анализ продуктовых рисков запуска.txt` | `rat.md` | [] cross |

---

## Task 1: Расширение схемы — node_type арсенала + CP-политики

Фундамент: новые artefact-типы и политики доверия, на которые ссылаются harvest-map линз.

**Files:**
- Modify: `sa_documentation/nexus_schema.md` (§3.1 — добавить строки)
- Modify: `.claude/skills/prd-research/resources/node_conventions.md` (добавить раздел «CP-политики»)

**Interfaces:**
- Produces: валидные `node_type` для узлов линз; таблица `cp_policy` → `hyp_status`+CP.

- [ ] **Step 1: Проверка (ожидаемо провалится)**

Run:
```bash
grep -q 'segment' sa_documentation/nexus_schema.md && grep -q 'cp_policy\|CP-полит' .claude/skills/prd-research/resources/node_conventions.md && echo OK || echo FAIL
```
Expected: `FAIL`

- [ ] **Step 2: Дополнить §3.1 в `sa_documentation/nexus_schema.md`**

В подсекции `### 3.1 Discovery artifact-типы` в таблицу типов добавить строки (перед закрывающей заметкой про Steps 2/4–8):

```markdown
| `opportunity` | niche-opportunities, OST | market/customer |
| `segment` | segmentation | customer |
| `jtbd` | segmentation, ODI | customer |
| `outcome` | ODI (desired outcome) | customer/product |
| `persona-context` | consumer-context | customer |
| `nsm-metric` | NSM | product/growth |
| `input-metric` | NSM, AARRR | growth |
| `value-prop` | consumer-context, ODI | product |
| `unit-econ` | unit-economics | growth |
| `cohort` | unit-economics, AARRR | growth |
| `funnel-stage` | AARRR | growth |
| `positioning` | 4P, Rory | product/growth |
| `four-p` | 4P | growth |
| `channel` | distribution-channels | growth |
| `risk-card` | RAT | product |
| `solution` | OST | product |
| `experiment` | OST | product |
| `ab-test` | A/B design | product/growth |
```

- [ ] **Step 3: Добавить раздел «CP-политики» в `node_conventions.md`**

В конец файла добавить:

```markdown
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
```

- [ ] **Step 4: Проверка**

Run:
```bash
grep -q '`segment`' sa_documentation/nexus_schema.md && grep -q '`value-prop`' sa_documentation/nexus_schema.md && grep -q 'cp_policy' .claude/skills/prd-research/resources/node_conventions.md && grep -q 'estimate' .claude/skills/prd-research/resources/node_conventions.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/nexus_schema.md .claude/skills/prd-research/resources/node_conventions.md
git commit -m "feat(prd-research): §3.1 node_type арсенала + CP-политики линз (judgment/estimate/desk/evidence)"
```

---

## Task 2: Копии 14 промтов + реестр lenses.yaml

**Files:**
- Create: `.claude/skills/prd-research/resources/lenses/` (14 файлов)
- Create: `.claude/skills/prd-research/resources/lenses.yaml`

**Interfaces:**
- Produces: `lenses.yaml` — список из 14 линз; каждая с `id, title, prompt_file, role, host_steps, cross_cutting, lang`. Для 3 customer-линз (segmentation, consumer-context, odi) — блок `harvest`.

- [ ] **Step 1: Скопировать 14 промтов дословно**

Run (точный маппинг источник→dest из «File Structure»):
```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p .claude/skills/prd-research/resources/lenses
D="/Users/aleksishmanov/Downloads"; L=".claude/skills/prd-research/resources/lenses"
cp "$D/Анализ нишевых возможностей.txt"            "$L/niche-opportunities.md"
cp "$D/Сегментация ЦА.txt"                          "$L/segmentation.md"
cp "$D/Единый контекст потребителя.txt"            "$L/consumer-context.md"
cp "$D/Outcome-Driven Innovation.txt"               "$L/odi.md"
cp "$D/TAM _ SAM _ SOM.txt"                          "$L/tam-sam-som.md"
cp "$D/NSM - консультант.txt"                        "$L/nsm.md"
cp "$D/Маркетинговый допрос (Rory Sutherland).txt"  "$L/rory-interrogation.md"
cp "$D/Проектирование UNIT-экономики.txt"          "$L/unit-economics.md"
cp "$D/Проектирование AARRR воронки.txt"           "$L/aarrr.md"
cp "$D/4P распаковка позиционирования.txt"         "$L/positioning-4p.md"
cp "$D/Выбор каналов дистрибуции.txt"              "$L/distribution-channels.md"
cp "$D/OST (Opportunity Solution Tree).txt"         "$L/ost.md"
cp "$D/Проектирование A_B.txt"                       "$L/ab-design.md"
cp "$D/RAT -  анализ продуктовых рисков запуска.txt" "$L/rat.md"
ls "$L" | wc -l
```
Expected: `14`

- [ ] **Step 2: Создать `resources/lenses.yaml`**

```yaml
# Реестр Research-линз. Промт-тело — в resources/lenses/<id>.md (дословно, read-only).
# harvest добавляется, когда host-шаг реализован (сейчас — для 3 customer-линз).
lenses:
  - id: niche-opportunities
    title: "Анализ нишевых возможностей"
    prompt_file: "resources/lenses/niche-opportunities.md"
    role: "Senior digital market analyst — ранжирование ниш/ROI"
    host_steps: [idea]
    cross_cutting: false
    lang: ru
  - id: segmentation
    title: "Сегментация ЦА"
    prompt_file: "resources/lenses/segmentation.md"
    role: "Expert PM — сегментация B2B/SaaS (6-step)"
    host_steps: [customer]
    cross_cutting: false
    lang: ru
    harvest:
      - output: "HIGH-сегменты (STEP 6 summary)"
        nexus: customer
        node_type: segment
        cp_policy: estimate
      - output: "JTBD каждого HIGH-сегмента"
        nexus: customer
        node_type: jtbd
        cp_policy: judgment
      - output: "5 тестируемых гипотез сегмента (STEP 5)"
        nexus: customer
        node_type: opportunity
        cp_policy: judgment
  - id: consumer-context
    title: "Единый контекст потребителя"
    prompt_file: "resources/lenses/consumer-context.md"
    role: "Consumer Context Analysis Expert (Тихомиров)"
    host_steps: [customer]
    cross_cutting: false
    lang: ru
    harvest:
      - output: "context_structure (Stage 3)"
        nexus: customer
        node_type: persona-context
        cp_policy: judgment
      - output: "value_propositions (Stage 5)"
        nexus: product
        node_type: value-prop
        cp_policy: judgment
  - id: odi
    title: "Outcome-Driven Innovation"
    prompt_file: "resources/lenses/odi.md"
    role: "Lead ODI Consultant (Ulwick)"
    host_steps: [customer, value]
    cross_cutting: false
    lang: ru
    harvest:
      - output: "Core Functional Job"
        nexus: customer
        node_type: jtbd
        cp_policy: judgment
      - output: "Desired Outcome Statements"
        nexus: customer
        node_type: outcome
        cp_policy: judgment
      - output: "Opportunity Scores (Mode CALCULATION)"
        nexus: customer
        node_type: opportunity
        cp_policy: estimate
  - id: tam-sam-som
    title: "TAM / SAM / SOM"
    prompt_file: "resources/lenses/tam-sam-som.md"
    role: "Senior TAM/SAM/SOM consultant"
    host_steps: [market]
    cross_cutting: false
    lang: ru
  - id: nsm
    title: "North Star Metric"
    prompt_file: "resources/lenses/nsm.md"
    role: "North Star Framework consultant"
    host_steps: []
    cross_cutting: true
    lang: ru
  - id: rory-interrogation
    title: "Маркетинговый допрос (Rory Sutherland)"
    prompt_file: "resources/lenses/rory-interrogation.md"
    role: "Behavioral marketing strategist (Rory Sutherland)"
    host_steps: [value, gtm]
    cross_cutting: false
    lang: ru
  - id: unit-economics
    title: "Проектирование UNIT-экономики"
    prompt_file: "resources/lenses/unit-economics.md"
    role: "Unit economics consultant"
    host_steps: [bizmodel]
    cross_cutting: false
    lang: ru
  - id: aarrr
    title: "Проектирование AARRR воронки"
    prompt_file: "resources/lenses/aarrr.md"
    role: "Product analytics & growth consultant (AARRR)"
    host_steps: [bizmodel, acquisition]
    cross_cutting: false
    lang: ru
  - id: positioning-4p
    title: "4P распаковка позиционирования"
    prompt_file: "resources/lenses/positioning-4p.md"
    role: "4P positioning consultant"
    host_steps: [gtm]
    cross_cutting: false
    lang: ru
  - id: distribution-channels
    title: "Выбор каналов дистрибуции"
    prompt_file: "resources/lenses/distribution-channels.md"
    role: "Geography & distribution channel consultant"
    host_steps: [gtm, acquisition]
    cross_cutting: false
    lang: ru
  - id: ost
    title: "Opportunity Solution Tree"
    prompt_file: "resources/lenses/ost.md"
    role: "OST consultant (Teresa Torres)"
    host_steps: []
    cross_cutting: true
    lang: ru
  - id: ab-design
    title: "Проектирование A/B"
    prompt_file: "resources/lenses/ab-design.md"
    role: "A/B experiment design assistant"
    host_steps: []
    cross_cutting: true
    lang: ru
  - id: rat
    title: "RAT — анализ рисков запуска"
    prompt_file: "resources/lenses/rat.md"
    role: "Risky Assumption Testing expert (JTBD)"
    host_steps: []
    cross_cutting: true
    lang: ru
```

- [ ] **Step 3: Проверка (файлы + валидный YAML + 14 записей + prompt_file существуют)**

Run:
```bash
cd "$(git rev-parse --show-toplevel)"
python3 - <<'PY'
import yaml,os
r=yaml.safe_load(open('.claude/skills/prd-research/resources/lenses.yaml'))
ls=r['lenses']; assert len(ls)==14, len(ls)
req={'id','title','prompt_file','role','host_steps','cross_cutting','lang'}
base='.claude/skills/prd-research'
for l in ls:
    assert req<=set(l), (l['id'], req-set(l))
    assert os.path.exists(os.path.join(base,l['prompt_file'])), l['prompt_file']
    assert os.path.getsize(os.path.join(base,l['prompt_file']))>0
for cid in ('segmentation','consumer-context','odi'):
    l=[x for x in ls if x['id']==cid][0]; assert 'harvest' in l and l['harvest'], cid
print("OK 14 lenses, files present, customer harvest set")
PY
```
Expected: `OK 14 lenses, files present, customer harvest set`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/prd-research/resources/lenses/ .claude/skills/prd-research/resources/lenses.yaml
git commit -m "feat(prd-research): 14 промтов-линз (дословно) + реестр lenses.yaml"
```

---

## Task 3: Wrap-исполнитель (lens_runtime.md) + SKILL.md

**Files:**
- Create: `.claude/skills/prd-research/resources/lens_runtime.md`
- Modify: `.claude/skills/prd-research/SKILL.md` (добавить раздел про линзы)

**Interfaces:**
- Consumes: `lenses.yaml` (Task 2), node_conventions CP-политики (Task 1).
- Produces: единый контракт исполнения линзы (PULSE/SCOUT/HARVEST/STOP), на который ссылаются `/prd-customer` и `/prd-lens`.

- [ ] **Step 1: Создать `resources/lens_runtime.md`**

```markdown
# prd-research — Wrap: единый исполнитель линзы

Любая линза (шаговая или cross-cutting) исполняется одинаково. Промт-тело (`resources/lenses/<id>.md`) — read-only, НЕ редактируется; Wrap добавляет только вход и персист.

## PULSE — собрать вход
1. По `lenses.yaml` найти линзу по `id`; прочитать `prompt_file`, `host_steps`, `harvest`.
2. Прочитать `GROUND/NEXUS/_registry.yaml` + существующие узлы шага-хозяина и узлы-первопричины (по теме).
3. Собрать **input-пак** и заполнить входную форму промта (`input_request`/Input Block/Context): `product_description`, `target_audience`, `problem_or_hypothesis`, прошлые находки (Step 1 узлы и т.д.). Пусто → `[УТОЧНИТЬ]`, не выдумывать.

## SCOUT — запустить промт дословно
4. Исполнить промт линзы **как есть**: его роль, стадийность, структурный вывод (YAML/карточки), его правила `[Assumption]`.
5. **Нормализация гейт-языка (обёртка, не правка тела):** перед запуском объяви PO: «переход между стадиями — командой `продолжить`/`далее`; правка — `ревизия`». Разные сигналы промтов (`start`/`next`/`continue`) трактуй как эти команды. Тело промта не меняем.
6. **Язык:** если промт англ. по умолчанию — инструктируй «отвечай по-русски» (промты это допускают).
7. `data_needed`/недостаток данных → показать PO список недостающего, пауза (как предписывает промт).

## HARVEST — персист выходов в узлы
8. По `harvest`-мапу линзы: каждый указанный `output` → узел в `nexus` с `node_type`, `cp_policy` (см. node_conventions «CP-политики»). Frontmatter — строго по node_conventions (обяз. ключи + hyp_status/CP по политике + sources + depends_on на input-узлы + ttl_days по нексусу + ripeness: fresh).
9. Уважать разметку допущений промта: помеченное `[Assumption]`/оценка → `estimate`/`judgment`, не `validated`.
10. Узел без `sources` не создавать.
11. Обновить `{discovery_workspace(step)}/state.yaml` (nodes/cp/status/open_questions/last_touched) + дописать `journal.md` (какая линза, какие выходы, ссылки).

## STOP
Отчёт: линза, создано узлов N по типам, средний CP, `[estimate]`-узлов k. Пауза PO.

> Cross-cutting линза (`host_steps: []`) исполняется тем же Wrap, но HARVEST-нексус берётся из контекста текущего шага (диспетчер `/prd-lens` передаёт `step`).
```

- [ ] **Step 2: Добавить раздел в `SKILL.md`**

После раздела «## Движок каждой стадии» вставить:

```markdown
## Research Lens Arsenal (сменные линзы)

Шаги наполняются проверенными промтами PO как **сменными линзами** (реестр `resources/lenses.yaml`, тела — `resources/lenses/<id>.md`, дословно). Единый исполнитель — `resources/lens_runtime.md` (PULSE → запуск промта дословно → HARVEST в узлы).

- Шаг-команда `/prd-<step>` = адаптивный плейлист линз шага (рекомендуемый порядок, PO волен отклоняться).
- Cross-cutting линзы (rat/ab-design/ost/nsm) — через `/prd-lens <id>` на текущем шаге; оркестратор предлагает их на гейтах.
- Промт не редактируется; Wrap добавляет только вход и персист. Оценки линз → `estimate`/`judgment` (низкий CP), не факты.
```

- [ ] **Step 3: Проверка**

Run:
```bash
test -f .claude/skills/prd-research/resources/lens_runtime.md && grep -q 'HARVEST' .claude/skills/prd-research/resources/lens_runtime.md && grep -q 'Research Lens Arsenal' .claude/skills/prd-research/SKILL.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/prd-research/resources/lens_runtime.md .claude/skills/prd-research/SKILL.md
git commit -m "feat(prd-research): Wrap-исполнитель линз (lens_runtime) + раздел Lens Arsenal в SKILL"
```

---

## Task 4: Cross-cutting диспетчер `/prd-lens`

**Files:**
- Create: `.claude/commands/prd-lens.md`

**Interfaces:**
- Consumes: lenses.yaml, lens_runtime.md.
- Produces: команда `/prd-lens <id>` — запускает cross-cutting линзу на текущем шаге.

- [ ] **Step 1: Создать `.claude/commands/prd-lens.md`**

```markdown
---
description: 'Cross-cutting Research-линза — запуск rat/ab-design/ost/nsm на текущем шаге через единый Wrap (роль: по линзе)'
---

## Использование

```
/prd-lens <id> [step]
```
`<id>` — из lenses.yaml (rat | ab-design | ost | nsm). `[step]` — текущий шаг для HARVEST-нексуса (по умолчанию — активный шаг доски).

Пример: `/prd-lens rat solution`

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `skills/prd-research/SKILL.md` и `skills/prd-research/resources/lens_runtime.md`.
2. Прочитай `skills/prd-research/resources/lenses.yaml`; найди линзу по `<id>`. Нет / не `cross_cutting` → сообщи PO и остановись.
3. Определи `step` (аргумент или активный шаг из state.yaml доски).

### Этап 2: Исполнение по Wrap
4. Исполни линзу строго по `lens_runtime.md`: PULSE (вход из узлов `step` + первопричин) → запуск `prompt_file` дословно (гейты `продолжить/ревизия`, язык ru) → HARVEST.
5. HARVEST: если у линзы есть `harvest` — по нему; иначе (rat/ab-design/ost/nsm без harvest в реестре) создай узлы по природе выхода: rat → `risk-card` (product), ab-design → `ab-test` (product), ost → `opportunity`/`solution`/`experiment` (product), nsm → `nsm-metric`/`input-metric` (growth). CP-политика: risk/ab/ost → `judgment` (или `estimate` для числовых); nsm → `judgment`. Нексус — по `step`.

### Этап 3: СТОП
```
Линза <id> на шаге <step>: создано узлов N (<типы>). Средний CP: X. [estimate]: k.
── СТОП ── PO: проверь узлы. Вернуться к доске → /prd-research.
```

## Запреты
1. Тело промта линзы НЕ редактировать — только вход/персист (Wrap).
2. Оценки/допущения → `estimate`/`judgment`, не `validated`. Узел без `sources` не создавать.
3. Линза не `cross_cutting` → не запускать здесь (это шаг-команда `/prd-<step>`).
```

- [ ] **Step 2: Проверка**

Run:
```bash
test -f .claude/commands/prd-lens.md && grep -q 'lens_runtime' .claude/commands/prd-lens.md && grep -q 'cross_cutting' .claude/commands/prd-lens.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/prd-lens.md
git commit -m "feat(prd-research): команда /prd-lens — cross-cutting диспетчер линз (rat/ab/ost/nsm)"
```

---

## Task 5: Эталонный хост-шаг `/prd-customer` (плейлист 3 линз)

**Files:**
- Create: `.claude/commands/prd-customer.md`

**Interfaces:**
- Consumes: lenses.yaml (segmentation/consumer-context/odi + harvest), lens_runtime.md, Step 1 узлы (depends_on).
- Produces: узлы в `GROUND/NEXUS/{customer,product}/` (segment/jtbd/outcome/persona-context/value-prop/opportunity) + `state.yaml(customer)`.

- [ ] **Step 1: Создать `.claude/commands/prd-customer.md`**

```markdown
---
description: 'Discovery Step 2 (Customer) — адаптивный плейлист линз: сегментация → единый контекст → ODI; наполняет customer-Нексус (роль: Discovery Facilitator + консультант линзы)'
---

## Использование

```
/prd-customer            # весь плейлист по порядку
/prd-customer <lens_id>  # запустить одну линзу шага (segmentation|consumer-context|odi)
```

Вход: узлы Step 1 (market/product/growth). Выход: узлы customer-Нексуса + state.yaml(customer).

## Инструкция для LLM

### Этап 0: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`, `resources/lens_runtime.md` (Wrap), `resources/node_conventions.md` (frontmatter + CP-политики), `resources/lenses.yaml` (линзы customer).
2. Прочитай `docs/AI-PROCESSES/STEP-2-CUSTOMER/overview.md` (какие фазы активны).

### Этап 1: PULSE — вход из Step 1
3. Прочитай узлы market/product/growth (особенно `idea-lens-market-*`) — они станут input-паком и `depends_on` для узлов Customer. Пусто → предложи PO сначала `/prd-idea`.

### Этап 2: Плейлист линз (адаптивно; PO может пропустить/переставить)
Рекомендуемый порядок: `segmentation` → `consumer-context` → `odi`. Для каждой линзы — исполни по `lens_runtime.md` (PULSE→промт дословно→HARVEST):

- **segmentation** → HARVEST по lenses.yaml: HIGH-сегменты → `segment` (customer, `estimate`), JTBD → `jtbd` (customer, `judgment`), 5 гипотез сегмента → `opportunity` (customer, `judgment`). `depends_on` = релевантные Step 1 узлы.
- **consumer-context** → context_structure → `persona-context` (customer, `judgment`); value_propositions → `value-prop` (product, `judgment`, depends_on сегмент).
- **odi** → Core Job → `jtbd` (customer); Desired Outcomes → `outcome` (customer); Opportunity Scores → `opportunity` (customer, `estimate`).

После каждой линзы — мини-STOP (PO проверяет её узлы).

### Этап 3: HARVEST-свод + состояние
4. Обнови `{discovery_workspace(customer)}/state.yaml`: nodes[], cp (среднее), status (`converging`/`gate-ready`), open_questions[], last_touched. Допиши `journal.md` (какие линзы пройдены).

### Этап 4: СТОП
```
Step 2 (Customer): линз пройдено L/3. Узлов N (customer a / product b). Средний CP: X.
[estimate]-узлов: k. Открытых вопросов: q.
── СТОП ── PO: проверь узлы. Дальше → /prd-market, /prd-lens rat (риски), либо /prd-assemble.
```

## Запреты
1. Тело промтов-линз НЕ редактировать (Wrap: только вход/персист).
2. Оценки (размеры сегментов, LTV/CAC, scores) → `estimate` CP ≤ 0.4, не факт. Узел без `sources` не создавать.
3. «Не знаю» PO → `hyp_status: parked`, не выдумывать.
4. RACI: customer → Product Engineer, product → Product Engineer. Методология `docs/` read-only.
```

- [ ] **Step 2: Проверка**

Run:
```bash
test -f .claude/commands/prd-customer.md && grep -q 'segmentation' .claude/commands/prd-customer.md && grep -q 'consumer-context' .claude/commands/prd-customer.md && grep -q 'odi' .claude/commands/prd-customer.md && grep -q 'lens_runtime' .claude/commands/prd-customer.md && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 3: Acceptance dry-run (ручной, статически)**

Сценарий: в тест-vault (с узлами Step 1 из итерации 1) вызвать `/prd-customer`.
Ожидаемо (трассировать по тексту команды + lens_runtime, интерактив deferred): PULSE читает `idea-lens-market-channel`; плейлист запускает segmentation (YAML-стадии) → создаёт `segment`/`jtbd` узлы customer с `estimate`/`judgment` CP и `depends_on: [idea-lens-market-channel]`; consumer-context → `persona-context`+`value-prop`; odi → `outcome`. state.yaml(customer) обновлён. Ни один размерный показатель не помечен `validated`.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/prd-customer.md
git commit -m "feat(prd-research): стадия /prd-customer (Step 2) — плейлист 3 линз с харвестом в customer-Нексус"
```

---

## Task 6: pipeline.md + регистрация в install.sh

**Files:**
- Modify: `.claude/skills/prd-research/resources/pipeline.md`
- Modify: `install.sh`

- [ ] **Step 1: Аннотировать pipeline.md**

В `resources/pipeline.md` после таблицы 8 шагов добавить строку:
```markdown
> **Линзы шагов** — `resources/lenses.yaml` (реестр) + `resources/lenses/<id>.md` (промты дословно). Step 2 Customer: плейлист segmentation → consumer-context → odi. Cross-cutting (rat/ab-design/ost/nsm) — через `/prd-lens`.
```

- [ ] **Step 2: Зарегистрировать команды в install.sh**

В массиве `COMMANDS=( ... )`, в строку с prd-командами (`prd-research prd-idea prd-assemble`) добавить `prd-customer prd-lens`:
```bash
  prd-research prd-idea prd-assemble prd-customer prd-lens
```

- [ ] **Step 3: Проверка**

Run:
```bash
grep -q 'lenses.yaml' .claude/skills/prd-research/resources/pipeline.md && grep -q 'prd-customer' install.sh && grep -q 'prd-lens' install.sh && bash -n install.sh && echo OK || echo FAIL
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/prd-research/resources/pipeline.md install.sh
git commit -m "feat(prd-research): pipeline линзы Step 2 + регистрация /prd-customer /prd-lens в install.sh"
```

---

## Task 7: Сквозная проверка итерации

**Files:** —

- [ ] **Step 1: Структурная целостность арсенала**

Run:
```bash
cd "$(git rev-parse --show-toplevel)"
echo "-- lenses files --"; ls .claude/skills/prd-research/resources/lenses/*.md | wc -l   # ждём 14
echo "-- новые артефакты --"
for f in .claude/skills/prd-research/resources/lenses.yaml \
         .claude/skills/prd-research/resources/lens_runtime.md \
         .claude/commands/prd-lens.md .claude/commands/prd-customer.md; do
  test -f "$f" && echo "ok  $f" || echo "MISSING $f"
done
python3 -c "import yaml; l=yaml.safe_load(open('.claude/skills/prd-research/resources/lenses.yaml'))['lenses']; print('lenses:',len(l))"
grep -q '`segment`' sa_documentation/nexus_schema.md && echo "ok node_type §3.1" || echo "FAIL node_type"
```
Expected: `14`, четыре `ok`, `lenses: 14`, `ok node_type §3.1`.

- [ ] **Step 2: Сквозной dry-run (customer поверх Step 1)**

В тест-vault: `/prd-idea` (из итерации 1 уже даёт Step-1 узлы) → `/prd-customer` → `/prd-research` (доска: Step 2 не `planned`) → `/prd-assemble` (раздел «Потребитель» 🟡 assumed).
Ожидаемо: customer-узлы валидны по Node schema (новые node_type), оценки `estimate` не выданы за validated, `depends_on` связывает с Step 1.

- [ ] **Step 3: Обновить статус спеки**

В `docs/superpowers/specs/2026-07-06-research-lens-arsenal-design.md` шапку `Статус:` → `дизайн утверждён; итерация 2 (PP-2 инфраструктура + PP-3 Customer) реализована`.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-07-06-research-lens-arsenal-design.md
git commit -m "docs(prd-research): отметить реализацию итерации 2 (PP-2 + PP-3) в спеке арсенала"
```

---

## Self-Review (план против спеки)

**Spec coverage:**
- §1.2 Lens определение → lenses.yaml схема (Task 2) ✓
- §2.1 реестр → Task 2 ✓; §2.2 Wrap → lens_runtime (Task 3) ✓; §2.3 команды → /prd-lens (Task 4), /prd-customer (Task 5) ✓; §2.4 адаптивный плейлист → Task 5 ✓
- §3.1 step-bound маппинг (Customer) → Task 5 ✓; §3.2 cross-cutting → Task 4 ✓; §3.3 node_type → Task 1 ✓
- §4 CP-политики → Task 1 (node_conventions) ✓
- §5 витрина эволюция → **вне итерации** (PP-cross, отмечено в §6 спеки) ✓ (осознанный scope)
- §6 порядок → эта итерация = PP-2 (Tasks 1–4,6) + PP-3 (Task 5) ✓
- 14 промтов копии → Task 2 ✓

**Placeholder scan:** содержимое всех файлов приведено; для 11 не-customer линз `harvest` в реестре намеренно отсутствует (добавляется при сборке их шага — не placeholder, а optional-поле схемы). Ссылки «mirror prd-idea.md» указывают на существующий файл. ✓

**Type consistency:** node_type (segment/jtbd/outcome/persona-context/value-prop/opportunity), cp_policy (judgment/estimate/desk/evidence), lens-поля (id/prompt_file/host_steps/cross_cutting/harvest), команды (/prd-customer, /prd-lens) — согласованы между Tasks 1,2,3,4,5. ✓
