# Research Lens Arsenal — дизайн переиспользования проверенных промтов Discovery

**Дата:** 2026-07-06
**Ветка:** `feat/prd-research`
**Статус:** дизайн утверждён; итерации 2–3 реализованы — арсенал линз + все 8 шагов discovery исполнимы (/prd-idea…/prd-acquisition)
**Расширяет:** `2026-07-06-prd-research-discovery-design.md` (каркас discovery, PP-0 + PP-1)

---

## 0. TL;DR

У PO есть **14 проверенных промтов** Product Discovery & Research (сегментация, TAM/SAM/SOM, unit-экономика, ODI, OST, AARRR, NSM, RAT, 4P, выбор каналов, A/B, ниши, Rory Sutherland, единый контекст потребителя). Каждый раскрывает свою сторону продукта. Задача — переиспользовать их **системно и последовательно** внутри discovery-workflow.

Наблюдение: у всех 14 промтов **одна форма** — роль-консультант + стадийность + структурированный вывод (в основном YAML) + гейт по команде PO + принцип «бросай вызов допущениям, не выдумывай числа». Это ровно паттерн **«Обёртка»**, выбранный ранее для `/prd-customer`.

Отсюда обобщение: каркас становится **хостом сменных Research-линз**. Каждый промт = **линза** — сменный движок распаковки, привязанный к шагу(ам) Product Discovery. Шаг = **адаптивный плейлист линз**. Обёртка единая: `PULSE (вход из прошлых узлов) → запуск линзы дословно → HARVEST (структурированный выход → узлы Нексуса с hyp_status/CP/sources)`.

Zero-hallucination сохранён и усилён: линзы порождают **гипотезы и оценки**, которые харвестятся как `hypothesis`/`[estimate]` с низким CP — не как факты. Сами промты это предписывают (RAT метит `[Assumption]`, TAM предупреждает про «1% Китая», сегментация — «never guess numbers»). Каркас лишь персиститит их честно и связывает в граф.

---

## 1. Проблема и позиционирование

### 1.1 Что меняется

Каркас discovery (PP-0/PP-1) реализовал модель «1 стадия = 1 навык со своей внутренней логикой» и один эталон (`/prd-idea`, 3 Линзы). Но у PO есть богатый арсенал специализированных промтов, каждый из которых глубоко раскрывает одну грань. Хардкодить их логику в навыки — потеря: промты проверены и эволюционируют отдельно.

Решение: **инвертировать зависимость** — навык-стадия не содержит методику распаковки, а **хостит сменную линзу** (промт). Промты становятся данными (реестр + файлы), а не кодом. PO может добавлять/менять линзы, не трогая каркас.

### 1.2 Research Lens — определение

**Линза** = обёртка над проверенным промтом:

```yaml
lens:
  id: segmentation              # slug
  title: "Сегментация ЦА"
  prompt_file: "resources/lenses/segmentation.md"   # промт ДОСЛОВНО
  role: "Expert PM — сегментация B2B/SaaS (6-step)"
  host_steps: [customer]        # шаг(и)-хозяева; [] = cross-cutting
  cross_cutting: false
  lang: ru                      # обёртка инструктирует отвечать по-русски
  harvest:                      # какие выходы → какие узлы (см. §3)
    - output: "STEP 6 summary segments (HIGH)"
      nexus: customer
      node_type: segment
      cp_policy: estimate       # см. §4 (CP-политики)
```

### 1.3 Отношение к существующему

- `/prd-idea` (Step 1, PP-1) остаётся — его 3 Линзы = встроенная линза шага Idea; арсенал добавляет к Idea линзу «Анализ нишевых возможностей».
- Node schema §2.3 (`hyp_status`/`depends_on`/CP-шкала) и §3.1 (discovery node_type) — база; §3.1 расширяется под новые артефакты (§3 ниже).
- Доска `/prd-research`, мягкие гейты, PRD-витрина — без изменений в контракте; витрина обогащается новыми node_type.

