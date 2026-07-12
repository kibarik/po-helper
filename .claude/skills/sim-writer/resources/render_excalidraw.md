# Рендер Карты реализации историй через Excalidraw MCP

Как стадия `/sim-deliver` превращает собранную матрицу в наглядную карту. Движок — **Excalidraw MCP** (инструмент `create_view`, рендерит «от руки» прямо в чат с анимацией отрисовки).

> Перед первым вызовом `create_view` один раз вызови `read_me` (справка по формату элементов). Повторно `read_me` не нужен.

---

## Идея раскладки: матрица карточек

КРИ — не дорожки и точки (это XPM), а **матрица прямоугольников**:

- **Каждая рабочая история = столбец из 5 карточек-прямоугольников**, сверху вниз: **Ц · Н · С · Д · О→О′**.
- **Слева направо** между столбцами — следование процесса (шаги дела по времени).
- **Сверху вниз** внутри столбца — подчинение функции (цель держит историю сверху).
- Под столбцом — **горизонтальная черта**, ниже неё карточки **форм реализации** («что» отделено от «чем»).
- Слева — колонка подписей строк (Ц/Н/С/Д/О→О′).

```
        подписи      история 1     история 2     история 3   → следование процесса
                    ┌─────────┐   ┌─────────┐   ┌─────────┐
          Ц         │  цель   │   │  цель   │   │  цель   │
          Н         │носитель │   │носитель │   │носитель │  ↓ подчинение
          С         │ситуация │   │ситуация │   │ситуация │    функции
          Д         │ способ  │   │ способ  │   │ способ  │
          О→О′      │ объекты │   │ объекты │   │ объекты │
                    ╞═════════╡   ╞═════════╡   ╞═════════╡  ← черта
        формы       │ форма 1 │   │ форма 1 │   │ форма 1 │
     реализации     │ форма 2 │   │         │   │ форма 2 │
                    └─────────┘   └─────────┘   └─────────┘
```

---

## Соответствие структуры КРИ → элементы Excalidraw

| Элемент КРИ | Excalidraw |
|---|---|
| Карточка элемента истории | `rectangle` ~200×60, `label` с текстом элемента, `roundness:{type:3}` |
| Карточка цели (Ц) | та же, тон-акцент `#fff3bf` (жёлтая) — цель держит историю сверху |
| Карточки Н·С·Д·О→О′ | `rectangle` `#dbe4ff` (голубые), `strokeColor "#4a9eed"` |
| Подпись строки (Ц/Н/С/Д/О→О′) | `text` слева, `fontSize 16`, серый `strokeColor` |
| Заголовок истории | `text` над столбцом, `fontSize 16` |
| Черта-разделитель | `line`/`arrow` без стрелок, `strokeWidth 2`, `strokeColor "#1e1e1e"` во всю ширину столбца |
| Карточка формы реализации | `rectangle` `#d3f9d8` (зелёная), `strokeColor "#22c55e"` под чертой |
| Заголовок карты | `text` сверху, `fontSize 20` |

**Палитра смыслов:** суть (выше черты) — голубая/жёлтая; воплощение (ниже черты) — зелёная. Разный цвет над и под чертой визуально держит разделитель «что / чем».

---

## Правила раскладки

- **Ось X — следование процесса:** столбцы историй слева направо, шаг ~220 px (ширина карточки 200 + зазор 20).
- **Ось Y — подчинение функции:** карточки истории сверху вниз строго Ц→Н→С→Д→О→О′, шаг ~70 px (высота 60 + зазор 10).
- **Подчинение шагов:** крупный шаг ставь **выше** его под-шагов отдельной карточкой-«шапкой» над группой столбцов.
- **Черта** — на одной Y для всех столбцов; формы реализации выравнивай по строкам под ней.
- Камера: начинай с `cameraUpdate` (для 3 историй ~`840×640`); для широкой карты панорамируй `cameraUpdate` по секциям.
- Шрифты: текст карточек `fontSize 13–14`, заголовки историй `16`, заголовок карты `20`. Не мельчи.
- Порядок отрисовки (для анимации): заголовок → подписи строк → столбец за столбцом (5 карточек сверху вниз → черта → формы).
- Без эмодзи внутри `text`/`label` (шрифт Excalidraw их не рисует).

