# Domain Profile — адаптация po-helper под проект

> Скопируйте этот файл в `.claude/domain-profile.md` вашего проекта и заполните под свою предметную область.
> Команды po-helper (`/bft-*`, `/okr-*`, `/po-research`) читают этот файл и подставляют значения вместо хардкода путей и доменных терминов.
> Незаполненное поле → команда работает в дефолтном режиме и помечает результат `[УТОЧНИТЬ]`. Каждый факт ← источник: принцип нулевого допуска к галлюцинациям не зависит от профиля.

---

## 1. Пути (paths)

Где живут документы планирования и артефакты пайплайнов. `{quarter}` / `{year}` / `{epic}` — подстановки во время выполнения.

```yaml
paths:
  # Корень квартального планирования (OBJ/KR, стандарты, индексы) — deliverable-артефакты Нексуса project-management (delivery map PO)
  planning_root:    "GROUND/NEXUS/project-management/{quarter}/Планирование"
  # Корень исполнения (планы/факты спринтов — для переноса незавершённого)
  execution_root:   "GROUND/NEXUS/project-management/{quarter}/Исполнение"
  # Годовой roadmap (стратегический вход)
  roadmap_year_doc: "GROUND/NEXUS/project-management/Roadmap {year}.md"
  # Стандарты формулировок OBJ/KR (формулы, чеклисты)
  standards_doc:    "{planning_root}/BEST-PRACTICES-OBJ-KR.md"
  # Индекс OKR квартала (таблица KR по OBJ)
  index_doc:        "{planning_root}/INDEX.md"
  # Карта связи KR ↔ Epic трекера
  kr_epic_map_doc:  "{planning_root}/KR-EPIC-MAP.md"
  # Финальный артефакт OKR
  okr_output_doc:   "{planning_root}/OKR-{quarter}.md"
  # Roadmap по спринтам на квартал (матрица KR × спринт; rolling)
  sprint_roadmap_doc: "{planning_root}/SPRINT-ROADMAP-{quarter}.md"
  # Финальный план спринта (для обсуждения с командой)
  sprint_output_doc: "{execution_root}/{sprint}/ПЛАН-{sprint}.md"
  # ФАКТ спринта (итог по завершении: velocity, carryover, достижение Sprint Goal) — вход для /sprint-sync следующего
  sprint_fact_doc:  "{execution_root}/{sprint}/ФАКТ-{sprint}.md"
  # Рабочая папка пайплайна спринта (промежуточные артефакты стадий)
  sprint_workspace: "CORTEX/_context-packs/sprint/{sprint}"
  # Рабочая папка пайплайна OKR (промежуточные артефакты стадий)
  okr_workspace:    "CORTEX/_context-packs/okr/{quarter}"
  # Корень груминга OKR Фазы 2 (1 степ = 1 KR: SMART-якорь + US-декомпозиция + вопросы)
  okr_grooming_root: "{okr_workspace}/grooming"
  # Рабочая папка пайплайна BFT (папка конкретного БФТ: финальный <epic>.md + artefacts/)
  bft_workspace:    "bft_documentation/{epic}"
  # Корень всех БФТ (готовые документы + золотые референсы)
  bft_store:        "bft_documentation"
  # Рабочая папка пайплайна po-research (контекст-паки)
  research_workspace: "CORTEX/_context-packs/{domain}/{topic}"
  # Рабочая папка релиза (baseline/change-log/ledger/status). {release} — подстановка
  release_workspace:   "CORTEX/_releases/{release}"
  # Папка алертов о дрейфе (плоская, общая на проект)
  release_alerts_root: "CORTEX/release-alerts"
  # Рабочая папка пайплайна request-intake (обработка внешних запросов)
  intake_workspace: "CORTEX/_intake/{request_id}"
  # Реестр информационных каналов (Нексус channels) — питает /channel-route разметкой входящей информации
  channels_nexus: "GROUND/NEXUS/channels"
  # Рабочая папка прогона калибровки People Graph (nexus-calibration). {run_id} — слаг прогона (short-01…)
  calibration_workspace: "GROUND/NEXUS/team/_calibration/{run_id}"
  # Папка оперативных сведений — #summary-заметки встреч (/summary). Файл = встреча: {дата}-{slug}.md
  summary_notes: "GROUND/PULSE/summaries"
```

Если у проекта нет какого-то документа (например `KR-EPIC-MAP`) — оставьте путь, команда при отсутствии файла предложит его создать (bootstrap), не выдумывая содержимое.

---

## 2. Команды и роли (teams)

Кто исполняет KR. Используется в «Образ действия» (теги ролей) и при распределении.

```yaml
teams:
  - { code: "TEAM-A", name: "Команда A", domain: "что делает" }   # пример
# роли-теги в образе действия (стадия /okr-enrich, /bft-draft):
role_tags: ["BA", "SA", "BE", "FE", "QA", "RELEASE", "ADR", "PO"]
# модификатор [EXT] = шаг исполняет внешняя команда (напр. [BE][EXT], [FE][EXT])
# Фаза 2 (груминг): префиксы вопросов исследования по ответственной роли — ADR# / SA# / BA# / DEL#
```