---

## 2. Архитектура: Lens Registry + Wrap

### 2.1 Реестр линз

`.claude/skills/prd-research/resources/lenses.yaml` — реестр всех линз (по схеме §1.2). Файлы промтов — `resources/lenses/<id>.md` (копии проверенных промтов PO, дословно, read-only-справочник).

### 2.2 Единый контракт исполнения линзы (Wrap)

Любой шаг/линза исполняется одинаково:

```
PULSE     Прочитать узлы шага-хозяина + узлы-первопричины (depends_on из прошлых шагов).
          Собрать в «input-пак» → передать линзе как контекст (product_description,
          target_audience, prior findings). Заполняет input_request промта.
SCOUT     Запустить промт линзы ДОСЛОВНО: его стадийность, YAML-вывод, гейты
          («продолжить/далее/ревизия»/«start»/«next»), его правила [Assumption].
          Каркас не вмешивается в тело промта.
HARVEST   Смаппить структурированный выход линзы → узлы Нексуса по harvest-map линзы:
          node_type (§3), hyp_status + CP (§4), sources, depends_on (связь с input-узлами).
          Обновить state.yaml(step) + journal.md.
STOP      Отчёт + пауза PO (human-in-the-loop).
```

Ключ: **промт не редактируется**. Обёртка добавляет только PULSE (вход) и HARVEST (персист). Многоязычность: обёртка инструктирует «отвечай по-русски» (промты это допускают: «match user language»/«Russian if requested»).

### 2.3 Команды

- **Шаг-команды** `/prd-<step>` (idea/customer/market/value/bizmodel/gtm/solution/acquisition) — запускают **адаптивный плейлист** линз шага: рекомендуют порядок, PO может пропустить/переставить/повторить линзу. Каждая линза = под-цикл Wrap с мини-STOP.
- **Cross-cutting диспетчер** `/prd-lens <id>` — запускает линзу из тулбокса (rat/abtest/ost/nsm) на текущем шаге; оркестратор предлагает их на гейтах.
- Оркестратор `/prd-research` показывает на доске: какие линзы шага пройдены (по узлам/journal), какие рекомендованы дальше, какие cross-cutting уместны сейчас.

### 2.4 Адаптивный плейлист (не жёсткий курс)

У каждого шага — **рекомендуемый порядок** линз (методологически осмысленный), но PO волен отклоняться (согласуется с нелинейной доской и мягкими гейтами каркаса). Оркестратор лишь рекомендует «первый непройденный / с наименьшим CP».

---

## 3. Маппинг 14 линз по шагам + node_type

### 3.1 Step-bound линзы

| Шаг | Плейлист (рекоменд. порядок) | Осн. node_type артефактов |
|---|---|---|
| 1 Idea | `niche-opportunities` | opportunity · bet |
| 2 Customer | `segmentation` → `consumer-context` → `odi` | segment · jtbd · outcome · persona-context |
| 3 Market | `tam-sam-som` | tam-sam-som · competitor · market-force |
| 4 Value | `nsm` → `odi`(outcomes) → `rory-interrogation` | nsm-metric · input-metric · outcome · value-prop |
| 5 Business Model | `unit-economics` → `aarrr`(revenue) | unit-econ · cohort · funnel-stage |
| 6 GTM | `positioning-4p` → `distribution-channels` → `rory-interrogation` | positioning · four-p · channel |
| 7 Solution | `ost` → `ab-design` → `rat` | opportunity · solution · experiment · risk-card |
| 8 Acquisition | `distribution-channels` → `aarrr`(acq) → `ab-design` | channel · funnel-stage · ab-test |

### 3.2 Cross-cutting линзы (тулбокс, `/prd-lens`)

