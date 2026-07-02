---
title: Контекст внешних команд — OKR landscape → BFT
date: 2026-07-01
status: approved
branch: patch/okr-external-team-context
---

# Контекст внешних команд вокруг PO (OKR landscape → BFT)

## Проблема

При квартальном планировании и при написании БФТ у LLM нет структурированного
контекста «что делают команды вокруг нашего PO». Единственный след
кроссфункциональных зависимостей сегодня — тег `[EXT]` на отдельных шагах
«Образа действия» (`okr_standards.md`), который помечает *шаг*, но не описывает
*команду*: кто она, чем занята в квартале, какие системы держит, где точки
касания с нами, через что мы можем на неё влиять — прямо или косвенно.

Из-за этого при формировании БФТ-требований нельзя точно ответить на вопрос:
«Я разрабатываю эту задачу — с PO каких команд я могу быть связан и почему».
Блокаторы и связи всплывают поздно, уже на исполнении.

## Образ результата

1. При OKR-планировании появляется отдельная стадия-роль (LLM-«команда»),
   которая заполняет контекст окружающего ландшафта: «мы делаем X» vs
   «команды вокруг делают Y».
2. При написании БФТ отдельный этап аналитики читает этот контекст и выдаёт
   артефакт `external-teams-actions.md` — «эта задача связывает меня с PO
   команд A/B по таким-то причинам, прямо/косвенно».
3. Знание накапливается между кварталами, а не собирается с нуля каждый раз.

## Ключевые решения (зафиксированы с PO)

| # | Решение | Выбор |
|---|---|---|
| 1 | Источник истины | **Гибрид**: постоянный GROUND-Нексус + per-quarter снимок; BFT читает снимок |
| 2 | Модель в GROUND | **Новый Нексус `landscape`** (`node_type: ext-team`), отдельно от People-Graph `team` |
| 3 | Размещение в OKR | **Новая стадия `/okr-landscape`** между context-gen и objectives, STOP-пауза |
| 4 | Встраивание в BFT | **Новая команда `/bft-ext-teams`** между context-gen и problem, свой артефакт |
| 5 | Объём итерации | **Полный**: ядро + OKR enrich/validate-гейт + BFT problem/draft + GROUND scaffold |

## Архитектура и поток данных

Три слоя: стабильное знание → снимок квартала → проекция на эпик.

```
GROUND/NEXUS/landscape/         ПОСТОЯННОЕ знание
  ext-team узлы: кто, PO, mission, owned_systems, relationship, touchpoints, influence
        │  (читает + дополняет)
        ▼
/okr-landscape <quarter>  ──►  {okr_workspace}/landscape-{quarter}.md   СНИМОК КВАРТАЛА
  §1 «мы в квартале»  §2 «команды вокруг + их OKR/фокус»  §3 матрица  §4 [УТОЧНИТЬ]
        │  (feeds)                                   │
        ▼                                            ▼
  /okr-objectives, /okr-enrich, /okr-validate   /bft-ext-teams <epic>
                                                     │
                                                     ▼
                                artefacts/external-teams-actions.md   ПРОЕКЦИЯ НА ЭПИК
                                причина связи (таксономия) · direct/indirect · действие
                                                     │
                                                     ▼
                                      /bft-problem, /bft-draft (цитируют)
```

**Разделение ответственности слоёв:**
- **Persistent node** — стабильные факты: кто команда, какие системы держит, тип
  связи с нами. Переживает кварталы.
- **Snapshot** — что команда делает именно в этом квартале + свежесть + релевантность
  к нашим OBJ/KR. Текущий OKR внешней команды НЕ пишется в узел — он квартальный.
- **Проекция на эпик** — что из ландшафта релевантно конкретному БФТ + причина связи.

Принцип нулевого допуска сохраняется: каждый факт ← источник (интервью PO / их
OKR / Confluence / JIRA / вывод из C1-архитектуры), иначе `[УТОЧНИТЬ у {кого}]`.
Вывод LLM помечается явно и отделяется от факта.

