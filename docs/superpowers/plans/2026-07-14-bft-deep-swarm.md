# V2 БФТ-конвейер (Fast→Deep→Sync) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить V2-способ работы с БФТ: `/bft-fast` авто-форкает фоновую роль-Обогатитель (Deep), которая берёт быстрый черновик как seed, наращивает глубину (ценность/what-if/границы) и синхронизирует в канонический bft-writer — не заменяя его.

**Architecture:** Три lane. Fast (существующий bft-fast, письмо-seed). Deep — новый скилл `bft-deep-swarm`: ruflo координирует, нативные Claude-субагенты исполняют с MCP-грудингом; обогащает seed по 3 осям. Sync переиспользует `/bft-draft`+`/bft-validate` (канон = ориентир качества). Адаптивный форк: RICH-контекст → Deep параллельно Fast; THIN → Deep после Fast.

**Tech Stack:** Markdown skills/commands (исполняются LLM), Claude Code `Agent` tool (`run_in_background`), ruflo MCP (`swarm_init`/`agent_spawn`/`memory_*`/`coordination_consensus`), MCP-источники (JIRA/Confluence/repowise). **Нет компилируемого кода.** «Тест» = прогон скилла на фикстуре + грейдинг рубрикой отдельным LLM-судьёй.

## Global Constraints

- **Markdown-only, аддитивно.** Существующие `bft-*` команды и `skills/bft-writer/*` НЕ переписывать — Deep/Sync их вызывают. (спека §7)
- **Нулевой допуск галлюцинаций.** Факт без источника → `[УТОЧНИТЬ у {кого}]`, никогда инвент, никогда тихий `[UNANCHORED]`. (§3, §6)
- **Стоп на валидированном черновике.** НЕ запускать `/bft-deliver` — запись в JIRA/Confluence = ручной гейт PO. (§7)
- **ruflo down ≠ прогон прерван** — деградация на native-subagent-only + локальный файловый хендофф. (§5)
- **Convergence-stop**, не фикс.лимит: гоняем пока гейты `/bft-validate` улучшаются; 2 раунда без прогресса → 🟡 + validation-notes. (§6)
- **Merge-гейт:** eval-рубрика §8 (hallucination=0 · SOURCE-recall полный · No Silent Skip · false-gap=0 · canon-структура · anchor 100% · канон-паритет). Ниже бара = блок мержа.
- Работа на ветке `feat/bft-deep-swarm` (от `origin/main`, там bft-fast).
- Голос текста: `.claude/skills/bft-writer/resources/writing_style.md`.
- Config-резолв: `.claude/domain-profile.md` (нет → `domain-profile.template.md` + `[УТОЧНИТЬ]`, без остановки).

---

## Файловая структура

- `.claude/skills/bft-deep-swarm/examples/golden_deep_summary.md` — eval-вход (Task 1).
- `.claude/skills/bft-deep-swarm/examples/golden_deep_gold.md` — аннотированный эталон + answer-key + рубрика (Task 1).
- `.claude/skills/bft-deep-swarm/resources/eval_rubric.md` — протокол LLM-судьи, merge-гейт (Task 2).
- `.claude/skills/bft-deep-swarm/SKILL.md` — role-card Обогатителя, принципы, этапы, config-резолв (Task 3).
- `.claude/skills/bft-deep-swarm/resources/orchestration.md` — 11-стадийный seed→enrich→sync, ruflo-контракт, degradation (Task 4).
- `.claude/skills/bft-deep-swarm/resources/enrichment.md` — 3 оси обогащения (ценность/what-if/границы) (Task 5).
- `.claude/skills/bft-deep-swarm/resources/grounding_verifier.md` — типизированный грудинг, forced-citation, convergence-stop (Task 6).
- `.claude/commands/bft-deep.md` — ручной вход `/bft-deep` (THIN-ветка/standalone) (Task 7).
- `.claude/skills/bft-fast/resources/deep_fork.md` — context-probe + адаптивный форк + `--no-deep` + нотификация (Task 8).
- `.claude/skills/bft-fast/SKILL.md`, `.claude/commands/bft-fast.md` — подключить форк-хук (Task 8).
- `domain-profile.template.md` — `models.deep_lane`, ruflo namespace, порог probe (Task 9).
- `README.md` — раздел V2-конвейера + финальный eval-прогон (Task 10).

