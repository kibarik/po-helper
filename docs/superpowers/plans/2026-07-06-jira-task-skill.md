# jira-task Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить навык `jira-task` для po-helper: свободный текст задачи → шаблон описания → короткое интервью по пробелам → relevance-research по JIRA/Confluence → превью → создание Issue в JIRA.

**Architecture:** Навык — это набор markdown-инструкций (prompt-artifact), а не исполняемый код. Основной файл `SKILL.md` описывает роль и 6-шаговый пайплайн; два reference-файла в `resources/` выносят детали шаблона и поиска; `examples/` содержит эталонный прогон. Реальные значения (проект, MCP, base_url) резолвятся из `.claude/domain-profile.md`.

**Tech Stack:** Markdown; MCP-инструменты `jira_*` / `confluence_*` (сервер задаётся `tracker.mcp` / `wiki.mcp` в профиле); стиль и конвенции — как у существующих навыков (`okr-planner`, `bft-writer`).

## Global Constraints

- Язык всех артефактов — русский (как остальные навыки).
- **Нулевой допуск к галлюцинациям:** каждое поле ← текст/ответ PO или `[УТОЧНИТЬ у {кого}]`; relevance-ссылки — только реально найденные с якорем.
- **Read-only до явного «ок» PO:** JIRA/Confluence не пишем до подтверждения превью.
- Реальные значения — из `.claude/domain-profile.md`; пустое поле профиля → дефолт + `[УТОЧНИТЬ]`. Примеры кодов (`PROJ-123`) иллюстративны.
- MCP недоступен → честно `[УТОЧНИТЬ: MCP <tracker.mcp> недоступен]` + payload для ручного создания; успех не эмулировать.
- Нет тестового харнесса для markdown-навыков: «верификация» = self-check по чеклисту приёмки + проверка, что frontmatter валиден и нет плейсхолдеров (`TBD`/`TODO`).

**Спека:** `docs/superpowers/specs/2026-07-06-jira-task-skill-design.md`

## File Structure

- Create: `.claude/skills/jira-task/SKILL.md` — роль, вход/выход, 6-шаговый пайплайн, 2 такта, обработка недоступности MCP; ссылается на resources.
- Create: `.claude/skills/jira-task/resources/template.md` — эталон шаблона описания, правила классификации Task/Bug, маппинг полей → `jira_create_issue`.
- Create: `.claude/skills/jira-task/resources/relevance-search.md` — построение запросов JQL/Confluence, ранжирование, формат «почему релевантно», порог тишины.
- Create: `.claude/skills/jira-task/examples/email-to-task.md` — эталонный прогон: письмо → интервью → relevance → превью → Issue.
- Modify: `README.md` — строка в таблице «Пайплайны и команды».

Порядок: сначала reference-файлы (`template.md`, `relevance-search.md`) — на них ссылается `SKILL.md`; затем `SKILL.md`; затем `examples/`; в конце `README.md`.

---

### Task 1: resources/template.md

**Files:**
- Create: `.claude/skills/jira-task/resources/template.md`

**Interfaces:**
- Produces: канонический блок шаблона описания (Образ результата / ASIS / ПРОБЛЕМА / TOBE / Описание / Связанные материалы); список критичных полей `[Образ результата, ПРОБЛЕМА, TOBE]`; правила классификации Task/Bug; маппинг `field → jira_create_issue(project_key, summary, issue_type, description, labels)`. На это ссылаются `SKILL.md` (Task 3) и example (Task 4).

- [ ] **Step 1: Определить критерии приёмки файла**

Файл ДОЛЖЕН содержать:
1. Точный блок шаблона тела Issue (verbatim, включая опциональный блок «Связанные материалы»).
2. Явный список критичных полей: `Образ результата`, `ПРОБЛЕМА`, `TOBE`; и некритичных: `ASIS`, `Описание`.
3. Правило Summary: краткая императивная формулировка из «Образа результата».
4. Правила классификации: `Task` по умолчанию; `Bug` при явных сигналах дефекта (ошибка, не работает, регресс, падает, сломалось); неоднозначность → Task + пометка предположения.
5. Маппинг полей → аргументы `jira_create_issue`: `summary`←Summary, `issue_type`←Task/Bug, `description`←собранный блок шаблона, `project_key`←аргумент/профиль, `labels`←пусто (не выдумывать).
6. Правило пустого поля: критичное пустое → в интервью (см. SKILL.md); некритичное пустое → `[УТОЧНИТЬ у {кого}]`.

