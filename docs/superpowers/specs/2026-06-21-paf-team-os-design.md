# Spec — PAF Team OS (коробочное решение) · v3 (расширяемый Nexus Catalog)

> **Цель:** дистрибутивный git-template. Клиент клонирует → инструменты + **подробный онбординг** цифровизуют контекст в **GROUND Vault** (персонализированный, насыщенный Нексус) → ведёт продуктовый процесс + разработку по **PAF** (https://productframework.ru/ops/main, Тихомиров С., CC BY-SA 4.0).
> **v3 (от клиента):** коробка кураторски даёт **минимально-необходимый набор Нексусов** для продуктового контекста + платформа позволяет клиенту **собирать множество кастомных Нексусов** под своё решение. Нексус-модель **расширяемая** (каталог = дефолтный минимум + кастом).
> **Status:** design v3 approved 2026-06-21. → `writing-plans`.
> **Ground:** построены vault (TRADITIONAL/AI-TRANSFORMATION/AI-PROCESSES) + Cortex (6 агентов) + Nexus schema (`sa_documentation/nexus_schema.md`) + ruflo MCP (`.mcp.json`, Phase 2-complete).

---

## 1. Решения (зафиксированы)

| Развилка | Решение |
|---|---|
| Форм-фактор | **Git template + LLM-агенты** (`/paf-init`, `/paf-onboard`, `/paf-nexus-create`). Не CLI. |
| Стек | **Claude Code обязателен**; Obsidian рекомендован; ruflo MCP опционален (graceful degradation). |
| Рабочая область | **GROUND Vault** (`GROUND/`) — персонализированный волт клиента с насыщенным Нексусом. |
| **Нексус-модель** | **Расширяемый каталог**: дефолтный минимально-необходимый набор (PAF-базлайн) + **кастомные Нексусы** клиента под его решение. Поле `nexus` открытое (любой slug). |
| Онбординг — механизм | **Гибрид**: ингестия доков → Cortex парсит+структурирует → интервью по пробелам → верификация. |
| Онбординг — глубина/CP | Цифровизация существующих знаний по **всем Нексусам каталога** как **low-CP допущений** (`confidence: 0.2–0.4`). Steps 1–8 валидируют + поднимают CP. |
| Дистрибуция | Эволюция текущего репо в box. |
| Лицензия | Методология PAF = **CC BY-SA 4.0**; код = **MIT**. |

---

## 2. Nexus Catalog (минимум + кастом) — КЛЮЧЕВАЯ ВОЗМОЖНОСТЬ v3

Модель Нексусов **расширяемая**: коробка кураторски даёт минимально-необходимый набор, клиент добавляет кастомные под своё решение.

### 2.1 Мастер-каталог платформы (`sa_documentation/nexus_catalog.md`, shipped, read-only)
Кураторский набор типов Нексусов PAF. Каждый тип = определение:
```yaml
slug: customer            # ascii
name: Нексус потребителя
purpose: сегменты, JTBD, боли, mNSM-гипотеза
owner_role: Product Engineer
paf_step_ref: 2           # какой Step насыщает
minimal: true             # минимально-необходимый (входит в дефолт)
seed_questions:           # для онбординг-интервью (Phase B)
  - Кто основные сегменты?
  - Какие работы (JTBD) нанимают?
  - Главные боли?
schema_extensions: {}     # (опц.) тип-специфичные поля поверх базовой Node schema
```

**Дефолтный минимально-необходимый набор** (`minimal: true`):
| slug | name | Step |
|---|---|---|
| `market` | Нексус рынка | 3 |
| `customer` | Нексус потребителя | 2 |
| `product` | Нексус продукта | 1,4,7 |
| `growth` | Нексус системы роста | 5,6,8 |

**Опц. PAF-типы** (`minimal: false`, клиент включается по необходимости): `ops-model` (опер.модель), `company` (портфель/компания) — PAF определяет 6 типов.

### 2.2 Каталог клиента (`GROUND/NEXUS/_registry.yaml`, генерируется)
Реестр Нексусов, **инстанцированных для данного клиента** = дефолтные (minimal) + кастомные. `/paf-init` создаёт из дефолтного минимума; `/paf-nexus-create` добавляет кастомные; `/paf-onboard` работает по всему реестру.
```yaml
# GROUND/NEXUS/_registry.yaml
nexus_types:
  - {slug: market,    source: default, onboarded: partial}
  - {slug: customer,  source: default, onboarded: partial}
  - {slug: product,   source: default, onboarded: partial}
  - {slug: growth,    source: default, onboarded: partial}
  # кастомные (добавлены /paf-nexus-create):
  - {slug: sellers,   source: custom,  name: Нексус продавцов, owner: Growth Engineer, purpose: "...", onboarded: todo}
  - {slug: buyers,    source: custom,  ...}
```

### 2.3 `/paf-nexus-create` — кастомный Нексус (skill)
Клиент: `/paf-nexus-create` → интервью (name, slug, purpose, owner из roster, seed_questions, (опц.) paf_step, (опц.) schema_extensions) → создаёт `GROUND/NEXUS/<slug>/` (`_index.md` + template) + регистрирует в `_registry.yaml` (`source: custom`) + (опц.) мини-онбординг сразу.
- Гвардраилы: slug уникальный; конфликт с дефолтными/master-каталогом — предупредить; owner должен быть из roster.

### 2.4 Открытая Node schema
Поле `nexus` в frontmatter = **открытый slug** (любой из реестра клиента), не фиксированный enum. `nexus_schema.md` обновляется: базовая schema + как определить кастомный тип (schema_extensions).

---

## 3. Поток входа клиента

```
1. git clone <paf-team-os>
2. открыть в Claude Code
3. /paf-init                         ← конфиг + GROUND + дефолтный минимальный каталог Нексусов (one-shot)
4. /paf-nexus-create (опц., repeatable) ← добавить кастомные Нексусы под решение клиента
5. /paf-onboard                      ← цифровизация контекста по ВСЕМУ реестру Нексусов (главное; repeatable)
     A: ингестия доков (GROUND/_intake/) → узлы
     B: интервью по всем Нексусам реестра (дефолт + кастом) → заполнение пробелов
     C: verify + low-CP + anti-workslop
     D: readiness-отчёт GROUND Vault
6. готово → Steps 1–8 (насыщенный Нексус, ВАЛИДИРУЕМ и поднимаем CP)
```

> Каталог Нексусов живой: клиент добавляет кастомные когда угодно (`/paf-nexus-create`), потом `/paf-onboard` наполняет и их.

---

## 4. `/paf-init` — конфиг + GROUND + дефолтный каталог (one-shot)

Skill → `.claude/skills/paf-init/SKILL.md`. Интервью: компания · продукт + slug · pitch · команда · Product Engineer · (опц.) др. роли · Cortex-фаза.
**Генерирует:**
- `GROUND/config.yaml` (§7).
- `GROUND/` skeleton: `_intake/`, `NEXUS/` с **дефолтным минимальным набором** (market/customer/product/growth — из мастер-каталога, `source: default`) + `_registry.yaml` + `_index.md`.
- `PULSE/`, `BUNCH/`, `RESULTS/`.
- (опц.) `PULSE/00-init-pulse.md`.
- Detect ruflo MCP → config. Idempotent.
- Финал: «Конфиг + базовый каталог готов → `/paf-nexus-create` (если нужны кастомные) → `/paf-onboard`».

---

## 5. `/paf-onboard` — цифровизация контекста (главное; repeatable)

Skill → `.claude/skills/paf-onboard/SKILL.md`. Ведёт `scouting`/`nexus-builder`/`cp-scorer`. Работает по **всем Нексусам `_registry.yaml`** (дефолт + кастом).
- **Phase A — ингестия доков** (`GROUND/_intake/`): Cortex парсит → узлы (`sources=["onboarding:<doc>"]`). Дедуп (ruflo memory_search / Grep).
- **Phase B — интервью**: по каждому Нексусу реестра — его `seed_questions` (из мастер-каталога или определения кастомного) → ответы в узлы (`sources=["onboarding:interview"]`).
- **Phase C — verify + CP**: `cp-scorer` ставит low-CP (0.2–0.4); anti-workslop пометка «допущение, требует валидации». Обновляет `_registry.yaml: onboarded`.
- **Phase D — readiness**: Context Ripeness по всем Нексусам + карта пробелов + top low-CP для валидации. Финал: «GROUND насыщен → Steps 1–8 валидируют».

---

## 6. CP-дисциплина [S1] Принцип 4, [S2] III.7

| Источник узла | `kind` | `confidence` | Валидация |
|---|---|---|---|
| Онбординг (доки/интервью) | empirical | **0.2–0.4** (допущение) | Steps 1–8: интервью/эксперименты → растёт |
| Steps 1–8 (валидировано) | empirical | 0.5–1.0 | CP растёт от новой информации |
| Методология PAF (справочник) | normative | 1.0 | — |

> Онбординг цифровизует, **не валидирует**. Не выдавать допущения за факты. CP поднимают Steps 1–8.

---

## 7. `GROUND/config.yaml` + `_registry.yaml`

```yaml
# config.yaml (генерируется /paf-init)
company: <имя>
product: {name: <>, slug: <ascii-slug>, idea: <>}
team: {size: <N>, roster: {product_engineer: <>, product_ops: <|"Cortex">, growth_engineer: <|"Cortex">, ...}}
cortex: {phase_target: 2, ruflo_mcp: true, obsidian: true}
onboarding: {status: init, sources_ingested: [], baseline_cr: {}, onboarded_at: null}
nexus: {catalog: master, custom_count: 0}   # ссылка на _registry.yaml
created: 2026-06-21
paf_step: 0
```
`GROUND/NEXUS/_registry.yaml` — реестр инстанцированных Нексусов (§2.2).

---

## 8. Структура репо (box layout)

```
paf-team-os/
├── README.md · INSTALL.md · LICENSE · .gitignore · .mcp.json
├── .claude/
│   ├── agents/              ← 6 Cortex-агентов (есть)
│   ├── skills/
│   │   ├── paf-init/        ← НОВОЕ: конфиг + GROUND + дефолтный каталог
│   │   ├── paf-nexus-create/← НОВОЕ (v3): кастомные Нексусы
│   │   └── paf-onboard/     ← НОВОЕ: цифровизация по всему реестру
│   └── CORTEX.md
├── AI-PROCESSES/ · AI-TRANSFORMATION/ · TRADITIONAL/   ← СПРАВОЧНИК (read-only)
├── sa_documentation/
│   ├── nexus_schema.md      ← UPDATED (v3): открытый slug + кастомные типы
│   ├── nexus_catalog.md     ← НОВОЕ (v3): мастер-каталог PAF-типов
│   ├── naming_conventions.md · nexus_index.py
└── GROUND/                  ← GROUND VAULT (клиента)
    ├── README.md · config.yaml
    ├── _intake/             ← доки клиента для онбординга
    └── NEXUS/
        ├── _registry.yaml   ← реестр Нексусов клиента (дефолт + кастом)
        ├── _index.md        ← MOC
        ├── market/ · customer/ · product/ · growth/   ← дефолт (minimal)
        └── <custom-slug>/   ← кастомные (создаются /paf-nexus-create)
    ├── PULSE/ · BUNCH/ · RESULTS/
```

**Правка справочника запрещена** — методология read-only. Контекст клиента — в `GROUND/`. `GROUND/` tracked (контекст клиента); `.claude/memory.db`, `.swarm/` gitignored.

---

## 9. Graceful degradation
| Компонент | Без него | Поведение |
|---|---|---|
| Claude Code | — | ОБЯЗАТЕЛЕН. |
| Obsidian | нет graph/wiki-link рендера | markdown, любой редактор. Работает. |
| ruflo MCP | нет semantic RAG | fallback Grep (structured). Дедуп/семантика слабее. |

## 10. Лицензия + credits
- Методология PAF → **CC BY-SA 4.0** (Тихомиров). README — credit + ссылка.
- Код (agents/skills/scripts) → **MIT**.

---

## 11. Scope сборки (что создать)
1. **`sa_documentation/nexus_catalog.md`** — мастер-каталог PAF-типов (§2.1): дефолт 4 (minimal) + опц. ops-model/company.
2. **`sa_documentation/nexus_schema.md`** — UPDATE: открытое поле `nexus` + формат определения кастомного типа (schema_extensions); секция «empirical узлы клиента» (low-CP по умолчанию).
3. **`.claude/skills/paf-init/`** — конфиг + GROUND + дефолтный минимальный каталог (§4).
4. **`.claude/skills/paf-nexus-create/`** (v3) — кастомные Нексусы (§2.3): интервью → `NEXUS/<slug>/` + `_registry.yaml`.
5. **`.claude/skills/paf-onboard/`** — цифровизация по всему реестру (§5): Phase A/B/C/D.
6. **`GROUND/` skeleton** — `_intake/`, `NEXUS/`(дефолт 4 + `_registry.yaml` + `_index.md`), `PULSE/`, `BUNCH/`, `RESULTS/`.
7. **`GROUND/config.yaml` + `NEXUS/_registry.yaml`** schema (§7).
8. **Cortex адаптация** — агенты читают `GROUND/config.yaml` + `_registry.yaml` → продукт-namespace + все Нексусы реестра (вместо хардкода `ai-kortex`/фикс. 4).
9. **`README.md`** (верхний) — quickstart (clone → /paf-init → /paf-nexus-create? → /paf-onboard → Steps), credits.
10. **`INSTALL.md`** — prerequisites, шаги, troubleshooting.
11. **`LICENSE`** — dual CC BY-SA + MIT.

---

## 12. Out of scope (YAGNI)
CLI-установщик; multi-product per clone; Neo4j / Phase 3; hosting/marketplace; `/paf-step-N` агенты; i18n; **Nexus-тип inheritance/sharing между клиентами** (каждый клиент — свой реестр; общий только мастер-каталог платформы).

## 13. Готовность = «done»
Новый клиент за ≤1 рабочий день: clone → `/paf-init` → (опц. `/paf-nexus-create` для кастомных) → `/paf-onboard` (доки + интервью) → GROUND Vault насыщен по всему реестру Нексусов (low-CP) → readiness + карта пробелов → открыл `AI-PROCESSES/STEP-1-IDEA/overview` → начал Product Sprint с Кортексом над насыщенным GROUND Nexus.

## 14. Риски
- **Онбординг = workslop-зона №1** (допущения как «контекст»). Контрмера: low-CP + пометка + cp-scorer гейт (§6).
- **Разрастание кастомных Нексусов** (клиент создаёт слишком много) → распыление контекста. Контрмера: мастер-каталог кураторский; `/paf-nexus-create` напоминает «минимально-необходимый набор уже покрывает Steps 1–8»; owner+seed_questions обязательны.
- **ruflo MCP quirk** — INSTALL фикс; без ruflo работает.
- **Клиент правит справочник** — README: read-only.
- **Пере-онбординг затирает** — `/paf-onboard` idempotent (дедуп+upsert).

---
**Version:** 3.0 · **Approved:** 2026-06-21 · **Next:** `writing-plans` → implementation plan (11 scope items).
