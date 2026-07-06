# OKR Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить навык `okr-status` — 3-стадийный pipeline подведения промежуточного/итогового статуса квартальных OKR для руководства с фактуркой ПЛАН/ФАКТ/ИЗМЕНЕНИЕ по каждому KR.

**Architecture:** Навык оформлен по конвенции каркаса: `SKILL.md` + `resources/` + `examples/` в `.claude/skills/okr-status/`, а три стадии — слэш-команды в `.claude/commands/`. Стадия 1 (`/okr-status-sync`) собирает ФАКТ параллельными субагентами (JIRA · релизы+спринт-ФАКТ · переписки+люди) с кросс-валидацией; стадия 2 (`/okr-status-assess`) считает по каждому KR светофор + прогноз EOQ + дрейф; стадия 3 (`/okr-status-report`) финализирует с PO и собирает один `.md` для руководства. Переиспользуются progress-шкала/IMP из `okr-planner` и drift-формулы из `release-guard` — без дублирования.

**Tech Stack:** Markdown-артефакты (skills/commands каркаса Claude Code). Инструменты внутри команд: `atlassian` (JIRA MCP), `obsidian.vault_write/vault_patch`, `repowise` (best-effort), субагенты через Task/Agent. Никакого исполняемого кода — «тесты» = структурные grep-инварианты (frontmatter, обязательные секции, отсутствие висячих `{переменных}` и битых ссылок).

## Global Constraints

Скопировано дословно из спеки `docs/superpowers/specs/2026-07-07-okr-status-design.md`. Требования каждой задачи неявно включают этот раздел:

- **Нулевой допуск к галлюцинациям.** Каждый ФАКТ ← JIRA-key / `status.md` / спринт-ФАКТ / якорь summary / узел People Graph. Нет источника → `[УТОЧНИТЬ]`. Прогноз EOQ обоснован фактом, не «на глаз».
- **Параллельность обязательна.** Субагенты A–C стадии 1 запускаются одновременно, не последовательно.
- **Конфликты не схлопываются.** Разногласие источников → явный раздел «Разногласия источников».
- **Честно про недоступность.** VPN/MCP недоступен → `[НЕДОСТУПНО: <источник>]`, состав ФАКТА не выдумывается.
- **STOP после каждой стадии.** Human-in-the-loop, особенно на финализации отчёта.
- **Переиспользование, не дублирование.** progress-шкала и IMP — из `okr-planner/resources/okr_standards.md`; drift-формулы — из `release-guard/resources/release_standards.md` §8; ФАКТ спринта — из `sprint-fact`; сигналы каналов — из `info-channels`; люди — из People Graph (нексус `team`).
- **Стиль артефактов** — по `.claude/skills/bft-writer/resources/writing_style.md`: деловая проза, семантические эмодзи только как маркеры (светофор 🟢🟡🔴, статус субагентов 🔵🟢🔴, `✅`/`⚠️` в матрицах), без декоративных эмодзи.
- **Пути в фигурных скобках** (`{status_workspace}`, `{status_report_doc}`, `{planning_root}`, `{index_doc}`, `{kr_epic_map_doc}`, `{okr_output_doc}`, `{execution_root}`, `{release_workspace}`, `{summary_notes}`, `{tracker.mcp}`, `{tracker.projects}`) резолвятся из `.claude/domain-profile.md` проекта. Пустое поле → дефолт + `[УТОЧНИТЬ]`.

## Deviations from spec (важно для исполнителя)

1. **`role_bindings` / `source_policy` отсутствуют в `domain-profile.template.md`** (проверено grep — есть только в `/bft-context-gen-deep` как forward-конвенция). Поэтому стадия `/okr-status-sync` резолвит доступность из **реального** `tracker` (`mcp`/`access`/`projects`) + доступных коннекторов и честно помечает `[НЕДОСТУПНО]`. `role_bindings`/`source_policy` упоминаются как «если заданы в профиле», но **не являются жёсткой зависимостью**. Класс `status-critical` в профиль **не добавляем** — единственный жёстко требуемый источник (JIRA) резолвится из `tracker.mcp`.
2. **Confluence + Код** — best-effort обогащение внутри субагента A/дополнительного шага, не отдельный жёсткий субагент (соответствует ответу PO в брейншторминге).

## File Structure

Новые файлы:

- `.claude/skills/okr-status/resources/status_standards.md` — единый источник правды: checkpoint-модель, % готовности (reuse progress-шкала), светофор-рубрика KR, модель прогноза EOQ, drift-формулы (reuse), формат таблицы ПЛАН/ФАКТ/ИЗМЕНЕНИЕ, схемы `fact-pack.md` / `assessment.md` / отчёта.
- `.claude/skills/okr-status/resources/hard_gates.md` — бинарные гейты статуса + Светофор.
- `.claude/skills/okr-status/examples/ideal_status_report.md` — эталонный отчёт (аннотированный).
- `.claude/skills/okr-status/SKILL.md` — обзор навыка: роль, pipeline, принципы, ссылки на ресурсы.
- `.claude/commands/okr-status-sync.md` — стадия 1 (Fact Investigator).
- `.claude/commands/okr-status-assess.md` — стадия 2 (Progress Assessor).
- `.claude/commands/okr-status-report.md` — стадия 3 (Reporter + Finalizer).

Модифицируемые файлы:

- `domain-profile.template.md` — новые пути `{status_workspace}`, `{status_report_doc}`.
- `README.md` — строка/раздел про `okr-status`.
- `sa_documentation/nexus_process_map.md` — регистрация процесса `okr-status`.

Порядок задач следует зависимостям: пути → стандарты → гейты → SKILL → пример → команды (sync→assess→report) → регистрация + сквозная проверка целостности.

---

### Task 1: Пути `okr-status` в domain-profile

**Files:**
- Modify: `domain-profile.template.md:40` (после строки `okr_grooming_root:`)

**Interfaces:**
- Consumes: ничего.
- Produces: две path-переменные, на которые ссылаются все команды навыка:
  - `status_workspace` = `"CORTEX/_context-packs/okr-status/{quarter}"`
  - `status_report_doc` = `"GROUND/NEXUS/project-management/{quarter}/Статус/OKR-STATUS-{quarter}-{checkpoint}.md"`

- [ ] **Step 1: Написать проверку-инвариант (должна упасть)**

Run: `grep -c "status_workspace\|status_report_doc" domain-profile.template.md`
Expected: `0` (переменных ещё нет).

- [ ] **Step 2: Вставить переменные в секцию `paths`**