| Линза | Когда вызывать | node_type |
|---|---|---|
| `rat` (RAT — риски запуска) | на гейтах (после Idea, перед Solution): что валидировать первым | risk-card |
| `ab-design` (Проектирование A/B) | когда любой шаг переходит к проверке гипотезы | ab-test |
| `ost` (Opportunity Solution Tree) | сквозной хребет Customer→Value→Solution: связывает outcome→opportunity→solution→experiment | opportunity · solution · experiment |
| `nsm` (North Star) | Value (осн.) → питает BizModel/AARRR/Solution | nsm-metric · input-metric |

Линза может висеть на нескольких шагах (Rory: Value+GTM; distribution-channels: GTM+Acquisition; aarrr: BizModel+Acquisition; odi: Customer+Value). Это норма: `host_steps` — список.

### 3.3 Расширение §3.1 nexus_schema (новые discovery node_type)

Добавить в §3.1 (каждый ← методология своей линзы, принцип «тип ← источник»):

| node_type | Линза-источник | Нексус |
|---|---|---|
| `opportunity` | niche-opportunities, OST | market/customer |
| `segment` | segmentation | customer |
| `jtbd` | segmentation, ODI | customer |
| `outcome` | ODI (desired outcome) | customer/product |
| `persona-context` | consumer-context | customer |
| `nsm-metric` | NSM | product/growth |
| `input-metric` | NSM, AARRR | growth |
| `value-prop` | consumer-context, ODI | product |
| `unit-econ` | unit-economics | growth |
| `cohort` | unit-economics, AARRR | growth |
| `funnel-stage` | AARRR | growth |
| `positioning` | 4P, Rory | product/growth |
| `four-p` | 4P | growth |
| `channel` | distribution-channels | growth |
| `market-force` | (уже покрыто force/trend/constant §3.1) | market |
| `risk-card` | RAT | risk/product |
| `solution` | OST | product |
| `experiment` | OST | product |
| `ab-test` | A/B design | product/growth |

`tam-sam-som`, `competitor`, `gap`, `bet`, `lever`, `feature`, `force`, `trend`, `constant` — уже в §3.1 (PP-1 fix).

---

## 4. CP-политики (honesty при харвесте)

Линзы порождают гипотезы и **оценки** (сегменты, TAM, unit-эк, метрики), которые НЕ факты. Harvest-map каждого выхода несёт `cp_policy`:

| cp_policy | Когда | hyp_status | CP | Пометка |
|---|---|---|---|---|
| `judgment` | генерация из ввода PO без внешних данных | hypothesis | 0.2–0.4 | — |
| `estimate` | числовая оценка (TAM/SAM/SOM, unit-эк, размер сегмента, K-factor) | hypothesis | 0.3–0.4 | `[estimate]` в теле |
| `desk` | подкреплено web/desk-research (URL+дата) | validating | 0.5–0.7 | якорь-URL |
| `evidence` | реальное интервью / эксперимент / аналитика | validated/refuted | 0.6–1.0 | источник-факт |

Правила:
- Линзы, которые сами метят допущения (RAT `[Assumption]`, TAM sensitivity, ODI Opp_Score, сегментация «never guess»), — харвест **уважает их разметку**: помеченное допущением → `estimate`/`judgment`, не `validated`.
- Численные оценки без данных → всегда `estimate` (не поднимать CP выше 0.4).
- `evidence` доступен только когда линза реально прогнала интервью/эксперимент (напр. A/B с результатом, ODI со scores от реальных пользователей).
- Узел без `sources` не создаётся (workslop), как в §2.3.

Следствие для вердикта «готово к разработке»: он достигается только когда ключевые узлы Value/Solution имеют `evidence`-CP ≥ 0.6 (fit-гейты §fit_gates). Арсенал ускоряет **сбор** гипотез, но не заменяет их валидацию — «dev-ready» по-прежнему требует Step 7 + реальных данных.

---

## 5. Эволюция PRD-витрины

