---
source: internal (po-helper self-development)
version: 0.1
synced: 2026-07-14
issues: [113, 112, 98]
status: Черновик 0.1
depends_on: bft-fast (PR #122, merged), skills/bft-writer/*
---

# [Дизайн] bft-fast + фоновый deep-swarm: автономная генерация полного БФТ

> Итерация поверх **bft-fast (#113)**. `/bft-fast` из одного вызова даёт **два потока**: быстрое письмо в чат (существующее, синхронно) **и** фоновый multi-agent прогон полного deep-пайплайна bft-writer → черновик БФТ канон-структуры MTS со всей фактурой, автономно.
> Вне итерации: `/bft-deliver` (запись в JIRA/Confluence остаётся ручным гейтом PO), per-step замер каталога моделей (#112).

## 1. Образ результата

PO запускает `/bft-fast <summary>`. Немедленно:

- **Поток A (main, синхронно, ≤5 мин):** существующее письмо (How to demo / Открытые вопросы / Границы). **Не тронут.**
- **Поток B (фон, авто-форк):** ruflo-координируемый multi-agent прогон 7-стадийного deep-пайплайна → `workspace/<epic_slug>/<epic_slug>.md` — валидированный черновик БФТ со всей фактурой и `[УТОЧНИТЬ]`-маркерами на местах, требующих живого PO. По завершении — нотификация в чат.

Флаг `--no-deep` отключает поток B.

**Зачем.** bft-fast даёт форму за 5 мин, но глубину PO запускал руками отдельным шагом. Здесь глубина стартует **сразу и автономно**, параллельно письму: пока PO читает/рассылает письмо, фон уже строит полный документ. Paramount-требование — **качество не хуже прямого диалога PO** (см. §7).

## 2. Проблема

- **ДЛЯ КОГО:** PO, которому нужен полный БФТ-документ, а не только письмо-образ приёмки.
- **ЧТО ДЕЛАЕМ:** авто-форк фонового автономного прогона полного deep-пайплайна из того же Summary, параллельно письму.
- **AS-IS:** после письма bft-fast глубину PO запускает вручную, стадия за стадией, с STOP-паузой на ревью между каждой из 7 команд. Полный документ — это отдельная длинная сессия PO.
- **ПРОБЛЕМА:** глубина не стартует, пока PO её не инициирует; 7 STOP-пауз требуют человека на каждом шаге; полный документ откладывается.
- **TO-BE:** глубина форкается автоматически при `/bft-fast`, проходит все 7 стадий автономно (паузы заменены на `[УТОЧНИТЬ]`-маркеры), отдаёт готовый к ревью PO черновик.

## 3. Автономность vs STOP-паузы

Deep-пайплайн bft-writer спроектирован со STOP-паузой для ревью PO между каждой стадией. Фоновому агенту некому отвечать. **Решение:** полностью автономный прогон; на местах, где нужен живой PO, агент ставит `[УТОЧНИТЬ у {кого}]`, **не выдумывает**. Выход — черновик, который PO ревьюит целиком потом. Соответствует принципу нулевого допуска к галлюцинациям bft-writer.

## 4. Подложка: ruflo координирует, Claude исполняет

Рыночный скан Q3 2026 (Anthropic MAS orchestrator-worker +90% vs single-agent; консенсус анти-галлюцinаций = типизированный грудинг + forced-citation + verifier-агент): качество автономного БФТ рождается в **дизайне оркестрации**, не в бренде движка.

- **ruflo** = слой координации: `swarm_init` (hierarchical, queen-coordinator), `agent_spawn` (cost-tracking + memory на роль), `memory_store/retrieve` (namespace `bft-deep/<epic_slug>`, shared fact-base + хендофф артефактов), `coordination_consensus` (вердикт дебатов + грудинг-споры).
- **Нативные Claude-субагенты** = реальное исполнение стадий с **прямым MCP-грудингом** (JIRA/Confluence/repowise уже подключены в сессии). Именно они держат качество/грудинг.
- **Failure-режим:** ошибка любого ruflo-tool → деградация на native-Task + локальный файловый хендофф, лог в error-callback. **ruflo down ≠ прогон прерван** — падает до native-subagent-only.

Обоснование выбора: `agent_spawn` описан как «когда нужны cost-tracking / cross-session learning / consensus; для one-shot native Task достаточно» — т.е. ruflo это координация поверх нативного исполнения, не замена ему. Грудинг к источникам сохранён.

## 5. Оркестрация (7 стадий)

```
0. FORK: pin repo commit hash → всем субагентам. epic_slug = date-slug из темы Summary (всегда выводим,
   независим от JIRA epic key).
1. swarm_init (hierarchical, queen-coordinator + role-card + guardrails).
   Seed: Summary + сущности из письма A → ruflo memory. Vague/противоречивый Summary → шире [УТОЧНИТЬ], не догадки.
2. S0 context  → субагент /bft-context-gen-deep (parallel: JIRA/Confluence/repowise/ADR/стейкхолдеры).
                 Per-source fallback: timeout/403 → источник=UNAVAILABLE в памяти; claim оттуда → [УТОЧНИТЬ],
                 никогда «пусто = нет данных». Pre-S4 memory-audit гейтит фактбазу.
3. S1 problem  → Problem Analyst (As-Is/Gap, без решения).
4. S2 concept  → Solution Designer (2-3 варианта, CATWOE).
5. S3 debate   → Devil's Advocate, раунды до стабильности → coordination_consensus.
6. S4 draft    → Requirements Writer (БТ/ПТ/ИТ/ФТ/НФТ).
7. S5 verify   → Grounding-Verifier: типизация claim (grounded/ungrounded/contradicted).
                 ungrounded → [УТОЧНИТЬ у {кого}]; contradicted → регенерация стадии С reasoning контр-примера;
                 после 1 regen всё contradicted → escalate [УТОЧНИТЬ].
                 Evaluator-optimizer: гоняем пока гейты /bft-validate улучшаются; 2 раунда без прогресса
                 → стоп, emit 🟡 + validation-notes (convergence-stop, не фикс.лимит).
8. S6 citation → forced-citation: каждый факт ← якорь (JIRA/Confluence/PO/CORTEX). Нет якоря → [УТОЧНИТЬ],
                 никогда инвент, никогда тихий [UNANCHORED].
9. S7 review   → свежий агент, весь документ целиком.
10. emit: workspace/<epic_slug>/<epic_slug>.md + artefacts/ + нотификация.
```

## 6. Границы

- Deep-прогон **останавливается на валидированном черновике** (через `/bft-validate`). **НЕ** запускает `/bft-deliver` — запись в JIRA/Confluence остаётся ручным гейтом PO (никаких автономных побочек).
- Существующие `bft-*` команды и `skills/bft-writer/*` **не переписываются** — swarm их **вызывает**.
- Вход/эпик: от Summary; JIRA-эпика нет → линковка = `[УТОЧНИТЬ]`, заполнимо позже. Валидатор трактует явный `[УТОЧНИТЬ]`-пробел как 🟡-допустимо, только фабрикацию как 🔴.

## 7. Валидация качества — «не хуже прямого PO» (eval-харнесс, merge-гейт)

Paramount-требование нуждается в регресс-гейте, не в вере. Двухъярусный синтетический фикстур:

- `examples/golden_deep_summary.md` — насыщенный Summary (факты сказаны + открытые точки не решены).
- `examples/golden_deep_gold.md` — аннотированный claim-table: каждый gold-claim помечен **SOURCE-DERIVABLE** (swarm ОБЯЗАН грудить) vs **PO-ONLY** (swarm ОБЯЗАН пометить `[УТОЧНИТЬ]`); + answer-key (значения, что дал бы живой PO — swarm НЕ должен их выдать) + рубрика.

**Принцип честности.** У автономного прогона нет живого PO, поэтому `[УТОЧНИТЬ]` там, где PO бы ответил — законно. Сравнение двухъярусное, не байт-в-байт:

- SOURCE claim пропущен/неверен → регрессия качества → **FAIL**.
- PO-ONLY claim выдуман (совпал с answer-key) → галлюцинация → **hard FAIL**.
- PO-ONLY claim помечен `[УТОЧНИТЬ]` → **PASS**.

**Рубрика (hard-gates):** hallucination = 0 · SOURCE-recall = полный · все пробелы помечены (No Silent Skip) · false-gap = 0 · canon MTS структура present · anchor validity = 100%.

**Судья:** ОТДЕЛЬНЫЙ свежий LLM-агент (не из пайплайна) грейдит swarm-вывод против gold по рубрике; любой прогон ниже бара = «хуже прямого PO» = **блок мержа фичи**.

**Почему доказывает «не хуже PO»:** на выводимом контенте swarm совпадает с PO+аналитиком; на PO-зависимом честно откладывает через `[УТОЧНИТЬ]` вместо догадки; hallucination-гейт=0 → swarm никогда не изобретает ответы PO — ровно тот провал, что показал бы «хуже PO».

Фикстуры: `docs/superpowers/specs/fixtures/2026-07-14-bft-deep-*` (черновые; при реализации дописывается реальный gold-BFT текст поверх claim-table).

## 8. Нотификация

- Успех: `deep БФТ готов: <path> · N [УТОЧНИТЬ]-точек · валидация 🟢/🟡`.
- Провал: `deep БФТ УПАЛ на <стадии>: <ошибка>; письмо не затронуто`. Никогда молча.

Харнесс сам ре-инвокнет при завершении фонового Agent.

## 9. Файлы (план, аддитивно)

- `.claude/skills/bft-fast/SKILL.md`, `.claude/commands/bft-fast.md` — хук авто-форка + `--no-deep`.
- `.claude/skills/bft-deep-swarm/SKILL.md` + `resources/` — оркестратор, role-cards, ruflo-контракт, grounding-verifier, convergence-loop.
- `.claude/skills/bft-deep-swarm/examples/golden_deep_summary.md`, `golden_deep_gold.md` — финальный eval-фикстур (доведённый из черновых `docs/superpowers/specs/fixtures/2026-07-14-bft-deep-*`).
- `domain-profile.template.md` — `models.deep_lane`, ruflo-настройки namespace.

## 10. Открытые вопросы реализации

- Точный маппинг ruflo agentType → роль стадии (queen-coordinator vs hierarchical-coordinator для lead).
- Формат хендоффа артефактов: ruflo memory namespace vs файлы `artefacts/` (дизайн допускает оба; выбрать при реализации).
- Порог convergence-stop «нет прогресса» (счёт улучшившихся гейтов между раундами).