В `domain-profile.template.md` сразу после строки 40 (`  okr_grooming_root: "{okr_workspace}/grooming"`) добавить:

```yaml
  # Рабочая папка пайплайна okr-status (fact-pack + assessment + raw/ субагентов). {quarter} — подстановка
  status_workspace:  "CORTEX/_context-packs/okr-status/{quarter}"
  # Финальный статус-отчёт по кварталу (рядом с Планированием). {checkpoint} = equator | final
  status_report_doc: "GROUND/NEXUS/project-management/{quarter}/Статус/OKR-STATUS-{quarter}-{checkpoint}.md"
```

- [ ] **Step 3: Проверить, что переменные добавлены и YAML не сломан**

Run: `grep -n "status_workspace\|status_report_doc" domain-profile.template.md`
Expected: две строки с корректными путями.
Run: `grep -n "  okr_grooming_root" domain-profile.template.md`
Expected: строка на месте, отступ (2 пробела) совпадает с новыми ключами.

- [ ] **Step 4: Commit**

```bash
git add domain-profile.template.md
git commit -m "feat(okr-status): пути status_workspace и status_report_doc в domain-profile"
```

---

### Task 2: Ресурс `status_standards.md` (схемы, шкалы, формулы)

**Files:**
- Create: `.claude/skills/okr-status/resources/status_standards.md`

**Interfaces:**
- Consumes: progress-шкала и IMP из `.claude/skills/okr-planner/resources/okr_standards.md`; drift-формулы из `.claude/skills/release-guard/resources/release_standards.md` §8.
- Produces: единственный источник правды по форматам навыка. Ключевые якоря, на которые ссылаются гейты и команды (названия должны совпадать буквально):
  - Раздел `## 1. Checkpoint и дельта`
  - Раздел `## 2. % готовности KR` (ссылка на progress-шкалу okr-planner)
  - Раздел `## 3. Светофор KR (рубрика)` — статусы 🟢/🟡/🔴
  - Раздел `## 4. Прогноз EOQ` — значения `будет` / `частично` / `не будет`
  - Раздел `## 5. Дрейф KR` — `scope-дрейф`, `сдвиг срока`
  - Раздел `## 6. Таблица ПЛАН / ФАКТ / ИЗМЕНЕНИЕ` — фиксированные колонки
  - Раздел `## 7. Схемы артефактов` — `fact-pack.md`, `assessment.md`, отчёт
  - Раздел `## 8. Источники и якоря`

- [ ] **Step 1: Создать файл со всеми 8 разделами**

Создать `.claude/skills/okr-status/resources/status_standards.md` со следующим содержанием (полностью):

````markdown
# OKR Status — стандарты артефактов, шкалы, формулы

Единый источник правды навыка `okr-status`. Все три команды `/okr-status-*` ссылаются сюда, чтобы не расходиться в формулах и форматах. Переиспользует шкалы `okr-planner` и дрейф `release-guard` — не дублирует их.

---

## 1. Checkpoint и дельта

Команды принимают `<quarter> [checkpoint]`, где `checkpoint ∈ {equator, final}`.

- Если аргумент не задан → вывести из текущей даты относительно границ квартала: первая половина → `equator`, вторая → `final`.
- `equator` — промежуточный срез; базой сравнения служит ПЛАН.
- `final` — итоговый срез; если существует снимок `equator` (`status_report_doc` с `{checkpoint}=equator`), колонка ИЗМЕНЕНИЕ показывает дельту **и к ПЛАНУ, и к прошлому чекпоинту**.

`ожидаемый %` (опорная линия по времени) = `доля прошедшего времени квартала × 100%`. Это опорная величина для светофора, не догма: KR с бэк-загрузкой (релиз в конце) может отставать от линии и оставаться 🟢, если прогноз EOQ = «будет».

---

## 2. % готовности KR

% готовности берётся по **progress-шкале** из `okr-planner/resources/okr_standards.md` (раздел «Образ результата»):

`Собраны требования — 10% / Согласована документация — 30% / Фича разработана — 50% / Пройдено ревью — 70% / Закончены тесты и отладка — 90% / Фича в проде — 100%`

Правила:
- Ступень выбирается по **фактическим** статусам JIRA/релизов, не «на глаз».
- Если у KR нет progress-шкалы в ПЛАНе → % = `delivered_SP / total_SP` по эпику (округление до ступени), с пометкой источника.
- Для `[RESEARCH]`/`[POC]` KR (тег из okr_standards) образ результата = план/решение: 100% = «согласованный план готов».

---

## 3. Светофор KR (рубрика)

Каждому KR присваивается ровно один статус:

| 🚦 | Условие (любое достаточно для понижения) |
|----|------------------------------------------|
| 🟢 On-track | `% готовности ≥ ожидаемый %` (или обоснованная бэк-загрузка) **И** прогноз EOQ = `будет` **И** `scope-дрейф < порог` **И** нет открытого блокера |
| 🟡 At-risk | Отставание от линии, но восстановимо в квартал **ИЛИ** прогноз EOQ = `частично` **ИЛИ** дрейф в пределах буфера **ИЛИ** есть риск без реализовавшегося блокера |
| 🔴 Off-track | Прогноз EOQ = `не будет` **ИЛИ** `scope-дрейф ≥ порог` **ИЛИ** открытый блокер без решения **ИЛИ** срыв зафиксированного коммитмента (IMP=9) |

`порог` дрейфа = `release.drift_threshold` из профиля (дефолт 2 спринта), если релиз-контекст применим; иначе 20% от планового объёма KR.

---

## 4. Прогноз EOQ

Прогноз, «что реально будет готово к концу квартала», принимает одно из трёх значений и **обязан** сопровождаться обоснованием на факте:

| Значение | Когда | Обоснование |
|----------|-------|-------------|
| `будет` | `% + прогнозируемый прирост ≥ 100%` к концу квартала | текущий % + (оставшиеся спринты × средняя velocity KR) − carryover ≥ остаток |
| `частично` | доведём до промежуточной ступени, но не до 100% | назвать ступень, до которой дойдём (напр. «до 70% — ревью»), и что не успеем |
| `не будет` | остаток > прогнозируемого прироста, либо блокер нерешаем в квартал | назвать причину: блокер / нехватка capacity / внешняя зависимость |

Эвристика прироста: средняя velocity KR — из `sprint-fact` последних спринтов квартала (velocity, carryover). Нет данных velocity → `[УТОЧНИТЬ]`, прогноз понижается на одну ступень уверенности.

