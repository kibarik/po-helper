# Рендер Карты процесса-опыта через Excalidraw MCP

Как стадия `/xpm-deliver` превращает собранную карту в наглядную схему. Движок — **Excalidraw MCP** (инструмент `create_view`, рендерит «от руки» прямо в чат с анимацией отрисовки).

> Перед первым вызовом `create_view` один раз вызови `read_me` (справка по формату элементов). Повторно `read_me` не нужен.

---

## Соответствие нотации XPM → элементы Excalidraw

| Элемент XPM | Значок | Excalidraw |
|---|---|---|
| Дорожка участника | — | `rectangle` во всю ширину, `opacity: 30`, зона-подложка + `text`-подпись слева |
| Ключевая точка | ● | `ellipse` ~46×46 (заливка по смыслу) + отдельный `text` с названием над точкой |
| Точка вне контроля | ○ | `ellipse` с `backgroundColor: "transparent"` (только контур) |
| Опциональная точка | ◠ | `ellipse` + тонкая дуга/пунктирный контур (`strokeStyle: "dashed"`) |
| Триггер / событие | ◇ | `diamond` ~40×40 |
| Линия тока (надёжная) | ⎯ | `arrow` сплошная, `endArrowhead: "arrow"` |
| Линия тока (ненадёжная) | ┈ | `arrow` `strokeStyle: "dashed"` |
| Линия взаимодействия | ⦙ | `arrow` вертикальная, `strokeStyle: "dashed"`, `endArrowhead: null`, `startArrowhead: null`, серый `strokeColor` |
| Аннотация точки | — | `rectangle` `#fff3bf` под точкой + `label` с деталями (вход/выход/каналы) |

**Цвета дорожек** (зоны-подложки, `opacity: 30`):
- Актор (клиент) — синяя зона `#dbe4ff`;
- Агенты-люди — сиреневая зона `#e5dbff`;
- Агенты-системы — зелёная зона `#d3f9d8`.

**Заливка точек** (по желанию, для читаемости типа):
- решение — `#fff3bf` (жёлтая); контакт — `#a5d8ff` (голубая); изменение — `#b2f2bb` (зелёная).

---

## Правила раскладки

- **Ось X — время:** точки одного участника идут слева направо с шагом ~160–200 px.
- **Ось Y — дорожки:** актор сверху, каждый следующий агент — ниже (шаг ~120–140 px). Дорожка обслуживает ту, что над ней.
- **Синхронные точки** разных участников — на одной вертикали `x`; соединяются вертикальной ⦙.
- Камера: начинай с `cameraUpdate` (обычно `800×600`); для крупной карты панорамируй по секциям (несколько `cameraUpdate`).
- Шрифты: названия точек `fontSize ≥ 16`, заголовок карты `≥ 20`. Не мельчи.
- Порядок отрисовки (важно для анимации): зона-дорожка → точки этой дорожки → их подписи → линии тока → вертикальные взаимодействия → следующая дорожка.
- Без эмодзи внутри `text` (шрифт Excalidraw их не рисует).

---

## Пример: фрагмент карты «доставка пиццы»

Готовый вызов `create_view` (можно взять за основу и дополнять). Две дорожки, точки клиента, ненадёжный переход к «Ожиданию», взаимодействие клиент⦙оператор.

