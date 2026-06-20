# Spec — PAF Team OS (коробочное решение)

> **Цель:** превратить репозиторий AI-KORTEX в дистрибутивный git-template — «коробку», которую любая команда клонирует, проходит LLM-setup (`/paf-init`) и ведёт продуктовый процесс + разработку по методологии **PAF** (https://productframework.ru/ops/main, Тихомиров С., CC BY-SA 4.0).
> **Status:** design approved 2026-06-21. → `writing-plans`.
> **Ground:** построен vault (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES) + Cortex (6 агентов, `.claude/agents/`) + Nexus schema (`sa_documentation/nexus_schema.md`) + ruflo MCP (`.mcp.json`, Phase 2-complete). Коробка ≈ 90% готова; этот spec покрывает недостающие ~10%: setup-визард, разделение справочник/работа, дистрибуция.

---

## 1. Решения (зафиксированы)

| Развилка | Решение |
|---|---|
| Форм-фактор | **Git template + LLM setup-агент** (`/paf-init` skill). Не CLI. |
| Стек | **Claude Code обязателен**; Obsidian рекомендован; ruflo MCP опционален (graceful degradation: без ruflo агенты fallback на Grep). |
| Рабочая область | **Отдельная `WORKSPACE/`** — живой продукт-Nexus команды. Справочные слои (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES/sa_documentation) — read-only методология. |
| Дистрибуция | Эволюция текущего репо в box (не новый репо). |
| Лицензия | Методология PAF = **CC BY-SA 4.0**; код (агенты, scripts, paf-init) = **MIT**. |

---

## 2. Поток входа команды

```
1. git clone <paf-team-os>         (или Use this template)
2. открыть папку в Claude Code
3. /paf-init                        ← LLM-визард (skill)
     интервью → генерация WORKSPACE/ → первый Pulse
4. готово к Step 1 → AI-PROCESSES/STEP-1-IDEA/overview (или /paf-step-1, будущий)
```

---

## 3. `/paf-init` — setup-визард

**Форма:** Claude Code skill → `.claude/skills/paf-init/SKILL.md`. Команда вводит `/paf-init`, Claude ведёт диалог и генерирует артефакты.

### 3.1 Интервью (вопросы собираются диалогом, не одной формой)
1. Компания (имя).
2. Продукт: название + elevator pitch (идея).
3. Размер команды.
4. Кто **Product Engineer** (единственная обязательная роль PAF [S1] III.2).
5. (опц.) Другие роли — Product Ops / Growth Engineer / Portfolio Manager / Discovery-Launcher PM / AI UX Designer — кто или «Cortex (Claude) совмещает».
6. Целевая **Cortex-фаза** зрелости: 1 (ассистент) / 2 (проводник + RAG) / 3 (event-driven, future).
7. (опц.) Существующий контент для сидирования (документы, ссылки, интервью) — старт не с пустого Nexus.

### 3.2 Что генерирует (артефакты в `WORKSPACE/`)
- **`WORKSPACE/config.yaml`** — параметры команды/продукта (schema в §4).
- **`WORKSPACE/NEXUS/`** — 4 пустых Нексуса (`market/`, `customer/`, `product/`, `growth/`) со структурой Node schema + по одному шаблонному узлу-placeholder в каждом + `NEXUS/_index.md` (MOC).
- **`WORKSPACE/PULSE/01-pulse.md`** — первый Progress Pulse (snapshot: 4 Нексуса пустые, CR≈0; гэп = «есть идея, нет валидации»; intent = Step 1; стартовый CP низкий).
- **(если ruflo MCP жив)** продукт-namespace в `config.yaml` (`ruflo.namespace: <slug>`); `nexus-builder`/`memory_store` готовы к записи.
- **Финальный ответ**: readiness-отчёт (4 критерия STEP-0 → PASS для продукта) + «Готово → Step 1».

### 3.3 Гвардраилы paf-init
- **Idempotent**: если `WORKSPACE/config.yaml` уже есть — предупредить, не затирать без подтверждения.
- **Detect ruflo MCP**: проверить доступность `mcp__ruflo__memory_stats`; выставить `config.yaml: cortex.ruflo_mcp: true|false`. Без ruflo — заметка в INSTALL-стиле «RAG опционален, fallback Grep».
- **Ноль галлюцинаций**: paf-init НЕ выдумывает продукт-контекст; пустые Нексусы остаются пустыми (команда насыщает в Steps 1–8).

---

## 4. `WORKSPACE/config.yaml` — schema

```yaml
# Сгенерировано /paf-init. Редактируется командой.
company: <имя>
product:
  name: <название>
  slug: <ascii-slug>        # → ruflo namespace, node_id prefix (напр. "acme-billing")
  idea: <elevator pitch>
team:
  size: <N>
  roster:
    product_engineer: <человек>          # обязательно
    product_ops: <человек | "Cortex">
    growth_engineer: <... | "Cortex">
    portfolio_manager: <... | "Cortex" | null>
    discovery_launcher_pm: <... | null>
    ai_ux_designer: <... | null>
cortex:
  phase_target: 2          # 1 | 2 | 3
  ruflo_mcp: true          # auto-detected
  obsidian: true           # recommended
created: 2026-06-21
paf_step: 0                # текущий шаг (растёт 0→8 по мере прохождения)
```

---

## 5. Структура репо (box layout)

```
paf-team-os/
├── README.md              ← что это + quickstart (clone → /paf-init)
├── INSTALL.md             ← prerequisites + шаги + troubleshooting
├── LICENSE                ← CC BY-SA (методология) + MIT (код)
├── .gitignore             ← .claude/*.db, .swarm/, .DS_Store (есть)
├── .mcp.json              ← ruflo MCP (есть; опц., team approves)
├── .claude/               ← ДВИЖОК (engine)
│   ├── agents/            ← 6 Cortex-агентов (есть)
│   ├── skills/paf-init/   ← НОВОЕ: setup-визард
│   └── CORTEX.md          ← (есть)
├── AI-PROCESSES/          ← СПРАВОЧНИК: 9-шаговый фреймворк (read-only)
├── AI-TRANSFORMATION/     ← СПРАВОЧНИК: почему (read-only)
├── TRADITIONAL/           ← СПРАВОЧНИК: классические методы RB-STEP (read-only)
├── sa_documentation/      ← СПРАВОЧНИК: nexus_schema, naming, nexus_index.py (read-only)
└── WORKSPACE/             ← ЖИВАЯ РАБОТА КОМАНДЫ (НОВОЕ; init'ится /paf-init)
    ├── README.md          ← «здесь ваш продукт-Nexus; /paf-init»
    ├── config.yaml        ← (генерируется)
    ├── NEXUS/             ← empirical узлы продукта (market/customer/product/growth)
    ├── PULSE/             ← Progress Pulse логи по шагам
    ├── BUNCH/             ← Банч-артефакты
    └── RESULTS/           ← Harvesting (NPV, PMF, фиксации)
```

**Правка справочника:** команды НЕ должны править AI-PROCESSES/AI-TRANSFORMATION/TRADITIONAL/sa_documentation — это канон PAF (read-only). Их продукт-контекст — только в `WORKSPACE/`. Wiki-links работают (Obsidian резолвит по имени ноты; ссылки из WORKSPACE → AI-PROCESSES ведут к методу).

**Template vs fork:** template шлёт `WORKSPACE/` пустым (skeleton + README placeholder, tracked). Команда клонирует → `/paf-init` заполняет → команда коммитит свой WORKSPACE в свой fork. `WORKSPACE/` НЕ gitignored (это работа команды). `.claude/memory.db` — gitignored (регенерируется).

---

## 6. Graceful degradation

| Компонент | Без него | Поведение |
|---|---|---|
| Claude Code | — | ОБЯЗАТЕЛЕН (setup-агент + Кортекс). |
| Obsidian | нет графического vault/wiki-link рендера | vault = markdown, любой редактор. Cortex/агенты работают (читают файлы). |
| ruflo MCP | нет semantic RAG | агенты fallback на Grep (structured frontmatter). `nexus_index.py` пропускается. `/paf-init` ставит `ruflo_mcp: false`. |

INSTALL.md документирует все 3 уровня.

---

## 7. Лицензия + credits

- **Методология PAF** (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES текст, термины, принципы) → **CC BY-SA 4.0**, автор Сергей Тихомиров (productframework.ru). README — явный credit + ссылка.
- **Код** (`.claude/agents/*`, `sa_documentation/nexus_index.py`, `.claude/skills/paf-init/*`) → **MIT**.
- `LICENSE` — dual: файл-заглушка с разъяснением какой слой под какой лицензией.

---

## 8. Scope сборки (что создать)

1. **`.claude/skills/paf-init/SKILL.md`** (+ вспомогательные) — setup-визард: интервью-логика + bootstrap-процедура (§3) + readiness-отчёт.
2. **`WORKSPACE/` skeleton** — `README.md` placeholder + пустые `NEXUS/`(4 поддиректории + template-узлы + `_index.md`), `PULSE/`, `BUNCH/`, `RESULTS/` (с `.gitkeep`).
3. **`WORKSPACE/config.yaml` schema** — задокументировать (§4); paf-init генерирует.
4. **`README.md`** (переписать верхний) — что это, quickstart, credits PAF.
5. **`INSTALL.md`** — prerequisites (Claude Code обязат./Obsidian реком./ruflo опц.), шаги, troubleshooting (MCP approval, ruflo path).
6. **`LICENSE`** — dual CC BY-SA + MIT.
7. **Адаптация Cortex под продукт-namespace**: `nexus-builder`/`scouting`/`bunch-former` — читать `WORKSPACE/config.yaml` → ruflo namespace продукта (вместо хардкода `ai-kortex`); если ruflo нет — Grep по `WORKSPACE/NEXUS/`.
8. **`nexus_schema.md`** — секция «empirical узлы продукта» (поля для kind:empirical: гипотезы/интервью/метрики; ttl короче).

---

## 9. Out of scope (YAGNI)
- CLI-установщик (`npx ...`) — отказано в пользу template+skill.
- Multi-product per clone — один `WORKSPACE/` на продукт; новый продукт → новый fork.
- Neo4j / Phase 3 (event-driven, swarm) — будущая работа.
- Хостинг/marketplace — только git.
- `/paf-step-N` агенты для каждого шага — будущая UX (сейчас команды идут по AI-PROCESSES/overview).
- i18n — только русский (matching PAF source).

---

## 10. Готовность = определение «done»
Коробка готова, когда новая команда (никогда не видевшая репо) может за ≤30 мин:
1. `git clone` + открыть в Claude Code.
2. Запустить `/paf-init` → ответить на интервью → получить инициализированный `WORKSPACE/`.
3. Прочитать readiness-отчёт (4 критерия STEP-0 → PASS) + «Готово → Step 1».
4. Открыть `AI-PROCESSES/STEP-1-IDEA/overview` и начать Product Sprint с Кортексом над своим Nexus.

---

## 11. Риски
- **ruflo MCP registration quirk** (plugin vs mcpServers) — INSTALL даёт чёткий фикс (`.mcp.json` approval + restart); без ruflo коробка всё равно работает (degradation).
- **Команды правят справочник** — README/WORKSPACE-README явно: «методология read-only, работа в WORKSPACE/».
- **paf-init выдумывает контент** — гвардраил: пустые Нексусы остаются пустыми; /paf-init только структура + config + первый Pulse.
- **LLM-вариативность интервью** — skill фиксирует ОБЯЗАТЕЛЬНЫЕ поля config.yaml; опциональные — на усмотрение диалога.

---
**Version:** 1.0 · **Approved:** 2026-06-21 · **Next:** `writing-plans` → implementation plan.
