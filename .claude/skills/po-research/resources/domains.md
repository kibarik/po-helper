# Domain Presets — po-research

> Пресет по домену: какие источники дёргать + seed sub-Q + разделы pack (оси coverage) + порог. Planner берёт subset → не дёргает всё подряд. Источники — см. `source-registry.md`.

## Сводка

| Domain | trigger | порог coverage | источники (пресет) |
|---|---|---|---|
| `sprint` | sprint-id (`2026Q3-S3`) | 75% | jira, vault, conf |
| `epic` | jira_key (`PROJ-101`) | 80% | jira, conf, code, vault |
| `bft` | epic_code + jira_key | 80% | как `epic` + vault(БФТ/СА) |
| `risk` | topic / risk-id | 95% | jira, conf, vault, code |
| `decision` | topic | 80% | vault, conf, jira, code |

Зависимости — **hard-gate** во всех доменах: незакрытая → обязательно `[УТОЧНИТЬ]`, не «не covered».

**Слой фактов = GROUND Нексусы.** Помимо `jira`/`conf`/`code`/`vault`, каждый пресет грунтуется релевантными Узлами из `GROUND/NEXUS/` (реестр — `GROUND/NEXUS/_registry.yaml`, источник истины по составу). В пресете строка **NEXUS** перечисляет ключевые Нексусы домена (якорь `R2` = путь `GROUND/NEXUS/<slug>/…`). Полная матрица «Нексус × Процесс» — `sa_documentation/nexus_process_map.md`. Нексус пуст → `[УТОЧНИТЬ: нет в <slug>]`, не выдумывать.

---

## `sprint`

- **Источники:** `jira`(epics/tasks/sprint), `vault`(INDEX/KR-MAP/факт пред.), `conf`.
- **NEXUS:** `capacity`(velocity/ёмкость/cost of delay) · `ownership`(зависимые команды/согласования) · `strategy`(KR квартала) · `precedents`(перенос/техдолг).
- **Разделы pack (оси coverage):** Цели/KR · Кандидаты беклога · Capacity · Зависимости · Риски · Перенос с пред. спринта.
- **Seed sub-Q:**
  - Какие KR приоритета Critical/High в фокусе квартала? → `vault(INDEX/KR-MAP)`
  - Какие эпики/задачи релевантны этим KR и проходят DoR? → `jira("Epic Link" in ...)`
  - Что не закрыто из прошлого ФАКТ (перенос)? → `vault(факт пред. спринта)`
  - Какая capacity (отпуска, занятость)? → `vault` + `[УТОЧНИТЬ у PO]`
  - Какие зависимости между командами (API-слой↔Шина↔Процессинг↔BI)? → `jira(links)` + `vault`
  - Какие риски спринта? → `jira(blockers)` + `[УТОЧНИТЬ у PO]`

## `epic`

- **Источники:** `jira`(epic+children+links), `conf`(TZ), `code`(blast/decisions), `vault`(BR/ADR из базы знаний).
- **NEXUS:** `system-landscape`(границы/API/что есть vs строить) · `ownership`(владельцы доменов/согласования) · `precedents`(похожие/техдолг) · `compliance`(NFR/security/legal).
- **Разделы pack:** Границы системы · Образ результата (БТ) · ПТ/ФТ · НФТ · Зависимости/блокеры · Регуляторика · Принятые решения.
- **Seed sub-Q:**
  - Какие границы системы затрагивает эпик? → `code(get_risk)` + `conf(TZ)` + `vault(C1)`
  - Каков образ результата? → `conf(TZ)` + `jira(epic desc)`
  - Какие зависимости/блокеры? → `jira(links)` + `vault(KR-EPIC-MAP)`
  - Какие регуляторные ограничения? → `vault(C3)` + `conf`
  - Какие решения уже приняты? → `vault(ADR)` + `code(get_why)` + `conf`

## `bft`

- **Источники:** как `epic` + `vault`({bft_store} / смежные СА).
- **NEXUS:** полный набор intake→БФТ — `problem`(проблема, не симптом) · `system-landscape` · `ownership` · `requester-domain`(KPI заказчика) · `precedents` · `compliance`. Это те же Нексусы, что грунтуют `/bft-context-gen` (см. `nexus_process_map.md`).
- **Разделы pack:** наследует матрицу `bft-context-gen` — Границы · БТ · ПТ · ФТ · НФТ · Negative flows · Риски/Compliance · Зависимости (см. `README базы знаний`).
- **Seed sub-Q:** как `epic` + «Какие смежные БФТ/СА уже описывают аспект?» → `vault({bft_store}, {cortex.sa_store})`.
- **Примечание:** это текущая матрица `bft-context-gen`, обобщённая. Артефакт совместим.

## `risk`