---

## Рабочий пример: 3 истории «Запись в парикмахерскую»

Готовый вызов `create_view` (можно взять за основу). Три столбца — «Выбор услуги», «Выбор времени», «Подтверждение», каждый из 5 карточек Ц·Н·С·Д·О→О′; под чертой — формы реализации. Пример из `docs/SIM/primer/skvoznoy-primer.md`.

```json
[
  {"type":"cameraUpdate","width":840,"height":640,"x":0,"y":0},
  {"type":"text","id":"title","x":30,"y":8,"text":"Карта реализации историй: онлайн-запись в парикмахерскую (как будет)","fontSize":20,"strokeColor":"#1e1e1e"},

  {"type":"text","id":"rL1","x":35,"y":100,"text":"Ц","fontSize":16,"strokeColor":"#868e96"},
  {"type":"text","id":"rL2","x":35,"y":170,"text":"Н","fontSize":16,"strokeColor":"#868e96"},
  {"type":"text","id":"rL3","x":35,"y":240,"text":"С","fontSize":16,"strokeColor":"#868e96"},
  {"type":"text","id":"rL4","x":35,"y":310,"text":"Д","fontSize":16,"strokeColor":"#868e96"},
  {"type":"text","id":"rL5","x":30,"y":380,"text":"О→О′","fontSize":16,"strokeColor":"#868e96"},
  {"type":"text","id":"rL6","x":30,"y":470,"text":"формы","fontSize":14,"strokeColor":"#2b8a3e"},

  {"type":"text","id":"hA","x":110,"y":72,"text":"A. Выбор услуги","fontSize":16,"strokeColor":"#1e1e1e"},
  {"type":"rectangle","id":"a1","x":110,"y":90,"width":200,"height":60,"backgroundColor":"#fff3bf","fillStyle":"solid","strokeColor":"#f59e0b","strokeWidth":1,"roundness":{"type":3},"label":{"text":"не ошибиться с выбором","fontSize":13}},
  {"type":"rectangle","id":"a2","x":110,"y":160,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Клиент","fontSize":13}},
  {"type":"rectangle","id":"a3","x":110,"y":230,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"решил постричься, деталей нет","fontSize":13}},
  {"type":"rectangle","id":"a4","x":110,"y":300,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"подбирает услугу из доступных","fontSize":13}},
  {"type":"rectangle","id":"a5","x":110,"y":370,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"хочу постричься -> услуга","fontSize":13}},
  {"type":"line","id":"cutA","x":110,"y":445,"width":200,"height":0,"points":[[0,0],[200,0]],"strokeColor":"#1e1e1e","strokeWidth":2},
  {"type":"rectangle","id":"aF1","x":110,"y":455,"width":200,"height":42,"backgroundColor":"#d3f9d8","fillStyle":"solid","strokeColor":"#22c55e","strokeWidth":1,"roundness":{"type":3},"label":{"text":"каталог услуг на сайте","fontSize":13}},
  {"type":"rectangle","id":"aF2","x":110,"y":505,"width":200,"height":42,"backgroundColor":"#d3f9d8","fillStyle":"solid","strokeColor":"#22c55e","strokeWidth":1,"roundness":{"type":3},"label":{"text":"звонок администратору","fontSize":13}},

  {"type":"text","id":"hB","x":330,"y":72,"text":"B. Выбор времени","fontSize":16,"strokeColor":"#1e1e1e"},
  {"type":"rectangle","id":"b1","x":330,"y":90,"width":200,"height":60,"backgroundColor":"#fff3bf","fillStyle":"solid","strokeColor":"#f59e0b","strokeWidth":1,"roundness":{"type":3},"label":{"text":"удобное время, без очереди","fontSize":13}},
  {"type":"rectangle","id":"b2","x":330,"y":160,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Клиент","fontSize":13}},
  {"type":"rectangle","id":"b3","x":330,"y":230,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"услуга выбрана, видна занятость","fontSize":13}},
  {"type":"rectangle","id":"b4","x":330,"y":300,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"выбирает свободное время","fontSize":13}},
  {"type":"rectangle","id":"b5","x":330,"y":370,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"список слотов -> выбранный слот","fontSize":13}},
  {"type":"line","id":"cutB","x":330,"y":445,"width":200,"height":0,"points":[[0,0],[200,0]],"strokeColor":"#1e1e1e","strokeWidth":2},
  {"type":"rectangle","id":"bF1","x":330,"y":455,"width":200,"height":42,"backgroundColor":"#d3f9d8","fillStyle":"solid","strokeColor":"#22c55e","strokeWidth":1,"roundness":{"type":3},"label":{"text":"виджет-календарь на сайте","fontSize":13}},

  {"type":"text","id":"hC","x":550,"y":72,"text":"C. Подтверждение","fontSize":16,"strokeColor":"#1e1e1e"},
  {"type":"rectangle","id":"c1","x":550,"y":90,"width":200,"height":60,"backgroundColor":"#fff3bf","fillStyle":"solid","strokeColor":"#f59e0b","strokeWidth":1,"roundness":{"type":3},"label":{"text":"закрепить место, обе стороны знают","fontSize":13}},
  {"type":"rectangle","id":"c2","x":550,"y":160,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Клиент","fontSize":13}},
  {"type":"rectangle","id":"c3","x":550,"y":230,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"услуга и время выбраны","fontSize":13}},
  {"type":"rectangle","id":"c4","x":550,"y":300,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"подтверждает, оставляет контакт","fontSize":13}},
  {"type":"rectangle","id":"c5","x":550,"y":370,"width":200,"height":60,"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","strokeWidth":1,"roundness":{"type":3},"label":{"text":"черновик -> подтверждённая запись","fontSize":13}},
  {"type":"line","id":"cutC","x":550,"y":445,"width":200,"height":0,"points":[[0,0],[200,0]],"strokeColor":"#1e1e1e","strokeWidth":2},
  {"type":"rectangle","id":"cF1","x":550,"y":455,"width":200,"height":42,"backgroundColor":"#d3f9d8","fillStyle":"solid","strokeColor":"#22c55e","strokeWidth":1,"roundness":{"type":3},"label":{"text":"кнопка Записаться","fontSize":13}},
  {"type":"rectangle","id":"cF2","x":550,"y":505,"width":200,"height":42,"backgroundColor":"#d3f9d8","fillStyle":"solid","strokeColor":"#22c55e","strokeWidth":1,"roundness":{"type":3},"label":{"text":"SMS/пуш с подтверждением","fontSize":13}}
]
```

