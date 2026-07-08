# PAF Loop Schema — Pulse / Bunch / Harvest узлы GROUND (мост)

> Единый словарь трёх loop-артефактов, материализующих цикл Product Sprint в `GROUND/PULSE|BUNCH|RESULTS`. Реализация моста из спеки `docs/superpowers/specs/2026-07-08-paf-loop-bridge-design.md`. Выровнено по каноническим `docs/AI-PROCESSES/STEP-*/{1.pulse,3.bunch,6.harvest}.md` и `4.progress-pulse.md`.
> **Все структурированные поля — во frontmatter** (машиночитаемо, проверяется `validate_ground.py`). Тело ноты — человеческая проза.

## Общее (все три артефакта)

Наследуют базовую Node schema ([[nexus_schema]] §2) + правила:

| Ключ | Значение |
|---|---|
| `node_type` | `sprint-phase` (не выдумывать новый тип) |
| `sprint_phase` | `pulse` \| `bunch` \| `harvest` |
| `kind` | `empirical` (контекст клиента, не методология) |
| `nexus` | первичная Линза цикла: `product` (Линза Продукта) \| `growth`/`market` (Бизнес/Стратегия) |
| `paf_step` | `null` (операционный цикл, не привязан к шагу) |
| `owner` | RACI Accountable: спринт → Product Engineer; harvest → +Growth Engineer; квартал → Portfolio Manager |
| `confidence` | float 0..1 (уровень доказательств) |
| `sources` | непустой список (нет источника = workslop) |
| `ttl_days` | ≈ длина окна (спринт=14) → wilting на границе окна = сигнал «пора Harvest» |
| `level` | `sprint` \| `quarter` |
| `cycle_ref` | идентификатор цикла (`S14`, `Q3`) |

## PULSE (`sprint_phase: pulse`, папка `PULSE/`)

Канонические 5 частей ([[docs/AI-PROCESSES/STEP-0-FOUNDATION/4.progress-pulse|4.progress-pulse]] §54):

| Ключ | Обяз. | Значение |
|---|---|---|
| `nexus_snapshot` | ✅ | map: `{<nexus>: {ripeness: <float>, gaps: [...]}}` — Context Ripeness **вычисляется** (не вписывается руками) |
| `gap_vs_vision` | — | разрыв текущего состояния и Vision |
| `intent` | ✅ | какую часть гэпа закрываем в цикле |
| `cp_start` | — | текущий CP ключевых гипотез |
| `lens` | ✅ | `product` \| `business` \| `strategy` (3PL) |

Правило: Pulse **не генерирует решения** (это Scout); не приукрашивать спелость/CP.

## BUNCH (`sprint_phase: bunch`, папка `BUNCH/`) — вместо беклога

| Ключ | Обяз. | Значение |
|---|---|---|
| `parent_bunch` | ✅ для `level: sprint` | ссылка на квартальный Банч (вложенность по ссылке) |
| `goal_map_ref` | — | под какую Карту Целей (OKR) сформирован |
| `bunch_size` | ✅ | лимит скорости восприятия рынка |
| `bunch_window` | ✅ | период ожидания результата |
| `items` | ✅ | непустой список; каждый: `ref` (ССЫЛКА на JIRA, не копия) + `kind` (`hypothesis`\|`feature`\|`mechanic` / `lever`\|`bet`) + `trace` (путь к узлу Нексуса — обязателен, нет → резервная) + опц. `vp_offer`, `initial_cp` (ICE/RICE 1–10) |
| `gate` | ✅ | Pitch-штамп: `{final_cp, cost_of_risk, decision}`; `decision` ∈ `commit`\|`defer`\|`refuse` (осознанный отказ) |
| `selection_rationale` | — | ① max mNSM ② min риск(CP) ③ эффект в окне |
| `npv_estimate` | — | число или `[УТОЧНИТЬ: growth тонкий]` |

Критерий выхода в Pitch: ≥3 items с трассировкой на ≥1 источник. Банч формируется заново каждый цикл из состояния Нексуса — беклог не воскресает.

## HARVEST (`sprint_phase: harvest`, папка `RESULTS/`) — урожай + writeback

| Ключ | Обяз. | Значение |
|---|---|---|
| `bunch_ref` | — | какой Банч собрали |
| `rolls_up_to` | ✅ для `level: sprint` | ссылка на квартальный Harvest |
| `outcomes` | — | `{cp_change (обяз. валюта L0), mNSM_delta (L1+), npv_actual (L2+)}` |
| `insights` | ✅ | что узнали |
| `nexus_writeback` | ✅ | **сердце моста**; непустой список; каждый: `{nexus, node, change, source}`. Пишется по Node schema: проставить `sources`, поднять `confidence`, обновить `updated` в целевом узле |
| `next_intent` | — | передача в следующий Pulse |

## Уровни зрелости метрик (прогрессивно, анти-workslop)

| Уровень | Разблокировка (вычисляемо) | Обязательно |
|---|---|---|
| L0 CP-only | `growth` тонкий | `cp_change`, `nexus_writeback`, `insights`; `npv/mNSM = [УТОЧНИТЬ]` |
| L1 mNSM | Context Ripeness `growth` ≥ 0.6 | `mNSM_delta`, ребро mNSM→NPV |
| L2 NPV/дерево | Business Sprint активен | композитный NPV Ставок, дерево метрик |

## Bridge-отклонения от чистого PAF (зафиксировано)

1. Pulse привязан к Scrum-каденции (канон: event-based/Kanban).
2. Pitch — штамп `gate` на Банче, не отдельная фаза.
3. Scout свёрнут в `po-research` + гэп-идентификацию Pulse.

**Version:** 1.0 · **Связанные:** [[nexus_schema]] · [[nexus_process_map]] · [[docs/AI-PROCESSES/operating-model|operating-model]]
