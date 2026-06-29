# Release Guard — стандарты артефактов и алгоритм дрейфа

Единый источник правды по схемам и расчётам. Все команды `/release-*` ссылаются сюда, чтобы не расходиться в формулах.

---

## 1. Единицы и конвертация

Дрейф всегда измеряется и сравнивается с порогом **в спринтах**. Оценки могут вестись в другой единице — конвертируем.

| Поле baseline | Значение |
|---|---|
| `estimate_unit` | `sprint` \| `story_point` \| `dev_day` (из `release.estimate_unit` профиля) |
| `sprint_capacity` | сколько единиц `estimate_unit` = 1 спринт (для `sprint` → 1) |

**Конвертация:** `drift_sprints = delta_in_unit / sprint_capacity`.

Примеры `sprint_capacity`: для `story_point` = velocity команды (поинтов/спринт); для `dev_day` = `cadence.sprint_weeks × 5 × team_size`. Неизвестна velocity → `[УТОЧНИТЬ]`, обязательство понижается до `Intent`.

Период синка: `sync_period_days` (по умолчанию = `cadence.sprint_weeks × 7`, т.е. один синк = один спринт). `staleness_n` пропущенных синков = `staleness_n × sync_period_days` дней без актуализации.

---

## 2. Лестница обязательств

| Уровень | CP | Предусловие | Что обещаем |
|---|---|---|---|
| **Intent** | низкий | БФТ нет | дату **гейта дискавери**, не поставки |
| **Target** | средний | БФТ-черновик есть | диапазон **P50/P80** |
| **Commitment** | высокий | объём заморожен | жёсткую дату/объём; изменение = ре-baseline |

Форма обязательства (вершина iron triangle), фиксируется в `commitment_mode`:

| `commitment_mode` | Жёстко | Клапан при дрейфе |
|---|---|---|
| `date_fixed` | дата | режем объём |
| `scope_fixed` | объём | двигаем дату |
| `both_fixed` | ⚠ обе | **некоммитбельно** — `/release-frame` выдаёт встречку |

---

## 3. Схема `baseline.md`

YAML-фронтматтер + тело. При ре-baseline создаётся новая версия, старая помечается `status: superseded`.

```yaml
---
release:           <id>                # напр. REL-PAYMENTS-Q3
version:           1
date:              YYYY-MM-DD
status:            active              # active | superseded
requesters:        [<имя/роль>]        # КТО заказал (атрибуция)
cp:                low|med|high        # Confidence Point на момент фиксации
commitment_level:  intent|target|commitment
commitment_mode:   date_fixed|scope_fixed|both_fixed
fixed_date:        YYYY-MM-DD | null   # для date_fixed
estimate_unit:     sprint|story_point|dev_day
sprint_capacity:   1                   # единиц = 1 спринт
estimate_baseline: <value>             # суммарная оценка в estimate_unit
contingency_buffer: <sprints>          # из риск-реестра
drift_threshold:   2                   # спринтов до 🔴
staleness_n:       2                   # пропущенных синков → зона риска
sync_period_days:  14
alert_recipients:  [<роль/имя>]
tracker_epic:      <KEY>               # эпик-источник факта
risk_refs:         [<R1>, <R2>]        # ссылки в риск-реестр
sources:           ["<якорь>", ...]    # источник каждого ключевого факта
---

## Scope IN (границы)
- [REQ-1] <требование> — источник: <якорь>
- [REQ-2] ...

## Scope OUT (явно вне)
- <что НЕ входит> — почему

## Definition of Releasable
- [ ] <критерий отгружаемости 1>
- [ ] <критерий 2>
> Закладывается СЕЙЧАС, не обнаруживается в конце. Без DoR обязательство = Intent.

## Требования (трекинг-таблица)
| id | Заголовок | tracker_key | owner | est (unit) | status | last_actualized |
|----|-----------|-------------|-------|------------|--------|-----------------|
| REQ-1 | ... | PROJ-101 | <продакт> | 3 | in_progress | YYYY-MM-DD |
```

`owner` требования — тот, кто отвечает за актуализацию его статуса (обычно продакт-заказчик). По нему считается staleness.

---

## 4. Схема `change-log.md`

Таблица, одна строка на change request (demand-lane). Append-only.

```markdown
# Change Log — <release>

| id | дата | автор | описание | lane | Δ (unit) | решение | владелец последствия | baseline_ver |
|----|------|-------|----------|------|----------|---------|----------------------|--------------|
| CR-1 | YYYY-MM-DD | <продакт A> | +валидация по справочнику | demand | +0.5 | absorb | <продакт A> | 1 |
| CR-2 | YYYY-MM-DD | <риск R3> | сработал риск интеграции | supply | +0.4 | buffer | — | 1 |
| CR-3 | YYYY-MM-DD | 🦢 блокер БД | найдено при разработке | supply | +0.9 | move-date | <PO+стейкхолдер> | 1→2 |
```

