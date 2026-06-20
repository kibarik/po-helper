# 🧠 CORTEX — roster агентов Кортекса (Phase 1 + Phase 2 CLI-мост)

> 6 агентов Кортекса PAF [S1] III.1. Оживляют опер.модель из `AI-PROCESSES/operating-model.md`, читая/паря Нексус по `sa_documentation/nexus_schema.md`.
> **Phase 0** (Нексус-as-Obsidian) — выполнен: 64 ноты AI-PROCESSES проштампованы frontmatter.
> **Phase 1** (Claude Code как рантайм) — выполнен: 6 агентов в `.claude/agents/`, тест-драйв пройден.
> **Phase 2** (CLI-мост ruflo memory) — **активен**: семантический RAG над Нексусом. MCP-регистрация — следующий шаг.

---

## Roster агентов → фазы цикла Product Sprint

| Агент | Фаза Sprint | Функция | Tools | PAF-источник |
|---|---|---|---|---|
| **nexus-builder** | (сквозной) | Создаёт/обновляет Узлы Нексуса (frontmatter); отказ без `sources[]`; дедуп через RAG | Read,Write,Edit,Bash,Glob,Grep | [S1] III.1 |
| **wilting-detector** | PULSE | Пересчитывает `ripeness`; считает Context Ripeness по Нексусам | Read,Edit,Bash,Glob,Grep | [S1] III.1, VI.4 |
| **scouting** | SCOUT | Скаутинг возможностей/угроз через 3 Линзы (Understand, Und-Id-Ex); WebSearch + RAG | Read,Bash,Glob,Grep,WebSearch | [S1] Принцип 5, VI.5 |
| **cp-scorer** | (сквозной) | Оценка/челлендж Confidence Point (колесо Гилада); стоимость риска | Read,Edit,Glob,Grep | [S1] VI.7, Принцип 4 |
| **bunch-former** | BUNCH | Черновой Банч из текущего состояния (Identify); Size/Window/NPV; RAG-контекст | Read,Write,Bash,Glob,Grep | [S1] VI.6, Принцип 1 |
| **pitching-opponent** | PITCH | Red-team Банча в Pitching of Trust; кандидаты на отказ | Read,Glob,Grep | [S1] VI.4, VI.3 |

> RAG (Bash + `ruflo memory`) подключён к агентам, которым нужен **семантический** поиск по смыслу (scouting, bunch-former, nexus-builder). Структурный поиск по полям frontmatter — у всех через Grep. EXECUTE/HARVEST ведёт инженер + nexus-builder; полноценная агентизация — Phase 3.

---

## Общие гвардраилы (во всех 6 агентах)
1. **Ноль галлюцинаций** — каждое утверждение → `sources[]`; Узел без источников = workslop.
2. **Метапознание** — результат верифицирует человек; veto за человеком; low-CP помечается.
3. **Анти-workslop** — TAM-цифры/AI-персоны/офферы/креативы только из источника.
4. **Зона человека** — стратегия, NPV-решения, Ставки (Bets), синхронизация людей; агенты = инструменты, не акторы [S2] III.4.
5. **Запрещённые синонимы** — Банч (не беклог), Product Engineer (не PM), скаутинг (не приоритизация), риски (не потери), Comb-shaped (не T-shaped).

---

## Цикл Product Sprint × агенты

```
PULSE   → wilting-detector (Context Ripeness, snapshot)
SCOUT   → scouting (возможности/угрозы, 3 Линзы, RAG по Нексусу)
BUNCH   → bunch-former (Банч в моменте, NPV, RAG-контекст)
PITCH   → cp-scorer + pitching-opponent (CP-гейт, red-team)
EXECUTE → инженер + nexus-builder (валидация/Build+Bale+Germination)
HARVEST → nexus-builder (фиксация NPV/mNSM, инкремент контекста)
(сквозной: cp-scorer, nexus-builder)
```

---

## 🔍 Phase 2 — CLI-мост ruflo memory (активен)

Семантический RAG над Нексусом: Узлы индексируются в `ruflo memory` (ns=`ai-kortex`), агенты ищут по смыслу (не exact-match).

**Индексация:**
```bash
python3 sa_documentation/nexus_index.py          # индекс/переиндекс AI-PROCESSES (ns=ai-kortex)
# хранит САНИТИРОВАННЫЙ однострочный summary (title + meta + body без markdown);
# ruflo ломается на сыром контенте с `---`/YAML → санитация обязательна.
```

**Семантический поиск (в агентах, через Bash):**
```bash
ruflo memory search --query "<запрос по смыслу>" --namespace ai-kortex --limit 5
```

**Когда что:**
- **Тема/смысл** («что мы знаем про churn в SMB») → `ruflo memory search` (семантика).
- **Фильтр по полю** (все market-узлы, CP<0.5, wilting) → `Grep` frontmatter (точно).
- Всегда сверяй RAG-результат с Grep/Read — ранжирование приближённое.

**Известные quirks CLI-моста (документировано, не блокирует):**
- ⚠️ **Flush-задержка**: новые узлы появляются в поиске через ~секунды (не мгновенно).
- ⚠️ **Ранжирование приближённое**: 384-dim эмбеддинги дают релевантное, но не всегда точное #1 (aip-7-harvest может не возглавить PMF-запрос) → сверять.
- ⚠️ **`delete` ненадёжён**, `compress`/`cleanup` ломаются (`MCP tool not found: memory_*`) — та же не-регистрация ruflo MCP.
- ⚠️ Только sanitized single-line `--value` (сырой markdown-контент → `boolean (true)` error).

**Почему не MCP:** ruflo стоит как **plugin** в `~/.claude/settings.json`, но **не как mcpServers** → `mcp__ruflo__*` не зарегистрированы. Регистрация ruflo MCP-сервера (`.mcp.json` + рестарт Claude Code) даст нативные `memory_store/search`, `hooks_route` (event-driven wilting), `swarm_init` (параллельные агенты) — это **Phase 2-complete / Phase 3**.

---

## Модель зрелости Кортекса [S1] Часть VII
- **Phase 1 (выполнено):** агенты как Claude Code subagents; промпты = фазовые ноты; Нексус = Obsidian frontmatter.
- **Phase 2 (CLI-мост — активен; MCP — следующий шаг):** RAG над Нексусом через `ruflo memory` CLI; нативные MCP-инструменты (`memory_*`, `hooks_route`, `swarm_init`) — после регистрации ruflo MCP-сервера.
- **Phase 3 (будущее):** сквозной event-driven Кортекс; Neo4j как канонический граф; авто-пересчёт CP; `swarm_init` для параллельных агентов.

**Связанные:** [[AI-PROCESSES/operating-model|operating-model]] · [[sa_documentation/nexus_schema|nexus_schema]] · [[sa_documentation/nexus_index|nexus_index.py]] · [[AI-PROCESSES/STEP-0-FOUNDATION/2.cortex-setup|2.cortex-setup]] · [[AI-PROCESSES/fit-points|fit-points]]