- **Источники:** `jira`(blockers/links), `conf`(incidents), `vault`(реестр рисков), `code`(get_risk/hotspots).
- **NEXUS:** `system-landscape`(blast radius/зависимости) · `ownership`(владелец риска) · `compliance`(регуляторный impact) · `precedents`(прошлые инциденты/решения).
- **Разделы pack:** Вероятность · Impact · Триггеры · Mitigation · Владелец · Связанные инциденты.
- **Порог 95%** — риск требует максимального покрытия.
- **Seed sub-Q:**
  - Какова вероятность реализации? → `code(get_risk)` + `jira(история)` + `[УТОЧНИТЬ у владельца]`
  - Каков impact (системы/деньги/SLA)? → `code(blast)` + `conf(incidents)`
  - Какие триггеры/предвестники? → `conf(incidents)` + `vault`
  - Какая mitigation планируется/есть? → `vault(реестр)` + `jira`
  - Кто владелец риска? → `vault` + `[УТОЧНИТЬ у PO]`

## `decision`

- **Источники:** `vault`(ADR-реестр), `conf`(meeting/decisions), `jira`(related), `code`(get_why).
- **NEXUS:** `precedents`(прошлые решения/отказы) · `strategy`(связь с OKR) · `ownership`(кто решает) · `system-landscape`(последствия для систем).
- **Разделы pack:** Контекст/проблема · Варианты · Trade-off · Принятое решение · Последствия · Открытые вопросы.
- **Seed sub-Q:**
  - В чём проблема/контекст решения? → `conf(meeting)` + `vault(ADR)`
  - Какие варианты рассматривались? → `vault(ADR)` + `conf`
  - Каков trade-off вариантов? → `code(get_why)` + `conf`
  - Что решено и кем? → `vault(ADR)` + `[УТОЧНИТЬ у PO]`
  - Какие последствия/открытые вопросы? → `jira(related)` + `vault`

---

## Phase 0 seed-вопросы (опрос PO перед Deep)

> Deep не гонится «вообще по топику» — сначала опрос PO (по 1 вопросу, как `sprint-planning` Шаг 1). Ответы собираются в `seed` → planner приоритизирует sub-Q вокруг образа результата PO, а не автономно. PO может прервать опрос фразой «достаточно» → идём с тем что есть. Поля, на которые ответ «не знаю / [УТОЧНИТЬ]» → пустые в seed, Deep по ним работает автономно (fallback на пресет). Честность важнее додумывания.
>
> Для routine-Deep — краткая форма: один вопрос `intent` + запрос `known_anchors`. Остальное — дефолт пресета.

Каждый домен — 5 вопросов, мапятся на поля `seed` (`intent` / `hypotheses` / `scope` / `risks` / `known_anchors`). Задавай по одному, в порядке убывания ценности.

### `sprint`
- **intent:** Какой образ результата ты хочешь от команды за этот спринт?
- **scope:** Какие KR в фокусе квартала, какие явно вне?
- **hypotheses:** Какие допущения/гипотезы лежат в основе плана?
- **risks:** Какие риски спринта видишь (зависимости команд, capacity, блокеры)?
- **known_anchors:** Какие эпики/задачи точно релевантны? (jira-key)

### `epic`
- **intent:** Какую ценность/результат должен принести эпик?
- **scope:** Границы системы — что затрагиваем, что точно нет?
- **hypotheses:** Какие технические/продуктовые гипотезы заложены?
- **risks:** Какие блокеры/зависимости известны заранее?
- **known_anchors:** JIRA-ключи, Confluence pageId, ADR — что точно релевантно?

### `bft`
- **intent:** Какой образ результата бизнес-требования? Что считаем выполненным?
- **scope:** Какие типы страниц/сущностей в фокусе, какие вне?
- **hypotheses:** Гипотеза ценности / поведения пользователя?
- **risks:** Compliance / регуляторика / безопасность (XSS, ПДн) видишь?
- **known_anchors:** JIRA, Confluence, commit, BR-ID, ADR — что точно релевантно?

### `risk`
- **intent:** Какое решение по риску нужно от исследования?
- **hypotheses:** Твоя оценка вероятности и impact на сегодня?
- **scope:** Какие системы / SLA / деньги в зоне риска?
- **risks:** Триггеры / предвестники известны?
- **known_anchors:** Инциденты, JIRA-блокеры, код-хотспоты — что точно релевантно?

### `decision`
- **intent:** Какое решение нужно принять по итогам исследования?
- **hypotheses:** Какие варианты уже видишь?
- **scope:** Что в контексте решения, что вне?
- **risks:** Какие trade-off / последствия беспокоят?
- **known_anchors:** ADR, meeting-notes, JIRA — что точно релевантно?

---

## Расширение (после Фазы 2, по спросу)

`incident`, `okr-review` — добавить, если PO начнёт запрашивать. Не плодить пресеты заранее (open Q #3, дефолт v0.2).
