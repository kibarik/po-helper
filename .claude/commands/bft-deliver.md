---
description: 'Отгрузка БФТ — публикация в JIRA+Confluence, связывание артефактов (роль: Deliverer). Сухой прогон → ок PO → запись'
---

## Использование

```
/bft-deliver <epic_code> [bft_space] [bft_parent_id] [project]
```

**Параметры:**
- `<epic_code>` — короткий код БФТ (напр. `EPIC-10`, `EPIC-FAQ`). По нему находится финальный БФТ `{bft_store}/{epic_code}/{epic_code}*.md`.
- `[bft_space]` — Confluence space для публикации БФТ команды API-слой. **Дефолт — `wiki.space` из профиля** (из `skills/bft-writer/SKILL.md`).
- `[bft_parent_id]` — parent page для БФТ-страницы (опц.). Если не задан → `[УТОЧНИТЬ у PO]`.
- `[project]` — JIRA-проект для создания Эпика. **Дефолт — `bft.default_project` из профиля.**

## Примеры

```
/bft-deliver EPIC-10
/bft-deliver EPIC-10 {wiki.space} {bft.parent_page_id}
/bft-deliver EPIC-FAQ {wiki.space} {bft.parent_page_id} PROJ2
```

## Важно

**Роль: Deliverer.** Финальная (9-я) стадия pipeline после `/bft-validate` (итог 🟢/🟡). Берёт **валидный** черновик БФТ и публикует 4 артефакта: JIRA Эпик + 2 страницы Confluence + связи между ними.

> Аналог sa-helper: нет прямого; это финал публикации после `/validate-doc`.

**Анти-правило (приоритет):** JIRA и Confluence — **только чтение до явного «ок» PO**. Поэтому команда работает в 2 такта:
1. **Сухой прогон** — собирает preview всех 4 артефактов БЕЗ записи, выводит STOP.
2. После «ок» PO — **выполняет 4 шага подряд**, захватывая ID каждого артефакта для связывания.

**Принципы:**
- Источник содержимого — **только валидный черновик БФТ** из vault. Не выдумывай факты заново.
- `{bft.parent_page_id}` — родительская страница «краткого сутевого описания запроса» (из профиля).
- Каждый шаг захватывает ID (epicKey, pageId) → передаёт на шаг связывания. **Последовательно, не параллельно.**
- VPN/Confluence/JIRA недоступны → честно `[УТОЧНИТЬ: MCP недоступен]`, не эмулировать успех.

---

## Инструкция для ЛLM

### ТАКТ 1. СУХОЙ ПРОГОН (без записи)

#### Этап 1: Загрузка входов
1. Найди финальный БФТ: `{bft_store}/<epic_code>/<epic_code>*.md`. Если нет → СТОП:
   ```
   🔴 Финальный БФТ <epic_code> не найден в {bft_store}/<epic_code>/.
   → /bft-draft <epic_code>, затем /bft-validate <epic_code>.
   ```
2. Проверь `validation.md` (в `{bft_workspace}/` или рядом). Если есть 🔴 в Hard Gates → СТОП, отгрузка запрещена:
   ```
   🔴 БФТ <epic_code> не прошёл валидацию (есть 🔴 в Hard Gates).
   → /bft-draft <epic_code> (исправить), затем /bft-validate.
   ```
3. Прочитай `problem.md` + `concept.md` (если есть) — для краткой выжимки.
4. Зафиксируй параметры: `epic_code`, `bft_space` (дефолт = `wiki.space`), `bft_parent_id`, `project` (дефолт = `bft.default_project`).

#### Этап 2: Сборка preview 4 артефактов

**Превью 1 — JIRA Эпик** (project=`<project>`):
- `summary`: название БФТ (из H1 черновика, без префикса `[БФТ]`).
- `issue_type`: `Epic`. Если тип в проекте называется иначе → пометь `[УТОЧНИТЬ: issue_type Epic в <project>]`.
- `description`: из раздела «Бизнес описание» + ключевые БТ + ссылка на полный БФТ (placeholder, ссылку подставишь на шаге связывания). Markdown.
- `labels`: `bft`, `epic_code`.
- Доп. поля: priority/assignee только если явно есть в черновике, иначе не выдумывать.

**Превью 2 — Дочерняя страница «краткое сутевое описание»** (parent=`{bft.parent_page_id}`):
- `title`: `<epic_code>: <Название БФТ> — краткое описание запроса`.
- `body` — **выжимка** (не копия всего БФТ):
  - Суть запроса: 2-3 предложения (из «Бизнес описание»).
  - As-Is → Gap (из problem.md, 2-4 строки).
  - Образ результата (из концепта/БТ, 1-2 пункта).
  - Ключевые ФТ (3-5 шт, верхнеуровнево).
  - Плейсхолдеры: `[Эпик: подставится]`, `[Полный БФТ: подставится]`.
- `content_format`: markdown.

