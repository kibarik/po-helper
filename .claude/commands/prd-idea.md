---
description: 'Discovery Step 1 (Idea) — BIG Idea + 3 Линзы через цикл Product Sprint; наполняет market/product/growth узлами-гипотезами (роль: Discovery Facilitator)'
---

## Использование

```
/prd-idea
```

Вход: пустые/частичные market/product/growth. Выход: узлы-гипотезы в этих Нексусах + `state.yaml(idea)`.

## Инструкция для LLM

### Этап 0: Загрузка роли и конвенций
1. Прочитай `skills/prd-research/SKILL.md`.
2. Прочитай `skills/prd-research/resources/node_conventions.md` (формат узла), `pipeline.md` (строка Step 1), `board_state.md` (state.yaml/journal).
3. Прочитай `sa_documentation/nexus_schema.md` §2.3 (hyp_status/depends_on) и `docs/AI-PROCESSES/STEP-1-IDEA/overview.md` (какие фазы активны).
4. Прочитай эталон `skills/prd-research/examples/ideal_idea_nodes.md`.

### Этап 1: PULSE — что уже есть
5. Прочитай `GROUND/NEXUS/_registry.yaml`; собери существующие узлы market/product/growth (frontmatter). Пусто → «Нексусы пусты, стартуем с нуля». Зафиксируй гэп в `journal.md`.

### Этап 2: SCOUT — 3 Линзы (диалог + desk-research)
Опрос PO по одному вопросу (паттерн okr-context-gen Этап 3), по трём Линзам методологии (docs/TRADITIONAL/RB-STEP-1-IDEA/2.1–2.3):
- **Линза Strategy:** «Какую большую цель/сдвиг ты хочешь этим продуктом? Для кого он и почему сейчас?»
- **Линза Business:** «Как это создаёт ценность, которую готовы оплачивать? Кто платит?»
- **Линза Product:** «Что конкретно продукт делает — в одном предложении (elevator pitch)?»
PO может ответить «не знаю» → узел `hyp_status: parked`, не выдумывать.
Если `discovery.web_research: true` и вопрос требует внешних фактов (тренд/аналог) → `WebSearch`/`WebFetch` (лёгкий) или предложи `/po-research` (тяжёлый); находку → источник узла с URL+датой, CP 0.5–0.7.

### Этап 3: BUNCH/PITCH — скоринг + под-дебаты
6. Сформулируй из ответов 3–6 гипотез (по Линзам). Для каждой — краткий скоринг (важность×неопределённость).
7. **Под-дебаты (опц., если PO хочет или гипотеза спорная):** проведи 1 раунд Адвоката Дьявола (паттерн okr-debate) на ключевую гипотезу → пересчитай CP, залогируй раунд в `journal.md`.

### Этап 4: HARVEST — запись узлов
8. Для каждой принятой гипотезы создай узел в соответствующем Нексусе (`GROUND/NEXUS/{market|product|growth}/<node_id>.md`) строго по frontmatter из `node_conventions.md`: `paf_step: 1`, `kind: empirical`, `hyp_status`, `confidence` по CP-шкале, `sources` (обязательно), `ttl_days` (growth=60, иначе 90), `ripeness: fresh`, `depends_on: []`. В тело — суть + пометка «⚠️ гипотеза discovery».
9. Обнови `{discovery_workspace(idea)}/state.yaml`: `nodes[]`, `cp` (среднее), `status` (`converging` или `gate-ready`), `open_questions[]`, `last_touched`. Допиши `journal.md`.

### Этап 5: СТОП
```
Step 1 (Idea): создано узлов N (market a / product b / growth c). Средний CP: X.
Гипотез на валидации: p · parked: q. Открытых вопросов: k.
── СТОП ── PO: проверь узлы, поправь формулировки/CP.
Дальше → /prd-customer (Step 2), либо /prd-research (доска), либо /prd-assemble (витрина).
```

## Запреты
1. Нет ответа PO и нет источника → `hyp_status: parked`, НЕ выдумывать гипотезу.
2. Узел без `sources` не создавать (workslop).
3. Не выдавай суждение PO за факт: CP 0.2–0.4, `hyp_status: hypothesis`.
4. Методология `docs/` — read-only. Пиши только в `GROUND/` + `{discovery_workspace}`.
