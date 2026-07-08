# Матрица Нексус × Процесс — грунтовка процессов GROUND-Нексусами

> **Назначение.** Единый источник истины: какие Нексусы GROUND грунтуют какой процесс. Дефолтный набор (12 Нексусов, см. [[nexus_catalog]]) должен **использоваться**, а не только создаваться `/paf-init`. Этот файл связывает слой фактов (GROUND Vault) с движками процессов (`request-intake`, `bft-writer`, `okr-planner`, `sprint-planner`, `release-guard`, `po-research`).
>
> **Источник истины по составу** — `GROUND/NEXUS/_registry.yaml` (реестр клиента). Процессы читают **релевантные по теме** Узлы, а не хардкод из 4 типов. Нет контекста в Нексусе → `[УТОЧНИТЬ]`, не блокируй (graceful degradation): онбординг мог не наполнить Нексус.

---

## 1. Дефолтный набор (напоминание)

| Ярус | Нексусы |
|---|---|
| **PAF-минимум** (продуктовый контекст) | `market`, `customer`, `product`, `growth` |
| **po-helper intake→БФТ** (контекст внешнего запроса) | `problem`, `system-landscape`, `ownership`, `requester-domain`, `precedents`, `compliance`, `strategy`, `capacity` |

Полные определения и `seed_questions` — [[nexus_catalog]] §3 (PAF) и §3A (po-helper).

---

## 2. Матрица: какой Нексус грунтует какой процесс

`●` — ключевой источник процесса, `○` — вспомогательный.

| Нексус \ Процесс | intake<br>`/req-context` | intake<br>`/req-score` | БФТ<br>`/bft-context-gen(-deep)` | БФТ<br>`/bft-problem` | OKR<br>`/okr-context-gen` | Sprint<br>`/sprint-sync` | Release<br>`/release-baseline` | Research<br>`/po-research` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `problem` | ● | ○ | ● | ● | | | | ○ |
| `system-landscape` | ● | | ● | ● | | | ○ | ● |
| `ownership` | ● | ○ | ● | ● | | ○ | ○ | ○ |
| `requester-domain` | ● | ○ | ● | ○ | | | | ○ |
| `precedents` | ● | ● | ● | ○ | ○ | ○ | | ● |
| `compliance` | ○ | ● | ● | ○ | | | ● | ● |
| `strategy` | ○ | ● | ○ | | ● | ○ | ● | ○ |
| `capacity` | | ● | ○ | | ● | ● | ● | ○ |
| `market`/`customer`/`product`/`growth` | ○ | ○ | ○ | ○ | ● | ○ | ○ | ● |

---

## 3. Как процесс грунтуется (единый контракт)

Каждый **context-stage** процесса (стадия 0 / sync / baseline) выполняет один и тот же шаг грунтовки:

1. Прочитать `GROUND/NEXUS/_registry.yaml` — какие Нексусы инстанцированы (учесть кастомные `source: custom`).
2. По теме топика прочитать **релевантные** Узлы из ключевых Нексусов процесса (колонка `●` матрицы §2).
3. Каждый факт из Нексуса → якорь `R2` (путь `GROUND/NEXUS/<slug>/<node>.md`), CP и freshness Узла учитываются.
4. Нексус пуст / нет Узла по теме → `[УТОЧНИТЬ: нет в <slug>]`, не выдумывать. Наполнение — `/paf-onboard`.
5. Устаревший Узел (`ripeness: wilting`) → пометить `⚠️ протухло, верифицировать`.

> Нексусы — **слой фактов** (empirical, CP отражает валидацию). Они не заменяют CORTEX (слой знаний: C1 архитектура, C3 регуляторика, ADR) и трекер (JIRA) — они дополняют их структурированным контекстом онбординга и разбора запросов.

---

## 4. Обратная запись (процесс → Нексус)

Грунтовка двунаправленна: процессы не только читают, но и **обновляют** Нексусы (по мере появления фактов). Обновление идёт по правилам Node schema ([[nexus_schema]]): проставить `sources`, поднять `confidence`, обновить `updated`.

| Процесс | Пишет в Нексус |
|---|---|
| `request-intake` (разбор запроса) | `problem`, `requester-domain`, `precedents` (новый прецедент — почему приняли/отклонили) |
| `bft-writer` (диагноз/концепт) | `system-landscape`, `ownership`, `compliance` |
| `okr-planner` | `strategy` (OKR квартала → образ действия) |
| `sprint-planner` | `capacity` (velocity/ёмкость по факту спринта) |
| `release-guard` | `capacity` (cost of delay, дрейф) |

> Обратная запись — по спросу, не обязательна в v1: минимально процессы **читают** Нексусы (§3). Запись включается, когда PO хочет, чтобы разбор запросов накапливал прецеденты и мощность в GROUND, а не только в артефактах пайплайна.

---

## 5. Связи

- [[nexus_catalog]] — определения 12 дефолтных Нексусов (§3 PAF, §3A po-helper).
- [[nexus_schema]] — Node schema, правила `sources`/`confidence`/`ripeness`.
- [[ground_schema]] — `_registry.yaml` (реестр — источник истины по составу).
- `/paf-init` — создаёт набор; `/paf-onboard` — наполняет; `/paf-nexus-create` — добавляет кастомные.

---
**Version:** 1.0 · **Last updated:** 2026-07-01 · **Связанные:** [[nexus_catalog]] · [[nexus_schema]] · [[ground_schema]]