Что показывает пример: три столбца-истории в порядке процесса (A→B→C); в каждом жёлтая карточка Ц сверху держит историю, ниже голубые Н·С·Д·О→О′; чёрная `line` = черта-разделитель; зелёные карточки под чертой = формы реализации (у A и C по два варианта, у B — один). Стрелки «→» в тексте заменены на `->` — Excalidraw не всегда рисует юникод-стрелку в label.

---

## Итеративная доработка

`create_view` возвращает `checkpointId`. Чтобы дополнить карту (добавить историю D, формы, требования), не пересылая всё заново, начни массив с `{"type":"restoreCheckpoint","id":"<checkpointId>"}` и добавь новые элементы. Удаление — псевдоэлемент `{"type":"delete","ids":"bF1,cutB"}`. Новым элементам всегда давай новые `id`.

---

## Fallback-движки

Если Excalidraw MCP недоступен:
- **Официальный инструмент автора** — среда **Социотех** (`sociotech.center`): единственный инструмент от автора метода, полностью поддерживает КРИ на уровне сценариев и структуры данных.
- **Шаблоны автора для электронных досок** (переиспользовать): Holst.so, Figma (community), Miro (miroverse), Numbers, Excel — отдаём матрицу в один из них. См. `examples/README.md`.

> Рендер — последний шаг. Сначала карта должна быть связной и пройти `/sim-validate` (🟢/🟡). Красоту наводим после логики.