---

## 5. Дрейф KR

Переиспользует §8 `release-guard/resources/release_standards.md`:

- **scope-дрейф** = `(текущий_объём − плановый_объём) / плановый_объём` (в SP или спринтах). Показывает, насколько раздулся/сжался KR относительно плана.
- **сдвиг срока** = разница между плановым дедлайном KR (из образа результата / коммитмента) и прогнозируемой датой готовности. В днях/спринтах, со знаком.
- Атрибуция дрейфа (кто/что нагнал) — по образцу `/release-status`: demand (изменение требований) vs supply (риск/блокер). Если источник несёт change-request — назвать его.

---

## 6. Таблица ПЛАН / ФАКТ / ИЗМЕНЕНИЕ

Фиксированные колонки (порядок обязателен), одна строка на KR:

```
| KR | IMP | ПЛАН (образ результата · срок) | ФАКТ (% · что в проде) | ИЗМЕНЕНИЕ (🚦 · scope-дрейф · сдвиг срока · прогноз EOQ · доп. риски/ресурсы) | Источник |
```

- **ПЛАН** ← `enriched-okr.md` / `{okr_output_doc}`: образ результата (сжатый) + плановый срок/коммитмент.
- **ФАКТ** ← fact-pack: % по §2 + что реально в проде (релиз/эпик).
- **ИЗМЕНЕНИЕ** ← §3–§5: светофор, scope-дрейф, сдвиг срока, прогноз EOQ, доп. риски/ресурсы (что нужно, чтобы вытащить 🟡/🔴).
- **Источник** — якоря фактов (JIRA-key / release status.md / ФАКТ-спринта / summary / People Graph node).

---

## 7. Схемы артефактов

### `{status_workspace}/fact-pack.md` (стадия 1)

```markdown
# Fact Pack: OKR {quarter} — checkpoint {checkpoint} @ {дата}

## Шапка
Режим: DEEP (okr-status-sync) · Субагенты: 🔵A JIRA / 🟢B Релизы+ФАКТ / 🔴C Переписки+люди · доступность источников.

## ПЛАН-каркас (из okr-planner)
[Таблица OBJ→KR→образ результата→IMP→плановый срок→плановый объём. Источник: {okr_output_doc}/INDEX/KR-EPIC-MAP]

## ФАКТ по источникам
### 🔵 A — JIRA (по каждому KR-эпику)
[Таблица KR | эпик | дочерние done/total | SP done/total | статусы | блокеры | сигналы срыва]
### 🟢 B — Релизы + спринт-ФАКТ
[release status.md + ФАКТ-спринтов: что в проде, velocity, carryover]
### 🔴 C — Переписки + стейкхолдеры
[summaries/каналы + People Graph: сигналы о сроках/рисках/эскалациях, с якорями]
### (best-effort) Confluence + Код
[если доступно; иначе [НЕДОСТУПНО]]

## Разногласия источников
[JIRA «Done» ↔ «в проде» ↔ «в чате жалуются» — конфликты явно, не схлопывать]

## Матрица покрытия
| KR | JIRA | Релизы/ФАКТ | Переписки | Статус |

## Требует уточнения [УТОЧНИТЬ]
[что не установлено — что, у кого, как проверить]
```

### `{status_workspace}/assessment.md` (стадия 2)

```markdown
# Assessment: OKR {quarter} — checkpoint {checkpoint} @ {дата}

## По каждому OBJ → таблица ПЛАН/ФАКТ/ИЗМЕНЕНИЕ (формат §6)

## Сводка светофора
[счётчик 🟢/🟡/🔴 по KR и по OBJ]

## Прогноз EOQ (агрегат)
[что будет / частично / не будет — списком по KR]
```

### `{status_report_doc}` (стадия 3, для руководства)

```markdown
# Статус OKR {quarter} — {checkpoint} @ {дата}

## Executive summary
[Светофор по каждому OBJ + одна строка «что реально будет к концу квартала». 5–7 строк, для CPO/CTO.]

## OBJ {n}: {название}   🚦
[Таблица ПЛАН/ФАКТ/ИЗМЕНЕНИЕ по KR этого OBJ — формат §6]
... (секция на каждый OBJ)

## Сроки
[Актуальность сроков: какие KR сдвигаются, на сколько, почему]

## Изменение объёма
[Агрегированный scope-дрейф по кварталу + атрибуция demand/supply]

## Прогноз на конец квартала
[Что будет готово / частично / не будет — с обоснованием]

## Доп. риски и запросы ресурсов
[Для каждого 🟡/🔴: что нужно, чтобы вытащить — люди/сроки/решения/эскалации]
```

---

## 8. Источники и якоря

Допустимые якоря ФАКТА (каждый факт обязан нести один):

| Источник | Якорь |
|----------|-------|
| JIRA | `tracker_key` (напр. `PROJ-101`) |
| Релиз | `{release_workspace}/<id>/status.md` |
| Спринт | `ФАКТ-{sprint}.md` |
| Переписка/встреча | файл `{summary_notes}/{дата}-{slug}.md` |
| Люди | узел People Graph (нексус `team`) |

Нет якоря → `[УТОЧНИТЬ у {кого}]`. Источник недоступен → `[НЕДОСТУПНО: <источник>]`.
````

- [ ] **Step 2: Проверить наличие всех обязательных якорных разделов и колонок**

Run: `grep -c "^## 1. Checkpoint\|^## 2. % готовности\|^## 3. Светофор\|^## 4. Прогноз EOQ\|^## 5. Дрейф\|^## 6. Таблица ПЛАН\|^## 7. Схемы\|^## 8. Источники" .claude/skills/okr-status/resources/status_standards.md`
Expected: `8`

- [ ] **Step 3: Проверить фиксированные колонки таблицы и значения прогноза**

Run: `grep -c "ПЛАН (образ результата · срок)\|ФАКТ (% · что в проде)\|прогноз EOQ" .claude/skills/okr-status/resources/status_standards.md`
Expected: `≥ 1`
Run: `grep -c "\`будет\`\|\`частично\`\|\`не будет\`" .claude/skills/okr-status/resources/status_standards.md`
Expected: `≥ 1`

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/okr-status/resources/status_standards.md
git commit -m "feat(okr-status): ресурс status_standards — шкалы, светофор, прогноз EOQ, дрейф, схемы"
```

---

### Task 3: Ресурс `hard_gates.md` (бинарные гейты)

**Files:**
- Create: `.claude/skills/okr-status/resources/hard_gates.md`

**Interfaces:**
- Consumes: рубрики из `status_standards.md` (§3 светофор, §4 прогноз, §8 источники).
- Produces: 9 гейтов (G1–G9), критичные 1–6 блокируют финализацию отчёта; Светофор-таблица. На неё ссылается `/okr-status-report` (предусловие финализации) и `/okr-status-assess`.

- [ ] **Step 1: Создать файл гейтов**

Создать `.claude/skills/okr-status/resources/hard_gates.md` (полностью):

```markdown
# Hard Gates — валидация статус-отчёта OKR (9 бинарных гейтов)