## Компонент 1 — GROUND Нексус `landscape`

Новый custom-Нексус, регистрируется в `GROUND/NEXUS/_registry.yaml` рядом с `team`.
Разграничение: `team` = наши люди внутри (People Graph, `node_type: person`),
`landscape` = команды вокруг (`node_type: ext-team`).

Файлы: `GROUND/NEXUS/landscape/_template.md`, `_index.md`, `.gitkeep`.

Схема узла (`schema_extensions`), помимо стандартных полей Нексуса
(`node_id`, `kind`, `owner`, `confidence`, `sources`, `updated`, `ttl_days`,
`ripeness`, `tags`):

```yaml
node_id: landscape-team-<slug>      # ascii-slug, напр. landscape-team-payments
node_type: ext-team

team_name: "Название команды"
po_name: "Имя PO"                    # ссылка [[team-...]] если PO есть в People Graph
po_channels:                         # как связаться с PO
  - "Slack: @handle"
mission: >                           # что делает команда, 1–2 фразы
  ...
owned_systems:                       # сервисы/системы во владении (имена из C1-архитектуры)
  - "Система X"
relationship: upstream               # upstream | downstream | peer | platform | regulator
                                     #   (относительно нашей команды)
touchpoints:                         # точки касания с нами
  - "общий сервис / API / поток данных / общий стейкхолдер"
influence: direct                    # direct (прямой стык) | indirect (через посредника)
collaboration_history: >             # опц.: прошлый совместный опыт
  ...
```

`confidence` (CP) трактуется как у всех Нексус-узлов: 0.2–0.4 допущение
онбординга, 0.6–0.8 подтверждено, 0.9–1.0 верифицировано несколькими источниками.

## Компонент 2 — Секция `landscape` в domain-profile

Добавляется в `domain-profile.template.md`:

```yaml
landscape:
  nexus_root:      "GROUND/NEXUS/landscape"      # узлы внешних команд
  snapshot_doc:    "{okr_workspace}/landscape-{quarter}.md"
  bft_artifact:    "external-teams-actions.md"   # имя проекции в artefacts/ эпика
  ext_teams:                                      # засев (bootstrap Нексуса)
    - { code: "TEAM-PAY", name: "Платежи", po: "Имя", relationship: "upstream" }  # пример
```

Поле пустое → команда работает на дефолте и помечает `[УТОЧНИТЬ]`.

## Компонент 3 — `/okr-landscape <quarter>` (роль: Landscape Analyst)

Новая стадия OKR-пайплайна между стадией 0 и 1:
`context-gen → landscape → objectives`.

Вход: `context-pack.md` (стадия 0). Выход: `{okr_workspace}/landscape-{quarter}.md`
+ обновлённые узлы `GROUND/NEXUS/landscape/`.

Процесс:
1. Загрузка роли/стандартов + чтение GROUND `landscape` Нексуса, context-pack,
   годового roadmap, C1-архитектуры (кто владеет смежными системами), при
   доступе — JIRA cross-project эпиков.
2. Опрос PO **по одному вопросу за раз** про каждую команду вокруг: чем заняты
   в квартале, где точки касания, кто может блокировать/усиливать.
3. Дополняет/обновляет узлы Нексуса (новые команды, изменение CP/фактов).
4. Пишет снимок `landscape-{quarter}.md`:
   - **§1 «Наша команда в квартале»** — из context-pack/objectives («что делаем мы»).
   - **§2 «Команды вокруг»** — таблица: команда · PO · OKR/фокус квартала (источник)
     · тип связи · релевантность к нашим OBJ/KR · флаги `[RISK]`/`[BLOCKER]`/`[EXT]`.
   - **§3 Матрица покрытия** · **§4 Открытые вопросы `[УТОЧНИТЬ]`**.
5. STOP-пауза → PO ревьюит снимок. Дальше → `/okr-objectives`.

Запреты: не формулировать OBJ/KR на этой стадии; факт без источника → `[УТОЧНИТЬ]`;
JIRA недоступна → `[НЕДОСТУПНО]`, не выдумывать чужой беклог.