`teams` — это команды-исполнители KR (наши). Команды **вокруг** PO (внешний ландшафт) —
в секции `landscape` ниже.

---

## 2a. Ландшафт внешних команд (landscape)

Команды вокруг PO — «что делают команды рядом». Используется стадией `/okr-landscape`
(снимок квартала) и `/bft-ext-teams` (проекция на эпик), чтобы точно понимать блокаторы
и связи: «с PO каких команд я связан при разработке задачи и почему».

```yaml
landscape:
  nexus_root:   "GROUND/NEXUS/landscape"        # ext-team узлы (постоянное знание)
  snapshot_doc: "{okr_workspace}/landscape-{quarter}.md"   # снимок квартала
  bft_artifact: "external-teams-actions.md"      # имя проекции в artefacts/ эпика
  # засев Нексуса (bootstrap через /paf-nexus-create landscape):
  ext_teams:
    - { code: "TEAM-PAY", name: "Платежи", po: "Имя", relationship: "upstream" }   # пример
    # relationship: upstream (мы зависим) | downstream (зависят от нас) | peer | platform | regulator
```

Секция пустая → `/okr-landscape` работает от опроса PO и помечает пробелы `[УТОЧНИТЬ]`;
`/bft-ext-teams` при отсутствии снимка честно помечает `[УТОЧНИТЬ: нет landscape-снимка]`.

---

## 3. Трекер задач (tracker)

```yaml
tracker:
  type:      "jira"                    # jira | github | gitlab | none
  mcp:       "atlassian"               # имя MCP-сервера (если есть)
  projects:  ["PROJ1", "PROJ2"]        # ключи проектов / префиксы эпиков (для кросс-проектного reuse)
  base_url:  "https://jira.example.com"
  access:    "read-only"               # read-only | build   (см. ниже — «build» только для BUILD-прохода)

  # --- Метаданные проекта для BUILD-прохода (/sprint-build, /sprint-activate) ---
  # Резолвятся один раз через discovery в /sprint-sync. Пусто → навык помечает [УТОЧНИТЬ]
  # и запрашивает через MCP (не гадать id!). Значения ниже — ИЛЛЮСТРАТИВНЫЕ (кейс GDSLV).
  epic_link_field: "customfield_10101"  # поле связи история→эпик (Jira Server/DC — Epic Link, НЕ parent)
  sprint_field:    "customfield_10007"  # поле спринта (или board_id ниже)
  board_id:        ""                   # id доски для операций со слотами спринтов
  issuetype:
    story:   "10203"                    # id типа Story
    subtask:                            # карта типов подзадач (роль → issuetype id)
      analysis: "12007"                 # аналитика
      dev:      "10107"                 # разработка
      devops:   "12702"                 # девопс
      test:     "10109"                 # тестирование
  # Источник назначаемых пользователей (валидные учётки + роли). Пусто → брать из NEXUS/team
  # и валидировать через MCP (assignable users проекта) на discovery.
  assignable_users_source: "mcp"        # mcp | roster | none
```

Трекер недоступен (нет VPN/доступа) → команды честно помечают `[НЕДОСТУПНО]`, не выдумывают состав беклога.

**Режим `access`:**
- `read-only` (дефолт) — PLAN-проход (`/sprint-sync`…`/sprint-deliver`) и все read-стадии. Запись в трекер запрещена.
- `build` — разблокирует BUILD-проход (`/sprint-build`, `/sprint-activate`): необратимая запись в JIRA через MCP, только после dry-run→approve. Переключается осознанно PO, не «по умолчанию».

**Гигиена доступа:** трекер — **только через MCP** (`tracker.mcp`). Токены/PAT руками не собирать и не вставлять в чат. Нет MCP → остановиться и попросить поднять MCP/VPN, а не искать обходной путь.

---

## 4. Wiki / документация (wiki)

```yaml
wiki:
  type:   "confluence"                 # confluence | notion | none
  mcp:    "atlassian"
  space:  "SPACE_KEY"                  # дефолтный space для публикации (BFT)
  base_url: "https://confluence.example.com"
```

---

## 4a. База знаний / кортексы (cortex) — для BFT-пайплайна

Реестры доменных знаний, которые `/bft-context-gen` подключает как статичный фон. Пути опциональны: нет файла → раздел контекста помечается `[УТОЧНИТЬ]`.

> **Приоритет графа Нексусов.** Если инстанцированы Нексусы BFT-яруса (`system`/`decisions`/`rules`/`compliance` — см. `sa_documentation/nexus_catalog.md` §4.2), пайплайн читает их узлы **вместо** плоских `cortex.*`-реестров (узел несёт `sources`/`confidence`/`ripeness`). Плоский CORTEX ниже — **fallback** и источник первичного онбординга (`/paf-onboard` наполняет из него узлы). Маппинг: `system`←`architecture` (C1), `decisions`←`decisions` (C5), `rules`←`business_rules` (C2), `compliance`←`regulatory` (C3).