**Превью 3 — Страница БФТ команды API-слой** (space=`<bft_space>`, parent=`<bft_parent_id>`):
- `title`: `[БФТ] <epic_code>: <Название>` (как H1 черновика).
- `body`: **полное содержимое** vault-файла `{bft_store}/<epic_code>/<epic_code>*.md` (frontmatter убери, остальное 1:1 — PlantUML-блоки сохраняй как есть).
- Если `bft_parent_id` не задан → пометь `[УТОЧНИТЬ у PO: parent page для БФТ в space <bft_space>]`, СТОП.
- `content_format`: markdown.

**Превью 4 — План связей** (связать всё с JIRA Эпиком):
- Remote link: `epicKey` ↔ `pageId 2` (краткое описание).
- Remote link: `epicKey` ↔ `pageId 3` (полный БФТ).
- В тексты страниц 2 и 3 подставить `epicKey` (зависит от шага 1).

#### Этап 3: Вывод preview + STOP

```
── СУХОЙ ПРОГОН ОТГРУЗКИ БФТ <epic_code> ──
Записи не было. Параметры: project=<project>, bft_space=<bft_space>, summary_parent={bft.parent_page_id}, bft_parent=<bft_parent_id|TBD>.

▸ АРТЕФАКТ 1 — JIRA Эпик (<project>)
   summary: ...
   issue_type: Epic
   description: <превью>

▸ АРТЕФАКТ 2 — Дочерняя страница «краткое описание» (parent {bft.parent_page_id})
   title: ...
   body: <превью выжимки>

▸ АРТЕФАКТ 3 — Страница БФТ (space <bft_space>, parent <bft_parent_id>)
   title: ...
   body: <полный БФТ из vault, N символов>

▸ АРТЕФАКТ 4 — Связи
   epicKey ↔ [страница 2], epicKey ↔ [страница 3]

── СТОП ──
PO: подтверди «ок» (или поправь параметры) → выполню все 4 шага с записью.
Без «ок» — ничего не публикую.
```

---

### ТАКТ 2. ЗАПИСЬ (только после явного «ок» PO)

Выполняй **последовательно**, захватывая ID каждого шага.

#### Шаг 1: Создать JIRA Эпик
- `jira_create_issue(project_key=<project>, summary=..., issue_type='Epic', description=..., labels=[...])`.
- Захвати `epicKey` (напр. `PROJ-102`).
- Если `issue_type='Epic'` отвергнут → СТОП, спроси PO точное имя типа.

#### Шаг 2: Дочерняя страница «краткое описание»
- `confluence_create_page(space_key=<space страницы {bft.parent_page_id}>, title=..., content=..., parent_id='{bft.parent_page_id}', content_format='markdown')`.
- В `content` подставь `epicKey` (из шага 1) в плейсхолдер ссылки на Эпик.
- Захвати `pageId_краткое`.
- Если parent `{bft.parent_page_id}` недоступен/нет прав → СТОП, доложи.

#### Шаг 3: Страница БФТ команды API-слой
- `confluence_create_page(space_key=<bft_space>, title=..., content=<полный БФТ>, parent_id=<bft_parent_id>, content_format='markdown')`.
- В `content` подставь `epicKey` (из шага 1) в плейсхолдер.
- Захвати `pageId_БФТ`.

#### Шаг 4: Связать документы с JIRA Эпиком
- `jira_create_remote_issue_link(issue_key=<epicKey>, url=<Confluence URL страницы 2>, title='Краткое описание запроса (<epic_code>)')`.
- `jira_create_remote_issue_link(issue_key=<epicKey>, url=<Confluence URL страницы 3>, title='БФТ <epic_code> (полный)')`.
- Опционально: добавить комментарий на Эпик со ссылками на обе страницы (`jira_add_comment`).

#### Этап 5: Манифест отгрузки + отчёт
- Сохрани `{bft_workspace}/delivery.md`:
  ```
  # Отгрузка БФТ <epic_code>
  - Дата: ...
  - JIRA Эпик: <epicKey> — <URL>
  - Краткое описание (Confluence): pageId <id> — <URL>  (parent {bft.parent_page_id})
  - Полный БФТ (Confluence): pageId <id> — <URL>  (space <bft_space>, parent <bft_parent_id>)
  - Связи: epicKey ↔ обе страницы
  ```
- Финальный вывод:
  ```
  ✅ БФТ <epic_code> отгружен.
  Эпик: <epicKey> — <URL>
  Краткое описание: <URL>
  Полный БФТ: <URL>
  Связи проставлены. Манифест: {bft_workspace}/delivery.md
  ```

---

## Запреты

1. **Не публикуй без явного «ок» PO** — сухой прогон обязателен, запись только во 2-м такте.
2. **Не публикуй при 🔴 в validation.md** — сначала `/bft-draft` + `/bft-validate`.
3. **Не выдумывай факты** в описаниях — только из черновика БФТ / problem / concept. Незакрытое → `[УТОЧНИТЬ]`.
4. **Не хардкодь `epicKey` / pageId** — они неизвестны до выполнения шагов 1-3.
5. **Не выполняй шаги параллельно** — шаг 4 зависит от ID шагов 1-3.
6. **Не эмулируй успех** при недоступности MCP (VPN) — честно `[УТОЧНИТЬ]`.
7. **Не подставляй секреты/токены** в описания; `.mcp.json` вне git.
