# Рендер Карты гипотез через Excalidraw MCP

Как стадия `/hm-deliver` превращает собранную карту в наглядную схему. Движок — **Excalidraw MCP** (инструмент `create_view`, рендерит «от руки» прямо в чат с анимацией отрисовки).

> Перед первым вызовом `create_view` один раз вызови `read_me` (справка по формату элементов). Повторно `read_me` не нужен.

---

## Соответствие нотации → элементы Excalidraw

| Элемент карты | Excalidraw | Заливка |
|---|---|---|
| Карточка **Цели** + метрики | `rectangle` + `label` | `#cadf58` |
| Карточка **Субъекта** + мотивация | `rectangle` + `label` | `#ffc831` |
| **Негативный субъект** | `rectangle` + `label` | `#ffb373` |
| Карточка **Гипотезы** | `rectangle` + `label` | `#ffef73` |
| Карточка **Задачи** | `rectangle` + `label` | `#a6cdff` |
| **Заметка** | `rectangle` + `label` | `#f1f1f1` |
| **Блокер** | `rectangle` + `label` | `#ffa391` |
| **Стрелка влияния** | `arrow` | цвет/толщина = приоритет |
| Подложка группы (топологии 7–8) | `rectangle`, `opacity:30` | нейтральный фон |

Полная кодировка карточек и приоритета стрелок — `resources/color_codes.md`.

---

## Правила раскладки

- **Колонки слева направо:** `Цель | Субъекты | Гипотезы | Задачи`. Шаг между колонками ~250 px.
- **Стрелки влияния — справа налево:** задача → гипотеза → субъект → цель. Наконечник (`endArrowhead:"arrow"`) стоит на **левом** (целевом) конце — влияние «течёт» к цели. Рисуй стрелку от правой карточки к левой: `points:[[0,0],[-Δ, ±δ]]`.
- **Приоритет = толщина + цвет стрелки** (не карточки): 🔴 красная толстая `strokeWidth:4` · 🟡 жёлтая средняя `2.5` · 🟢 зелёная тонкая `1`. На карте должен проступить приоритетный путь.
- Карточки одной колонки — по вертикали с шагом ~120 px. Гипотеза может кормиться несколькими задачами и кормить одного субъекта — стрелки сходятся/расходятся.
- Камера: старт `cameraUpdate` (для небольшой карты ~1050×380); крупную панорамируй по секциям несколькими `cameraUpdate`.
- Шрифты: текст карточек `fontSize ≥ 14`, заголовок `≥ 20`. Без эмодзи внутри `text/label` (шрифт Excalidraw их не рисует).
- Порядок отрисовки (важно для анимации): заголовок → карточки Цели → Субъектов → Гипотез → Задач → стрелки влияния.

---

## Пример: карта «Высыпаться» (из сквозного примера)

Готовый вызов `create_view` — одна цель, один субъект, две гипотезы (A — высокий приоритет, B — средний), задачи под каждую. Стрелки влияния идут справа налево, приоритет закодирован в стрелках гипотез.

