# Рендер доски Связанного SWOT через Excalidraw MCP

Как стадия `/swot-deliver` превращает собранный анализ в наглядную доску. Движок — **Excalidraw MCP** (инструмент `create_view`, рендерит «от руки» прямо в чат с анимацией отрисовки).

> Перед первым вызовом `create_view` один раз вызови `read_me` (справка по формату элементов). Повторно `read_me` не нужен.

---

## Три зоны-подложки

Доска — три вертикальные зоны (`rectangle`, `opacity: 30`, `fillStyle: "solid"`), слева направо:

| Зона | Что внутри | Цвет подложки |
|---|---|---|
| **Внутренние факторы** (слева) | 🟢 сильные сверху, 🔴 слабые снизу | `#F0F9F3` |
| **Стратегические ставки** (центр) | 🟡 ставки, приоритет высотой | `#FFFCEA` |
| **Внешние факторы** (справа) | 🟣 тренды сверху, 🟠 угрозы снизу | `#F1F7FE` |

## Карточки

`rectangle` c `roundness: {type:3}` + `label` с текстом и ИД. Цвет заливки по области:

| Карточка | Цвет | Область |
|---|---|---|
| Сильные | `#AFE192` | внутр., сверху слева |
| Слабые | `#FFACA7` | внутр., снизу слева |
| Ставки | `#FFEE73` | центр |
| Тренды | `#BCC0F8` | внешн., сверху справа |
| Угрозы | `#FFB373` | внешн., снизу справа |

## Стрелки-связи (ниточки)

`arrow`, тонкие (`strokeWidth: 1.5`), **без наконечников** (`endArrowhead: null`, `startArrowhead: null`) — это связи, а не потоки. Цвет по типу фактора (тёмный оттенок карточки): сильные `#6DBE45`, слабые `#E8605B`, тренды `#6E74D6`, угрозы `#E8843C`.

**Точки крепления (критично):**
- внутренние факторы крепятся к **левому** краю карточки-ставки (сильные — сверху слева, слабые — снизу слева);
- внешние факторы крепятся к **правому** краю (тренды — сверху справа, угрозы — снизу справа).

## Отметки использования

Маленький `ellipse` (~14×14, заливка `#2f9e44`) в правом-верхнем углу задействованного фактора. Непокрытые факторы **оставляем без маркера** — визуально видно «осиротевшие» карточки (в примере ниже — Сл2 и У2).

## Приоритет — положением

Внутри каждой области карточки идут сверху вниз по убыванию приоритета. У ставок так же: самая перспективная — выше. Между ставками сохраняй одинаковый вертикальный шаг, чтобы приоритет читался по высоте.

---

## Правила раскладки

- Три зоны по оси X: внутренние `x≈20`, ставки `x≈380`, внешние `x≈800`.
- Шрифты: текст карточек `fontSize ≥ 14`, заголовки зон `≥ 16`, заголовок доски `≥ 20`. Не мельчи.
- Порядок отрисовки (для анимации): подложка зоны → её заголовок → карточки этой зоны сверху вниз → маркеры → и лишь в конце все стрелки-связи (чтобы ниточки легли поверх).
- Без эмодзи внутри `text`/`label` (шрифт Excalidraw их не рисует) — тип области несёт цвет, а не значок.
- Камера: начни с `cameraUpdate` (для этого кейса `1180×580`).

---

## Рабочий пример: кейс «репетитор» (из `docs/LINKED-SWOT/primer/skvoznoy-primer.md`)

Готовый вызов `create_view`. Внутренние: С1/С2 (сильные), Сл1/Сл2 (слабые). Внешние: Т1/Т2 (тренды), У1/У2 (угрозы). Ставки: А (онлайн-курс), Б (пакеты). Связи: А←С1,С2 / А→Т1,У1 · Б←Сл1 / Б→Т2. Сл2 и У2 остаются без маркера — непокрытые.