---

### Task 1: Финализировать eval-фикстур в скилле

**Files:**
- Create: `.claude/skills/bft-deep-swarm/examples/golden_deep_summary.md`
- Create: `.claude/skills/bft-deep-swarm/examples/golden_deep_gold.md`
- Source: `docs/superpowers/specs/fixtures/2026-07-14-bft-deep-golden-summary.md`, `...-gold.md` (черновые, довести)

**Interfaces:**
- Produces: `golden_deep_summary.md` (вход для всех прогонов), `golden_deep_gold.md` с секциями: `## Two-tier annotated claim table`, `## Answer key`, `## Scoring rubric` — читаются Task 2 (судья) и Task 10 (финальный гейт).

- [ ] **Step 1: Скопировать черновые фикстуры в скилл**

```bash
mkdir -p .claude/skills/bft-deep-swarm/examples
cp docs/superpowers/specs/fixtures/2026-07-14-bft-deep-golden-summary.md \
   .claude/skills/bft-deep-swarm/examples/golden_deep_summary.md
cp docs/superpowers/specs/fixtures/2026-07-14-bft-deep-golden-gold.md \
   .claude/skills/bft-deep-swarm/examples/golden_deep_gold.md
```

- [ ] **Step 2: Довести gold — добавить канон-паритет ось в рубрику**

В `golden_deep_gold.md`, в `## Scoring rubric`, добавить пункт 7 (verbatim):

```markdown
7. Канон-паритет — обогащённый выход покрывает все 3 оси (ценность/what-if/границы),
   уложен в канон-структуру MTS (ASIS/PROBLEM/TOBE, БТ/ПТ/ИТ/ФТ/НФТ) и проходит
   канонические hard-gates /bft-validate на уровне старого БФТ (ориентир). Gate: 🟢/🟡, не 🔴.
```

- [ ] **Step 3: Проверить полноту эталона (self-check)**

Убедиться, что claim-table содержит: ≥6 SOURCE-claim, ≥5 PO-ONLY-claim, answer-key на каждый PO-ONLY, каждый SOURCE-claim имеет anchor. Проверка глазами по таблице.
Expected: 11 строк, ярусы размечены, answer-key покрывает C7-C10.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/bft-deep-swarm/examples/
git commit -m "test(bft-deep): golden eval-фикстур (summary + аннотированный gold + рубрика)"
```

---

### Task 2: Протокол LLM-судьи (merge-гейт)

**Files:**
- Create: `.claude/skills/bft-deep-swarm/resources/eval_rubric.md`
- Test-вход: `examples/golden_deep_gold.md` (Task 1)

**Interfaces:**
- Consumes: `golden_deep_gold.md` секции claim-table/answer-key/rubric.
- Produces: процедуру грейдинга — на вход swarm-вывод (`<epic>.md`), на выход per-metric PASS/FAIL + evidence-строка + итог `MERGE-OK` / `BLOCK`. Вызывается Task 10.

- [ ] **Step 1: Написать «failing test» — негативный сэмпл**

Создать `examples/bad_sample_hallucinated.md` (временный) — заведомо плохой БФТ: содержит значение из answer-key (напр. «модерация свыше 5000₽» как утверждение, без `[УТОЧНИТЬ]`).

```bash
mkdir -p .claude/skills/bft-deep-swarm/examples
cat > /tmp/bad_sample.md <<'MD'
## НФТ
- Модерация возврата свыше 5000₽ обязательна.   <- answer-key C9 как факт, без источника
MD
```

- [ ] **Step 2: Определить, что судья ДОЛЖЕН завалить этот сэмпл**

Ожидаемое поведение судьи: метрика 1 (hallucination) → FAIL (найдено answer-key значение C9 как утверждение) → итог `BLOCK`. Пока `eval_rubric.md` нет — прогнать нечем (это «red»).

- [ ] **Step 3: Написать `eval_rubric.md`**

Содержимое (verbatim скелет):

```markdown
# eval_rubric — LLM-судья качества V2-БФТ (merge-гейт)

