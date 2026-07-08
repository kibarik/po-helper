# Spec — PAF Loop Bridge: замыкание петли Pulse→Bunch→Harvest

> **Цель:** достроить недостающий движок Product Sprint в po-helper так, чтобы «спелый контекст превращался в поставку по-PAF» — материализовать пустые `PULSE/BUNCH/RESULTS` и замкнуть обратную запись в Нексус, **не ломая** корпоративную спину поставки (OKR→Scrum→БФТ→Release).
> **Подход:** мост (эволюция), не замена. Врезаем PAF-фазы в существующие швы корп-пайплайна.
> **Status:** design approved 2026-07-08 (диагноз → целевая модель «мост» → топология «два вложенных уровня» → схемы выровнены по канону). → `writing-plans`. · implemented 2026-07-08 (план docs/superpowers/plans/2026-07-08-paf-loop-bridge.md)
> **Ветка:** `fix/context-architecture-update`.

---

## 0. Ретроспективный диагноз (обоснование)

Дрейфа «от изначальной архитектуры» в строгом смысле **не было**. Движок Product Sprint (Pulse→Scout→Bunch→Pitch→Execute→Harvest) **никогда не был реализован** — он живёт только в нормативном каноне `docs/AI-PROCESSES`, но был сознательно вынесен за scope первой спеки сборки [2026-06-21-paf-team-os-design.md](2026-06-21-paf-team-os-design.md).

Два расходящихся источника истины:

| Слой | Предписывает | Статус |
|---|---|---|
| Нормативный канон (`operating-model.md`, `fit-points.md`, `STEP-*/{1.pulse,3.bunch,6.harvest}.md`) | Банч вместо Беклога, цикл 6 фаз, 3 Линзы, mNSM/NPV/CP | Эталон `confidence: 1.0` |
| Спека сборки v3 (§11 scope, §13 «done») | только `/paf-init` + `/paf-nexus-create` + `/paf-onboard` + Нексус-каталог | То, что построили |

Улика — критерий готовности §13: «…GROUND насыщен → открыл `STEP-1-IDEA/overview` → **начал Product Sprint** [вручную]». `PULSE/BUNCH/RESULTS` заведены как пустой скелет (§4, §8); ни один скилл в scope не назначен их наполнять.

Хронология (git): после «левой половины» вся правая (21.06 БФТ · 24.06 OKR · 29.06 intake/sprint/release) — **корпоративная спина**, ни одна итерация не замкнула PAF-цикл. Подтверждено grep: **ни один скилл не пишет в `BUNCH/`/`RESULTS/`**; `PULSE/` наполняют только `paf-init` (init-пульс) и `summary` (саммари); [nexus_process_map.md](../../../sa_documentation/nexus_process_map.md) §4 перечисляет 5 процессов-писателей — все в Нексусы, ни один в Pulse/Bunch/Results (разрыв закреплён в проектной матрице).

**Вывод:** «работаем только с нексусами», потому что построили только то, что вокруг нексусов, а не движок, проворачивающий их в поставку.

---

## 1. Решения (зафиксированы)

| Развилка | Решение |
|---|---|
| Целевая модель | **Мост**: сильный Nexus-слой + корп-спина остаются; достраиваем недостающие фазы (Progress Pulse, Bunch, Harvest) и связываем OKR/Sprint/БФТ с PAF-циклом. Эволюция, не ломка. |
| Уровень Банча | **Два вложенных уровня**: квартальный крупный Банч (Ставки, Линзы Бизнеса/Стратегии) + вложенные спринтовые Банчи (Линза Продукта). |
| Механизм | **Аддитивный**: материализация артефакта + обратная запись врезаются в существующие стадии, не новый параллельный пайплайн. |
| Глубина метрик | **Прогрессивно** (L0 CP-only → L1 mNSM → L2 NPV/дерево), разблокировка по вычисляемой Context Ripeness. Никаких выдуманных чисел (анти-workslop). |

---

## 2. Топология вложенной петли

Два цикла, вложенных по Bunch Window, оба замыкаются в Нексус:

```
КВАРТАЛ (Линза Бизнеса/Стратегии) ── Window = квартал
  okr-context-gen ──▶ PULSE/Q{n}-pulse       снимок Нексусов рынка/роста → intent квартала
  okr-deliver     ──▶ BUNCH/Q{n}-bunch        связка Ставок (Bets/Рычагов), Size/Window, mNSM/NPV/CP
        │                    ▲
        │  порождает         │ rollup урожая
        ▼                    │
  СПРИНТ (Линза Продукта) ── Window = спринт
    sprint-sync   ──▶ PULSE/S{n}-pulse         снимок Нексуса продукта → intent спринта
    sprint-deliver──▶ BUNCH/S{n}-bunch         связка фич/гипотез, parent = Q-bunch, Size/CP
    sprint-fact   ──▶ RESULTS/S{n}-harvest      факт + NPV/mNSM/инсайты → запись в Нексус
        └──────────────────▶ вход следующего sprint-sync (петля уже декларирована)
  конец квартала:
  /sprint-harvest-quarter ──▶ RESULTS/Q{n}-harvest  rollup → Нексус рынка/роста → intent Q+1
```

**Три принципа связывания:**
1. **Вложенность по ссылкам, не по копированию** — `S-bunch.parent_bunch: Q{n}`, `S-harvest.rolls_up_to: Q{n}-harvest`. Квартальный Банч = Карта Целей (Goal Map, ← OKR); спринтовый формируется под неё из текущего Нексуса.
2. **Аддитивность** — врезаемся в 5 существующих швов + 1 новая стадия квартального Harvest.
3. **Обе петли замыкаются в Нексус** — спринтовый Harvest пишет в `product`, квартальный в `market`/`growth`. Это и есть недостающее «контекст → поставка → контекст».

---

## 3. Схемы артефактов (выровнены по канону)

Все три = `node_type: sprint-phase` + дискриминатор `sprint_phase` + `kind: empirical` (отличие от нормативных STEP-нот, которые `normative`). Наследуют базовую Node schema ([nexus_schema.md](../../../sa_documentation/nexus_schema.md) §2): `nexus`, `node_id`, `paf_step`, `owner`, `confidence`, `sources`, `updated`, `ttl_days`, `ripeness`. Единый словарь — новый read-only канон `sa_documentation/paf_loop_schema.md`.

### 3.1 PULSE-узел (`GROUND/PULSE/{Q|S}{n}-pulse.md`)
Канонические 5 частей ([4.progress-pulse.md](../../../docs/AI-PROCESSES/STEP-0-FOUNDATION/4.progress-pulse.md) §54):
```yaml
nexus: product              # первичная Линза цикла (product|growth|market)
node_type: sprint-phase
sprint_phase: pulse
paf_step: null
kind: empirical
owner: Product Engineer
# --- тело ---
level: quarter | sprint
cycle_ref: S14 | Q3
nexus_snapshot:             # Context Ripeness ВЫЧИСЛЯЕТСЯ формулой (§4 схемы), не вписывается руками
  product: {ripeness: 0.72, gaps: ["mNSM-гипотеза не валидирована"]}
  growth:  {ripeness: 0.30, gaps: [...]}
gap_vs_vision: "разрыв между текущим и Vision"
intent: "какую часть гэпа закрываем в этом цикле"
cp_start: "текущий CP ключевых гипотез"
lens: product | business | strategy      # 3PL
```
Правила: Pulse **не генерирует решения** (это Scout); метапознание — не приукрашивать Context Ripeness/CP.

### 3.2 BUNCH-узел (`GROUND/BUNCH/{Q|S}{n}-bunch.md`) — вместо беклога
```yaml
nexus: product
node_type: sprint-phase
sprint_phase: bunch
paf_step: null
kind: empirical
owner: Product Engineer     # квартальный → Portfolio Manager
confidence: 0.4
sources: ["OKR-Q3", "sprint-deliver:S14"]
ttl_days: 14                # ≈ Bunch Window → wilting на границе окна = сигнал «пора Harvest»
# --- тело ---
level: sprint
parent_bunch: bunch-q3      # вложенность по ссылке (только sprint)
goal_map_ref: OKR-Q3
bunch_size: 5               # лимит скорости восприятия рынка
bunch_window: sprint-14     # период ожидания результата
items:
  - ref: PROJ-123           # ССЫЛКА на JIRA, не копия
    kind: hypothesis        # sprint: hypothesis|feature|mechanic · quarter: lever|bet
    vp_offer: "..."         # оффер (продукт-уровень), ≠ ценность
    trace: "GROUND/NEXUS/product/feature-x.md"   # ОБЯЗАТЕЛЬНО: нет источника → резервная
    initial_cp: 3           # ICE/RICE 1–10, старт низкий
gate:                       # Pitch-штамп из sprint-deliver/okr-validate гейтов
  final_cp: 0.5
  cost_of_risk: "..."
  decision: commit          # commit | defer→next bunch | refuse (осознанный отказ)
selection_rationale: "① max mNSM ② min риск(CP) ③ эффект в окне → композитный NPV"
npv_estimate: "..." | "[УТОЧНИТЬ: growth тонкий]"
```
Критерий выхода в Pitch: ≥3 items с трассировкой на ≥1 источник. Банч формируется заново каждый цикл из состояния Нексуса — беклог не появляется.