```json
[
  {"type":"cameraUpdate","width":1180,"height":580,"x":0,"y":0},
  {"type":"text","id":"title","x":30,"y":16,"text":"Связанный SWOT: репетитор Анна (как есть)","fontSize":20,"strokeColor":"#1e1e1e"},

  {"type":"rectangle","id":"zoneIn","x":20,"y":70,"width":320,"height":460,"backgroundColor":"#F0F9F3","fillStyle":"solid","strokeColor":"#63b06f","strokeWidth":1,"opacity":30},
  {"type":"text","id":"zoneInL","x":34,"y":78,"text":"ВНУТРЕННИЕ ФАКТОРЫ (про меня)","fontSize":16,"strokeColor":"#2b8a3e"},
  {"type":"rectangle","id":"c1","x":40,"y":110,"width":280,"height":64,"backgroundColor":"#AFE192","fillStyle":"solid","strokeColor":"#5aa845","strokeWidth":1,"roundness":{"type":3},"label":{"text":"С1. Умею объяснять сложное простыми словами","fontSize":14}},
  {"type":"rectangle","id":"c2","x":40,"y":190,"width":280,"height":64,"backgroundColor":"#AFE192","fillStyle":"solid","strokeColor":"#5aa845","strokeWidth":1,"roundness":{"type":3},"label":{"text":"С2. Есть блог с лояльной аудиторией","fontSize":14}},
  {"type":"rectangle","id":"w1","x":40,"y":360,"width":280,"height":64,"backgroundColor":"#FFACA7","fillStyle":"solid","strokeColor":"#e8605b","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Сл1. Стесняюсь называть цену","fontSize":14}},
  {"type":"rectangle","id":"w2","x":40,"y":440,"width":280,"height":64,"backgroundColor":"#FFACA7","fillStyle":"solid","strokeColor":"#e8605b","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Сл2. Нет системы, всё держится на мне","fontSize":14}},

  {"type":"rectangle","id":"zoneBet","x":380,"y":70,"width":380,"height":460,"backgroundColor":"#FFFCEA","fillStyle":"solid","strokeColor":"#e6c700","strokeWidth":1,"opacity":30},
  {"type":"text","id":"zoneBetL","x":394,"y":78,"text":"СТРАТЕГИЧЕСКИЕ СТАВКИ (что делать)","fontSize":16,"strokeColor":"#b59b00"},
  {"type":"rectangle","id":"betA","x":400,"y":140,"width":340,"height":90,"backgroundColor":"#FFEE73","fillStyle":"solid","strokeColor":"#e6c700","strokeWidth":1,"roundness":{"type":3},"label":{"text":"А. Запустить онлайн-курс с личным разбором, чтобы зарабатывать на умении объяснять","fontSize":14}},
  {"type":"rectangle","id":"betB","x":400,"y":340,"width":340,"height":90,"backgroundColor":"#FFEE73","fillStyle":"solid","strokeColor":"#e6c700","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Б. Ввести пакеты с фикс. ценой и гарантией по баллам, чтобы продавать результат","fontSize":14}},

  {"type":"rectangle","id":"zoneEx","x":800,"y":70,"width":340,"height":460,"backgroundColor":"#F1F7FE","fillStyle":"solid","strokeColor":"#6e74d6","strokeWidth":1,"opacity":30},
  {"type":"text","id":"zoneExL","x":814,"y":78,"text":"ВНЕШНИЕ ФАКТОРЫ (про мир)","fontSize":16,"strokeColor":"#4149c4"},
  {"type":"rectangle","id":"t1","x":820,"y":110,"width":300,"height":64,"backgroundColor":"#BCC0F8","fillStyle":"solid","strokeColor":"#6e74d6","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Т1. Люди всё чаще учатся онлайн","fontSize":14}},
  {"type":"rectangle","id":"t2","x":820,"y":190,"width":300,"height":64,"backgroundColor":"#BCC0F8","fillStyle":"solid","strokeColor":"#6e74d6","strokeWidth":1,"roundness":{"type":3},"label":{"text":"Т2. Родители платят за результат (баллы ЕГЭ)","fontSize":14}},
  {"type":"rectangle","id":"th1","x":820,"y":360,"width":300,"height":64,"backgroundColor":"#FFB373","fillStyle":"solid","strokeColor":"#e8843c","strokeWidth":1,"roundness":{"type":3},"label":{"text":"У1. Море бесплатных уроков на видеохостингах","fontSize":14}},
  {"type":"rectangle","id":"th2","x":820,"y":440,"width":300,"height":64,"backgroundColor":"#FFB373","fillStyle":"solid","strokeColor":"#e8843c","strokeWidth":1,"roundness":{"type":3},"label":{"text":"У2. Другие репетиторы открывают онлайн-школы","fontSize":14}},

  {"type":"ellipse","id":"mC1","x":300,"y":114,"width":14,"height":14,"backgroundColor":"#2f9e44","fillStyle":"solid","strokeColor":"#2f9e44"},
  {"type":"ellipse","id":"mC2","x":300,"y":194,"width":14,"height":14,"backgroundColor":"#2f9e44","fillStyle":"solid","strokeColor":"#2f9e44"},
  {"type":"ellipse","id":"mW1","x":300,"y":364,"width":14,"height":14,"backgroundColor":"#2f9e44","fillStyle":"solid","strokeColor":"#2f9e44"},
  {"type":"ellipse","id":"mT1","x":1106,"y":114,"width":14,"height":14,"backgroundColor":"#2f9e44","fillStyle":"solid","strokeColor":"#2f9e44"},
  {"type":"ellipse","id":"mT2","x":1106,"y":194,"width":14,"height":14,"backgroundColor":"#2f9e44","fillStyle":"solid","strokeColor":"#2f9e44"},
  {"type":"ellipse","id":"mTh1","x":1106,"y":364,"width":14,"height":14,"backgroundColor":"#2f9e44","fillStyle":"solid","strokeColor":"#2f9e44"},

  {"type":"arrow","id":"lA_C1","x":320,"y":142,"width":80,"height":23,"points":[[0,0],[80,23]],"strokeColor":"#6DBE45","strokeWidth":2,"endArrowhead":null,"startArrowhead":null},
  {"type":"arrow","id":"lA_C2","x":320,"y":222,"width":80,"height":-32,"points":[[0,0],[80,-32]],"strokeColor":"#6DBE45","strokeWidth":2,"endArrowhead":null,"startArrowhead":null},
  {"type":"arrow","id":"lA_T1","x":740,"y":165,"width":80,"height":-23,"points":[[0,0],[80,-23]],"strokeColor":"#6E74D6","strokeWidth":2,"endArrowhead":null,"startArrowhead":null},
  {"type":"arrow","id":"lA_Th1","x":740,"y":205,"width":80,"height":187,"points":[[0,0],[80,187]],"strokeColor":"#E8843C","strokeWidth":2,"endArrowhead":null,"startArrowhead":null},
  {"type":"arrow","id":"lB_W1","x":320,"y":392,"width":80,"height":-15,"points":[[0,0],[80,-15]],"strokeColor":"#E8605B","strokeWidth":2,"endArrowhead":null,"startArrowhead":null},
  {"type":"arrow","id":"lB_T2","x":740,"y":378,"width":80,"height":-156,"points":[[0,0],[80,-156]],"strokeColor":"#6E74D6","strokeWidth":2,"endArrowhead":null,"startArrowhead":null}
]
```

