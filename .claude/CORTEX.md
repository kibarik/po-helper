# 🧠 CORTEX — рoster агентов Кортекса (Phase 1)

> 6 агентов Кортекса PAF [S1] III.1 — Phase 1 зрелости (Claude Code как рантайм). Оживляют опер.модель из `AI-PROCESSES/operating-model.md`, читая/паря Нексус по `sa_documentation/nexus_schema.md`.
> Phase 0 (Нексус-as-Obsidian) — выполнен: 64 ноты AI-PROCESSES проштампованы frontmatter.
> Phase 2 (ruflo RAG/memory/event-driven) — следующий шаг.

---

## Рoster агентов → фазы цикла Product Sprint

| Агент | Фаза Sprint | Функция | Tools | PAF-источник |
|---|---|---|---|---|
| **nexus-builder** | (сквозной) | Создаёт/обновляет Узлы Нексуса (frontmatter); отказ без `sources[]` | Read,Write,Edit,Glob,Grep | [S1] III.1 |
| **wilting-detector** | PULSE | Пересчитывает `ripeness`; считает Context Ripeness по Нексусам | Read,Edit,Bash,Glob,Grep | [S1] III.1, VI.4 |
| **scouting** | SCOUT | Скаутинг возможностей/угроз через 3 Линзы (Understand, Und-Id-Ex); WebSearch | Read,Glob,Grep,WebSearch | [S1] Принцип 5, VI.5 |
| **cp-scorer** | (сквозной) | Оценка/челлендж Confidence Point (колесо Гилада); стоимость риска | Read,Edit,Glob,Grep | [S1] VI.7, Принцип 4 |
| **bunch-former** | BUNCH | Черновой Банч из текущего состояния (Identify); Size/Window/NPV | Read,Write,Glob,Grep | [S1] VI.6, Принцип 1 |
| **pitching-opponent** | PITCH | Red-team Банча в Pitching of Trust; кандидаты на отказ | Read,Glob,Grep | [S1] VI.4, VI.3 |

> EXECUTE и HARVEST пока ведёт человек (инженер) с nexus-builder'ом для фиксации; полноценная агентизация этих фаз — Phase 2 (ruflo swarm).

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
SCOUT   → scouting (возможности/угрозы, 3 Линзы)
BUNCH   → bunch-former (Банч в моменте, NPV)
PITCH   → cp-scorer + pitching-opponent (CP-гейт, red-team)
EXECUTE → инженер + nexus-builder (валидация/Build+Bale+Germination)
HARVEST → nexus-builder (фиксация NPV/mNSM, инкремент контекста)
(сквозной: cp-scorer, nexus-builder)
```

---

## Модель зрелости Кортекса [S1] Часть VII
- **Phase 1 (текущая):** агенты как Claude Code subagents; промпты = фазовые ноты; Нексус = Obsidian frontmatter.
- **Phase 2 (далее):** ruflo `memory_store`/`memory_search` (RAG/GraphRAG), `hooks_route` (event-driven wilting), `swarm_init` (параллельные агенты).
- **Phase 3 (будущее):** сквозной event-based Кортекс всей компании; Neo4j как канонический граф; авто-пересчёт CP.

**Связанные:** [[AI-PROCESSES/operating-model|operating-model]] · [[sa_documentation/nexus_schema|nexus_schema]] · [[AI-PROCESSES/STEP-0-FOUNDATION/2.cortex-setup|2.cortex-setup]] · [[AI-PROCESSES/fit-points|fit-points]]