```json
[
  {"type":"cameraUpdate","width":1060,"height":400,"x":0,"y":0},
  {"type":"text","id":"title","x":40,"y":10,"text":"Карта гипотез: Высыпаться","fontSize":20,"strokeColor":"#1e1e1e"},

  {"type":"rectangle","id":"goal","x":40,"y":120,"width":210,"height":150,"backgroundColor":"#cadf58","fillStyle":"solid","strokeColor":"#94ad1f","strokeWidth":2,"roundness":{"type":3},"label":{"text":"ЦЕЛЬ\nВысыпаться и просыпаться бодрым\nсон 6 -> 7,5 ч\nбодрость 4 -> 8\n(удержать: 1 ч себе)","fontSize":14}},

  {"type":"rectangle","id":"subj","x":300,"y":120,"width":190,"height":150,"backgroundColor":"#ffc831","fillStyle":"solid","strokeColor":"#c99700","strokeWidth":2,"roundness":{"type":3},"label":{"text":"СУБЪЕКТ\nВечерняя Марина\nболи: телефон затягивает;\nхочет, чтобы вечер был её","fontSize":14}},

  {"type":"rectangle","id":"hA","x":540,"y":90,"width":210,"height":100,"backgroundColor":"#ffef73","fillStyle":"solid","strokeColor":"#c9b400","strokeWidth":2,"roundness":{"type":3},"label":{"text":"ГИПОТЕЗА A\nЕсли с 22:30 серый экран + телефон\nв коридор, то не залипает, п.ч.\nлень идти, тогда сон 6 -> 7,5","fontSize":13}},
  {"type":"rectangle","id":"hB","x":540,"y":215,"width":210,"height":100,"backgroundColor":"#ffef73","fillStyle":"solid","strokeColor":"#c9b400","strokeWidth":2,"roundness":{"type":3},"label":{"text":"ГИПОТЕЗА B\nЕсли вечерний ритуал (чай+книга),\nто вечер ощущается своим, п.ч.\nнужно личное время, тогда бодрость 4 -> 8","fontSize":13}},

  {"type":"rectangle","id":"t1","x":800,"y":40,"width":210,"height":48,"backgroundColor":"#a6cdff","fillStyle":"solid","strokeColor":"#4a90d9","strokeWidth":1.5,"roundness":{"type":3},"label":{"text":"Авто-серый экран с 22:30","fontSize":13}},
  {"type":"rectangle","id":"t2","x":800,"y":100,"width":210,"height":48,"backgroundColor":"#a6cdff","fillStyle":"solid","strokeColor":"#4a90d9","strokeWidth":1.5,"roundness":{"type":3},"label":{"text":"Купить будильник, зарядка в коридоре","fontSize":13}},
  {"type":"rectangle","id":"t3","x":800,"y":215,"width":210,"height":48,"backgroundColor":"#a6cdff","fillStyle":"solid","strokeColor":"#4a90d9","strokeWidth":1.5,"roundness":{"type":3},"label":{"text":"Чай + книги у кресла","fontSize":13}},
  {"type":"rectangle","id":"t4","x":800,"y":275,"width":210,"height":48,"backgroundColor":"#a6cdff","fillStyle":"solid","strokeColor":"#4a90d9","strokeWidth":1.5,"roundness":{"type":3},"label":{"text":"Напоминание ритуал 22:00","fontSize":13}},

  {"type":"arrow","id":"a_sg","x":300,"y":195,"points":[[0,0],[-50,0]],"strokeColor":"#e03131","strokeWidth":4,"endArrowhead":"arrow"},
  {"type":"arrow","id":"a_As","x":540,"y":140,"points":[[0,0],[-50,55]],"strokeColor":"#e03131","strokeWidth":4,"endArrowhead":"arrow"},
  {"type":"arrow","id":"a_Bs","x":540,"y":265,"points":[[0,0],[-50,-70]],"strokeColor":"#f08c00","strokeWidth":2.5,"endArrowhead":"arrow"},
  {"type":"arrow","id":"a_1A","x":800,"y":64,"points":[[0,0],[-50,76]],"strokeColor":"#495057","strokeWidth":1.5,"endArrowhead":"arrow"},
  {"type":"arrow","id":"a_2A","x":800,"y":124,"points":[[0,0],[-50,16]],"strokeColor":"#495057","strokeWidth":1.5,"endArrowhead":"arrow"},
  {"type":"arrow","id":"a_3B","x":800,"y":239,"points":[[0,0],[-50,26]],"strokeColor":"#495057","strokeWidth":1.5,"endArrowhead":"arrow"},
  {"type":"arrow","id":"a_4B","x":800,"y":299,"points":[[0,0],[-50,-34]],"strokeColor":"#495057","strokeWidth":1.5,"endArrowhead":"arrow"}
]
```

Что показывает пример: колонки `Цель · Субъект · Гипотезы · Задачи`; красные толстые стрелки `a_sg` и `a_As` = приоритетный путь (гипотеза A → субъект → цель, высокий приоритет); оранжевая средняя `a_Bs` = гипотеза B (средний); серые тонкие = связи задач с гипотезами. Влияние течёт справа налево, к цели.

---

## Итеративная доработка

`create_view` возвращает `checkpointId`. Чтобы дополнить карту, не пересылая всё, начни массив с `{"type":"restoreCheckpoint","id":"<checkpointId>"}` и добавь новые элементы. Удаление — `{"type":"delete","ids":"hB,a_Bs"}`. Новым элементам всегда давай новые `id`.

---

## Fallback-инструменты

Если Excalidraw MCP недоступен — официальные инструменты с нотацией метода:
- **Социотех** (`sociotech.center`) и **Гипотезная** (`maps.integrostrat.ru`).
- Ручные шаблоны — **Холст**, **Miro**, **Эсборд**, **Unidraw**. Бумажные стикеры не рекомендуются (тяжело двигать/перекрашивать/соединять).

> Рендер — последний шаг. Сначала карта должна быть связной и пройти `/hm-validate` (🟢/🟡). Красоту наводим после логики.