Проверяются на `/okr-status-assess` (черновик оценки) и на `/okr-status-report` перед финализацией. Каждый гейт бинарный: ✅ / 🔴. Один 🔴 в критичных (1–6) → отчёт не финализируется.

## Светофор

| Статус | Условие | Действие |
|--------|---------|----------|
| 🟢 Зелёный | Все 9 гейтов ✅ | Финализировать отчёт → публикация в {status_report_doc} |
| 🟡 Жёлтый | Нарушены гейты 7–9 (некритичные) | Финализировать с явными `[УТОЧНИТЬ]`, PO принимает риск |
| 🔴 Красный | Нарушен хотя бы один гейт 1–6 | Вернуться на /okr-status-assess (или /okr-status-sync), дозаполнить |

---

## Критичные гейты (1–6) — блокирующие

### Гейт 1: Нет факта без источника
**Правило:** каждый ФАКТ (% готовности, статус, «в проде», дрейф) несёт якорь (§8 status_standards: tracker_key / status.md / ФАКТ-спринта / summary / People Graph).
**Нарушение:** «сделано 60%» без того, откуда взято.

### Гейт 2: % готовности по шкале, не «на глаз»
**Правило:** % каждого KR выбран по progress-шкале (§2) на основании фактических статусов, либо `delivered_SP/total_SP` с пометкой.
**Нарушение:** процент назван без привязки к ступени/SP.

### Гейт 3: Прогноз EOQ обоснован
**Правило:** каждому KR присвоен прогноз `будет`/`частично`/`не будет` (§4) с обоснованием на факте (velocity/carryover/блокер).
**Нарушение:** прогноз без расчёта или без причины.

### Гейт 4: Светофор проставлен каждому KR
**Правило:** у каждого KR ровно один 🚦 по рубрике §3.
**Нарушение:** KR без статуса или со статусом вне рубрики.

### Гейт 5: Конфликты источников не схлопнуты
**Правило:** при расхождении JIRA/прод/чат есть раздел «Разногласия источников» с обеими версиями.
**Нарушение:** конфликт сведён к одной версии молча.

### Гейт 6: Нет [УТОЧНИТЬ] в оценке Critical KR
**Правило:** для KR с IMP ≥ 8 поля ФАКТ, светофор и прогноз EOQ заполнены полностью.
**Нарушение:** коммитмент-KR оценён «примерно».

---

## Некритичные гейты (7–9) — 🟡 допустимы

### Гейт 7: Дельта к прошлому чекпоинту показана
**Правило:** при `checkpoint = final` и наличии снимка `equator` колонка ИЗМЕНЕНИЕ несёт дельту и к ПЛАНУ, и к прошлому срезу.
**Нарушение:** сравнение только с ПЛАНом, хотя equator-снимок есть.

### Гейт 8: Доп. риски/ресурсы названы для 🟡/🔴
**Правило:** каждый не-зелёный KR несёт явный запрос: что нужно, чтобы вытащить (люди/срок/решение/эскалация).
**Нарушение:** 🔴 без «что требуется».

### Гейт 9: Недоступность честно помечена
**Правило:** источник, до которого не дотянулись, помечен `[НЕДОСТУПНО: <источник>]`, факты за него не выдуманы.
**Нарушение:** пробел закрыт догадкой вместо пометки.
```

- [ ] **Step 2: Проверить число гейтов и наличие Светофора**

Run: `grep -c "^### Гейт" .claude/skills/okr-status/resources/hard_gates.md`
Expected: `9`
Run: `grep -c "🟢 Зелёный\|🟡 Жёлтый\|🔴 Красный" .claude/skills/okr-status/resources/hard_gates.md`
Expected: `3`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/okr-status/resources/hard_gates.md
git commit -m "feat(okr-status): ресурс hard_gates — 9 бинарных гейтов статуса + Светофор"
```

---

### Task 4: `SKILL.md` навыка okr-status

**Files:**
- Create: `.claude/skills/okr-status/SKILL.md`

**Interfaces:**
- Consumes: `status_standards.md`, `hard_gates.md` (ссылки в разделе «Стандарты и ресурсы»), `examples/ideal_status_report.md` (форвард-ссылка на имя файла — создаётся в Task 5).
- Produces: обзор навыка. Frontmatter `name: okr-status` + `description`. Разделы: Роль, Доменный профиль, Принцип нулевого допуска, Pipeline (3 стадии), Роли и артефакты (таблица), Принципы, Стандарты и ресурсы, Главное правило процесса.

- [ ] **Step 1: Создать SKILL.md**

Создать `.claude/skills/okr-status/SKILL.md` по образцу `.claude/skills/okr-planner/SKILL.md`, содержание:

- **Frontmatter:**
```markdown
---
name: okr-status
description: Навык okr-status — подведение промежуточного/итогового статуса квартальных OKR для руководства. По каждому KR — фактурка ПЛАН/ФАКТ/ИЗМЕНЕНИЕ + светофор + прогноз EOQ + дрейф. Используй когда: статус квартала, отчёт руководству по OKR, экватор/конец квартала, что сделано и что успеем, /okr-status-sync /okr-status-assess /okr-status-report.
---
```
- **# Навык: OKR Status — статус исполнения квартальных OKR**
- **## Роль** — «Ты — Quarterly Status Reporter. Навык подводит честный промежуточный/итоговый статус квартальных OKR для руководства…». Указать: вход — утверждённый ПЛАН (артефакты `okr-planner`), выход — один `.md`-отчёт (executive-сводка + секция на OBJ). Multi-step pipeline из 3 команд, каждая = отдельный запуск + STOP.
- **## Доменный профиль** — пути `{status_workspace}`, `{status_report_doc}`, `{planning_root}`, `{index_doc}`, `{kr_epic_map_doc}`, `{okr_output_doc}`, `{execution_root}`, `{release_workspace}`, `{summary_notes}`, `{tracker.*}` резолвятся из `.claude/domain-profile.md`. Пустое поле → дефолт + `[УТОЧНИТЬ]`.
- **## Принцип нулевого допуска к галлюцинациям** — дословно из Global Constraints (каждый ФАКТ ← якорь; прогноз ← факт).
- **## Pipeline (3 стадии)** — ASCII-диаграмма:
```
/okr-status-sync <quarter> [checkpoint]   → fact-pack.md (+ raw/agent-*.md)   [СТОП: PO ревьюит факт]
        ↓
/okr-status-assess <quarter>              → assessment.md (по-KR ПЛАН/ФАКТ/ИЗМЕНЕНИЕ) [СТОП: PO ревьюит оценку]
        ↓
/okr-status-report <quarter>              → {status_report_doc} (отчёт для руководства)  [финал]
```
- **### Роли и артефакты** — таблица:
```
| Стадия | Команда | Роль | Артефакт |
|---|---|---|---|
| 1 Факт | /okr-status-sync | Fact Investigator | {status_workspace}/fact-pack.md + raw/agent-*.md |
| 2 Оценка | /okr-status-assess | Progress Assessor | {status_workspace}/assessment.md |
| 3 Отчёт | /okr-status-report | Reporter + Finalizer | {status_report_doc} |
```
- **## Принципы** — 3 источника ФАКТА (JIRA · релизы+спринт-ФАКТ · переписки+люди) обязательны, Confluence+Код best-effort; параллельность субагентов; кросс-валидация; светофор+прогноз+дрейф по `status_standards.md`; переиспользование шкал okr-planner и дрейфа release-guard.
- **## Стандарты и ресурсы:**
```markdown
- `resources/status_standards.md` — checkpoint-модель, % готовности, светофор KR, прогноз EOQ, дрейф, формат таблицы ПЛАН/ФАКТ/ИЗМЕНЕНИЕ, схемы артефактов.
- `resources/hard_gates.md` — 9 бинарных гейтов статуса + Светофор.
- `examples/ideal_status_report.md` — эталонный статус-отчёт (аннотированный).
```
- **## Главное правило процесса** — STOP после каждой стадии; опрос PO по одному вопросу на финализации.

- [ ] **Step 2: Проверить frontmatter и обязательные разделы**

Run: `grep -c "^name: okr-status\|^description:" .claude/skills/okr-status/SKILL.md`
Expected: `2`
Run: `grep -c "^## Роль\|^## Pipeline\|^## Стандарты и ресурсы\|^## Главное правило" .claude/skills/okr-status/SKILL.md`
Expected: `4`
Run: `grep -c "okr-status-sync\|okr-status-assess\|okr-status-report" .claude/skills/okr-status/SKILL.md`
Expected: `≥ 3`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/okr-status/SKILL.md
git commit -m "feat(okr-status): SKILL.md — роль, pipeline из 3 стадий, принципы"
```

---

### Task 5: Эталон `examples/ideal_status_report.md`

**Files:**
- Create: `.claude/skills/okr-status/examples/ideal_status_report.md`

**Interfaces:**
- Consumes: формат отчёта из `status_standards.md` §6–§7.
- Produces: аннотированный эталонный отчёт, на который ссылается `/okr-status-report` при сборке.

- [ ] **Step 1: Создать эталон**

Создать `.claude/skills/okr-status/examples/ideal_status_report.md` — реалистичный пример на 2 OBJ / 4 KR, строго по схеме `{status_report_doc}` (§7). Требования к содержанию:
- Шапка: `# Статус OKR 2026-Q3 — equator @ 2026-08-15`.
- `## Executive summary` — светофор по OBJ (🟢/🟡) + строка «что реально к концу квартала».
- Две секции `## OBJ 1: …  🟢` и `## OBJ 2: …  🟡`, в каждой — таблица §6 с колонками `KR | IMP | ПЛАН (образ результата · срок) | ФАКТ (% · что в проде) | ИЗМЕНЕНИЕ (🚦 · scope-дрейф · сдвиг срока · прогноз EOQ · доп. риски) | Источник`.
- Заполнить минимум по одному KR каждого статуса: 🟢 (прогноз `будет`), 🟡 (прогноз `частично`), 🔴 (прогноз `не будет` с блокером).
- В колонке Источник — реалистичные якоря: `PROJ-142`, `REL-PAY-Q3/status.md`, `ФАКТ-S6.md`, `2026-08-10-sync-платежи.md`.
- Разделы `## Сроки`, `## Изменение объёма`, `## Прогноз на конец квартала`, `## Доп. риски и запросы ресурсов`.
- Аннотации-комментарии `<!-- почему так -->` у ключевых мест (по образцу `okr-planner/examples/ideal_okr.md`), объясняющие: как выбран % по шкале, почему такой светофор, чем обоснован прогноз EOQ.
- Стиль — по `writing_style.md`: без декоративных эмодзи, семантические только как маркеры.

- [ ] **Step 2: Проверить структуру эталона**