- [ ] **Step 2: Написать файл**

Содержимое (verbatim-часть — блок шаблона):

```
Образ результата:
<краткое описание образа результата>

ASIS: <описание текущего состояния>
ПРОБЛЕМА: <ключевая проблема, почему текущее решение не устраивает>
TOBE: <целевое состояние>

Описание:
<остальной дополнительный контекст для решения>

Связанные материалы:
- <ключ/URL> — <почему релевантно>
```

Плюс разделы: «Критичные / некритичные поля», «Summary», «Классификация Task/Bug», «Маппинг → jira_create_issue», «Пустые поля». Блок «Связанные материалы» опускается, если PO ничего не выбрал в relevance-research.

- [ ] **Step 3: Self-check по чеклисту**

Проверить глазами: (a) блок шаблона совпадает символ-в-символ с шаблоном из ТЗ пользователя; (b) все 6 пунктов критериев из Step 1 присутствуют; (c) нет `TBD`/`TODO`; (d) коды-примеры помечены как иллюстративные.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/jira-task/resources/template.md
git commit -m "feat(jira-task): reference шаблона описания + правила классификации

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: resources/relevance-search.md

**Files:**
- Create: `.claude/skills/jira-task/resources/relevance-search.md`

**Interfaces:**
- Consumes: имена MCP-инструментов `jira_search`, `confluence_search` (сервер из `tracker.mcp` / `wiki.mcp`).
- Produces: процедура шага Relevance-research: как извлечь ключевые слова, как построить JQL / Confluence-запрос, порог кол-ва (~5), формат кандидата `<ключ/URL> — <почему релевантно>`, правило тишины (нет совпадений — норма). На это ссылается `SKILL.md` шаг 4 (Task 3).

- [ ] **Step 1: Определить критерии приёмки файла**

Файл ДОЛЖЕН содержать:
1. Извлечение ключевых слов из `Summary`, `Образ результата`, `ПРОБЛЕМА`, `TOBE` (существительные/термины/имена систем; выкинуть стоп-слова).
2. JIRA-запрос: пример JQL вида `project = <PROJ> AND text ~ "<kw1>" OR text ~ "<kw2>" ORDER BY updated DESC`, лимит ~10 на выдачу, инструмент `jira_search`.
3. Confluence-запрос: `confluence_search` по тем же ключевым словам, ограничение по `wiki.space` если задан; если `wiki.mcp`/`wiki.space` не заданы — шаг ищет только по JIRA.
4. Ранжирование: свести обе выдачи, отобрать до ~5 наиболее релевантных по совпадению терминов/сущностей.
5. Формат кандидата: `- <ключ Issue или URL страницы> — <1 строка: почему релевантно>`.
6. Правило нулевого допуска: включать только реально возвращённые поиском записи с якорем; ничего не додумывать.
7. Правило тишины: 0 совпадений — норма, не `[УТОЧНИТЬ]`, шаг просто ничего не добавляет.
8. Read-only: только `*_search`/чтение, никакой записи на этом шаге.

- [ ] **Step 2: Написать файл**

Разделы по 8 пунктам выше. Пример JQL и пример выдачи кандидатов пометить как иллюстративные (коды `PROJ-123`).

- [ ] **Step 3: Self-check по чеклисту**

Проверить: все 8 пунктов присутствуют; упомянут фолбэк «только JIRA» при отсутствии wiki-конфига; нет `TBD`/`TODO`; инструменты названы точно (`jira_search`, `confluence_search`).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/jira-task/resources/relevance-search.md
git commit -m "feat(jira-task): reference relevance-research (JQL/Confluence)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: SKILL.md

**Files:**
- Create: `.claude/skills/jira-task/SKILL.md`