Роль: СВЕЖИЙ судья, НЕ участник пайплайна. Вход — swarm-вывод `<epic>.md` + `examples/golden_deep_gold.md`.

## Процедура
1. Извлечь из вывода все claim-утверждения и все `[УТОЧНИТЬ]`-маркеры.
2. Сопоставить с claim-table эталона по смыслу (не по строке).
3. Прогнать 7 метрик-гейтов:

| # | Метрика | Гейт | FAIL если |
|---|---|---|---|
| 1 | Hallucination | =0 | любое answer-key значение (C7-C10) утверждается без `[УТОЧНИТЬ]`; либо claim не из sources и не помечен |
| 2 | SOURCE-recall | полный | любой C1-C6 отсутствует/искажён |
| 3 | Gaps flagged | все | любой PO-ONLY (C7-C11) не помечен `[УТОЧНИТЬ]` (No Silent Skip) |
| 4 | False-gap | =0 | SOURCE-факт ошибочно в `[УТОЧНИТЬ]` |
| 5 | Canon-структура | present | нет секции ASIS/PROBLEM/TOBE или БТ/ПТ/ИТ/ФТ/НФТ |
| 6 | Anchor validity | 100% | SOURCE-claim без резолвимого якоря |
| 7 | Канон-паритет | 🟢/🟡 | 3 оси не покрыты ИЛИ `/bft-validate` = 🔴 |

## Вывод судьи
Для каждой метрики: `<#> <PASS|FAIL>: <evidence-строка>`.
Итог: `MERGE-OK` если ВСЕ hard-gates PASS; иначе `BLOCK: <список проваленных>`.
```

- [ ] **Step 4: Прогнать судью на негативном сэмпле (verify «red→green» логики)**

Run: дать судье (по `eval_rubric.md`) `/tmp/bad_sample.md` против gold.
Expected: `метрика 1 FAIL: найдено "5000₽" (C9) как утверждение без [УТОЧНИТЬ]` → `BLOCK`.

- [ ] **Step 5: Прогнать судью на самом эталоне (позитив)**

Run: дать судье gold-claim-table как «идеальный вывод» (SOURCE утверждены, PO-ONLY → `[УТОЧНИТЬ]`).
Expected: все 7 метрик PASS → `MERGE-OK`.

- [ ] **Step 6: Убрать временный сэмпл, commit**

```bash
rm -f /tmp/bad_sample.md
git add .claude/skills/bft-deep-swarm/resources/eval_rubric.md
git commit -m "test(bft-deep): протокол LLM-судьи качества (merge-гейт, 7 метрик)"
```

---

### Task 3: SKILL.md — role-card Обогатителя

**Files:**
- Create: `.claude/skills/bft-deep-swarm/SKILL.md`

**Interfaces:**
- Produces: скилл `bft-deep-swarm` (роль, 3 оси, принципы, этапы-указатели на resources, config-резолв). Ссылается на resources Task 4-6.

- [ ] **Step 1: Написать SKILL.md**

Содержимое (verbatim):

```markdown
---
name: bft-deep-swarm
description: "V2 БФТ, роль-Обогатитель. Берёт быстрый черновик bft-fast как seed и автономно наращивает глубину по 3 осям (ценность / what-if демо / явные границы) с полным контекстом (JIRA/Confluence/repowise), затем синхронизирует в канонический bft-writer. ruflo координирует, Claude-субагенты исполняют. Используй когда: обогатить БФТ, глубокий БФТ автономно, deep-проработка после письма, /bft-deep."
---

# bft-deep-swarm — Обогатитель БФТ (V2, seed→enrich→sync)

Ты — **Обогатитель БФТ**. Не ре-ран канона с нуля. Берёшь быстрый черновик (письмо bft-fast) как **основу** и наращиваешь глубину, затем укладываешь в канон-структуру MTS. Старый bft-writer = **ориентир качества**, не перезатирается.

