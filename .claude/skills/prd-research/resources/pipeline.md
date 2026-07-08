# prd-research — карта пайплайна (8 шагов)

> Источник: docs/AI-PROCESSES/README.md (хребет) + spec §4.1. Read-only справочник для стадий.

| Шаг | Команда | paf_step | Нексусы | node_type/типы | overview | RB-источник | Fit-гейт |
|---|---|---|---|---|---|---|---|
| 1 Idea | /prd-idea | 1 | market·product·growth | 3 Линзы, BIG Idea | docs/AI-PROCESSES/STEP-1-IDEA/overview.md | docs/TRADITIONAL/RB-STEP-1-IDEA | — |
| 2 Customer | /prd-customer | 2 | customer | сегмент/проблема/JTBD | STEP-2-CUSTOMER/overview.md | RB-STEP-2 | — |
| 3 Market | /prd-market | 3 | market | Force/Trend/Constant/TAM-SAM-SOM/Competitor/Gap/Bet | STEP-3-MARKET/overview.md | RB-STEP-3 | — |
| 4 Value | /prd-value | 4 | product | ценностное предложение | STEP-4-VALUE/overview.md | RB-STEP-4 | Need/Value Fit |
| 5 Business Model | /prd-bizmodel | 5 | growth | монетизация/юнит-эк./NPV | STEP-5-BUSINESS-MODEL/overview.md | RB-STEP-5 | Biz-model |
| 6 GTM | /prd-gtm | 6 | growth | позиционирование/каналы | STEP-6-GO-TO-MARKET/overview.md | RB-STEP-6 | — |
| 7 Solution | /prd-solution | 7 | product·system-landscape | требования/прототип/PMF | STEP-7-SOLUTION-PMF/overview.md | RB-STEP-7 | PMF |
| 8 Acquisition | /prd-acquisition | 8 | growth | сегмент-канал-оффер/PCF | STEP-8-ACQUISITION-PCF/overview.md | RB-STEP-8 | PCF |

> **Линзы шагов** — `resources/lenses.yaml` (реестр) + `resources/lenses/<id>.md` (промты дословно). Step 2 Customer: плейлист segmentation → consumer-context → odi. Cross-cutting (rat/ab-design/ost/nsm) — через `/prd-lens`.

> **Плейлисты шагов 3–8:** Market → tam-sam-som · Value → nsm/odi/rory-interrogation (гейт Need/Value Fit) · BizModel → unit-economics/aarrr (гейт Biz-model) · GTM → positioning-4p/distribution-channels/rory-interrogation · Solution → ost/ab-design/rat (гейт PMF) · Acquisition → aarrr/distribution-channels (гейт PCF).