Что показывает пример: зелёные ниточки слева от ставки А (С1, С2) и фиолетовая/оранжевая справа (Т1, У1) — баланс есть; у ставки Б красная слева (Сл1) и фиолетовая справа (Т2) — тоже сбалансирована. Зелёные точки-маркеры на С1/С2/Сл1/Т1/Т2/У1 = задействованные факторы; **Сл2 и У2 без маркера** — непокрытые, сигнал на следующую волну (гейт G6 в `hard_gates.md`).

---

## Итеративная доработка

`create_view` возвращает `checkpointId`. Чтобы дополнить доску, не пересылая всё заново, начни массив с `{"type":"restoreCheckpoint","id":"<checkpointId>"}` и добавь новые элементы. Удаление — псевдоэлемент `{"type":"delete","ids":"betB,lB_T2"}`. Новым элементам всегда давай новые `id`.

---

## Fallback-движки

Если Excalidraw MCP недоступен:
- **Официальный инструмент метода — Социотех** (`sociotech.center`).
- **Ручной шаблон — Холст** (`app.holst.so`): экспортируй структуру (3 колонки, карточки с ИД, список связей) под шаблон Холст.
- База знаний и шаблоны автора — [github.com/Byndyusoft/linkedswot](https://github.com/Byndyusoft/linkedswot).

> Рендер — последний шаг. Сначала доска должна пройти `/swot-validate` (🟢/🟡): баланс связок, покрытие факторов, формат ставок. Красоту наводим после логики.