## Принципы
1. **Есть основа.** Обогащаешь seed (Fast-черновик или полный контекст), не генерируешь с нуля.
2. **Три оси обогащения:** ценность (зачем инвестировать) · «что если» демо · явные границы «нам здесь не важно».
3. **Ноль галлюцинаций.** Факт без источника → `[УТОЧНИТЬ у {кого}]`. Никогда инвент, никогда тихий `[UNANCHORED]`.
4. **Канон = ориентир.** Выход обязан достичь качества/глубины старого БФТ и пройти `/bft-validate`.
5. **Стоп на валидированном черновике.** НЕ запускать `/bft-deliver`.
6. **Автономность.** STOP-паузы канона заменены на `[УТОЧНИТЬ]`-маркеры.

## Этапы
Оркестрация (11 стадий seed→enrich→sync, ruflo-контракт, degradation) — `resources/orchestration.md`.
Три оси обогащения — `resources/enrichment.md`.
Грудинг-верификатор + forced-citation + convergence-stop — `resources/grounding_verifier.md`.
Merge-гейт качества — `resources/eval_rubric.md`.

## Резолв конфига
Читать `.claude/domain-profile.md` (нет → `domain-profile.template.md` + `[УТОЧНИТЬ]`, без остановки):
- `paths.bft_store` / workspace (куда `<epic_slug>/<epic_slug>.md`);
- `models.deep_lane` (опц.; нет → модель сессии);
- ruflo namespace `bft-deep/<epic_slug>` (§ orchestration);
- `stakeholders`, `capacity.roster_source` (владельцы `[УТОЧНИТЬ]`).

## Голос
`../bft-writer/resources/writing_style.md`.

## Границы навыка
Не пишет в JIRA/Confluence (стоп на черновике). Не переписывает `bft-*`/`bft-writer` — вызывает `/bft-draft`, `/bft-validate`. Sync-цель = канон-структура MTS.
```

- [ ] **Step 2: Verify — скилл читается, ссылки на resources валидны как пути**

Run: `ls .claude/skills/bft-deep-swarm/resources/ 2>/dev/null; echo "resources появятся в Task 4-6"`
Expected: директории пока нет — ок, resources создаются дальше; проверяем что SKILL.md ссылается ровно на orchestration.md/enrichment.md/grounding_verifier.md/eval_rubric.md.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/bft-deep-swarm/SKILL.md
git commit -m "feat(bft-deep): SKILL.md — role-card Обогатителя (seed→enrich→sync)"
```

---

### Task 4: resources/orchestration.md — 11 стадий + ruflo-контракт

**Files:**
- Create: `.claude/skills/bft-deep-swarm/resources/orchestration.md`

**Interfaces:**
- Consumes: SKILL.md (Task 3) ссылается сюда.
- Produces: пошаговую оркестрацию + ruflo-контракт + degradation-режим. Стадии value/what-if/bounds делегируют в `enrichment.md`; verify/validate/citation — в `grounding_verifier.md`.

- [ ] **Step 1: Написать orchestration.md**

Содержимое (verbatim, из спеки §5-§6):

```markdown
# orchestration — Deep+Sync (seed → обогащение → синк)

## ruflo-контракт (координация)
- `swarm_init(topology=hierarchical)` — один swarm на прогон; swarmId в память.
- `agent_spawn(agentType per роль, model=opus для lead/verify, sonnet для worker)` — cost-tracking + memory на стадию.
- `memory_store/retrieve(namespace="bft-deep/<epic_slug>")` — shared fact-base + хендофф артефактов.
- `coordination_consensus` — вердикт дебатов + грудинг-споры.
- **Degradation:** ошибка любого ruflo-tool → native-Task исполнение + файловый хендофф `artefacts/` + лог в error-callback. ruflo down ≠ прогон прерван.

## Стадии
0. FORK: pin repo commit hash → всем субагентам. epic_slug = date-slug из темы Summary (независим от JIRA key). Топология запуска — bft-fast/resources/deep_fork.md.
1. swarm_init + seed (Fast-черновик или полный контекст) → memory. Vague вход → шире `[УТОЧНИТЬ]`.

### DEEP (обогащение seed)
2. context: /bft-context-gen-deep (parallel JIRA/Confluence/repowise/ADR/стейкхолдеры). Per-source fallback: timeout/403 → источник=UNAVAILABLE; claim оттуда → `[УТОЧНИТЬ]`, никогда «пусто=нет данных». Memory-audit гейтит фактбазу.
3. value: ось 1 (enrichment.md §Ценность). bft-value.
4. what-if: ось 2 (enrichment.md §What-if).
5. bounds: ось 3 (enrichment.md §Границы).

### SYNC (укладка в канон)
6. draft: /bft-draft — обогащённый seed → канон-структура MTS.
7. verify: grounding_verifier.md §типизация.
8. validate: /bft-validate — hard-gates + Светофор. Convergence-stop (grounding_verifier.md §convergence).
9. citation: grounding_verifier.md §forced-citation.
10. review: свежий агент, весь документ против канон-ориентира.
11. emit: workspace/<epic_slug>/<epic_slug>.md + artefacts/ + нотификация (deep_fork.md §нотификация).
```