Run: `grep -c "^## Executive summary\|^## OBJ 1\|^## OBJ 2\|^## Сроки\|^## Изменение объёма\|^## Прогноз на конец квартала\|^## Доп. риски" .claude/skills/okr-status/examples/ideal_status_report.md`
Expected: `7`
Run: `grep -c "🟢\|🟡\|🔴" .claude/skills/okr-status/examples/ideal_status_report.md`
Expected: `≥ 3` (все три статуса присутствуют)
Run: `grep -c "будет\|частично\|не будет" .claude/skills/okr-status/examples/ideal_status_report.md`
Expected: `≥ 3`

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/okr-status/examples/ideal_status_report.md
git commit -m "feat(okr-status): эталонный статус-отчёт (2 OBJ / 4 KR, аннотированный)"
```

---

### Task 6: Команда `/okr-status-sync` (стадия 1 — Fact Investigator)

**Files:**
- Create: `.claude/commands/okr-status-sync.md`

**Interfaces:**
- Consumes: `SKILL.md`, `status_standards.md` (§7 схема fact-pack, §8 источники), ПЛАН-артефакты okr-planner (`{okr_output_doc}`, `{index_doc}`, `{kr_epic_map_doc}`, `enriched-okr.md`), `{release_workspace}/*/status.md`, `ФАКТ-{sprint}.md`, `{summary_notes}`, People Graph.
- Produces: `{status_workspace}/fact-pack.md` + `{status_workspace}/raw/agent-a-jira.md`, `agent-b-releases.md`, `agent-c-people.md`. STOP.

- [ ] **Step 1: Создать команду по образцу `/bft-context-gen-deep`**

Создать `.claude/commands/okr-status-sync.md`. Структура (mirror `bft-context-gen-deep.md`):

- **Frontmatter:** `description: 'OKR Status стадия 1 — глубокий сбор ФАКТА по источникам параллельными субагентами: JIRA · релизы+спринт-ФАКТ · переписки+люди (роль: Fact Investigator)'`
- **## Использование:** ```/okr-status-sync <quarter> [checkpoint]``` + примеры `/okr-status-sync 2026-Q3 equator`, `/okr-status-sync 2026-Q3 final`. Вход: ПЛАН okr-planner. Выход: `{status_workspace}/fact-pack.md` + `raw/`.
- **## Важно:** роль Fact Investigator; аналог `/bft-context-gen-deep`, но для статуса квартала. Это СТАДИЯ 1 — без неё `/okr-status-assess` запрещён.
- **## Инструкция для LLM:**
  - **Этап 0: Подготовка.** Создать `{status_workspace}/` и `{status_workspace}/raw/`. Определить `checkpoint` (аргумент или из даты, §1 status_standards). Прочитать `SKILL.md` + `status_standards.md`.
  - **Этап 1: Загрузка ПЛАНа.** Прочитать `{okr_output_doc}`, `{index_doc}`, `{kr_epic_map_doc}`, `{okr_workspace}/enriched-okr.md` (образ результата, progress-шкала, IMP, сроки). Прочитать прошлый снимок `status_report_doc` с `{checkpoint}=equator` (если `checkpoint=final` и файл есть) — база для дельты.
  - **Этап 2: Resolve capability.** Прочитать `tracker` из `.claude/domain-profile.md` (`mcp`/`access`/`projects`). Если `role_bindings`/`source_policy` заданы в профиле — учесть (опционально). JIRA недоступна (нет `tracker.mcp` / VPN) → субагента A не спавнить, его раздел → `[НЕДОСТУПНО: JIRA]`. **Не блокировать** весь прогон из-за одного источника (graceful degradation), но пометить в шапке fact-pack.
  - **Этап 3: Запуск 3 параллельных субагентов** (одновременно, в одном сообщении). Для каждого — задача + артефакт в `raw/`:
    - 🔵 **A — JIRA Deep.** По `{kr_epic_map_doc}`: для каждого KR-эпика — `jira_get_issue`, дочерние (`parent`/Epic Link), статусы, SP done/total, блокеры, linked issues, сигналы срыва срока (due dates). → `raw/agent-a-jira.md` (таблица KR | эпик | done/total | SP | блокеры | сигналы).
    - 🟢 **B — Релизы + спринт-ФАКТ.** Прочитать `{release_workspace}/*/status.md` (baseline-полнота, дрейф) и `ФАКТ-{sprint}.md` за спринты квартала (`{execution_root}`): velocity, carryover, что реально в проде. → `raw/agent-b-releases.md`.
    - 🔴 **C — Переписки + стейкхолдеры.** Прочитать `{summary_notes}` (summaries встреч) + `info-channels` (нексус `channels`) + People Graph (нексус `team`): сигналы о сроках/рисках/эскалациях по темам KR, каждый ← якорь. → `raw/agent-c-people.md`.
    - *(best-effort)* Confluence (`confluence_search`) + Код (`repowise`) — обогащение внутри общего прогона; недоступно → `[НЕДОСТУПНО]`, не жёсткий источник.
  - **Этап 4: Кросс-валидация.** Таблица проверок: «JIRA Done (A)» ↔ «в проде (B)» ↔ «в чате жалуются (C)». Конфликты → раздел «Разногласия источников», не схлопывать.
  - **Этап 5: Сборка `fact-pack.md`** по схеме §7 status_standards (шапка с режимом/субагентами/доступностью, ПЛАН-каркас, ФАКТ по источникам, разногласия, матрица покрытия, [УТОЧНИТЬ]).
  - **Этап 6: Сохранение + STOP.** `obsidian.vault_write` → `{status_workspace}/fact-pack.md` и raw-файлы. Вывести саммари (сколько KR покрыто по каждому источнику, конфликты, [УТОЧНИТЬ]) и `── СТОП ── PO: проверьте факт. Дальше → /okr-status-assess {quarter}`.
- **## Жёсткие правила:** параллельность обязательна; raw сохраняются; конфликты не схлопываются; нулевой допуск к галлюцинациям (§8 якоря); честно про недоступность; стиль по writing_style.md.

- [ ] **Step 2: Проверить frontmatter, параллельность, три субагента, STOP**

Run: `grep -c "^description:" .claude/commands/okr-status-sync.md`
Expected: `1`
Run: `grep -c "🔵\|🟢 \*\*B\|🔴 \*\*C\|параллельн\|одновременно" .claude/commands/okr-status-sync.md`
Expected: `≥ 3`
Run: `grep -c "fact-pack.md\|СТОП\|/okr-status-assess" .claude/commands/okr-status-sync.md`
Expected: `≥ 3`

- [ ] **Step 3: Проверить, что нет висячих путь-переменных вне профиля**

Run: `grep -oE "\{[a-z_]+[a-z_.]*\}" .claude/commands/okr-status-sync.md | sort -u`
Expected: только известные переменные (`{status_workspace}`, `{okr_output_doc}`, `{index_doc}`, `{kr_epic_map_doc}`, `{okr_workspace}`, `{release_workspace}`, `{execution_root}`, `{summary_notes}`, `{status_report_doc}`, `{quarter}`, `{checkpoint}`, `{sprint}`, `{tracker.mcp}`) — незнакомых нет.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/okr-status-sync.md
git commit -m "feat(okr-status): команда /okr-status-sync — сбор ФАКТА 3 параллельными субагентами"
```

---

### Task 7: Команда `/okr-status-assess` (стадия 2 — Progress Assessor)

**Files:**
- Create: `.claude/commands/okr-status-assess.md`

**Interfaces:**
- Consumes: `status_standards.md` (§2–§6), `hard_gates.md`, `{status_workspace}/fact-pack.md`, ПЛАН (`enriched-okr.md`).
- Produces: `{status_workspace}/assessment.md` (по-KR ПЛАН/ФАКТ/ИЗМЕНЕНИЕ, формат §6). STOP.

- [ ] **Step 1: Создать команду**

Создать `.claude/commands/okr-status-assess.md`. Структура (mirror `/okr-validate` + `/release-status`):