## Компонент 4 — `/bft-ext-teams <epic>` (роль: Dependency Analyst)

Новая стадия BFT-пайплайна между `/bft-context-gen` и `/bft-problem`.

Вход: quarter-снимок `landscape-{quarter}.md` + GROUND `landscape` Нексус + scope
эпика (из `bft-context-pack.md` / JIRA). Выход:
`bft_documentation/<epic>/artefacts/external-teams-actions.md`.

### Таксономия причин связи (смысловое ядро)

Почему разработчик задачи может быть связан с PO внешней команды:
1. **Общая система/компонент** — обе команды меняют один сервис.
2. **Зависимость по данным** — потребляем/поставляем данные во владении команды.
3. **Интеграционный контракт / API** на стыке.
4. **Последовательная зависимость roadmap** — их KR блокирует/включает наш.
5. **Общая регуляторика / compliance-поверхность**.
6. **Общий стейкхолдер / ресурс / люди**.
7. **Косвенное влияние (2-й порядок)** — рябь через посредника.

`influence`: `direct` (прямой стык) vs `indirect` (через посредника).

### Формат `external-teams-actions.md`

На каждую релевантную команду:
`команда · PO · причина (категория 1–7 + конкретика) · direct/indirect · чем заняты
в квартале (из снимка) · потенциальный блокер/синергия · рекомендованное действие
(«согласовать с PO X до …») · якорь-источник`.
Плюс раздел «Открытые вопросы `[УТОЧНИТЬ]`». STOP-пауза.

Если снимка квартала нет → честно `[УТОЧНИТЬ: нет landscape-снимка, запусти
/okr-landscape]`, работать с GROUND-Нексусом, что есть.

## Компонент 5 — Интеграция в существующие стадии

- **`/okr-enrich`** — в «Образ действия» шаг `[EXT]` связывается с конкретной
  командой из снимка (не абстрактный «внешний»).
- **`/okr-validate`** — новый hard-gate: KR с `[EXT]`/внешней зависимостью → эта
  команда обязана присутствовать в landscape-снимке, иначе 🔴.
- **`/bft-problem`, `/bft-draft`** — читают `external-teams-actions.md`; зависимости
  и стейкхолдеры в требованиях цитируют конкретные внешние команды/PO.
- **`/paf-nexus-create`** — знает каталожный тип `landscape`, засевает узлы из
  `domain-profile.landscape.ext_teams` (как `team` засевается из roster).

## Затрагиваемые файлы

**Новые:**
- `.claude/commands/okr-landscape.md`
- `.claude/commands/bft-ext-teams.md`
- `GROUND/NEXUS/landscape/_template.md`, `_index.md`, `.gitkeep`

**Правки:**
- `GROUND/NEXUS/_registry.yaml` — регистрация `landscape`
- `domain-profile.template.md` — секция `landscape`
- `.claude/skills/okr-planner/SKILL.md` — pipeline-схема + таблица ролей + стадия
- `.claude/skills/okr-planner/resources/okr_standards.md` — структура снимка
- `.claude/skills/okr-planner/resources/hard_gates.md` — новый гейт
- `.claude/commands/okr-context-gen.md` — указание next → landscape
- `.claude/commands/okr-enrich.md`, `okr-validate.md`
- `.claude/skills/bft-writer/SKILL.md` — pipeline + таблица ролей + стадия
- `.claude/skills/bft-writer/resources/bft_standards.md` — артефакт + таксономия
- `.claude/commands/bft-context-gen.md`, `bft-context-gen-deep.md` — next → bft-ext-teams
- `.claude/commands/bft-problem.md`, `bft-draft.md` — чтение проекции
- `.claude/skills/paf-nexus-create/*` — каталожный тип `landscape`
- `README.md` — упоминание новых команд/Нексуса

## Вне объёма (YAGNI, backlog)

- Авто-синхронизация OKR внешних команд из их трекеров.
- Визуальный граф ландшафта.
- Отдельный `/landscape-sync` на cron.
- Влияние на sprint-planner.