- [ ] **Step 2: Verify — все внешние ссылки существуют или запланированы**

Run: `ls .claude/commands/bft-context-gen-deep.md .claude/commands/bft-draft.md .claude/commands/bft-validate.md`
Expected: все три существуют (переиспользуемый канон).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/bft-deep-swarm/resources/orchestration.md
git commit -m "feat(bft-deep): оркестрация 11 стадий seed→enrich→sync + ruflo-контракт"
```

---

### Task 5: resources/enrichment.md — три оси обогащения

**Files:**
- Create: `.claude/skills/bft-deep-swarm/resources/enrichment.md`

**Interfaces:**
- Consumes: orchestration.md стадии 3-5 делегируют сюда.
- Produces: правила трёх осей — value / what-if / bounds. Каждая ось: вход из seed, чем углубляет, куда пишет.

- [ ] **Step 1: Написать enrichment.md**

Содержимое (verbatim):

```markdown
# enrichment — три оси обогащения seed'а

## Ось 1: Ценность (стадия value)
Глубинные вопросы «зачем инвестировать ресурсы». Переиспользует `bft-value`.
- Докопаться до реального ЗАЧЕМ (не «сделать фичу», а outcome).
- Привязка к KR/стратегии квартала (planning_root, если есть; нет → `[УТОЧНИТЬ]`).
- Выход: раздел «Продуктовая ценность» + список ценностных `[УТОЧНИТЬ]`-вопросов к PO.

## Ось 2: «Что если» демонстрация (стадия what-if)
Стресс How-to-demo из seed → вскрыть скрытые требования.
- Для каждого шага demo: что если пользователь X? крайний случай Y? альтернативный путь приёмки?
- Каждый what-if → либо требование (с источником), либо `[УТОЧНИТЬ]` (нет источника).
- Выход: расширенный сценарий приёмки + новые ФТ/НФТ из what-if.

## Ось 3: Явные границы (стадия bounds)
Заострить «вот это нам здесь не важно».
- Из seed-Границ + context: явный out-of-scope список.
- Формулировка «… не входит в зону БФТ этого эпика».
- Режет шум: то, что рядом, но не решаем сейчас.
- Выход: раздел «Границы» (in-scope / явный out-of-scope / операционные заметки).

## Правило грудинга (все оси)
Любой claim оси без источника в seed/контексте → `[УТОЧНИТЬ у {кого}]`, не выдумка. Владелец из `stakeholders`/ростера; неясен → `[кому?]`.
```

- [ ] **Step 2: Verify — bft-value существует для переиспользования**

Run: `ls .claude/commands/bft-value.md`
Expected: существует.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/bft-deep-swarm/resources/enrichment.md
git commit -m "feat(bft-deep): три оси обогащения (ценность/what-if/границы)"
```

---

### Task 6: resources/grounding_verifier.md — грудинг + citation + convergence

**Files:**
- Create: `.claude/skills/bft-deep-swarm/resources/grounding_verifier.md`

**Interfaces:**
- Consumes: orchestration.md стадии 7-9.
- Produces: правила типизированного грудинга, forced-citation, convergence-stop петли.

- [ ] **Step 1: Написать grounding_verifier.md**

Содержимое (verbatim, из спеки §6):