- **Frontmatter:** `description: 'OKR Status стадия 2 — по каждому KR ПЛАН/ФАКТ/ИЗМЕНЕНИЕ: светофор + прогноз EOQ + дрейф (роль: Progress Assessor)'`
- **## Использование:** ```/okr-status-assess <quarter>```. Вход: `fact-pack.md`. Выход: `{status_workspace}/assessment.md`.
- **## Важно:** роль Progress Assessor. Предусловие: `fact-pack.md` существует (иначе СТОП → «сначала /okr-status-sync»).
- **## Инструкция для LLM:**
  - **Этап 1: Загрузка.** Прочитать `status_standards.md`, `hard_gates.md`, `fact-pack.md`, ПЛАН (`enriched-okr.md`/`{okr_output_doc}`).
  - **Этап 2: Расчёт по каждому KR** (§2–§5):
    - **ПЛАН** ← enriched: образ результата, IMP, срок, плановый объём.
    - **ФАКТ** ← fact-pack: % по progress-шкале (§2, на статусах JIRA/релизов), SP done/total, что в проде — каждый с якорем (§8).
    - **ИЗМЕНЕНИЕ:** светофор (§3), scope-дрейф + сдвиг срока (§5), прогноз EOQ `будет/частично/не будет` (§4, обоснование velocity/carryover/блокер из fact-pack), доп. риски/ресурсы.
  - **Этап 3: Сборка `assessment.md`** по §7: секция на OBJ с таблицей §6 + сводка светофора + агрегат прогноза EOQ.
  - **Этап 4: Само-проверка гейтов.** Прогнать G1–G6 (критичные) из `hard_gates.md`. Нарушен критичный → пометить в assessment, что нужно дозаполнить (обычно возврат на `/okr-status-sync` за источником).
  - **Этап 5: Сохранение + STOP.** `obsidian.vault_write` → `{status_workspace}/assessment.md`. Вывести сводку светофора (счётчик 🟢/🟡/🔴) + статус гейтов + `── СТОП ── PO: проверьте оценку и прогноз. Дальше → /okr-status-report {quarter}`.
- **## Запреты:** не выдумывать % и прогресс (гейт 1–2); прогноз EOQ без обоснования запрещён (гейт 3); нет источника → `[УТОЧНИТЬ]`, не «на глаз»; конфликты из fact-pack не схлопывать.

- [ ] **Step 2: Проверить структуру и ссылки на гейты/стандарты**

Run: `grep -c "^description:" .claude/commands/okr-status-assess.md`
Expected: `1`
Run: `grep -c "hard_gates\|status_standards\|assessment.md\|прогноз EOQ\|светофор" .claude/commands/okr-status-assess.md`
Expected: `≥ 4`
Run: `grep -c "fact-pack.md\|СТОП\|/okr-status-report" .claude/commands/okr-status-assess.md`
Expected: `≥ 3`

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/okr-status-assess.md
git commit -m "feat(okr-status): команда /okr-status-assess — светофор + прогноз EOQ + дрейф по KR"
```

---

### Task 8: Команда `/okr-status-report` (стадия 3 — Reporter + Finalizer)

**Files:**
- Create: `.claude/commands/okr-status-report.md`

**Interfaces:**
- Consumes: `status_standards.md` (§6–§7), `hard_gates.md` (Светофор — предусловие финализации), `examples/ideal_status_report.md`, `{status_workspace}/assessment.md`.
- Produces: `{status_report_doc}` (финальный отчёт для руководства).

- [ ] **Step 1: Создать команду**

Создать `.claude/commands/okr-status-report.md`. Структура (mirror `/okr-deliver` — сухой прогон → ок PO → запись):

- **Frontmatter:** `description: 'OKR Status стадия 3 — финализация статус-отчёта с PO и публикация сводки для руководства (роль: Reporter + Finalizer)'`
- **## Использование:** ```/okr-status-report <quarter> [checkpoint]```. Вход: `assessment.md`. Выход: `{status_report_doc}`.
- **## Важно:** роль Reporter + Finalizer. Human-in-the-loop: PO правит фактуру/прогноз/риски по одному вопросу. JIRA/Confluence — только чтение.
- **## Инструкция для LLM:**
  - **Предусловие:** прочитать `assessment.md` и прогнать Светофор `hard_gates.md`. Критичный гейт 🔴 → СТОП: «Гейт N нарушен, вернуться на /okr-status-assess».
  - **Этап 1: Загрузка.** `assessment.md`, `status_standards.md` (§6–§7 формат), `examples/ideal_status_report.md` (эталон).
  - **Этап 2: Интерактивная финализация с PO** (по одному вопросу за раз): подтвердить/скорректировать светофор спорных KR, уточнить прогноз EOQ и доп. риски, добавить контекст, которого нет в источниках. PO может ответить «достаточно».
  - **Этап 3: Сборка отчёта** по схеме `{status_report_doc}` (§7): executive summary (светофор по OBJ + «что реально к концу квартала») → секция на каждый OBJ с таблицей §6 → Сроки → Изменение объёма (агрегат дрейфа + атрибуция) → Прогноз на конец квартала → Доп. риски и запросы ресурсов. При `checkpoint=final` с equator-снимком — дельта к прошлому срезу (гейт 7).
  - **Этап 4: Сухой прогон → СТОП для PO.** Вывести план публикации (`📄 СОЗДАТЬ: {status_report_doc}` + превью executive summary; `⚠️ Не изменяется: JIRA, Confluence`) + `── СТОП ── PO: подтвердите публикацию («да, публикуй»/«ок») или скорректируйте`.
  - **Этап 5: Запись (только после «ок» PO).** `obsidian.vault_write` → `{status_report_doc}` (папка `.../Статус/`, имя с `{checkpoint}`). Опционально по отдельному запросу — выгрузка в Confluence (best-effort).
  - **Этап 6: Финал.** Вывести: путь к отчёту, сводку светофора, ключевые 🔴/риски для эскалации.
- **## Запреты:** не записывать до «ок PO» (только сухой прогон); не финализировать при критичном 🔴 гейте; не выдумывать контекст сверх источников и правок PO; не публиковать в Confluence без отдельного запроса.

- [ ] **Step 2: Проверить структуру, предусловие-гейт, сухой прогон**

Run: `grep -c "^description:" .claude/commands/okr-status-report.md`
Expected: `1`
Run: `grep -c "assessment.md\|hard_gates\|ideal_status_report\|сухой прогон\|status_report_doc" .claude/commands/okr-status-report.md`
Expected: `≥ 4`
Run: `grep -c "СТОП\|только чтение\|да, публикуй\|ок PO" .claude/commands/okr-status-report.md`
Expected: `≥ 3`

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/okr-status-report.md
git commit -m "feat(okr-status): команда /okr-status-report — финализация с PO и публикация отчёта"
```

