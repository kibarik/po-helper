---
description: 'Discovery-оркестратор — доска 8 шагов Product Discovery: статусы/CP/рассинхроны + навигация (роль: Discovery Facilitator)'
---

## Использование

```
/prd-research            # показать доску и рекомендацию следующего шага
/prd-research init       # инициализировать состояние discovery (первый запуск)
```

Вход: наполненность Нексусов + `{discovery_workspace}/*/state.yaml`. Выход: доска + рекомендация.

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `skills/prd-research/SKILL.md`.
2. Прочитай `skills/prd-research/resources/board_state.md` (алгоритм доски) и `pipeline.md` (8 шагов).
3. Резолвни `{discovery_workspace}` из `.claude/domain-profile.md` (пусто → дефолт `CORTEX/_context-packs/discovery/{step}` + `[УТОЧНИТЬ]`).

### Этап 2: init (только для `/prd-research init`)
4. Прочитай `GROUND/NEXUS/_registry.yaml`.
5. Для каждого из 8 шагов создай `{discovery_workspace(step)}/state.yaml` со `status: planned`, `cp: 0`, пустыми `nodes`/`open_questions` (шаблон — board_state.md).
6. Выведи: «Discovery инициализирован. 8 шагов, все planned. Начни с /prd-idea».

### Этап 3: Рендер доски (для `/prd-research` без аргумента)
7. По алгоритму board_state.md §«Алгоритм рендера»: собери статусы 8 шагов, выведи таблицу `Шаг | Статус | CP | Откр.вопросов | Гейт`.
8. Собери рассинхроны (узлы wilting с непустым depends_on) → отдельным блоком «⚠️ Рассогласование».
9. Дай рекомендацию следующего шага.

### Этап 4: СТОП
```
Доска discovery: <таблица>
⚠️ Рассинхроны: <список или «нет»>
Рекомендую: <next step команда>
── СТОП ── PO: выбери шаг (/prd-idea …) или /prd-assemble для витрины.
```

## Запреты
1. НЕ наполняй Нексусы на этой команде — это задача стадий `/prd-*`.
2. Нет `state.yaml` шага → status `planned`, не выдумывай прогресс.
3. Методология `docs/` — read-only.
