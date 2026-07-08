# po-helper full-ecosystem installer — design

**Дата:** 2026-07-06
**Статус:** approved (brainstorming)
**Топик:** переустройство `install.sh` из «урезанного копировщика skills/commands» в полноценный установщик всей экосистемы + оркестрирующий скилл `/paf-install`.

## Проблема

Текущий `install.sh` копирует в проект только `.claude/{skills,commands,workflows}` + шаблон домен-профиля и ставит `entire`/`backlog` (а `ruflo` лишь проверяет). Он **не переносит** `.mcp.json`, `.serena/`, `.entire/`-конфиг, `docs/`, `sa_documentation/`, `bft_documentation/`, `GROUND/`-скелет, `settings.json`, `.gitignore` — и не адаптирует то, что требует правки под проект (хардкод пути ruflo в `.mcp.json`, случайное `project_name` в `.serena/project.yml`). Итог: после установки пользователь получает не готовую экосистему, а фрагмент.

## Цель

Любой AI-агент по команде «Установи po-helper» проводит полную безошибочную установку и первичную настройку: копирует весь репозиторий, ставит и адаптирует весь тулзен (`.entire`, `backlog`, `.serena`, `ruflo`, MCP), доводит проектную адаптацию — так, чтобы пользователь сразу получил рабочую экосистему.

## Решения (из брейншторма)

- **Топология:** сорс → отдельный проект (две локации, как `curl | bash` сейчас).
- **Форма поставки:** `install.sh` (детерминированный движок) + новый скилл `.claude/skills/paf-install/` (оркестрация + рассуждающие шаги).
- **Тулзен:** все 4 CLI (ruflo, entire, backlog, serena) — best-effort + graceful fallback (частичная экосистема валидна).
- **Источник репо (approach B):** запущен из клона → копирую из `SCRIPT_DIR`; иначе (`curl|bash`) → `git clone --depth 1 https://github.com/kibarik/po-helper` в temp, копирую, чищу за собой (trap). Fail-fast с понятной ошибкой, если нет ни клона, ни git+сети.

## Архитектура

Два артефакта, чёткие роли:

| Артефакт | Роль |
|---|---|
| `install.sh` | Детерминированный движок: source resolution, копия репо, bootstrap CLI, адаптация конфигов, self-check, машиночитаемый отчёт |
| `.claude/skills/paf-install/SKILL.md` | Оркестратор для агента: запускает `install.sh`, парсит отчёт, добивает рассуждающие шаги, верифицирует, хендофф в `/paf-init` |

**Принцип границы:** скрипт делает только детерминированное и всегда одинаковое; всё, что требует выбора/интервью (домен-профиль, язык serena, разрешение конфликтов), — в скилле. Скрипт никогда не выдумывает доменные данные.

### Фазы install.sh

```
Phase 0  Source resolution   — клон? копирую отсюда : git clone --depth 1 в temp (+trap cleanup)
Phase 1  Target resolution   — target = $PWD (или arg); проверка git-репо
Phase 2  Copy repo           — всё дерево, кроме VCS-внутренностей и runtime-мусора
Phase 3  Tool bootstrap      — ruflo · entire · backlog · serena (best-effort + fallback)
Phase 4  Config adaptation   — .mcp.json путь · .serena project_name · domain-profile template · backlog init
Phase 5  Self-check + report — структурный блок статусов (OK/DEGRADED/MISSING)
```

## Phase 2 — семантика копирования

Копируем всё дерево сорса в target. Единственный (вынужденный) список исключений — копировать в чужой проект нельзя, всё «выключенное» переинициализируется в Phase 3–4:

| Исключение | Почему |
|---|---|
| `.git` | В сорсе — указатель worktree; у target свой VCS |
| `.claude/worktrees/` | Локальный scratch агента |
| `.serena/cache`, `.serena/project.local.yml` | Машинно-локальный кэш |
| `.entire/{logs,metadata,tmp,settings.local.json,redactors/local}` | Сессионный стейт машины; `entire enable` создаёт заново |
| `.claude/*.db`, `.swarm/` | Runtime-артефакты ruflo |
| `repomix-output.xml`, `**/repomix-*.xml`, `.DS_Store`, `__pycache__/`, `*.pyc` | Регенерируемый мусор |

Реализация: `rsync -a --exclude-from` если есть rsync; иначе `tar --exclude … | tar -x`. Оба уважают один список.

### Идемпотентность — два режима

- **`install` (default):** файл уже есть в target → не трогаем; недостающее добавляем.
- **`--update`:** освежаем generic framework-слой (`.claude/{skills,commands,workflows,agents}`, `docs/`, `sa_documentation/`, `bft_documentation/`, `README.md`, шаблоны), но не перезаписываем domain/project-слой.

**Защищённый (domain/project) слой — не перезаписывается никогда:**
- `.claude/domain-profile.md`
- `GROUND/**` при наличии непустых (не скелетных `_index/_template/.gitkeep`) данных
- `.claude/skills/*/examples/` проекта
- `backlog/**`
- `.serena/project.yml` с уже кастомизированным `project_name`
- `.mcp.json`, если путь уже адаптирован
- `.claude/settings.json` / `settings.local.json`