---

### Task 9: Регистрация навыка + сквозная проверка целостности

**Files:**
- Modify: `README.md` (раздел `## 🧰 Что внутри`, таблица навыков — после строки про OKR ~line 175, и/или таблица в шапке)
- Modify: `sa_documentation/nexus_process_map.md` (вводный абзац перечня процессов + примечание к §2)

**Interfaces:**
- Consumes: все файлы навыка (Tasks 1–8).
- Produces: обнаружимость навыка (README) + грунтовка Нексусами (`strategy`/`capacity`/`precedents`) в матрице процессов. Финальная проверка целостности всех перекрёстных ссылок.

- [ ] **Step 1: README — добавить окр-status в перечень навыков**

В `README.md`, в разделе `## 🎯 OKR` (около строки 175, после описания okr-planner) добавить абзац:

```markdown
### 📈 OKR Status — статус исполнения квартала

Когда идёт экватор или конец квартала: `/okr-status-sync` (глубокий сбор ФАКТА по JIRA · релизам+спринт-ФАКТ · перепискам+людям параллельными субагентами) → `/okr-status-assess` (по каждому KR ПЛАН/ФАКТ/ИЗМЕНЕНИЕ: светофор + прогноз EOQ + дрейф) → `/okr-status-report` (финализация с PO → один `.md` для руководства). Детально — [okr-status/SKILL.md](.claude/skills/okr-status/SKILL.md).
```

- [ ] **Step 2: nexus_process_map — зарегистрировать процесс**

В `sa_documentation/nexus_process_map.md`:
- В вводном абзаце (перечень «движков процессов») добавить `okr-status` в список: `… 'okr-planner', 'okr-status', 'sprint-planner', …`.
- После таблицы §2 добавить примечание:

```markdown
> **`okr-status`** (context-stage `/okr-status-sync`) грунтуется теми же Нексусами, что и `/okr-context-gen`: `strategy` (● связь с приоритетами квартала), `capacity` (● velocity для прогноза EOQ), `precedents` (○ незакрытые долги). Источники ФАКТА (JIRA/релизы/переписки) — не Нексусы, а живые коннекторы, резолвятся из `tracker` и `.mcp.json`.
```

- [ ] **Step 3: Проверить регистрацию**

Run: `grep -c "okr-status" README.md`
Expected: `≥ 2`
Run: `grep -c "okr-status" sa_documentation/nexus_process_map.md`
Expected: `≥ 2`

- [ ] **Step 4: Сквозная проверка целостности навыка**

Run (все файлы навыка на месте):
```bash
ls .claude/skills/okr-status/SKILL.md .claude/skills/okr-status/resources/status_standards.md .claude/skills/okr-status/resources/hard_gates.md .claude/skills/okr-status/examples/ideal_status_report.md .claude/commands/okr-status-sync.md .claude/commands/okr-status-assess.md .claude/commands/okr-status-report.md
```
Expected: все 7 путей существуют, без «No such file».

Run (каждая команда имеет frontmatter-описание):
```bash
for f in okr-status-sync okr-status-assess okr-status-report; do head -3 ".claude/commands/$f.md" | grep -q "^description:" && echo "$f OK" || echo "$f MISSING description"; done
```
Expected: три строки `... OK`.

Run (нет ссылок на несуществующий класс/фичу профиля):
```bash
grep -rn "source_policy\|role_bindings\|status-critical" .claude/commands/okr-status-*.md .claude/skills/okr-status/
```
Expected: упоминания `role_bindings`/`source_policy` только с оговоркой «если заданы»; **нет** упоминаний `status-critical` как обязательного (соответствует Deviation #1).

Run (каждый путь-плейсхолдер в командах определён в профиле или является рантайм-подстановкой):
```bash
grep -rhoE "\{[a-z_]+[a-z_.]*\}" .claude/commands/okr-status-*.md | sort -u
```
Expected: каждый элемент — либо ключ из `domain-profile.template.md` (`grep <key> domain-profile.template.md`), либо рантайм-подстановка `{quarter}`/`{checkpoint}`/`{sprint}`.

- [ ] **Step 5: Commit**

```bash
git add README.md sa_documentation/nexus_process_map.md
git commit -m "feat(okr-status): регистрация навыка в README и матрице процессов"
```

---

## Self-Review

**1. Spec coverage** (сверка со спекой `2026-07-07-okr-status-design.md`):

| Требование спеки | Задача |
|---|---|
| Новый навык okr-status (SKILL+resources+examples) | Tasks 2–5 |
| 3 стадии sync→assess→report, STOP | Tasks 6–8 |
| Обязательные источники JIRA · релизы+спринт-ФАКТ · переписки+люди | Task 6 (субагенты A/B/C) |
| Confluence+Код best-effort | Task 6 (best-effort шаг) |
| Один документ, секция на OBJ | Tasks 2 (§7 схема), 5, 8 |
| Светофор + % + прогноз EOQ + дрейф | Task 2 (§3–§5), Task 7 |
| Параметр checkpoint + дельта | Task 1 (path), Task 2 (§1), Task 6/8 |
| Публикация в project-management/<quarter>/Статус/ | Task 1 (`status_report_doc`), Task 8 |
| Нулевой допуск / конфликты не схлопывать / честная недоступность | Global Constraints + Task 3 (гейты) + Task 6 |
| Переиспользование шкал okr-planner и дрейфа release-guard | Task 2 (ссылки §2/§5) |
| Правки domain-profile / README / nexus_process_map | Tasks 1, 9 |

Пробелов не найдено.

**2. Placeholder scan:** плейсхолдеров-провалов («TBD», «add error handling», «similar to Task N») в задачах нет — контент задан либо дословно (frontmatter, YAML путей, гейты, таблицы, grep-проверки), либо детальной спецификацией секций для прозаических артефактов (SKILL, команды, эталон), что уместно для домена markdown-навыков.

**3. Type consistency:** имена якорных разделов и файлов согласованы между задачами — `status_standards.md` §1–§8, `fact-pack.md`, `assessment.md`, `{status_report_doc}`, гейты G1–G9, значения прогноза `будет/частично/не будет`, колонки таблицы §6 — используются одинаково в Tasks 2/3/5/6/7/8. Deviation #1 (нет `source_policy`) отражён и в Task 6, и в проверке Task 9.
