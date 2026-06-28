# Domain Profile — адаптация po-helper под проект

> Скопируйте этот файл в `.claude/domain-profile.md` вашего проекта и заполните под свою предметную область.
> Команды po-helper (`/bft-*`, `/okr-*`, `/po-research`) читают этот файл и подставляют значения вместо хардкода путей и доменных терминов.
> Незаполненное поле → команда работает в дефолтном режиме и помечает результат `[УТОЧНИТЬ]`. Каждый факт ← источник: принцип нулевого допуска к галлюцинациям не зависит от профиля.

---

## 1. Пути (paths)

Где живут документы планирования и артефакты пайплайнов. `{quarter}` / `{year}` / `{epic}` — подстановки во время выполнения.

```yaml
paths:
  # Корень квартального планирования (OBJ/KR, стандарты, индексы)
  planning_root:    "ROADMAP/{quarter}/Планирование"        # пример
  # Корень исполнения (планы/факты спринтов — для переноса незавершённого)
  execution_root:   "ROADMAP/{quarter}/Исполнение"
  # Годовой roadmap (стратегический вход)
  roadmap_year_doc: "ROADMAP/Roadmap {year}.md"
  # Стандарты формулировок OBJ/KR (формулы, чеклисты)
  standards_doc:    "{planning_root}/BEST-PRACTICES-OBJ-KR.md"
  # Индекс OKR квартала (таблица KR по OBJ)
  index_doc:        "{planning_root}/INDEX.md"
  # Карта связи KR ↔ Epic трекера
  kr_epic_map_doc:  "{planning_root}/KR-EPIC-MAP.md"
  # Финальный артефакт OKR
  okr_output_doc:   "{planning_root}/OKR-{quarter}.md"
  # Рабочая папка пайплайна OKR (промежуточные артефакты стадий)
  okr_workspace:    "CORTEX/_context-packs/okr/{quarter}"
  # Рабочая папка пайплайна BFT
  bft_workspace:    "CORTEX/_context-packs/{epic}"
  # Хранилище готовых БФТ
  bft_store:        "CORTEX/БФТ"
  # Рабочая папка пайплайна po-research (контекст-паки)
  research_workspace: "CORTEX/_context-packs/{domain}/{topic}"
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
```

---

## 3. Трекер задач (tracker)

```yaml
tracker:
  type:      "jira"                    # jira | github | gitlab | none
  mcp:       "atlassian"               # имя MCP-сервера (если есть)
  projects:  ["PROJ1", "PROJ2"]        # ключи проектов / префиксы эпиков
  base_url:  "https://jira.example.com"
  access:    "read-only"               # по умолчанию только чтение
```

Трекер недоступен (нет VPN/доступа) → команды честно помечают `[НЕДОСТУПНО]`, не выдумывают состав беклога.

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

```yaml
cortex:
  architecture:    "CORTEX/Архитектура/00-архитектура.md"      # C1: границы, потоки, сервисы
  regulatory:      "CORTEX/Регуляторика/00-Реестр-регуляторики.md"  # C3: применимые законы
  business_rules:  "CORTEX/Бизнес-правила/00-Реестр-BR.md"     # C2+: бизнес-правила BR-*
  decisions:       "CORTEX/Решения/00-Реестр-решений-ADR.md"   # C5: ADR + PO-решения
  sa_store:        "CORTEX/SA/"                                  # смежные системные анализы
```

## 4b. Привязка ролей к коннекторам (role_bindings) — для deep-research

Семантический слой: какая роль-источник каким MCP-сервером из `.mcp.json` обслуживается.
`.mcp.json` знает «есть сервер `atlassian`», но не знает, что он играет роль `jira`/`conf`.
Эту привязку объявляем здесь. Settings (base_url/space/projects) НЕ дублируются — берутся
из секций `tracker:`/`wiki:`/`cortex:` выше.

```yaml
role_bindings:
  jira:    atlassian            # роль tracker; settings ← секция tracker:
  conf:    atlassian            # роль wiki;    settings ← секция wiki:
  code:    repowise             # свой RAG-сервер → впиши его имя (напр. my-internal-rag)
  vault:   obsidian            # локальная база знаний / Obsidian Vault; замени на имя из .mcp.json
  web:     builtin              # WebSearch / WebFetch (встроенные, не из .mcp.json)
  vision:  atlassian            # confluence_get_page_images
  compute: [playwright, serena, bash]
  # роль НЕ указана  =>  недоступна (её раздел pack → [НЕДОСТУПНО])
```

Кастом-коннектор с нестандартными tool-именами/якорем — развёрнутая форма:

```yaml
role_bindings:                 # пример — развёрнутая форма одной роли, не копируй целиком
  code:
    mcp:    my-internal-rag     # имя сервера из .mcp.json
    tools:  [rag_query, rag_context]
    anchor: symbol_id
```

Подключить новый источник (D): добавь сервер в `.mcp.json` + одну строку сюда. Скиллы не трогаются.

## 4c. Минимум источников по классу (source_policy) — governance

Обязательные роли для класса исследования. Deep-research сверяет `required ∩ available`;
недостающую required-роль — warn/block (по `on_missing_required`) + явно в coverage-matrix.

```yaml
source_policy:
  on_missing_required: warn     # warn (продолжить, флаг в pack) | block (СТОП со списком)
  classes:
    bft-critical:  [jira, conf] # список = required-роли; /bft-context-gen-deep
    bft-normal:    [jira]       # /bft-context-gen (быстрый)
    research-deep: [jira, conf] # /po-research deep
    research-fast: [jira]       # /po-research fast
```

Роль из `required` отсутствует в `role_bindings` или сервер не отвечает → срабатывает политика.

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
  current_quarter: "2026Q3"
```

---

## Как команды используют профиль

1. Каждая команда на «Этапе 1: Загрузка контекста» читает `.claude/domain-profile.md`.
2. Все пути в инструкциях команды (`{planning_root}`, `{okr_workspace}`, …) резолвятся из секции `paths`.
3. Доменные примеры в SKILL/examples — иллюстративные (предметная область автора шаблона). Команда опирается на **профиль проекта**, а не на примеры.
4. Поле профиля пустое → дефолт + пометка `[УТОЧНИТЬ]` в артефакте. Профиль не отменяет требование источника на каждый факт.