Правило: **framework-слой освежается, domain/project-слой неприкосновенен.**

## Phase 3 — bootstrap тулзена (best-effort + fallback)

Единый паттерн: `есть? → верифицировать : поставить → верифицировать`. Провал не роняет установку — печатает инструкцию, помечает `DEGRADED`.

| Тул | Установка | Верификация | Fallback |
|---|---|---|---|
| ruflo | `npm i -g ruflo@latest` | `ruflo --version` ≥ 3.14.4 | инструкция; MCP `ruflo` degraded |
| entire | `curl -fsSL entire.io/install.sh \| bash` (`$HOME/.local/bin`) | `entire version` | ручной curl; session-tracking off |
| backlog | `bun add -g backlog.md` → `npm i -g backlog.md` | `backlog --version` | инструкция; штаб off |
| serena | проверка `uvx` (глобальный MCP) | `uvx --help` | `pip install uv`; serena-MCP degraded |

Порядок: ruflo раньше Phase 4 (нужен реальный путь для `.mcp.json`). `entire enable --agent claude-code --telemetry=false` — здесь же (нужен git-репо target).

## Phase 4 — адаптация конфигов (детерминированная)

Каждая правка: «проверь, адаптировано ли уже → адаптируй → иначе пропусти» (идемпотентно).

1. **`.mcp.json`** — `/opt/homebrew/bin/ruflo` → `$(command -v ruflo)`; если ruflo не на PATH — оставить bare `"ruflo"`. `backlog` не трогаем.
2. **`.serena/project.yml`** — `project_name` → `basename target`, только если ещё «случайное» (маска `*-<hex>` / совпадает с сорсовым). `languages` в скрипте не трогаем (выбор → скилл/paf-init).
3. **domain-profile** — если нет `.claude/domain-profile.md`, кладём `.claude/domain-profile.template.md`. Заполненный профиль не фабрикуем (интервью `/paf-init`).
4. **backlog** — `backlog init <basename> --defaults --integration-mode mcp` + `remoteOperations false` + `backlog/docs/operational-hq.md`. Идемпотентно.
5. **entire** — `settings.json` скопирован в Phase 2; `enable` — в Phase 3.

## Phase 5 — self-check + отчёт

Машиночитаемый блок, который парсит скилл:

```
=== PAF-INSTALL-REPORT ===
repo_copied:      OK | FAILED
excluded_clean:   OK
ruflo:            OK <ver> | DEGRADED | MISSING
entire:           OK <ver> | DEGRADED
backlog:          OK | DEGRADED
serena:           OK | DEGRADED
mcp_json:         ADAPTED | SKIPPED
serena_name:      SET <old> → <new> | SKIPPED
domain_profile:   TEMPLATE | PRESENT
backlog_init:     OK | SKIPPED | FAILED
=== END-REPORT ===
```

Exit `0` при любой деградации (частичная экосистема валидна); `!=0` только при фатале Phase 0–2.

## Скилл /paf-install

`.claude/skills/paf-install/SKILL.md`. Триггеры: «Установи po-helper», «разверни po-helper», «настрой экосистему», `/paf-install`.

Шаги (с чеклистом):
1. Прогон `install.sh` (или `--update`, если проект уже проинициализирован); захват отчёта.
2. Разбор отчёта: каждый `DEGRADED/MISSING` → причина + команда ремедиации + предложение повторить. Не врать про готовность.
3. Рассуждающая адаптация: имя проекта (дефолт basename, дать переопределить); язык(и) `.serena/project.yml` (определить по target); разрешение конфликтов защищённого слоя через diff-вопрос.
4. Хендофф в `/paf-init` (домен-профиль + засев GROUND) — не дублировать, а вызвать.
5. Финальная верификация: тулы резолвятся, MCP-серверы поднимаются, ключевые файлы на месте → честный итоговый чеклист.

Разделение: скрипт = «сделал одинаково и проверил факты», скилл = «разрулил выбор, объяснил человеку, довёл до готового».

## Тестирование

1. **Статика:** `bash -n install.sh` + `shellcheck` (если доступен).
2. **Смоук в scratch-репо** (`git init` во временной target, сорс = текущий клон): ключевые деревья на месте (`.claude/skills`=14, `GROUND/NEXUS`, `docs/`, `sa_documentation/`); `.git` сорса не скопирован; runtime-мусор отсутствует; `.mcp.json` путь переписан; `.serena` `project_name` = basename; блок отчёта присутствует; exit 0.
3. **Fallback-ветка:** прогон с «спрятанными» тулами (PATH без npm/bun/uvx/entire) → всё `DEGRADED`, не падает, exit 0.
4. **Идемпотентность:** два прогона; между ними правим `.claude/domain-profile.md` и файл в `GROUND/` → второй прогон их не затирает; `--update` освежает `skills/`, но сохраняет `examples/` и домен.

Реальные сетевые инсталлы в тестах не гоняем — проверяем ветку fallback и адаптацию; `npm/curl/uvx` мокаем отсутствием бинарей.

## Out of scope

- Установка самого Claude Code / MCP-хоста.
- Windows-нативная поддержка (ориентир — bash: macOS/Linux/WSL).
- Изменение содержимого доменных скиллов/пайплайнов.
