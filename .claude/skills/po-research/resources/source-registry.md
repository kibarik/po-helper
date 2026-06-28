# Source Registry — L1 контракт (po-research)

> Реестр **ролей-источников**. Каждая роль = `{id, intent, extract, anchor}`. Конкретные tool-имена НЕ хардкодятся здесь — резолвятся из `role_bindings` в `.claude/domain-profile.md` (роль `id` → MCP-сервер сотрудника). Колонка `tools (дефолт)` — типовая привязка, если `role_bindings` не переопределяет. Нет источника на факт → `[УТОЧНИТЬ]`. Все операции — **read-only**.

## Источники

| id (роль) | source | tools (дефолт, override ← role_bindings) | extract | anchor |
|---|---|---|---|---|
| `jira` | трекер / роль tracker | `jira_get_issue`, `jira_search`, `jira_get_issue_development_info`, `jira_get_link_types`, `jira_get_sprint_issues` | scope / status / assignee / SP / deps | `PROJ-101` |
| `conf` | wiki / роль conf | `confluence_search`, `confluence_get_page`, `confluence_get_page_children`, `confluence_get_page_images` | TZ / decisions / as-is | `pageId=12345` |
| `code` | repowise | `get_answer`, `get_context`, `get_risk`, `get_why`, `search_codebase`, `get_dead_code`, `get_symbol`, `get_health`, `get_overview`, `list_repos` | blast-radius / decisions / hotspots / QA | `symbol_id` / commit |
| `vault` | obsidian | `search_query`, `search_simple`, `vault_read`, `vault_get_document_map` | OKR / plans / facts / BR / ADR | note-path |
| `web` | web | `WebSearch`, `WebFetch` | внешний контекст / vendor docs | url |
| `vision` | (web+) | `confluence_get_page_images` `[УТОЧНИТЬ: analyze-image MCP не подтверждён]` | скрины / диаграммы | image-ref |
| `compute` | tool-agent | `playwright` (`browser_*`), `serena` (`find_symbol`/`find_referencing_symbols`), `Bash` | проверить-вживую / трассировать / метрики | Compute-слой |

> **`compute` = Perplexity Compute.** Researcher не только читает — **действует** (проверить сайт playwright, трассировать символ serena, снять метрику Bash). Подключается только в **Deep + High-tier** и где нужен As-Is-факт. **Только read-операции** (whitelist, см. ниже).

## Резолв роли → коннектор (role_bindings)

Tool-имена строки выше — **дефолт**. Реальный сервер берётся из `role_bindings` (`.claude/domain-profile.md`):

- `role_bindings[id]` = имя сервера (строка) → используем его tools по дефолт-маппингу роли.
- развёрнутая форма `{mcp, tools, anchor}` → используем явные tools/anchor (кастом-коннектор).
- роль НЕ в `role_bindings` → **недоступна**: её раздел pack → `[НЕДОСТУПНО: роль <id>]`, субагент по ней не спавнится.
- `web: builtin`, `compute` (playwright/serena/bash) — встроенные, available по умолчанию (кроме явного отсутствия в `role_bindings`).

## Finding-объект (что возвращает researcher)

```json
{
  "fact":       "текст факта (атомарный)",
  "source":     "jira|conf|code|vault|web|vision|compute",
  "anchor":     "PROJ-101 | pageId=123 | note-path | url | symbol_id",
  "confidence": "High|Med|Low",
  "freshness":  "дата/версия источника",
  "excerpt":    "цитата-подтверждение",
  "section":    "раздел домена (см. domains.md)",
  "queries":    ["вариант запроса 1", "вариант 2"]
}
```

## Multi-query sweep (G2)

Каждый researcher на свой источник делает **2–3 переформулировки** запроса, не один. Один phrasing → пропуск релевантного.
- `jira_search`: разные JQL (`"Epic Link" = X`, `parent = X`, текстовый `summary ~`).
- `confluence_search`: синонимы термина + узко/широко.
- `WebSearch`: переформулировки + vendor-домены.
- `search_codebase`: семантический + по имени символа.
- `search_query` (vault): по тегу + по тексту.

Найденное по вариантам мерджится внутри researcher (dedupe по anchor) до возврата.

## Anchor-правила

- Каждый finding — с якорем. Нет якоря → факт не идёт в pack, идёт в `[УТОЧНИТЬ]`.
- Якорь смещён с `file:line` (sa-helper) на продуктовые: JIRA-key / Confluence pageId / vault note-path / ADR-ID / url / symbol_id.
- `freshness` обязателен где источник версионируется (Confluence latest version, последний sprint-факт).

## Compute read-only whitelist (R1 — hard-req)

`compute` действует только этими классами операций:
- **playwright:** `browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_network_requests` (read). **Запрет:** click/type/fill/upload, любая мутация.
- **serena:** `find_symbol`, `find_referencing_symbols`, `get_symbols_overview`, `search_for_pattern` (read). **Запрет:** insert/replace/rename/delete.
- **Bash:** только read-команды (`cat`/`grep`/`curl -s GET`/метрики). **Запрет:** запись, мутация состояния, сетевые POST/PUT/DELETE.

Нарушение whitelist = стоп, эскалация PO.
