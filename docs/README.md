# Документация и методология PO-Helper

Здесь — **обучающие материалы и описание методологии** для пользователей. Это справочный слой: код инструмента (`/bft-*`, `/okr-*`, `/po-research`, PAF) живёт в `.claude/`, а это — теория, на которой он построен.

## Методология (для пользователей)

| Раздел | Что внутри | Кому |
|--------|------------|------|
| [`AI-PROCESSES/`](AI-PROCESSES/README.md) | AI-Native фреймворк Product Discovery: 9 вех (Step 0…8, от Идеи до PCF) × движок Product Sprint (`PULSE → SCOUT → BUNCH → PITCH → EXECUTE → HARVEST`) + опер-модель и fit-точки | основной справочник процесса |
| [`AI-TRANSFORMATION/`](AI-TRANSFORMATION/index.md) | Принципы AI-Native команды по PAF (Тихомиров С.), источники `[S1]–[S7]` | теория и роли |
| `TRADITIONAL/` | Raw-раннбуки классического Product Discovery (`RB-STEP-1…8`) — первоисточник методов | глубокое погружение |
| [`BLUEPRINT/`](BLUEPRINT/README.md) | Методология построения Service Blueprint (гибридная нотация CJM × Blueprint по А. Шапиро): анатомия 5 дорожек + 3 линии, StepByStep-конвейер из 7 стадий (бизнес-процесс — зеркало `bft-writer`) | построение диаграмм опыта услуги |
| `RL/` | Research Library — заметки-исследования (рост, A/B, метрики) | точечные темы |

## Внутреннее (для контрибьюторов)

| Раздел | Что внутри |
|--------|------------|
| [`superpowers/`](superpowers/) | Планы и спеки разработки (PAF Team OS, blueprint-pipeline, ATLAS) — design-документы, не пользовательские |

> Методология PAF (`AI-TRANSFORMATION/`) — CC BY-SA 4.0, автор Тихомиров Сергей. Остальной код — MIT.