**Interfaces:**
- Consumes: `resources/template.md` (Task 1), `resources/relevance-search.md` (Task 2); поля профиля `tracker.type`, `tracker.mcp`, `tracker.projects`/`bft.default_project`, `tracker.base_url`, `wiki.mcp`/`wiki.space`.
- Produces: полную инструкцию навыка, вызываемого как `/jira-task [PROJ] [текст]`.

- [ ] **Step 1: Определить критерии приёмки файла**

Файл ДОЛЖЕН содержать:
1. YAML-frontmatter: `name: jira-task` и `description:` (одна строка, триггеры: «занести задачу в JIRA», «оформить задачу», «/jira-task»).
2. Раздел «Роль»: оформитель задачи PO.
3. Раздел «Доменный профиль»: резолв `tracker.*` / `wiki.*` из `.claude/domain-profile.md`; пустое поле → дефолт + `[УТОЧНИТЬ]`.
4. Раздел «Принцип нулевого допуска» + «Read-only до ок PO».
5. Раздел «Вход / Выход»: `/jira-task [PROJ] [текст]`, текст в вызове или следующим сообщением; выход — ключ + URL Issue.
6. Раздел «Пайплайн (6 шагов)» — по спеке: Parse → Gate-интервью → Classify → Relevance-research → Preview (такт 1) → Create (такт 2). Шаги 1/3 ссылаются на `resources/template.md`, шаг 4 — на `resources/relevance-search.md`.
7. Обработка недоступности MCP в шаге 6 (payload + `[УТОЧНИТЬ]`, без эмуляции успеха).
8. Проверка `tracker.type != jira` → предупредить PO.

- [ ] **Step 2: Написать файл**

Структура (по образцу `.claude/skills/okr-planner/SKILL.md`):

```markdown
---
name: jira-task
description: <одна строка с триггерами>
---

# Навык: jira-task — свободный текст → задача в JIRA

## Роль
...
## Доменный профиль
...
## Принцип нулевого допуска / Read-only
...
## Вход / Выход
...
## Пайплайн (6 шагов)
### 1. Parse            → см. resources/template.md
### 2. Gate-интервью    (критичные поля → 1-3 вопроса; некритичные → [УТОЧНИТЬ])
### 3. Classify         → Task/Bug + проект (см. resources/template.md)
### 4. Relevance-research (read-only) → см. resources/relevance-search.md
### 5. Preview (такт 1) → project/type/summary/описание + список найденных материалов; спросить ок и выбор ссылок
### 6. Create (такт 2)  → jira_create_issue(...); опц. jira_create_issue_link / jira_create_remote_issue_link; вернуть ключ+URL
```

Каждый шаг раскрыть 2–5 строками по спеке. Ссылки на resources — относительными путями от `SKILL.md`.

- [ ] **Step 3: Self-check по чеклисту**

Проверить: (a) frontmatter парсится (name+description); (b) все 8 пунктов из Step 1 присутствуют; (c) 6 шагов пайплайна названы точно и в порядке спеки; (d) сигнатура `jira_create_issue(project_key, summary, issue_type, description, labels)` совпадает с Task 1; (e) нет `TBD`/`TODO`; (f) ссылки на `resources/template.md` и `resources/relevance-search.md` корректны.

- [ ] **Step 4: Проверить обнаружение навыка**

Run: `python3 -c "import pathlib,re,sys; t=pathlib.Path('.claude/skills/jira-task/SKILL.md').read_text(); m=re.match(r'^---\n(.*?)\n---', t, re.S); assert m and 'name: jira-task' in m.group(1) and 'description:' in m.group(1), 'bad frontmatter'; print('frontmatter OK')"`
Expected: `frontmatter OK`

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/jira-task/SKILL.md
git commit -m "feat(jira-task): SKILL.md — 6-шаговый пайплайн

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: examples/email-to-task.md

**Files:**
- Create: `.claude/skills/jira-task/examples/email-to-task.md`

**Interfaces:**
- Consumes: шаблон из Task 1, процедуру relevance из Task 2, пайплайн из Task 3.
- Produces: иллюстративный сквозной прогон (не исполняется, служит эталоном стиля вывода).

