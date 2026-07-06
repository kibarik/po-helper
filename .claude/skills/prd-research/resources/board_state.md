# prd-research — состояние шага и доска

## `state.yaml` (на шаг) — `{discovery_workspace}/state.yaml`

```yaml
step: idea            # idea|customer|market|value|bizmodel|gtm|solution|acquisition
status: exploring     # exploring|debating|converging|gate-ready|revisit|planned
cp: 0.35              # средний CP узлов шага (для доски и гейтов)
open_questions:
  - "Кто именно первый платящий сегмент?"
nodes: ["idea-lens-market-1", "idea-lens-product-1"]  # node_id, созданные шагом
last_touched: 2026-07-06
```

## `journal.md` (на шаг) — `{discovery_workspace}/journal.md`
Свободный лог хода исследования: раунды дебатов, вердикты, ссылки на web-находки, решения PO. Append-only.

## Алгоритм рендера доски (что делает `/prd-research` на входе)
1. Прочитать `GROUND/NEXUS/_registry.yaml`.
2. Для каждого из 8 шагов прочитать `{discovery_workspace(step)}/state.yaml` (нет файла → status `planned`, cp 0).
3. Вывести таблицу: `Шаг | Статус | CP | Открытых вопросов | Гейт`.
4. **Рассогласование:** собрать все узлы с `ripeness: wilting`, у которых непустой `depends_on` → строка «⚠️ рассинхрон: узел X (Step N) устарел, зависит от изменённого Y (Step M)».
5. Рекомендовать следующий шаг: первый со статусом `planned`/`revisit`, иначе шаг с наименьшим CP.

## Расчёт рассогласования (при записи узла стадией)
При обновлении узла-первопричины: найти все узлы во всех Нексусах, где его `node_id` ∈ `depends_on`, проставить им `ripeness: wilting`. (Phase 1: стадия делает это Grep-обходом vault; узлы читаются по frontmatter.)