```markdown
# grounding_verifier — типизированный грудинг + forced-citation + convergence

## Типизация (стадия verify)
Каждый claim черновика → один из:
- **grounded** — есть резолвимый источник → оставить.
- **ungrounded** — источника нет → заменить на `[УТОЧНИТЬ у {кого}]`.
- **contradicted** — источник противоречит → регенерация стадии С reasoning контр-примера (передать в промпт следующей попытки). После 1 regen всё ещё contradicted → escalate `[УТОЧНИТЬ]`.

## Forced-citation (стадия citation)
Каждый факт финального документа ← якорь (JIRA / Confluence / решение PO / CORTEX).
Нет якоря → `[УТОЧНИТЬ]`. НИКОГДА не инвент, НИКОГДА тихий `[UNANCHORED]`.

## Convergence-stop (стадия validate, evaluator-optimizer)
- Прогнать `/bft-validate` → счёт пройденных hard-gates.
- Если гейты УЛУЧШИЛИСЬ vs прошлый раунд → регенерация проблемных секций, ещё раунд.
- Если 2 раунда подряд БЕЗ прогресса → стоп. Emit 🟡 + validation-notes (что не закрыто и почему).
- НЕ фикс.лимит ретраев (время идёт в качество, пока есть прогресс).
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/bft-deep-swarm/resources/grounding_verifier.md
git commit -m "feat(bft-deep): grounding-verifier + forced-citation + convergence-stop"
```

---

### Task 7: /bft-deep — ручной вход (THIN/standalone)

**Files:**
- Create: `.claude/commands/bft-deep.md`

**Interfaces:**
- Consumes: скилл `bft-deep-swarm` (Task 3-6).
- Produces: команду `/bft-deep <seed|summary> [epic_slug]` — ручной запуск Deep+Sync (для THIN-ветки после Fast, либо повторного прогона).

- [ ] **Step 1: Написать bft-deep.md**

Содержимое (verbatim):

```markdown
---
description: 'V2 БФТ-Обогатитель — берёт seed (Fast-черновик или Summary) и автономно наращивает глубину (ценность/what-if/границы) + синк в канон (роль: Обогатитель)'
---

## Использование
```
/bft-deep <seed> [epic_slug]
```
- `<seed>` — путь к Fast-черновику (письмо bft-fast) или к Summary/контексту.
- `[epic_slug]` — опц.; нет → date-slug из темы.

## Важно
Роль — Обогатитель (V2). Берёт основу, наращивает глубину, укладывает в канон-структуру MTS. Стоп на валидированном черновике; `/bft-deliver` — отдельный ручной шаг PO. Факт без источника → `[УТОЧНИТЬ]`.

## Инструкция для LLM
1. Загрузить `skills/bft-deep-swarm/SKILL.md` + resources (orchestration/enrichment/grounding_verifier/eval_rubric).
2. Резолв конфига (SKILL.md §Резолв).
3. Прогнать оркестрацию `resources/orchestration.md` стадии 0-11.
4. Emit: `workspace/<epic_slug>/<epic_slug>.md` + artefacts + нотификация.
```

- [ ] **Step 2: Verify — команда ссылается на существующий скилл**

Run: `ls .claude/skills/bft-deep-swarm/SKILL.md`
Expected: существует (Task 3).

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/bft-deep.md
git commit -m "feat(bft-deep): команда /bft-deep — ручной вход Обогатителя"
```

---

### Task 8: bft-fast — context-probe + адаптивный форк

**Files:**
- Create: `.claude/skills/bft-fast/resources/deep_fork.md`
- Modify: `.claude/skills/bft-fast/SKILL.md` (добавить этап форка + `--no-deep`)
- Modify: `.claude/commands/bft-fast.md` (документировать `--no-deep` + форк)

**Interfaces:**
- Consumes: `/bft-deep` (Task 7), скилл bft-deep-swarm.
- Produces: правило context-probe (RICH/THIN) + запуск фонового Agent + нотификация. Ссылается из bft-fast SKILL этап 7 (новый).

- [ ] **Step 1: Написать deep_fork.md**

Содержимое (verbatim, из спеки §4, §5, §8):

```markdown
# deep_fork — context-probe + адаптивный форк Deep + нотификация

## Флаг
`--no-deep` → пропустить форк целиком (только письмо).

