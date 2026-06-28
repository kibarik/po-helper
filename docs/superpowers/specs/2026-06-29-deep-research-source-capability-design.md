# Дизайн: фиксация инструментов и настроек deep-research на инсталле/онбординге

**Дата:** 2026-06-29
**Статус:** утверждён к реализации (brainstorming)
**Топик:** capability-слой источников для deep-research при разнородных окружениях сотрудников

---

## Проблема

Deep-research (`/po-research deep`, `/bft-context-gen-deep`, workflow `po-context-research`) собирает
контекст из ролей-источников: `tracker`, `wiki`, `code`, `vault`, `web`, `vision`, `compute`.
Окружения сотрудников разные: у одних подключён JIRA/Confluence, у других всё локально (vault/файлы),
третьи держат свои коннекторы. Сейчас `source-registry.md` хардкодит роль→tool-имена и **предполагает**,
что эти MCP подключены («tool-имена проверены в env (v0.2)»). Слоя, который бы знал, что реально доступно
у *этого* сотрудника и как роль маппится на его коннектор, нет.

## Цели (что должно стать лучше)

- **A. Детерминизм/воспроизводимость** — поведение deep-research определяется записанной, стабильной
  конфигурацией коннекторов, а не сиюминутным состоянием MCP. Один и тот же топик у двух сотрудников даёт
  сопоставимый pack; чего не хватает по источникам — помечено явно.
- **C. Управляемость/аудит** — для классов исследования объявлен обязательный минимум ролей; недотяг до
  минимума виден явно (warn/block + coverage-matrix).
- **D. Расширяемость коннекторов** — подключить свой MCP под роль без правки скиллов фреймворка.

## Не-цели (YAGNI — намеренно НЕ делаем)

- ❌ Отдельный `capability-profile.yaml` — дублирует `.mcp.json`.
- ❌ Скилл-мастер `/po-capability` с авто-пробой — дублирует MCP runtime discovery.
- ❌ Хэш/версия профиля, re-probe — `.mcp.json` стабилен сам по себе.
- ❌ Централизованный реестр профилей сотрудников.

## Ключевое решение: переиспользуем готовое

Большая часть задачи уже решена платформой — не изобретаем:

| Потребность | Готовое решение (используем) |
|---|---|
| Инвентарь коннекторов сотрудника | **`.mcp.json`** (уже в репо, уже вне git — per-машину) |
| «Что реально подключено сейчас» | **MCP runtime discovery** / `/mcp` (харнес перечисляет сам) |
| Кастом-коннектор (D) | добавить сервер в `.mcp.json` |
| Деградация при недоступности | уже есть: `[УТОЧНИТЬ]` / `[НЕДОСТУПНО]` + coverage-matrix в `bft-context-gen` |

**Единственный реальный гэп** — семантический биндинг: `.mcp.json` знает «есть сервер `atlassian`», но не
знает, что `atlassian` играет роль `tracker`. Эту привязку надо объявить (~10 строк). Плюс мини-policy
для governance (C).

---

## Архитектура (похудевшая)

Четыре точки, ни одного нового файла-подсистемы:

### 1. `.mcp.json` — без изменений
Остаётся инвентарём коннекторов сотрудника. Кастом-коннектор = добавить сюда сервер.

### 2. `domain-profile.md` — две новые секции

**2a. `role_bindings`** — маппинг абстрактная роль → MCP-сервер из `.mcp.json`. Connector-agnostic.
Settings (base_url/space/projects) НЕ дублируются — берутся из существующих секций `tracker:`/`wiki:`/`cortex:`.

```yaml
role_bindings:
  tracker: atlassian            # имя сервера из .mcp.json; settings ← секция tracker:
  wiki:    atlassian            # settings ← секция wiki:
  code:    repowise             # или свой сервер, напр. my-internal-rag
  vault:   obsidian
  web:     builtin              # WebSearch / WebFetch (встроенные, не MCP)
  compute: [playwright, serena, bash]
  # роль не указана  =>  считается недоступной (её разделы → [НЕДОСТУПНО])
```

