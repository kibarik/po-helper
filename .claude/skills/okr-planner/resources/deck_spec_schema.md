# deck-spec — схема YAML + каталог архетипов

`deck-spec.yaml` — единый источник для всех трёх рендереров движка (`render_html.py`, `render_pptx.py`, `render_roadmap.py`). Загружается `engine.deckspec.load_deckspec(path)` → `DeckSpec`. Ниже — точная форма полей (из `engine/deckspec.py`) и каталог архетипов слайдов, которые из неё строит `engine.build_slides.build_slides()`.

---

## 1. Top-level ключи

```yaml
product: GDS
quarter: Q3-2026
subtitle: витрина Ticketland
footer: "GDS · Q3 · витрина Ticketland"
directions: [ ... ]     # список Direction
authored: { ... }       # блок Authored
```

| Ключ | Тип | Обязателен | Примечание |
|------|-----|------------|-----------|
| `product` | str | да | `raw["product"]`, без дефолта — падает, если пусто |
| `quarter` | str | да | `raw["quarter"]`, без дефолта |
| `subtitle` | str | нет | дефолт `""` |
| `footer` | str | нет | дефолт `""`; печатается на каждом нетайтульном слайде |
| `directions` | list[Direction] | нет | дефолт `[]` |
| `authored` | Authored | нет | дефолт — все поля пустые |

---

## 2. `directions[]` → `Direction`

```yaml
directions:
  - name: Надёжный источник
    color: "#E4002B"        # опционально; иначе theme.direction_color(index)
    number: 1                # опционально; дефолт = позиция в списке + 1
    blurb: "Витрина берёт данные из старой базы БАЗИС и падает вместе с ней."
    objs: [ ... ]             # список OBJ
```

| Поле | Тип | Дефолт |
|------|-----|--------|
| `name` | str | обязателен |
| `color` | str \| null | `null` → рендерер берёт `theme.direction_color(i)` |
| `number` | int | `i + 1` (индекс направления в списке) |
| `blurb` | str | `""` |
| `objs` | list[OBJ] | `[]` |

## 3. `objs[]` → `OBJ`

```yaml
objs:
  - id: OBJ1
    title: Надёжный источник данных
    krs: [ ... ]              # список KR
```

| Поле | Тип |
|------|-----|
| `id` | str |
| `title` | str |
| `krs` | list[KR] |

## 4. `krs[]` → `KR`

```yaml
krs:
  - id: "1.1"
    title: Продажа мероприятий TicketsCloud на витрине
    now: "Мероприятия продаются через старую базу БАЗИС."
    becomes: "Те же мероприятия продаются напрямую из TicketsCloud."
    steps:
      - {role: SA, text: Исследование коннектора UMC→web_db}
      - {role: BE, text: TicketsCloud → UMC}
    risks:
      - {text: "Блокер: дедубликация web_db (KR 1.1.E1)"}
    sprint_cells: {S1: [SA·ADR], S2: [BE·Go], S4: [FE·PHP], S5: [QA]}
    owners: [Чеботков, Ананьев]
    src: "OKR-Q3-2026.md#KR-1.1"
```

| Поле | Тип | Дефолт | Примечание |
|------|-----|--------|-----------|
| `id` | str | обязателен | |
| `title` | str | обязателен | |
| `now` | str \| null | `null` | «СЕЙЧАС». Пусто → 🔴 в `present_gates.md` |
| `becomes` | str \| null | `null` | «СТАНЕТ». Пусто → 🔴 |
| `steps` | list[Step] | `[]` | образ действия |
| `risks` | list[Risk] | `[]` | пусто → 🟡 |
| `sprint_cells` | dict[str, list[str]] | `{}` | см. §5 ниже. Пусто → 🔴 |
| `owners` | list[str] | `[]` | |
| `src` | str \| null | `null` | якорь факта (см. §7) |

## 5. Формат `sprint_cells`

Ключ — метка спринта (`"S1"`, `"S2"`, …, сортируется по числу после `S`), значение — список строк-чипов вида `"РОЛЬ·СТЕК"`:

```yaml
sprint_cells: {S1: ["SA·ADR"], S2: ["BE·Go"], S4: ["FE·PHP"], S5: ["QA"]}
```

- Часть до `·` — роль (резолвится в цвет через `theme.role_color(role)`, см. `theme.md`).
- Часть после `·` — стек/технология (опциональна: `"QA"` без `·` — тоже валидная строка, но триггерит 🟡 «чип без стека», см. `present_gates.md`).
- Множество ключей `sprint_cells` по всем KR всех направлений собирается в общий список колонок таблицы жизненного цикла (`_collect_sprints` в `build_slides.py`), отсортированный численно.

## 6. `steps[]` → `Step`, `risks[]` → `Risk`

```yaml
steps: [{role: SA, text: "..."}]
risks:  [{text: "..."}]
```

| Dataclass | Поля |
|-----------|------|
| `Step` | `role: str`, `text: str` |
| `Risk` | `text: str` |

## 7. `authored{}` → `Authored`

Блок для контента, который не приходит из vault-фактов (KR/направления), а формируется PO/LLM на стадии B «Доавторинг рамки». Каждый под-ключ по умолчанию пуст:

```yaml
authored:
  market:
    - {value: "≈227 млрд ₽", label: "объём билетного рынка РФ", src: "PO-authored"}
  quarter_shift: "уводим витрину со старой базы БАЗИС на TicketsCloud"
  glossary:
    - {term: БАЗИС, plain: "старая билетная база"}
  order_of_work:
    now: ["Докатить кино и рестораны", "Починить критбаги"]
    august: ["★ Продажи TicketsCloud на витрине"]
    later: ["Дешевле Live — исследование"]
  right_now:
    - {title: "Докатить кино на витрину", note: "долг прошлого квартала"}
  after_meeting: "Детальные задачи распишем в JIRA — вместе."
  takeaways:
    - {title: "Всё крутится вокруг витрины Ticketland", note: "4 направления"}
```