## Context-probe (после emit письма)
Оценить richness контекста:
- JIRA-эпик указан/найден? Confluence-страницы по теме? прежние artefacts эпика? насыщенность Summary (>N фактов)?
- **RICH** (есть на что опереться) → форкать Deep СРАЗУ, параллельно (письмо уже отдано; Deep грудится на полный контекст, не ждёт seed).
- **THIN** (опереться не на что) → Deep уже имеет seed = только что отданное письмо; форкать Deep следом (Fast построил скелет).
(В обоих случаях письмо A уже в чате; разница — на чём Deep грудится: полный контекст vs письмо-seed.)

## Запуск фона
Agent tool, `run_in_background`: субагент выполняет `/bft-deep <seed> <epic_slug>` (seed = письмо; в RICH дополнительно полный контекст). Pin commit hash.

## Нотификация (по завершении фона)
- Успех: `deep БФТ готов: <path> · N [УТОЧНИТЬ]-точек · валидация 🟢/🟡`.
- Провал: `deep БФТ УПАЛ на <стадии>: <ошибка>; письмо не затронуто`. Никогда молча.
```

- [ ] **Step 2: Подключить хук в bft-fast SKILL.md**

Добавить в `.claude/skills/bft-fast/SKILL.md` после этапа `6. emit` (Modify — вставить новый этап):

```markdown
7. **deep-fork** — если нет `--no-deep`: по `resources/deep_fork.md` оценить richness контекста и форкнуть фоновый `/bft-deep` (RICH → параллельно; THIN → seed=письмо). Нотификация по завершении. Письмо A от форка не зависит.
```

И в `## Границы навыка` заменить строку «Не запускает deep-pipeline» на:

```markdown
Запускает deep-проработку ТОЛЬКО как фоновый форк (`resources/deep_fork.md`), сам её не исполняет — делегирует скиллу `bft-deep-swarm`.
```

- [ ] **Step 3: Документировать в команде bft-fast.md**

Добавить в `.claude/commands/bft-fast.md` секцию `## Параметры` строку:

```markdown
- `--no-deep` — не форкать фоновую deep-проработку (по умолчанию форкается: RICH-контекст → параллельно письму, THIN → следом, seed=письмо).
```

- [ ] **Step 4: Verify — прогон bft-fast на golden с и без --no-deep (концептуально)**

Run: исполнить `/bft-fast .claude/skills/bft-fast/examples/golden_summary.md --no-deep`
Expected: письмо как раньше, форк НЕ стартует (совместимость bft-fast не сломана).
Run: исполнить `/bft-fast .claude/skills/bft-fast/examples/golden_summary.md`
Expected: письмо + нотификация о старте фонового Deep.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/bft-fast/resources/deep_fork.md .claude/skills/bft-fast/SKILL.md .claude/commands/bft-fast.md
git commit -m "feat(bft-fast): context-probe + адаптивный форк Deep (--no-deep опт-аут)"
```

---

### Task 9: domain-profile — deep_lane + ruflo + порог probe

**Files:**
- Modify: `domain-profile.template.md`

**Interfaces:**
- Consumes: резолв конфига из SKILL.md (Task 3), deep_fork.md (Task 8).
- Produces: зарезервированные ключи `models.deep_lane`, `ruflo.namespace_prefix`, `bft_deep.context_probe`.

- [ ] **Step 1: Найти секцию models (уже есть fast_lane из #112)**

Run: `grep -n "fast_lane\|deep_lane\|models:" domain-profile.template.md`
Expected: `models.fast_lane` присутствует (зарезервирован в bft-fast PR); `deep_lane` возможно уже заглушкой.

- [ ] **Step 2: Дополнить конфиг (Modify рядом с models.fast_lane)**

Добавить (verbatim, адаптировать под YAML-стиль файла):

```yaml
models:
  fast_lane: null      # bft-fast (быстрый проход)
  deep_lane: null      # bft-deep-swarm (тяжёлая модель, PO не ждёт вживую)
ruflo:
  namespace_prefix: "bft-deep"   # memory namespace: <prefix>/<epic_slug>
bft_deep:
  context_probe:
    rich_min_facts: 8            # порог THIN/RICH по насыщенности Summary
    require_epic_for_rich: false # JIRA-эпик не обязателен для RICH