- `lane`: `demand` (изменение требований) \| `supply` (риск/лебедь).
- `решение`: `absorb` (влезает в окно) \| `cut-<REQ>` (вырезали другое) \| `move-date` \| `defer` (следующий банч) \| `refuse` (осознанный отказ) \| `buffer` (supply съел буфер).
- `владелец последствия`: КТО принял трейд-офф. Для demand — автор запроса. Это политический якорь атрибуции.

---

## 5. Алгоритм `/release-sync` (расчёт дрейфа)

Идемпотентно. Каждый прогон:

1. Загрузить `baseline` (активная версия) + `change-log` + предыдущий `ledger`.
2. Прочитать текущее состояние требований из трекер-эпика + дочерних (`{tracker}`). Недоступно → взять статусы из baseline-таблицы, пометить `[НЕДОСТУПНО]`.
3. `demand_drift` = Σ Δ строк change-log с `lane=demand`, ещё не влитых в baseline (`baseline_ver` = текущая) — в спринтах.
4. `supply_drift` = Σ Δ строк с `lane=supply`.
5. Буфер: `overflow = max(0, supply_drift − contingency_buffer)`; `buffer_remaining = max(0, contingency_buffer − supply_drift)`.
6. `total_drift = demand_drift + overflow`.
7. **Staleness:** для каждого требования `missed = floor((now − last_actualized) / sync_period_days)`. `missed ≥ staleness_n` → требование в `stale_requirements`.
8. Определить `band` (см. §6). Записать `ledger`.
9. Триггер алерта (см. §7) → записать артефакт в `{release_alerts_root}/`.

### Светофор дрейфа (§6)

| Band | Условие |
|------|---------|
| 🟢 | `total_drift == 0` И `stale_requirements` пуст |
| 🟡 | `0 < total_drift < drift_threshold` ИЛИ буфер исчерпан (`buffer_remaining == 0`, overflow ещё < порога) |
| 🔴 | `total_drift ≥ drift_threshold` |

Staleness — **ортогональный** флаг: непустой `stale_requirements` поднимает band минимум до 🟡 и даёт отдельный триггер алерта (тип `staleness`), независимо от дрейфа.

---

## 6. Схема `ledger.md`

```yaml
---
release:          <id>
baseline_version: <n>
last_sync:        <ISO ts>
demand_drift:     <sprints>
supply_drift:     <sprints>
buffer_remaining: <sprints>
overflow:         <sprints>
total_drift:      <sprints>
band:             🟢|🟡|🔴
stale_requirements: [<REQ-id>, ...]
tracker_status:   ok | "[НЕДОСТУПНО]"
---

## Дрейф по требованиям
| REQ-id | owner | est | факт-статус | missed синков | дрейф (sprints) | флаг |
|--------|-------|-----|-------------|---------------|-----------------|------|

## История синков
| ts | total_drift | band | событие |
|----|-------------|------|---------|
```

---

## 7. Схема алерта

Файл: `{release_alerts_root}/<release>-<YYYY-MM-DD>-<band>.md`. Триггеры: `threshold` (total_drift ≥ порог), `staleness` (зона риска по увяданию), `black_swan` (одиночное supply-событие > 1 спринта).

```yaml
---
release:    <id>
date:       YYYY-MM-DD
trigger:    threshold | staleness | black_swan
band:       🔴 | 🟡
baseline_version: <n>
recipients: [<роль/имя>]
---

# 🚨 Алерт по релизу <id> — дрейф <total_drift> спринтов

## Что пошло не так
<1 абзац: суть, без воды>

## Разбивка дрейфа (атрибуция)
- demand-lane: <X> спринтов — авторы: <CR-id → продакт>
- supply-lane: <Y> спринтов (буфер <buffer> исчерпан на <Z>) — причины: <риск/лебедь>

## Зона риска
- Требования без актуализации ≥ N синков: <REQ-id → owner>
- Что под угрозой: <DoR-критерии / даты>

## Рекомендованное действие
→ /release-gate <id>: [ cut-<REQ> | move-date к <дата> | refuse ]
обоснование: <по commitment_mode>

## Получатели
<из alert_recipients>
```

---

## 8. Три метрики `/release-status`

| Метрика | Формула | Назначение |
|---|---|---|
| **Baseline-полнота** | `delivered_scope / current_baseline_scope` | честная полнота против актуальной версии |
| **Scope drift** | `(current_estimate − v1_estimate) / v1_estimate` (или в спринтах) | рост относительно первого нуля = качество входа бизнеса |
| **Commitment hit-rate** | доля релизов уровня `commitment`, выполненных в срок/объём | жёсткость меряем только на `Commitment` |

`delivered_scope` — требования в статусе Done/Released в трекере. Все три — с разбивкой по авторам change requests (кто сколько нагнал дрейфа).
