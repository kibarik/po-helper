---
description: 'Release Guard фаза Run — регулярная синхронизация контекста и расчёт дрейфа; THE cron-команда (роль: Drift Monitor)'
---

## Использование

```
/release-sync <release-id>
```

Пример (cron): `/release-sync REL-PAY-SBP-Q3`

Вход: `baseline.md` + `change-log.md` + трекер. Выход: обновлённый `ledger.md`; при триггере — алерт в `{release_alerts_root}/`.

## Важно

**Роль: Drift Monitor. Это и есть регулярная команда** — ставится на cronjob (один прогон ≈ один спринт, см. `sync_period_days`). **Идемпотентна и без STOP:** гоняй сколько угодно, каждый прогон пересчитывает состояние и переписывает `ledger`. Алерт пишется только при пересечении порога или staleness — не на каждый прогон.

> Это сердце навыка: ранее предупреждение о дрейфе. Если эту команду не гонять — навык превращается в ручной чек-лист.

---

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `skills/release-guard/resources/release_standards.md` (§5 алгоритм, §6 ledger, §7 алерт).
2. Прочитай `{release_workspace}/<release-id>/baseline.md` (активная версия), `change-log.md`, предыдущий `ledger.md`.
3. Прочитай `.claude/domain-profile.md` — `tracker`, `release`.

### Этап 2: Чтение факта из трекера
Через `{tracker.mcp}`:
- Прочитай `tracker_epic` + дочерние: статусы, оценки, дату последнего изменения каждой задачи (→ `last_actualized`).
- Недоступен → возьми статусы из baseline-таблицы, в `ledger` пометь `tracker_status: "[НЕДОСТУПНО]"` (дрейф считается только по change-log, staleness — по датам из baseline).

### Этап 3: Расчёт дрейфа (строго по §5 standards)
1. `demand_drift` = Σ Δ строк change-log `lane=demand` для активной `baseline_ver`.
2. `supply_drift` = Σ Δ строк `lane=supply`.
3. `overflow = max(0, supply_drift − contingency_buffer)`; `buffer_remaining = max(0, contingency_buffer − supply_drift)`.
4. `total_drift = demand_drift + overflow`.
5. **Staleness:** по каждому требованию `missed = floor((now − last_actualized)/sync_period_days)`; `missed ≥ staleness_n` → в `stale_requirements`.
6. `band` по §6: 🟢 (drift 0 и нет stale) / 🟡 (0<drift<порог или буфер исчерпан или есть stale) / 🔴 (drift ≥ порог).

### Этап 4: Запись ledger
Перепиши `{release_workspace}/<release-id>/ledger.md` по схеме §6: фронтматтер с числами + таблица дрейфа по требованиям + допиши строку в «Историю синков».

### Этап 5: Триггер алерта
Алерт пишется, только если выполнено хотя бы одно И это **новое** состояние (не дублируй алерт того же типа/версии, если band не менялся с прошлого синка):
- `total_drift ≥ drift_threshold` → trigger `threshold`, band 🔴.
- `stale_requirements` непуст → trigger `staleness`, band ≥ 🟡.
- одиночное supply-событие > 1 спринта в этом синке → trigger `black_swan`.

Если триггер сработал:
- Собери алерт по схеме §7 (что пошло не так / разбивка с атрибуцией / зона риска / рекомендованное действие по `commitment_mode`).
- Рекомендованное действие: `date_fixed` → cut-<REQ>; `scope_fixed` → move-date; both → refuse/эскалация.
- Сохрани через `obsidian.vault_write` в `{release_alerts_root}/<release-id>-<YYYY-MM-DD>-<band>.md`.

### Этап 6: Вывод (без STOP)
```
sync <release-id> @ <ts>
drift: demand <D> + overflow <O> = total <T> сп. (порог <threshold>) → band <🟢|🟡|🔴>
буфер: <remaining>/<buffer> сп.  staleness: <N req в зоне риска>
[если алерт] 🚨 АЛЕРТ (<trigger>) → {release_alerts_root}/<file>
            → рекомендую: /release-gate <release-id>
```

## Запреты
1. НЕ выдумывай статусы, если трекер недоступен — честно `[НЕДОСТУПНО]`, считай по тому, что есть.
2. НЕ спам-алерть: один прогон при неизменном band не плодит новый алерт того же типа.
3. НЕ меняй baseline — это задача `/release-gate`. Sync только наблюдает и считает.