```

- [ ] **Step 3: Commit**

```bash
git add domain-profile.template.md
git commit -m "feat(bft-deep): конфиг deep_lane + ruflo namespace + порог context-probe"
```

---

### Task 10: README + финальный eval-прогон (merge-гейт)

**Files:**
- Modify: `README.md`
- Прогон: скилл `bft-deep-swarm` на `examples/golden_deep_summary.md`, грейдинг по `eval_rubric.md`.

**Interfaces:**
- Consumes: весь скилл (Task 1-9), судья (Task 2), фикстур (Task 1).
- Produces: документацию V2 + доказательство merge-гейта.

- [ ] **Step 1: Финальный eval-прогон**

Run: исполнить `/bft-deep .claude/skills/bft-deep-swarm/examples/golden_deep_summary.md golden-refund` → получить `<epic>.md`.
Затем дать СВЕЖЕМУ судье (по `resources/eval_rubric.md`) этот вывод + `examples/golden_deep_gold.md`.
Expected: 7 метрик → все hard-gates PASS → `MERGE-OK`. Особо: hallucination=0 (C7-C10 как `[УТОЧНИТЬ]`, не значения answer-key), SOURCE-recall 6/6, gaps 5/5.

- [ ] **Step 2: Если BLOCK — чинить скилл, не рубрику**

Если судья вернул `BLOCK`: причина = дефект оркестрации/грудинга (Task 4/6), не эталона. Поправить соответствующий resources/*.md, повторить Step 1. (Рубрику НЕ ослаблять.)

- [ ] **Step 3: Задокументировать V2 в README**

Добавить в `README.md` раздел (verbatim скелет):

```markdown
### V2 БФТ-конвейер: Fast → Deep → Sync
- `/bft-fast <summary>` — быстрое письмо-seed (≤5 мин) + авто-форк фоновой глубины (`--no-deep` отключает).
- Deep (`bft-deep-swarm` / `/bft-deep`) — Обогатитель: наращивает seed по 3 осям (ценность / what-if / границы), автономно, с полным контекстом.
- Sync — укладка в канон-структуру MTS + `/bft-validate`. Канонический `bft-writer` = ориентир качества, не заменяется.
- Стоп на валидированном черновике; запись в JIRA/Confluence (`/bft-deliver`) — ручной гейт PO.
- Качество гарантируется merge-гейтом: `skills/bft-deep-swarm/resources/eval_rubric.md` (7 метрик, hallucination=0).
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(bft-deep): README раздел V2-конвейера + зафиксирован merge-гейт eval PASS"
```

---

## Self-Review

**Spec coverage:**
- §1 3-lane → Task 3 (роль), 4 (оркестрация), 8 (форк). ✓
- §3 role-card 3 оси → Task 3, 5. ✓
- §4 адаптивный форк RICH/THIN → Task 8 (deep_fork.md), 9 (порог). ✓
- §5 ruflo-контракт + degradation → Task 4. ✓
- §6 seed→enrich→sync + verify/citation/convergence → Task 4, 5, 6. ✓
- §7 границы (стоп на черновике, канон не тронут) → Task 3 §Границы, 6, 7. ✓
- §8 eval двухъярусный + судья → Task 1, 2, 10. ✓
- §9 нотификация → Task 8 (deep_fork.md). ✓
- §10 файлы → покрыты Task 1-9. ✓

**Placeholder scan:** содержимое каждого .md дано verbatim; «test»-шаги = конкретные прогоны фикстур с ожиданием. Нет TBD/«add appropriate».

**Type consistency (для Markdown = имена файлов/секций/команд):** `eval_rubric.md`, `orchestration.md`, `enrichment.md`, `grounding_verifier.md`, `deep_fork.md` — имена совпадают между SKILL.md ссылками (Task 3) и созданием (Task 4-8). Namespace `bft-deep/<epic_slug>` совпадает Task 4/9. `golden_deep_summary.md`/`golden_deep_gold.md` совпадают Task 1/2/10. Команды `/bft-deep`, `/bft-draft`, `/bft-validate`, `/bft-context-gen-deep`, `/bft-value` — существующие проверяются `ls` перед использованием.
