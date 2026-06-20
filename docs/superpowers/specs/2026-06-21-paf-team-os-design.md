# Spec — PAF Team OS (коробочное решение) · v2 (GROUND Vault + онбординг)

> **Цель:** дистрибутивный git-template. Команда/клиент клонирует → инструменты + **подробный онбординг** цифровизуют существующий контекст клиента в **GROUND Vault** (персонализированный, насыщенный Нексус) → дальше ведут продуктовый процесс + разработку по **PAF** (https://productframework.ru/ops/main, Тихомиров С., CC BY-SA 4.0).
> **Рефрейм v2 (от клиента):** центр тяжести коробки — **онбординг**, который наполняет Нексусы **правильным контекстом** и **цифровизует его для работы с ИИ**. Не «пустой workspace», а насыщенный GROUND Vault.
> **Status:** design v2 approved 2026-06-21. → `writing-plans`.
> **Ground:** построены vault (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES) + Cortex (6 агентов, `.mcp/agents/`) + Nexus schema (`sa_documentation/nexus_schema.md`) + ruflo MCP (`.mcp.json`, Phase 2-complete).

---

## 1. Решения (зафиксированы)

| Развилка | Решение |
|---|---|
| Форм-фактор | **Git template + LLM-агенты** (`/paf-init`, `/paf-onboard`). Не CLI. |
| Стек | **Claude Code обязателен**; Obsidian рекомендован; ruflo MCP опционален (graceful degradation). |
| Рабочая область | **GROUND Vault** (`GROUND/`) — персонализированный под клиента волт с насыщенным Нексусом. Справочные слои (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES/sa_documentation) — read-only методология. |
| **Онбординг — механизм** | **Гибрид**: ингестия существующих доков клиента → Cortex парсит+структурирует → управляемое интервью заполняет пробелы + верифицирует. |
| **Онбординг — глубина/CP** | Цифровизация ВСЕХ существующих знаний по 4 Нексусам как **low-CP допущений** (`kind:empirical`, `sources=["onboarding"]`, `confidence: 0.2–0.4`). Формальные **Steps 1–8 валидируют** и поднимают CP. GROUND = насыщенный, но невалидированный. |
| Дистрибуция | Эволюция текущего репо в box. |
| Лицензия | Методология PAF = **CC BY-SA 4.0**; код = **MIT**. |

---

## 2. Поток входа клиента

```
1. git clone <paf-team-os>                (или Use this template)
2. открыть в Claude Code
3. /paf-init                              ← конфиг + структура GROUND (one-shot)
     компания / продукт / команда / роли / Cortex-фаза → GROUND/config.yaml + пустой каркас
4. /paf-onboard                           ← ПОДРОБНЫЙ ОНБОРДИНГ (главное; repeatable)
     Phase A: ингестия доков клиента (GROUND/_intake/) → Cortex парсит → узлы Нексуса
     Phase B: управляемое интервью по 4 Нексусам → заполнение пробелов
     Phase C: верификация + простановка low-CP + anti-workslop
     → GROUND Vault насыщен (baseline Context Ripeness)
5. готово → Steps 1–8 (насыщенный Нексус, теперь ВАЛИДИРУЕМ и поднимаем CP)
```

> `/paf-init` = быстрая setup-настройка (one-shot). `/paf-onboard` = подробная цифровизация контекста (повторяемо — клиент может подкидывать новые доки). Онбординг — центр коробки.

---

## 3. `/paf-init` — конфиг + структура GROUND (one-shot)

**Форма:** skill → `.claude/skills/paf-init/SKILL.md`.

**Интервью (быстро):** компания · название продукта + slug · elevator pitch · размер команды · кто Product Engineer · (опц.) др. роли · целевая Cortex-фаза (1/2/3) · (опц.) существующий контент для `_intake/`.

**Генерирует:**
- `GROUND/config.yaml` (schema §6).
- `GROUND/` skeleton: `_intake/` (клиент кладёт доки), `NEXUS/` (4 пустых Нексуса + `_index.md`), `PULSE/`, `BUNCH/`, `RESULTS/`.
- (опц.) первый `PULSE/00-init-pulse.md` (snapshot пустого → intent = онбординг).
- **Detect ruflo MCP** → `config.yaml: cortex.ruflo_mcp`. **Idempotent** (не затирать существующий config).
- Финал: «Конфиг готов → запусти `/paf-onboard` для цифровизации контекста».

---

## 4. `/paf-onboard` — подробная цифровизация контекста (главное; repeatable)

**Форма:** skill → `.claude/skills/paf-onboard/SKILL.md`. Ведёт Cortex-агентами (`scouting`, `nexus-builder`, `cp-scorer`).

### Phase A — ингестия доков клиента
- Клиент кладёт материалы в `GROUND/_intake/` (доки, презы, PRD, research, заметки, URLs).
- `scouting` + `nexus-builder` парсят каждый → извлекают факты/гипотезы → создают узлы Нексуса (`kind:empirical`, `sources=["onboarding:<doc>"]`).
- Дедуп через `mcp__ruflo__memory_search` (ruflo) или Grep (без ruflo).

### Phase B — управляемое интервью (заполнение пробелов)
LLM ведёт структурированное интервью по 4 Нексусам (только пробелы после Phase A):
- **market**: кто рынок, объём, конкуренты, тренды, Ставки.
- **customer**: сегменты, JTBD, боли, mNSM-гипотеза.
- **product**: идея, фичи, Vision, гэп.
- **growth**: каналы, модель, ограничения, AI-COGS (если AI-продукт).
Ответы → узлы (`sources=["onboarding:interview"]`).

### Phase C — верификация + CP + anti-workslop
- `cp-scorer` простанавливает **low-CP** всем онбординг-узлам: `confidence: 0.2–0.4` (допущение, не валидировано).
- **Anti-workslop гейт:** ни один онбординг-узел не маркируется как факт/валидированный. Явная пометка в теле: `> ⚠️ допущение клиента (онбординг), требует валидации в Steps 1–8`.
- (если ruflo) индекс GROUND-узлов в продукт-namespace.

### Phase D — readiness-отчёт GROUND Vault
- Context Ripeness по 4 Нексусам (baseline из покрытия; freshness высокий, CP низкий).
- Карта: что насыщено / где главные пробелы / top low-CP узлы для приоритетной валидации.
- Финал: «GROUND Vault насыщен → готов к Steps 1–8. Сейчас ВАЛИДИРУЕМ (Step 1 Idea → интервью/эксперименты → поднимаем CP)».

---

## 5. CP-дисциплина (критично) [S1] Принцип 4, [S2] III.7

| Источник узла | `kind` | `confidence` | Валидация |
|---|---|---|---|
| Онбординг (доки/интервью клиента) | empirical | **0.2–0.4** (допущение) | Steps 1–8: интервью/эксперименты → растёт |
| Steps 1–8 (валидировано) | empirical | 0.5–1.0 (по доказательствам) | CP растёт от новой информации |
| Методология PAF (справочник) | normative | 1.0 (трассируется до [S1]–[S4]) | — |

> **Принцип:** онбординг цифровизует, **не валидирует**. GROUND Vault = насыщенный, но low-CP. Не выдавать допущения клиента за факты (workslop). CP поднимают Steps 1–8 через реальные интервью/эксперименты. `wilting-detector` следит за CP/ripeness.

---

## 6. `GROUND/config.yaml` — schema

```yaml
company: <имя>
product:
  name: <название>
  slug: <ascii-slug>          # → ruflo namespace, node_id prefix
  idea: <elevator pitch>
team:
  size: <N>
  roster:
    product_engineer: <человек>            # обязательно
    product_ops: <человек | "Cortex">
    growth_engineer: <... | "Cortex">
    portfolio_manager: <... | "Cortex" | null>
    discovery_launcher_pm: <... | null>
    ai_ux_designer: <... | null>
cortex:
  phase_target: 2            # 1 | 2 | 3
  ruflo_mcp: true            # auto-detected at /paf-init
  obsidian: true             # recommended
onboarding:
  status: init               # init | in-progress | done
  sources_ingested: []       # список доков в _intake/ (Phase A)
  baseline_cr: {}            # Context Ripeness по Нексусам после онбординга
  onboarded_at: null         # дата завершения Phase D
created: 2026-06-21
paf_step: 0                  # текущий шаг (0=онбординг, потом 1→8)
```

---

## 7. Структура репо (box layout)

```
paf-team-os/
├── README.md · INSTALL.md · LICENSE · .gitignore · .mcp.json
├── .claude/                 ← ДВИЖОК (engine)
│   ├── agents/              ← 6 Cortex-агентов (есть)
│   ├── skills/
│   │   ├── paf-init/        ← НОВОЕ: конфиг + структура GROUND
│   │   └── paf-onboard/     ← НОВОЕ: цифровизация контекста (главное)
│   └── CORTEX.md            ← (есть)
├── AI-PROCESSES/            ← СПРАВОЧНИК: 9-шаговый фреймворк (read-only)
├── AI-TRANSFORMATION/       ← СПРАВОЧНИК: почему (read-only)
├── TRADITIONAL/             ← СПРАВОЧНИК: классические методы RB-STEP (read-only)
├── sa_documentation/        ← СПРАВОЧНИК: nexus_schema, naming, nexus_index.py (read-only)
└── GROUND/                  ← GROUND VAULT: персонализированный волт клиента (НОВОЕ)
    ├── README.md            ← «здесь ваш контекст; /paf-init → /paf-onboard»
    ├── config.yaml          ← (генерируется /paf-init)
    ├── _intake/             ← клиент кладёт доки для онбординга (Phase A)
    ├── NEXUS/               ← empirical узлы продукта (market/customer/product/growth)
    ├── PULSE/               ← Progress Pulse логи
    ├── BUNCH/               ← Банч-артефакты
    └── RESULTS/             ← Harvesting (NPV, PMF, фиксации)
```

**Правка справочника запрещена** — AI-PROCESSES/AI-TRANSFORMATION/TRADITIONAL/sa_documentation = канон PAF (read-only). Контекст клиента — только в `GROUND/`. Wiki-links работают (Obsidian резолвит по имени ноты).

**Template vs fork:** template шлёт `GROUND/` пустым (skeleton + README, tracked). Клиент клонирует → `/paf-init` → `/paf-onboard` → коммитит свой GROUND в свой fork. `GROUND/` НЕ gitignored (это контекст клиента). `.claude/memory.db`, `.swarm/` — gitignored.

---

## 8. Graceful degradation

| Компонент | Без него | Поведение |
|---|---|---|
| Claude Code | — | ОБЯЗАТЕЛЕН (онбординг + Кортекс). |
| Obsidian | нет графического vault/wiki-link рендера | vault = markdown, любой редактор. Онбординг/Cortex работают. |
| ruflo MCP | нет semantic RAG | `paf-onboard`/агенты fallback на Grep (structured). Дедуп/поиск по смыслу слабее. `config.yaml: cortex.ruflo_mcp: false`. |

INSTALL.md документирует все 3 уровня.

---

## 9. Лицензия + credits
- **Методология PAF** (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES, термины, принципы) → **CC BY-SA 4.0**, автор Сергей Тихомиров (productframework.ru). README — явный credit + ссылка.
- **Код** (`.claude/agents/*`, `.claude/skills/*`, `sa_documentation/nexus_index.py`) → **MIT**.
- `LICENSE` — dual с разъяснением слоёв.

---

## 10. Scope сборки (что создать)

1. **`.claude/skills/paf-init/SKILL.md`** — конфиг + структура GROUND (§3).
2. **`.claude/skills/paf-onboard/SKILL.md`** — подробная цифровизация контекста (§4): Phase A ингестия, B интервью, C verify/CP, D readiness. Главный skill.
3. **`GROUND/` skeleton** — `_intake/`, `NEXUS/`(4 поддиректории + template empirical-узлы + `_index.md`), `PULSE/`, `BUNCH/`, `RESULTS/` (с `.gitkeep` + README).
4. **`GROUND/config.yaml` schema** — задокументировать (§6); paf-init генерирует, paf-onboard обновляет (`onboarding.*`).
5. **`README.md`** (верхний) — что это, quickstart (clone → /paf-init → /paf-onboard → Steps), credits PAF.
6. **`INSTALL.md`** — prerequisites (Claude Code обязат./Obsidian реком./ruflo опц.), шаги, troubleshooting (MCP approval, ruflo path, _intake/).
7. **`LICENSE`** — dual CC BY-SA + MIT.
8. **Cortex адаптация под продукт-namespace** — `nexus-builder`/`scouting`/`bunch-former`/`cp-scorer` читают `GROUND/config.yaml` → ruflo namespace продукта + корень `GROUND/NEXUS/` (вместо хардкода `ai-kortex`/`AI-PROCESSES`). Grep fallback по `GROUND/NEXUS/`.
9. **`nexus_schema.md`** — секция «empirical узлы клиента» (kind:empirical, onboarding-source, low-CP по умолчанию, ttl короче).
10. **Онбординг-интервью скрипт/шаблон** — структурированные вопросы по 4 Нексусам (Phase B) как артефакт в `paf-onboard/`.

---

## 11. Out of scope (YAGNI)
- CLI-установщик; multi-product per clone; Neo4j / Phase 3 (event-driven, swarm); hosting/marketplace; `/paf-step-N` агенты; i18n.

## 12. Готовность = «done»
Коробка готова, когда НОВЫЙ клиент за ≤1 рабочий день:
1. `git clone` + открыть в Claude Code.
2. `/paf-init` → конфиг + структура GROUND.
3. `/paf-onboard` → закинул доки в `_intake/`, прошёл интервью → GROUND Vault насыщен (4 Нексуса с low-CP узлами, baseline Context Ripeness).
4. Прочитал readiness-отчёт + карту пробелов → понимает, что валидировать в Steps 1–8.
5. Открыл `AI-PROCESSES/STEP-1-IDEA/overview` → начал Product Sprint с Кортексом над насыщенным GROUND Nexus.

## 13. Риски
- **Онбординг = workslop-зона №1** (допущения клиента как «контекст»). **Контрмера:** low-CP + явная пометка «допущение, требует валидации» + `cp-scorer` гейт (§5).
- **ruflo MCP registration quirk** — INSTALL даёт фикс; без ruflo коробка работает (degradation).
- **Клиент правит справочник** — README/GROUND-README: «методология read-only, работа в GROUND/».
- **Пере-онбординг затирает** — `/paf-onboard` idempotent: дедуп + upsert (не дублировать/не затирать валидированные узлы без подтверждения).
- **Объём онбординга** — Phase B интервью модульное (по Нексусам), можно паузить/возобновлять; не один монолитный диалог.

---
**Version:** 2.0 · **Approved:** 2026-06-21 · **Next:** `writing-plans` → implementation plan (10 scope items).