- [ ] **Step 1: Определить критерии приёмки файла**

Пример ДОЛЖЕН показывать все 6 шагов на одном кейсе:
1. Вход — сырое письмо/сообщение (с пропущенным полем, напр. без явного TOBE).
2. Parse — как разложилось по полям.
3. Gate-интервью — 1 уточняющий вопрос по пустому критичному полю + ответ PO.
4. Classify — Task, проект `PROJ` (помечен иллюстративным).
5. Relevance-research — 2 найденных кандидата (`PROJ-101`, Confluence URL) с «почему релевантно» + отметка выбора PO.
6. Preview + Create — финальный блок описания (со «Связанными материалами») и результат `PROJ-124` + URL.

- [ ] **Step 2: Написать файл**

Собрать прогон по 6 пунктам. Вверху пометка: «Пример иллюстративный; коды `PROJ-*`, ключи и URL — вымышленные; реальные значения из `.claude/domain-profile.md`».

- [ ] **Step 3: Self-check по чеклисту**

Проверить: все 6 шагов видны; финальное описание соответствует блоку шаблона из Task 1 (включая «Связанные материалы»); пометка про иллюстративность есть; нет `TBD`/`TODO`.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/jira-task/examples/email-to-task.md
git commit -m "docs(jira-task): пример email → JIRA Issue

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: README.md — регистрация навыка

**Files:**
- Modify: `README.md` (таблица «Пайплайны и команды», ~строки 20–27)

**Interfaces:**
- Consumes: готовый навык `/jira-task` (Tasks 1–4).

- [ ] **Step 1: Добавить строку в таблицу**

После строки «Контекст» вставить:

```markdown
| **Задача в JIRA** | `/jira-task` | Свободный текст → задача в JIRA по шаблону (Образ результата/ASIS/ПРОБЛЕМА/TOBE) + relevance-ссылки |
```

- [ ] **Step 2: Self-check**

Проверить: строка добавлена в таблицу, разметка таблицы (3 колонки `|`) не сломана, соседние строки не тронуты.

Run: `grep -n "jira-task" README.md`
Expected: одна строка с `| **Задача в JIRA** |`

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(jira-task): регистрация навыка в README

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:**
- Роль/принципы (нулевой допуск, read-only) → Task 3 + Global Constraints. ✓
- Вход/выход `/jira-task [PROJ] [текст]` → Task 3. ✓
- Шаг Parse + Summary → Task 1 (правила) + Task 3 (пайплайн). ✓
- Шаг Gate-интервью (критичные/некритичные поля) → Task 1 (списки) + Task 3. ✓
- Шаг Classify (Task/Bug, проект из профиля) → Task 1 + Task 3. ✓
- Шаг Relevance-research (JIRA/Confluence, ранжирование, тишина, read-only) → Task 2 + Task 3. ✓
- Шаг Preview (такт 1, выбор ссылок) → Task 3. ✓
- Шаг Create (такт 2, jira_create_issue + links, MCP-недоступность) → Task 3. ✓
- Формат описания + блок «Связанные материалы» → Task 1. ✓
- Файлы SKILL/template/relevance/example → Tasks 1–4. ✓
- Строка в README → Task 5. ✓
- Конфиг профиля (tracker.*, wiki.*) → Task 3 (+ Global Constraints). ✓
- Границы YAGNI (один Issue, без assignee/sprint, без файла-артефакта) → отражены в SKILL.md шаге 6 и границах спеки; план не добавляет запрещённого. ✓

**2. Placeholder scan:** плейсхолдеров-инструкций нет; `<...>` в блоках шаблона — намеренные слоты шаблона, не плейсхолдеры плана.

**3. Type consistency:** сигнатура `jira_create_issue(project_key, summary, issue_type, description, labels)` едина в Tasks 1 и 3; критичные поля `[Образ результата, ПРОБЛЕМА, TOBE]` едины в Tasks 1, 3, 4; инструменты `jira_search`/`confluence_search`/`jira_create_issue_link`/`jira_create_remote_issue_link` названы одинаково в спеке и Tasks 2–3.
