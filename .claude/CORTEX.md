# 🧠 CORTEX — roster агентов Кортекса (Phase 0 + 1 + 2-complete)

> 6 агентов Кортекса PAF [S1] III.1. Оживляют опер.модель из `docs/AI-PROCESSES/operating-model.md`, читая/паря Нексус по `sa_documentation/nexus_schema.md`.
> **Phase 0** (Нексус-as-Obsidian) — выполнен: 64 ноты AI-PROCESSES проштампованы frontmatter.
> **Phase 1** (Claude Code как рантайм) — выполнен: 6 агентов, тест-драйв пройден.
> **Phase 2-complete** (ruflo MCP — native) — **выполнен**: `.mcp.json` зарегистрировал ruflo; `mcp__ruflo__*` живые; 3 агента на native MCP RAG. (CLI-мост retirнут, кроме bulk-переиндекса.)

---

## Roster агентов → фазы цикла Product Sprint

| Агент | Фаза | Функция | Tools | PAF |
|---|---|---|---|---|
| **nexus-builder** | сквозной | Узлы Нексуса (frontmatter); отказ без `sources[]`; дедуп + store через native MCP | Read,Write,Edit,Glob,Grep, mcp__ruflo__memory_search, mcp__ruflo__memory_store | [S1] III.1 |
| **wilting-detector** | PULSE | Пересчёт `ripeness`; Context Ripeness по Нексусам | Read,Edit,Bash,Glob,Grep | [S1] III.1, VI.4 |
| **scouting** | SCOUT | Скаутинг возможностей/угроз, 3 Линзы; WebSearch + native RAG | Read,Glob,Grep,WebSearch, mcp__ruflo__memory_search | [S1] Принцип 5, VI.5 |
| **cp-scorer** | сквозной | Оценка/челлендж CP (колесо Гилада); стоимость риска | Read,Edit,Glob,Grep | [S1] VI.7, Принцип 4 |
| **bunch-former** | BUNCH | Банч из текущего состояния; Size/Window/NPV; native RAG | Read,Write,Glob,Grep, mcp__ruflo__memory_search | [S1] VI.6, Принцип 1 |
| **pitching-opponent** | PITCH | Red-team Банча; кандидаты на отказ | Read,Glob,Grep | [S1] VI.4, VI.3 |

> Native MCP RAG (`mcp__ruflo__memory_search`) — у scouting/bunch-former/nexus-builder (семантика по смыслу). Структурный поиск по полям — Grep у всех. EXECUTE/HARVEST — инженер + nexus-builder; агентизация — Phase 3.

---

## Общие гвардраилы (во всех 6)
1. **Ноль галлюцинаций** — каждое утверждение → `sources[]`; Узел без источников = workslop.
2. **Метапознание** — результат верифицирует человек; veto за человеком; low-CP помечается.
3. **Анти-workslop** — TAM-цифры/AI-персоны/офферы/креативы только из источника.
4. **Зона человека** — стратегия, NPV-решения, Ставки, синхронизация людей; агенты = инструменты [S2] III.4.
5. **Запрещённые синонимы** — Банч (не беклог), Product Engineer (не PM), скаутинг (не приоритизация), риски (не потери), Comb-shaped (не T-shaped).

---

## Цикл Product Sprint × агенты

```
PULSE   → wilting-detector (Context Ripeness, snapshot)
SCOUT   → scouting (возможности/угрозы, 3 Линзы, native RAG по Нексусу)
BUNCH   → bunch-former (Банч в моменте, NPV, native RAG-контекст)
PITCH   → cp-scorer + pitching-opponent (CP-гейт, red-team)
EXECUTE → инженер + nexus-builder (валидация/Build+Bale+Germination)
HARVEST → nexus-builder (фиксация NPV/mNSM, инкремент контекста)
(сквозной: cp-scorer, nexus-builder)
```

---

## 🔍 Phase 2-complete — ruflo MCP native (активен)

`.mcp.json` (project) регистрирует ruflo MCP-сервер (`/opt/homebrew/bin/ruflo mcp start`, stdio). После рестарта Claude Code → `mcp__ruflo__*` (~300 инструментов) живые. Субагенты наследуют MCP-инструменты сессии (проверено).

**Семантический RAG (native, в агентах):**
- `mcp__ruflo__memory_search` (query, namespace="ai-kortex", limit) → релевантные Узлы по смыслу (мгновенно ~10-15ms, без flush-задержки; точное совпадение ~0.88).
- `mcp__ruflo__memory_store` (key=node_id, value=sanitized summary, namespace="ai-kortex", upsert=true) — запись Узла в индекс.
- Bulk переиндекс всех узлов: `python3 sa_documentation/nexus_index.py` (Bash; CLI, для массовых изменений).
- `mcp__ruflo__memory_stats` — состояние индекса.

**Состояние индекса:** 64 узла AI-PROCESSES в ns=`ai-kortex` (пережили рестарт; 100% embedding coverage, 384-dim, HNSW+sql.js).

**Когда что:**
- **Тема/смысл** → `mcp__ruflo__memory_search`.
- **Фильтр по полю** (nexus/owner/confidence/wilting) → Grep frontmatter.
- Всегда сверяй RAG-результат с Grep/Read.

**Известные quirks (документировано):**
- ⚠️ CLI-stored debug-записи (phase2-probe, t1, t3, dbg-*) **не удаляются** ни CLI, ни native MCP (кодировка ключа) — harmless noise, игнорировать.
- ⚠️ `nexus_index.py` хранит **sanitized single-line** summary (ruflo store ломается на сыром `---`/YAML) — для native store тоже санируй value.

---

## Модель зрелости Кортекса [S1] Часть VII
- **Phase 1 (выполнено):** агенты как Claude Code subagents; Нексус = Obsidian frontmatter.
- **Phase 2-complete (выполнено):** native MCP `mcp__ruflo__*` — `memory_store/search` (RAG), доступны `hooks_route`/`swarm_init`/`agent_spawn`.
- **Phase 3 (далее):** event-driven wilting (через Claude Code `settings.json` hooks → триггер wilting-detector по событию/времени); `swarm_init` для параллельных агентов над Нексусом; Neo4j как канонический граф.

**Связанные:** [[docs/AI-PROCESSES/operating-model|operating-model]] · [[sa_documentation/nexus_schema|nexus_schema]] · [[sa_documentation/nexus_index|nexus_index.py]] · [[docs/AI-PROCESSES/STEP-0-FOUNDATION/2.cortex-setup|2.cortex-setup]] · [[docs/AI-PROCESSES/fit-points|fit-points]]
