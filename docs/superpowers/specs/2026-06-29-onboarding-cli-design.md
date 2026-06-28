# Онбординг-CLI `onboard.py` — design

**Дата:** 2026-06-29
**Статус:** на ревью
**Цель PO-helper:** №2 — быстрый setup и онбординг для заполнения экосистемы (Кортексы и Нексусы).

## 1. Проблема

`/paf-init` (LLM-скилл) и `/paf-nexus-create` ссылаются 10+ раз на `/paf-onboard` — шаг наполнения Нексусов, которого **не существует**. Онбординг (цель 2) разорван: точки входа есть, наполнения нет. Плюс `install.sh` не ставит онбординг-инструменты. Нужен **детерминированный CLI-скрипт**, где пользователь интерактивно настраивает систему, надёжно и воспроизводимо.

## 2. Замысел (решения брейншторма)

- **Гибрид:** скрипт делает надёжную детерминированную часть (config, каркас Нексусов, захват ответов интервью), а **качественный синтез контента** Нексусов делегирует LLM-скиллу `/paf-onboard`.
- **Runtime:** Python 3 **stdlib без зависимостей**.
- **Канон:** `onboard.py` — единственный источник логики init; `/paf-init` ужимается в тонкую обёртку «запусти скрипт».
- **Запуск:** standalone (`python3 onboard.py`) + хук в конце `install.sh` («запустить онбординг сейчас?»).
- **Самодостаточность:** скрипт **не зависит** от `sa_documentation` — валидирует собранные данные в памяти, дефолтный каталог Нексусов встроен.

## 3. Архитектура

Один файл **`onboard.py`** в корне репозитория. Чистые функции (без I/O) для логики + тонкий интерактивный слой (`main`/`input`). Логика тестируется без TTY.

```
onboard.py
├── DEFAULT_NEXUSES        # встроенный каталог 4 minimal-типов (зеркало nexus_catalog.md §3)
├── slugify(text)          # кириллица/пробелы → ascii-slug [a-z0-9][a-z0-9-]*
├── validate_collected(d)  # проверки в памяти ДО записи → list[str] ошибок
├── build_config_yaml(d)   # dict ответов → текст config.yaml (YAML-шаблон)
├── build_registry_yaml(d) # → NEXUS/_registry.yaml
├── build_index_md(nx, d)  # → NEXUS/<slug>/_index.md (placeholder, CP 0.3)
├── build_pulse_md(d)      # → PULSE/00-init-pulse.md (baseline)
├── capture_to_markdown(a) # ответы Фазы 2 → _intake/onboarding-answers.md
├── ask(...)/ask_required  # интерактивные хелперы (TTY)
└── main(argv)             # оркестрация фаз + запись + soft-валидация
```

### 3.1 Поток (StepByStep, один вопрос за раз)

**Фаза 1 — INIT** (детерминированная, = текущий `/paf-init`):
1. Опрос: `company` → `product.name` → `product.slug` (валидация + `slugify`-подсказка) → `product.idea` → `team.size` → **`product_engineer` (обязателен, повтор пока не задан)** → опц. roster-роли (имя / `Cortex` / пропуск) → `cortex.phase_target` (1/2/3, дефолт 2).
2. Детект ruflo: `shutil.which("ruflo")` → `cortex.ruflo_mcp: true/false`. Скрипт **не** вызывает MCP.
3. `validate_collected()` в памяти; при ошибках — повтор соответствующего вопроса.
4. Запись: `GROUND/config.yaml`, `GROUND/NEXUS/_registry.yaml`, `GROUND/NEXUS/{customer,market,product,growth}/_index.md`, `GROUND/PULSE/00-init-pulse.md`.

**Фаза 2 — CAPTURE** (наполнение экосистемы):
5. По каждому из 4 Нексусов задаёт его `seed_questions` (из `DEFAULT_NEXUSES`), собирает сырые ответы (пустой ответ допустим → `[УТОЧНИТЬ]`).
6. Фиксирует наличие документов в `GROUND/_intake/`.
7. Запись `GROUND/_intake/onboarding-answers.md` (структура: Нексус → вопрос → ответ). `config.yaml: onboarding.status: in_progress`.

**Хендофф:** печать следующего шага — `/paf-onboard` (LLM).