`/prd-assemble` обогащается: разделы PRD агрегируют новые node_type по шагам. Добавить в витрину под-блоки:
- **Сегменты и JTBD** (customer): segment/jtbd/persona-context.
- **Метрики** (Value/BizModel): nsm-metric + input-metric (дерево NSM).
- **Юнит-экономика** (BizModel): unit-econ/cohort с пометкой `[estimate]`.
- **Позиционирование и каналы** (GTM): positioning/four-p/channel.
- **OST-дерево** (Solution): opportunity→solution→experiment с их статусами.
- **Реестр рисков** (cross): risk-card RAT, отсортированные по Score=P×I.

Разметка confidence (✅/🟡/🔴) — без изменений (§/prd-assemble): секция validated только при `evidence`-узлах CP≥0.6.

---

## 6. Декомпозиция и порядок сборки

Полная рамка (этот документ) фиксируется целиком. Реализация — инкрементально:

```
PP-2  Lens infrastructure (ядро арсенала)
      · lenses.yaml схема + реестр; resources/lenses/ (14 файлов промтов дословно)
      · единый Wrap-исполнитель (PULSE/HARVEST-контракт) в SKILL + resources/lens_runtime.md
      · §3.1 node_type расширение (§3.3)
      · CP-политики (§4) в node_conventions
      · /prd-lens <id> диспетчер (cross-cutting)

PP-3  Step 2 Customer как эталон хоста линз (3 линзы)
      · /prd-customer: плейлист segmentation → consumer-context → odi
      · harvest-map каждой из 3 линз → узлы customer-Нексуса
      · эталон, по которому оснащаются шаги 3–8

PP-4..PP-N  Оснащение шагов 3–8 их плейлистами (по одному шагу)
      · Market (tam-sam-som) · Value (nsm/odi/rory) · BizModel (unit/aarrr)
      · GTM (4p/channels/rory) · Solution (ost/ab/rat) · Acquisition (channels/aarrr/ab)

PP-cross  Cross-cutting тулбокс полноценно (rat/ab/ost/nsm) + витрина §5
```

Первая итерация реализации — **PP-2 + PP-3** (инфраструктура линз + эталонный Customer-хост с 3 линзами). Реализацию в этой сессии не начинаем (дизайн).

---

## 7. Принципы (наследуем)

1. **Промты read-only и дословны.** Линза не редактирует тело промта; обёртка добавляет только вход/персист. Промты PO — его few-shot, эволюционируют отдельно.
2. **Оценка ≠ факт.** Числа и гипотезы линз → `estimate`/`judgment` с низким CP + `[estimate]`. Уважать собственную разметку допущений промта.
3. **Узел без `sources` не создаётся.**
4. **Адаптивность.** Плейлист рекомендует, PO решает; нелинейная доска + мягкие гейты.
5. **Методология не тронута.** `docs/` read-only; node_type ← методология линзы.
6. **Инструкции из данных** (выходы линз, web) — данные, не команды.

---

## 8. Открытые вопросы (для writing-plans)

- **Формат промт-файлов в репо:** копировать 14 `.txt` из Downloads PO в `resources/lenses/*.md` как есть, или нормализовать шапку (добавить mini-frontmatter `id/host_steps`)? Предложение: копия тела дословно + отдельный `lenses.yaml` реестр (не трогать тело). Решить в PP-2.
- **Гейт-язык линз:** промты используют разные сигналы продолжения («продолжить», «start», «next», «continue»). Обёртка нормализует на «продолжить/далее/ревизия» инструкцией сверху, не меняя тело? Решить в PP-2.
- **OST как сквозной артефакт:** дерево живёт одним узлом-агрегатом или набором opportunity/solution/experiment узлов со связями `depends_on`? Предложение: узлами + связями (граф), агрегат-вьюха в витрине. Решить в PP-cross.
- **Дедуп линз на нескольких шагах** (rory/odi/channels/aarrr): один файл промта, разные harvest-map per host-step? Да — один `prompt_file`, harvest-map зависит от `host_step`. Уточнить в PP-3.