```yaml
cortex:
  architecture:    "CORTEX/Архитектура/00-архитектура.md"      # C1: границы, потоки, сервисы
  regulatory:      "CORTEX/Регуляторика/00-Реестр-регуляторики.md"  # C3: применимые законы
  business_rules:  "CORTEX/Бизнес-правила/00-Реестр-BR.md"     # C2+: бизнес-правила BR-*
  decisions:       "CORTEX/Решения/00-Реестр-решений-ADR.md"   # C5: ADR + PO-решения
  sa_store:        "CORTEX/SA/"                                  # смежные системные анализы
```

### BFT-дефолты

```yaml
bft:
  default_space:   "SPACE_KEY"         # Confluence space по умолчанию (= wiki.space)
  default_project: "PROJ1"             # JIRA-проект для создания эпика по умолчанию
  parent_page_id:  ""                  # родительская страница Confluence (если есть)
```

---

## 5. Глоссарий (glossary)

Доменные термины — чтобы команды понимали запросы и не путали сущности. Опционально, но сильно повышает точность.

```yaml
glossary_doc: "CLAUDE.md"              # где описан глоссарий, или inline ниже
glossary:
  - { term: "ТЕРМИН", meaning: "что это" }   # пример
```

---

## 6. Стейкхолдеры (stakeholders)

Кто согласует / кому коммитменты. Используется в гейтах (Critical KR → дедлайн/коммитмент перед кем).

```yaml
stakeholders:
  - { role: "CPO/ГД/...", name: "Имя", scope: "что согласует" }   # пример
po_name: "Имя PO"
```

---

## 7. Каденция (cadence)

```yaml
cadence:
  quarter_format: "{ГГГГ}Q{N}"         # как именуется квартал
  sprint_format:  "{ГГГГ}Q{N}-S{P}"    # как именуется спринт
  sprint_weeks:   2
  sprints_per_quarter: 6               # сколько спринтов в квартале (для /sprint-roadmap)
  current_quarter: "2026Q3"
```

---

## 7a. Ёмкость команды (capacity) — для пайплайна спринта

Как считается «максимальная загрузка каждого» в `/sprint-load` и `/sprint-roadmap`. Состав команды — из `GROUND/NEXUS/team/*` (person-узлы); ёмкости — отсюда. Отпуска/недоступность PO подтверждает в `/sprint-sync`.

```yaml
capacity:
  roster_source:      "GROUND/NEXUS/team"   # каталог person-узлов (источник ростера и ролей)
  focus_factor:       0.7                    # доля времени на плановую работу (Scrum: 0.6–0.8)
  sp_per_person_sprint: 8                    # дефолтная ёмкость, если нет истории velocity
  underload_threshold:  0.7                  # < этого порога ёмкости → 🟡 недогруз (добрать)
  # velocity по человеку (SP/спринт) — если ведётся история; иначе sp_per_person_sprint
  velocity:
    - { person: "team-lastname-firstname", sp: 8 }   # пример (node_id из NEXUS/team)
```

Поля пустые → команда работает на дефолтах (`focus_factor: 0.7`, `sp_per_person_sprint`) и помечает оценки `[УТОЧНИТЬ velocity]`.

---

## 8. Релиз-дефолты (release) — для навыка release-guard

Параметры мониторинга дрейфа объёма. Используются командами `/release-*`.

```yaml
release:
  drift_threshold_sprints: 2          # дрейф ≥ этого → 🔴 алерт
  staleness_n:             2          # пропущенных синков без актуализации → зона риска
  estimate_unit:           "sprint"   # sprint | story_point | dev_day
  sprint_capacity:         1          # единиц estimate_unit = 1 спринт (для story_point = velocity)
  sync_period_days:        14         # период синка (по умолчанию = sprint_weeks × 7)
  # источник «факта» по требованиям — трекер-эпик + дочерние (секция tracker выше)
```

Период `/release-sync` на cron должен совпадать с `sync_period_days` (один синк ≈ один спринт). Реже — staleness ловится с запозданием; чаще — лишний шум.

---

## Как команды используют профиль

1. Каждая команда на «Этапе 1: Загрузка контекста» читает `.claude/domain-profile.md`.
2. Все пути в инструкциях команды (`{planning_root}`, `{okr_workspace}`, …) резолвятся из секции `paths`.
3. Доменные примеры в SKILL/examples — иллюстративные (предметная область автора шаблона). Команда опирается на **профиль проекта**, а не на примеры.
4. Поле профиля пустое → дефолт + пометка `[УТОЧНИТЬ]` в артефакте. Профиль не отменяет требование источника на каждый факт.