| Поле | Тип | Дефолт | Используется в архетипе |
|------|-----|--------|--------------------------|
| `market` | list[dict] (`value`, `label`, `src`) | `[]` | `why_market` (только если непусто) |
| `quarter_shift` | str | `""` | `why_market.shift` |
| `glossary` | list[dict] (`term`, `plain`) | `[]` | `glossary` (только если непусто) |
| `order_of_work` | dict (`now`, `august`, `later` — каждый список str) | `{}` | `order_of_work` (только если непусто) |
| `right_now` | list[dict] (`title`, `note`) | `[]` | `right_now` (только если непусто) |
| `after_meeting` | str | `""` | `after_meeting` (только если непусто) |
| `takeaways` | list[dict] (`title`, `note`) | `[]` | `takeaways` (только если непусто) |

Слайды `why_market`, `glossary`, `order_of_work`, `right_now`, `after_meeting`, `takeaways` **условны** — `build_slides` включает их в план, только если соответствующее поле `authored` непусто.

## 8. Правило источника факта

Каждый факт на слайде обязан быть прослеживаем одним из двух способов:

- **`src:`** — на объекте, который несёт внешний факт (`KR.src`, элемент `authored.market[].src`) — якорь на исходник: OKR-документ, JIRA-ключ, PO-решение, Confluence.
- **живёт в блоке `authored:`** — PO-авторский контент (рамка презентации: направления+цвета, рынок+источник внутри самого market-айтема, глоссарий, closing), который по определению не требует внешней ссылки, но market-числа внутри `authored.market[]` всё равно обязаны нести собственный `src` (см. гейт 🔴 в `present_gates.md`: «рыночное число без источника»).

Факт без `src` и вне `authored:` — нарушение нулевого допуска к галлюцинациям; помечать `[УТОЧНИТЬ]` и возвращать PO на стадии A.

---

## 9. Каталог архетипов (`engine/archetypes.py::ARCHETYPES`, 13 штук)

Каждый архетип — функция `(data: dict, theme: Theme) -> list[Element]`. Ниже — имя, одна строка описания и форма `data`, которую он ожидает.

| Архетип | Описание | Форма `data` |
|---------|----------|--------------|
| `title` | Титульный слайд квартала | `{kicker, headline, sub}` |
| `big_picture` | Карточки направлений (до 4) | `{kicker, headline, cards: [{n, title, note, color}]}` |
| `why_market` | Рыночный контекст: до 3 чисел + сдвиг квартала | `{kicker, headline, stats: [{value, label, src}], shift}` |
| `glossary` | Термин → простыми словами (до 6, 2 колонки) | `{kicker, headline, terms: [{term, plain}]}` |
| `how_to_read` | Легенда СЕЙЧАС/СТАНЕТ перед деталями | `{kicker, headline, now_note?, becomes_note?, footnote}` |
| `direction_divider` | Разделитель направления (номер + название + подводка) | `{number, kicker, title, blurb, color}` |
| `order_of_work` | Порядок работ: сначала/к августу/дальше | `{kicker, headline, order: {now: [...], august: [...], later: [...]}}` |
| `right_now` | Нумерованный список «прямо сейчас» (до 5) | `{kicker, headline, items: [{title, note}]}` |
| `after_meeting` | Один абзац «что после встречи» | `{kicker, headline, body}` |
| `takeaways` | Нумерованные тезисы «что запомнить» (до 4) | `{kicker, headline, items: [{title, note}]}` |
| `sprint_lifecycle_table` | Строки-шаги направления × спринты S1..Sn, чипы роль·стек | `{kicker, headline, sprints: [str], rows: [{label, cells: {Sx: [str]}}], owners?}` |
| `roles_sprint_table` | Экспертиза + люди × спринты | `{kicker, headline, sprints: [str], rows: [{role, expertise, people, cells: {Sx: str}}], note?}` |
| `now_becomes_detail` | Деталь одного KR: СЕЙЧАС/СТАНЕТ + образ действия по этапам + риски | `{kicker, title, now, becomes, stages: [{label, steps: [{role, text}]}], risks: [str]}` |

`roles_sprint_table` определён в каталоге, но `build_slides` его сейчас не использует (не входит в стандартный план слайдов).

---

## 10. Порядок слайдов (`engine.build_slides.build_slides`)

Функция строит план `(archetype_name, data)` в этом фиксированном порядке, затем прогоняет каждый через `ARCHETYPES[name]`:

1. **`title`** — всегда. `page=0`, `footer=""`.
2. **`big_picture`** — всегда. Карточка на каждое направление из `directions[]`.
3. **`why_market`** — только если `authored.market` непусто.
4. **`glossary`** — только если `authored.glossary` непусто.
5. **`how_to_read`** — всегда.
6. Для **каждого** направления (в порядке `directions[]`):
   1. **`direction_divider`**
   2. **`sprint_lifecycle_table`** — строки = все KR направления (по всем OBJ, в порядке объявления)
   3. **`now_becomes_detail`** — один слайд на каждый KR направления (по всем OBJ, в порядке объявления)
7. **`order_of_work`** — только если `authored.order_of_work` непусто.
8. **`right_now`** — только если `authored.right_now` непусто.
9. **`after_meeting`** — только если `authored.after_meeting` непусто.
10. **`takeaways`** — только если `authored.takeaways` непусто.

Нумерация страниц (`page`) — сквозная с 1, начиная со второго слайда (`big_picture`); у `title` `page=0`. `footer` = `spec.footer` на всех слайдах, кроме `title` (там `""`).