### 3.2 Контракт `/paf-onboard` (новый LLM-скилл, вторая половина гибрида)

- **Вход:** `GROUND/_intake/onboarding-answers.md` + документы `GROUND/_intake/*` + `GROUND/config.yaml` + реестр.
- **Что делает:** синтезирует ответы и доки в узлы Нексусов (по `nexus_schema.md`), каждый факт ← `sources` (`onboarding:interview` / имя дока). Дедуп через ruflo MCP, если `cortex.ruflo_mcp: true`, иначе Grep.
- **Выход:** наполненные узлы в `GROUND/NEXUS/<slug>/`, `onboarding.status: done`, обновлённый PULSE (Context Ripeness).
- **Гвардраил:** узел без `sources` не создаётся (workslop).

## 4. Файлы на выходе (точно)

`config.yaml` по схеме `sa_documentation/ground_schema.md` (поля: company, product{name,slug,idea}, team{size,roster}, cortex{phase_target,ruflo_mcp,obsidian}, onboarding{status,sources_ingested,baseline_cr,onboarded_at}, nexus{catalog,custom_count}, created, paf_step).
`_registry.yaml` — 4 default-типа с `owner` из roster, `onboarded: todo`.
`_index.md` — placeholder per nexus: frontmatter (kind: empirical, confidence: 0.3, sources: [], ttl_days по типу: customer/market/product=90, growth=60, ripeness: fresh) + seed_questions.
`onboarding-answers.md` — захват Фазы 2.

## 5. Идемпотентность / валидация / ошибки

- `GROUND/config.yaml` существует → меню: **перезаписать / только Фаза 2 (capture) / отмена** (дефолт отмена). Без слепого затирания.
- Валидация — **в памяти** (`validate_collected`): `product.slug` ∈ `[a-z0-9][a-z0-9-]*`; `product_engineer` не пуст; slug Нексусов ∈ `[a-z][a-z0-9-]*`. Запись только после прохождения → битый GROUND не создаётся. PyYAML/subprocess не нужны.
- Доп. soft-проверка: если доступен `sa_documentation/validate_ground.py` (есть PyYAML) — запустить как subprocess и показать результат; **мягкая деградация** при отсутствии (предупреждение, не падение).
- Нет TTY / EOF / `--non-interactive` без данных → корректный выход с подсказкой, без трейсбека.

### 5.1 Флаги CLI
- `--phase init|capture|all` (дефолт `all`)
- `--ground PATH` (дефолт `GROUND`)
- `--non-interactive` (для CI/тестов: только проверки, без записи)

## 6. Изменения рядом

- **`.claude/skills/paf-init/SKILL.md`** → тонкая обёртка: «запусти `python3 onboard.py --phase init`», интервью больше не в LLM. Гвардраилы/связи сохраняются ссылкой.
- **`install.sh`** → в конце: prompt «Запустить онбординг сейчас? (`python3 onboard.py`)»; при согласии и наличии `python3` — запуск. Неинтерактивный режим (pipe) — пропуск с подсказкой.
- **Новый `.claude/skills/paf-onboard/SKILL.md`** — контракт §3.2.
- `diagram-view`, `bft-*`, `okr-*`, `po-research` — не трогаем.

## 7. Тестирование (`tests/test_onboard.py`, pytest, stdlib)

- Юнит: `slugify` (кириллица→ascii, пробелы, edge), `validate_collected` (пустой PE, битый slug), `build_config_yaml`/`build_registry_yaml`/`build_index_md` (структура, обязательные поля, ttl по типу), `capture_to_markdown`.
- **Drift-guard:** slug'и `DEFAULT_NEXUSES` совпадают с `sa_documentation/nexus_catalog.md` (защита от расхождения каталога).
- Интеграция: прогон в `tmp_dir` (через функции, без TTY) → файлы созданы → (если PyYAML есть) `validate_ground` = OK.
- Никаких сетевых/MCP-вызовов в тестах.

## 8. Вне scope

- LLM-синтез контента Нексусов — в `/paf-onboard` (отдельная половина, контракт §3.2; реализация — этот же PR-2 как instruction-файл, без кода).
- Кастомные Нексусы — остаются за `/paf-nexus-create`.
- Никаких новых runtime-зависимостей; PyYAML остаётся опциональным (только для soft-проверки и существующего валидатора).