### 3.3 RESULTS-узел (`GROUND/RESULTS/{Q|S}{n}-harvest.md`) — урожай + writeback
```yaml
nexus: product
node_type: sprint-phase
sprint_phase: harvest
paf_step: null
kind: empirical
owner: Product Engineer     # + Growth Engineer (владелец mNSM); квартальный → Portfolio Manager
# --- тело ---
level: sprint
cycle_ref: S14
bunch_ref: bunch-s14
rolls_up_to: harvest-q3     # только sprint
outcomes:
  cp_change: "+0.2 (гипотеза X валидирована)"   # ОБЯЗАТЕЛЬНО (валюта L0)
  mNSM_delta: "..." | "[УТОЧНИТЬ]"              # L1+
  npv_actual: "..." | "[УТОЧНИТЬ]"              # L2+
insights: ["..."]                               # ОБЯЗАТЕЛЬНО
nexus_writeback:                                # ← СЕРДЦЕ МОСТА, обязательное
  - {nexus: product, node: "feature-x", change: "cp 0.4→0.6", source: "harvest-s14"}
next_intent: "вход в S15-pulse"
```
`nexus_writeback` пишется по правилам Node schema (проставить `sources`, поднять `confidence`, обновить `updated`). Без него — результат в доке, а не в контексте.

---

## 4. Как строим: аддитивно (scope сборки)

Не создаём параллельный пайплайн. Итого — 1 новый канон, 5 расширенных стадий, 1 новая стадия, 1 расширение валидатора.

**Новый read-only канон:**
1. `sa_documentation/paf_loop_schema.md` — единый словарь Pulse/Bunch/Harvest (§3) + правила вложенности + контракт `nexus_writeback`.
2. UPDATE `sa_documentation/nexus_process_map.md` §4 — добавить `PULSE/BUNCH/RESULTS` как write-targets (сейчас только Нексусы — закреплённый разрыв).

**5 расширяемых швов** (добавить материализацию + writeback, не переписывать стадию):

| Шов (существующий) | Добавляем | Артефакт |
|---|---|---|
| `sprint-sync` (РЕСИНК) | снимок Нексуса как Pulse-узел | `PULSE/S{n}-pulse.md` |
| `sprint-deliver` (ПЛАН + гейты) | обёртка плана в Банч + gate-штамп (Pitch) | `BUNCH/S{n}-bunch.md` |
| `sprint-fact` (velocity) | урожай + `nexus_writeback` в `product` | `RESULTS/S{n}-harvest.md` |
| `okr-context-gen` (стратег-контекст) | квартальный Pulse (рынок/рост) | `PULSE/Q{n}-pulse.md` |
| `okr-deliver` (публикация OKR) | Банч Ставок под Goal Map | `BUNCH/Q{n}-bunch.md` |

**1 новая стадия** (нет хоста сейчас):
- `/sprint-harvest-quarter` (или под-режим okr-скилла) — конец квартала: rollup спринтовых урожаев → `RESULTS/Q{n}-harvest.md` → writeback в `market`/`growth` → `next_intent` для Pulse Q+1.

**1 расширение:**
- `sa_documentation/validate_ground.py` + фикстуры (`ground_ok`/`ground_bad`) — принимать empirical sprint-phase артефакты в `PULSE/BUNCH/RESULTS`; проверять обязательные поля (`nexus_writeback` у harvest, `gate.decision` у bunch, `parent_bunch`/`rolls_up_to` у вложенных).

Почему так: каденция остаётся лёгкой (материализация «падает» из стадий, которые PO и так гоняет); writeback становится частью гейта `sprint-fact` — забыть замкнуть петлю физически нельзя.

---

## 5. Глубина метрик: прогрессивно, анти-workslop во главе

`growth`/`market` Нексусы тонкие → требовать полный NPV/mNSM сейчас = фабриковать = workslop (канон запрещает, [6.harvest.md](../../../docs/AI-PROCESSES/STEP-4-VALUE/6.harvest.md) §123). Три уровня, поле есть всегда, наполнение по спелости:

| Уровень | Когда (вычисляемо) | Что обязательно |
|---|---|---|
| **L0 — CP-only** | `growth` тонкий | `cp_change`, `nexus_writeback`, `insights`. `npv/mNSM = [УТОЧНИТЬ]`. Петля работает на CP. |
| **L1 — mNSM** | `growth` ripeness ≥ 0.6 | `mNSM_delta`, ребро mNSM→NPV. Разблокируется само. |
| **L2 — NPV/дерево** | Business Sprint активен | композитный NPV Ставок, дерево метрик. Линза Бизнеса. |

