---
nexus: product
node_id: blueprint-steps-overview
node_type: pipeline-overview
kind: normative
owner: Service Designer
confidence: 0.9
sources: ["[SB1]", "[SB3]", "[SB4]"]
updated: 2026-07-12
ttl_days: 365
ripeness: fresh
tags: [service-blueprint, pipeline]
---

# 🔁 STEPS/overview — конвейер построения Blueprint (7 стадий)

> Карта конвейера. Бизнес-процесс **идентичен `bft-writer`**: каждая стадия = отдельная роль, отдельный артефакт, STOP-пауза для человека. Не строй всю диаграмму «за один промт» — STOP после каждой стадии.

---

## Конвейер

```
0. FRAME     → frame.md        Service Framer      [СТОП: человек ревьюит рамку]
      ↓
1. JOURNEY   → journey.md      Journey Analyst     [СТОП: человек ревьюит путь клиента]
      ↓
2. ONSTAGE   → onstage.md      Frontstage Designer
      ↓
3. BACKSTAGE → backstage.md    Backstage Analyst   [СТОП: человек ревьюит вертикали]
      ↓
4. WEAVE     → blueprint.puml  Systems Weaver      ← соединение опыта воедино (ядро)
      ↓
5. VALIDATE  → validation.md   Validator (свежий взгляд)
      ↓ 🔴 нарушен гейт → возврат на стадию-источник
      ↓ 🟢/🟡
6. DELIVER   → рендер + публикация  Deliverer      [СТОП: сухой прогон → ок человека]
      ↓
   Done
```

## Роли и артефакты

| Стадия | Команда (план) | Роль | Артефакт | Дорожки/линии, которые наполняет |
|---|---|---|---|---|
| 0 [[0.frame]] | `/bp-frame` | Service Framer | `artefacts/frame.md` | ось X (шаги), актор, скоуп, as-is/to-be |
| 1 [[1.journey]] | `/bp-journey` | Journey Analyst | `artefacts/journey.md` | `Customer Actions` + `Physical Evidence` + эмоции + Line of Interaction |
| 2 [[2.onstage]] | `/bp-onstage` | Frontstage Designer | `artefacts/onstage.md` | `Onstage` + Line of Visibility |
| 3 [[3.backstage]] | `/bp-backstage` | Backstage Analyst | `artefacts/backstage.md` | `Backstage` + `Supporting Processes` + Line of Internal Interaction |
| 4 [[4.weave]] | `/bp-weave` | Systems Weaver | `<service>.puml` | стрелки, вертикали, fail-points, моменты истины |
| 5 [[5.validate]] | `/bp-validate` | Validator | `artefacts/validation.md` | Светофор по гейтам ([[../principles]]) |
| 6 [[6.deliver]] | `/bp-deliver` | Deliverer | рендер + публикация | — |

> Имена команд (`/bp-*`) — план будущего навыка (зеркало `bft-writer` `/bft-*`). Эта папка описывает **методологию**; сам навык собирается поверх неё.

## Рабочая папка сервиса (staging)

Все наработки — внутри папки сервиса `<workspace>/<service>/`. Финальная диаграмма `<service>.puml` в корне; промежуточные артефакты — в `artefacts/`.

```
<workspace>/<service>/
├── <service>.puml           (4.weave) → ФИНАЛЬНАЯ диаграмма
└── artefacts/
    ├── frame.md             (0.frame)
    ├── journey.md           (1.journey)
    ├── onstage.md           (2.onstage)
    ├── backstage.md         (3.backstage)
    └── validation.md        (5.validate)
```

## Почему такое разделение (как в bft-writer)

- **Роли не загрязняют друг друга:** путь клиента (JOURNEY) ≠ фронт (ONSTAGE) ≠ бэк (BACKSTAGE). Тот, кто рисует бэк-процессы, не должен переписывать эмоции клиента.
- **WEAVE вынесен отдельно:** соединение слоёв — самая сложная и ценная операция, её нельзя делать «между делом».
- **VALIDATE свежим взглядом:** adversarial-проход ломает confirmation bias автора.
- **STOP-паузы:** human-in-the-loop на границах, где легко уехать (скоуп, путь, вертикали, финальный вид).

## Направление наполнения

**Сверху вниз по дорожкам, слева направо по времени.** Сначала горизонталь (путь клиента, стадия 1), затем вертикали под каждым шагом (стадии 2–3), затем сшивка (стадия 4). Обратный порядок (начать с систем) ведёт к диаграмме «процесс без опыта».

---

## Главное правило процесса

**STOP после каждой ключевой стадии.** После FRAME, JOURNEY, BACKSTAGE, DELIVER — выводи артефакт и жди решения человека. Только так конвейер = `bft-writer` по качеству, а не «генерация диаграммы за один промт».

---

**Version:** 0.1 · **Last updated:** 2026-07-12 · **См. также:** [[../README]] · [[../anatomy]] · [[../principles]]
