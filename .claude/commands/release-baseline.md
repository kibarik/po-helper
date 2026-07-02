---
description: 'Release Guard фаза Setup — фиксация версионируемого нуля релиза (роль: Baseline Setter)'
---

## Использование

```
/release-baseline <release-id>
```

Вход: `artefacts/frame.md` (стадия `/release-frame`). Выход: `{release_workspace}/<release-id>/baseline.md` (v1).

## Важно

**Роль: Baseline Setter.** Фиксирует **нуль**, относительно которого потом меряется дрейф. Без зафиксированного нуля «+2 спринта» неизмеримы. Это главный артефакт релиза.

> Без `/release-frame` запрещён — нужен зафиксированный заказчик и форма обязательства.

---

## Инструкция для LLM

### Этап 1: Загрузка
1. Прочитай `skills/release-guard/SKILL.md`.
2. Прочитай `skills/release-guard/resources/release_standards.md` (§1 единицы, §3 схема baseline).
3. Прочитай `skills/release-guard/resources/hard_gates.md` (10 гейтов).
4. Прочитай `{release_workspace}/<release-id>/artefacts/frame.md`.
5. Прочитай `.claude/domain-profile.md` — `release`, `cadence.sprint_weeks`, `tracker`, `stakeholders`, риск-реестр (`cortex` если есть).

### Этап 2: Состояние эпика из трекера
Через `{tracker.mcp}` (если доступен):
- Прочитай `tracker_epic` + дочерние задачи: ключи, заголовки, оценки, статусы.
- Заполни ими трекинг-таблицу требований.
- Недоступно → `[НЕДОСТУПНО: трекер]`, требования заполняются из ответов PO.

### Этап 2.5: GROUND NEXUS — грунтовка обязательства
Прочитай `GROUND/NEXUS/_registry.yaml` и релевантные Узлы ключевых Нексусов релиза (матрица — `sa_documentation/nexus_process_map.md`, колонка `/release-baseline`):
- `capacity` — velocity/доступная capacity/cost of delay: реалистична ли оценка и буфер (Этап 4).
- `compliance` — NFR-бейзлайн, security/legal: часть DoR (Q2) и Scope (нельзя выкатить без этих критериев).
- `strategy` — приоритет релиза относительно OKR квартала: обоснование обязательства.

Каждый факт ← якорь `(NEXUS:<slug>)`, учитывай CP/`ripeness`. Нексус пуст → `[УТОЧНИТЬ: нет в <slug>]`, не выдумывай.

### Этап 3: Опрос PO (один вопрос за раз) — добор недостающего
**Q1 (границы OUT):** «Что точно НЕ входит в релиз? Назови 2-3 вещи, которые могут попытаться "всунуть".» (Scope OUT — критичный гейт 5.)

**Q2 (DoR):** «По каким критериям мы поймём, что это можно ВЫКАТИТЬ, а не просто "написали код"? (прод, сверка, нагрузка, фискализация…)»

**Q3 (оценка):** «Суммарная оценка в `{estimate_unit}`? Кто её дал? Если оценки нет — фиксируем как Intent.»

**Q4 (буфер/риски):** «Какие заложенные риски и на сколько спринтов закладываем буфер? (ссылки в риск-реестр)»

**Q5 (получатели алертов):** «Кому уходит алерт, если дрейф превысит порог?»

### Этап 4: Расчёт параметров
- `sprint_capacity`, `sync_period_days` — из `cadence`/`release` профиля (см. standards §1).
- `drift_threshold`, `staleness_n` — из профиля (дефолт 2/2).
- Сконвертируй `estimate_baseline` и `contingency_buffer` в спринты для согласованности.

### Этап 5: Сборка baseline.md
Заполни схему из `release_standards.md` §3 (фронтматтер + Scope IN/OUT + DoR + трекинг-таблица). `version: 1`, `status: active`. Каждый ключевой факт → `sources`.

### Этап 6: Прогон hard gates
Прогони 10 гейтов (`hard_gates.md`). Выведи Светофор.
- 🔴 (нарушен 1–6) → НЕ фиксируй, верни PO список незаполненного.
- 🟡/🟢 → фиксируй.

### Этап 7: Сохранение + STOP
- Сохрани через `obsidian.vault_write` в `{release_workspace}/<release-id>/baseline.md`.
- Инициализируй пустой `change-log.md` (шапка таблицы) и `ledger.md` (band 🟢, дрейф 0).
- **Выведи и ОСТАНОВИСЬ:**
  ```
  Baseline v1 зафиксирован: {release_workspace}/<release-id>/baseline.md
  Светофор: 🟢/🟡/🔴 (гейты: N/10 ✅)
  Объём: <est> <unit> + буфер <buffer> сп. Порог дрейфа: <threshold> сп.
  Уровень: <level> (<mode>).
  ── СТОП ── PO: это зафиксированный нуль. Дальше:
    • требования → /bft-context-gen <epic> (bft-writer)
    • мониторинг → /release-sync <release-id> (на cron)
  ```

## Запреты
1. НЕ фиксируй baseline при 🔴 — нуль с дырами обесценит весь дрейф.
2. НЕ выдумывай оценку, если PO её не дал — фиксируй `Intent` + `[УТОЧНИТЬ]`.
3. НЕ оставляй Scope OUT пустым — без границы дрейф неизбежен.