Правило: артефакт коммитится с честным `[УТОЧНИТЬ]`, **не** с выдуманным числом. CP (уже дисциплинирован) — достаточная валюта L0. Гейт разблокировки — вычисляемая Context Ripeness (формула §4 схемы), не ручной флаг.

---

## 6. Границы scope (YAGNI)

| Не делаем | Почему | Маппинг вместо этого |
|---|---|---|
| **Scout** как отдельная фаза/скилл | скаутинг уже есть | `po-research` + идентификация гэпа в Pulse |
| **Pitch** как отдельный пайплайн | защита+CP-гейт реализованы | штамп `gate` на Банч из `sprint-deliver`/`okr-validate` |
| **Bale / Germination** | территория Execute-поставки | `release-guard` (не трогаем) |
| **Переназначение ролей-владельцев** | конфиг vault'а, не каркаса | квартальная петля = дом для Линз; владелец — в `config.yaml` PO |
| **Полное дерево метрик + A/B** на спринт | тяжело и без данных = workslop | уровень L2 по спелости |
| **Event-based/Kanban Pulse** | ломает корп-каденцию | sprint-каденция (bridge-deviation, §7) |
| **Бэкфилл истории** | ретро-урожаи = выдуманные данные | петля стартует «вперёд» |
| **Миграция реального vault'а** | отдельная задача поверх моста | follow-on после мержа |

Не убираем и не подчиняем OKR/Scrum/БФТ — мост, не замена.

---

## 7. Честные отклонения от канона (bridge-deviations)

Фиксируем явно, не прячем:

1. **Pulse привязан к Scrum-каденции.** Канон предписывает event-based/Kanban, Pulse НЕ привязан к каденциям ([4.progress-pulse.md](../../../docs/AI-PROCESSES/STEP-0-FOUNDATION/4.progress-pulse.md) §129, анти-workslop). Мост привязывает Pulse к границе спринта — сознательный компромисс сохранения корп-спины.
2. **Pitch не отдельная фаза, а штамп на Банче.** Канон даёт `4.pitch` отдельной фазой; мост сворачивает её в `gate`-блок Банча из существующих гейтов. Осознанный отказ сохранён (`gate.decision: refuse`).
3. **Scout свёрнут** в `po-research` + гэп-идентификацию Pulse, не отдельная фаза генерации opportunities/threats.

Эти отклонения — цена выбора «мост, а не чистый PAF-движок». Они документируются в `paf_loop_schema.md`, чтобы будущий переход к чистому PAF (если понадобится) знал, что достраивать.

---

## 8. Готовность = «done»

- `paf_loop_schema.md` создан; `nexus_process_map.md` §4 обновлён (Pulse/Bunch/Results как write-targets).
- 5 стадий расширены: материализуют артефакт + (для harvest) пишут `nexus_writeback`.
- `/sprint-harvest-quarter` замыкает верхний уровень.
- `validate_ground.py` + фикстуры валидируют новые артефакты; тесты зелёные.
- Один сквозной прогон одного спринт-цикла: `sprint-sync`→Pulse-узел → `sprint-deliver`→Bunch-узел (с gate) → `sprint-fact`→Harvest-узел с writeback в `product` → узел `product` реально обновлён (confidence/updated). Пустые `BUNCH/RESULTS` перестают быть пустыми **по факту работы**, а не бэкфиллом.

---

## 9. Риски

- **Двойной учёт (Bunch vs JIRA-беклог).** Контрмера: `items` — только ссылки на JIRA, Банч не хранит копий; беклог не воскресает (формируется заново каждый цикл).
- **Workslop в NPV/mNSM.** Контрмера: прогрессивные уровни L0/L1/L2 по вычисляемой спелости; `[УТОЧНИТЬ]` вместо выдумки.
- **Рассинхрон вложенности** (S-bunch ссылается на несуществующий Q-bunch). Контрмера: `validate_ground.py` проверяет `parent_bunch`/`rolls_up_to`.
- **Каденционное отклонение** (§7.1) уводит от чистого PAF. Контрмера: зафиксировано как осознанный bridge-deviation; путь к event-based оставлен в схеме.
- **Нагрузка на PO** (лишние артефакты). Контрмера: материализация автоматическая из стадий, которые он и так гоняет; отдельных команд минимум (+1).

---

**Version:** 1.0 · **Approved:** 2026-07-08 · **Next:** `writing-plans` → план реализации (scope §4).