```json
[
  {"type":"cameraUpdate","width":800,"height":600,"x":0,"y":0},
  {"type":"text","id":"title","x":40,"y":10,"text":"Карта процесса-опыта: доставка пиццы (как есть)","fontSize":20,"strokeColor":"#1e1e1e"},

  {"type":"rectangle","id":"laneA","x":30,"y":70,"width":740,"height":110,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"opacity":30},
  {"type":"text","id":"laneAl","x":40,"y":78,"text":"Клиент","fontSize":16,"strokeColor":"#2563eb"},
  {"type":"ellipse","id":"p1","x":110,"y":110,"width":46,"height":46,"backgroundColor":"#fff3bf","fillStyle":"solid","strokeColor":"#f59e0b","strokeWidth":2},
  {"type":"text","id":"p1t","x":92,"y":90,"text":"Голод","fontSize":16,"strokeColor":"#1e1e1e"},
  {"type":"ellipse","id":"p2","x":300,"y":110,"width":46,"height":46,"backgroundColor":"#a5d8ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":2},
  {"type":"text","id":"p2t","x":250,"y":90,"text":"Оформление заказа","fontSize":16,"strokeColor":"#1e1e1e"},
  {"type":"ellipse","id":"p3","x":540,"y":110,"width":46,"height":46,"backgroundColor":"#b2f2bb","fillStyle":"solid","strokeColor":"#22c55e","strokeWidth":2},
  {"type":"text","id":"p3t","x":520,"y":90,"text":"Ожидание","fontSize":16,"strokeColor":"#1e1e1e"},
  {"type":"arrow","id":"f1","x":156,"y":133,"width":144,"height":0,"points":[[0,0],[144,0]],"strokeColor":"#1e1e1e","strokeWidth":2,"endArrowhead":"arrow"},
  {"type":"arrow","id":"f2","x":346,"y":133,"width":194,"height":0,"points":[[0,0],[194,0]],"strokeColor":"#e8590c","strokeWidth":2,"strokeStyle":"dashed","endArrowhead":"arrow","label":{"text":"когда приедет?","fontSize":14}},

  {"type":"rectangle","id":"laneB","x":30,"y":200,"width":740,"height":110,"backgroundColor":"#e5dbff","fillStyle":"solid","strokeColor":"#8b5cf6","strokeWidth":1,"opacity":30},
  {"type":"text","id":"laneBl","x":40,"y":208,"text":"Оператор / сайт","fontSize":16,"strokeColor":"#6d28d9"},
  {"type":"ellipse","id":"q1","x":300,"y":240,"width":46,"height":46,"backgroundColor":"#a5d8ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":2},
  {"type":"text","id":"q1t","x":268,"y":290,"text":"Приём заказа","fontSize":16,"strokeColor":"#1e1e1e"},
  {"type":"arrow","id":"ix","x":323,"y":156,"width":0,"height":84,"points":[[0,0],[0,84]],"strokeColor":"#868e96","strokeWidth":2,"strokeStyle":"dashed","endArrowhead":null,"startArrowhead":null},

  {"type":"rectangle","id":"ann","x":250,"y":330,"width":260,"height":70,"backgroundColor":"#fff3bf","fillStyle":"solid","strokeColor":"#f59e0b","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Оформление: вход — выбор; выход — заказ. Каналы: сайт, телефон, чат-бот. Барьер: непонятно время","fontSize":14}}
]
```

Что показывает пример: пунктирная оранжевая линия тока `f2` = ненадёжный переход (клиент не знает время); серая вертикальная `ix` = взаимодействие клиента и оператора; жёлтый блок `ann` = аннотация точки с найденной болевой точкой.

---

## Итеративная доработка

`create_view` возвращает `checkpointId`. Чтобы дополнить карту, не пересылая всё заново, начни массив с `{"type":"restoreCheckpoint","id":"<checkpointId>"}` и добавь новые элементы. Удаление — псевдоэлемент `{"type":"delete","ids":"p3,f2"}`. Новым элементам всегда давай новые `id`.

---

## Fallback-движки

Если Excalidraw MCP недоступен:
- **Шаблоны автора** (переиспользовать): Figma (v3 автолэйаут), Holst.so, Miro, OmniGraffle-стенсил, библиотека `xpm-library.excalidrawlib` — см. `Byndyusoft/xp-mapping/templates`.
- **Официальный инструмент метода** — Социотех (`sociotech.center`).
- **PlantUML** — только как грубая эмуляция (нотация XPM нестандартна); использовать в крайнем случае.

> Рендер — последний шаг. Сначала карта должна быть связной и пройти `/xpm-validate` (🟢/🟡). Красоту наводим после логики.