Развёрнутая форма для кастом-коннектора с нестандартными tool-именами/якорем:

```yaml
  code:
    mcp:    my-internal-rag
    tools:  [rag_query, rag_context]
    anchor: symbol_id
```

**2b. `source_policy`** — обязательный минимум ролей по классу (мини-governance, C):

```yaml
source_policy:
  on_missing_required: warn     # warn | block
  classes:
    bft-critical:  [tracker, wiki]
    bft-normal:    [tracker]
    research-deep: [tracker, wiki]
```

### 3. `source-registry.md` — лёгкий рефактор
- Роли становятся connector-agnostic: `jira → tracker`, `conf → wiki`.
- Убрать хардкод «tools (проверены в env)» — tool-имена резолвятся из `role_bindings`, не из registry.
- Registry остаётся каноном: список ролей + `extract` + `anchor`-контракт + `intent`. Tool-биндинг — в профиле.

### 4. Deep-research: преамбула «Resolve capability»
Добавляется в начало `po-research` (SKILL, ветка deep), `bft-context-gen-deep.md`, workflow
`po-context-research` — **перед** спавном researcher-субагентов:

1. Прочитать `role_bindings` из `domain-profile.md` (+ при необходимости `.mcp.json` / harness discovery).
2. Для каждой нужной роли: привязана? → проверить, что tools сервера доступны (try → при ошибке
   существующий паттерн `[НЕДОСТУПНО]`). Не привязана или недоступна → роль = unavailable.
3. Прочитать `source_policy`, определить класс топика. Посчитать `required ∩ available`.
   Недоступна required-роль → `on_missing_required`:
   - `block` → СТОП с явным списком: «JIRA недоступна — `bft-critical` требует `tracker`. Проверь
     `.mcp.json`/`role_bindings` или понизь класс».
   - `warn` → продолжить, флаг в pack.
4. Спавнить субагентов **только по available-ролям**. Недоступные роли → их разделы помечаются
   `[НЕДОСТУПНО: роль <X> не привязана/недоступна]`, не галлюцинируются.
5. Coverage-matrix (уже печатается) — добавить колонки `required? | bound? | available?`.

---

## Как цели закрываются

- **A (детерминизм):** `.mcp.json` + `role_bindings` — записанная стабильная конфигурация. Одинаковый
  конфиг → одинаковое поведение. Нет дрейфа от пробы.
- **C (governance):** `source_policy` + coverage-matrix. Недотяг до минимума — явно (warn/block).
- **D (расширяемость):** новый коннектор = сервер в `.mcp.json` + одна строка в `role_bindings`.
  Скиллы фреймворка не трогаются.

## Точки касания (объём реализации)

| Файл | Изменение |
|---|---|
| `domain-profile.template.md` | +секции `role_bindings`, `source_policy` + пояснения |
| `.claude/skills/po-research/resources/source-registry.md` | рефактор: роли agnostic, убрать хардкод tools |
| `.claude/skills/po-research/SKILL.md` | +преамбула «Resolve capability» в ветке deep |
| `.claude/commands/bft-context-gen-deep.md` | +преамбула «Resolve capability» |
| `.claude/workflows/po-context-research*.js` | +резолв capability перед fan-out |
| `install.sh` | финальная подсказка: заполнить `role_bindings` (без нового файла/скилла) |

**Не меняется:** `.mcp.json`, `.gitignore` (нового локального файла нет), деградация и coverage-matrix
(переиспользуются как есть). Новых скиллов/команд нет.

## Открытые вопросы

- `web: builtin` и `compute` (playwright/serena/bash) — встроенные, не из `.mcp.json`. Резолв для них =
  «всегда available, кроме явного отключения». Зафиксировать в преамбуле.
- Класс топика для policy: брать из аргумента команды (напр. `bft-critical` vs `bft-normal`) или из
  KR-tier (как уже делает `po-research`)? — уточнить на этапе плана.
