# Схема channel-узла (Information Channels Graph)

Канонический источник — `sa_documentation/nexus_catalog.md` §4.2. Здесь — рабочая выжимка для `/channel-map` и `/channel-route`. Узел подчиняется базовой Node schema (`nexus_schema.md` §2); ниже — только `schema_extensions` поверх неё.

## Базовый frontmatter (обязателен для любого узла)

```yaml
nexus: channels
node_id: chan-<slug>        # ascii [a-z][a-z0-9-]*; напр. chan-billing-tg
node_type: channel
paf_step: null
kind: empirical
owner: Product Ops          # или имя из config.yaml team.roster
confidence: 0.2–1.0         # 0.2–0.4 допущение; 0.6–0.8 подтверждено PO; 0.9–1.0 верифицировано
sources: [...]              # onboarding:interview | po:observation | ссылка на канал. Узел без sources = workslop
updated: YYYY-MM-DD
ttl_days: 180
ripeness: fresh
tags: [channel]
```

## schema_extensions

| Поле | Обяз. | Значения / формат | Смысл |
|---|---|---|---|
| `channel_type` | ✅ | chat \| email \| telegram \| call \| tracker \| wiki \| other | Тип канала |
| `platform` | ✅ | строка (Telegram, Slack, Zoom, Email …) | Платформа |
| `handle` | — | @канал / id / email / ссылка | Идентификатор канала |
| `direction` | — | inbound \| outbound \| bidirectional | Направление потока |
| `cadence` | — | поток \| ежедневно \| еженедельно \| по событию | Ритм |
| `purpose` | ✅ | 1-2 фразы | **Для чего** канал |
| `topics` | ✅ | list[string] | **По каким вопросам** здесь пишут |
| `signal_types` | ✅ | requirement \| bug \| decision \| feedback \| status \| risk | Типы сигналов канала |
| `stakeholders` | ✅ | list[node_id из NEXUS/team] | **Кто** в канале |
| `system_areas` | — | list[ссылка на CORTEX/product] | Затрагиваемые участки системы |
| `goals` | — | list[OBJ/KR-код] | Цели, которые питает канал |
| `ingest_action` | — | правило | Что делать с входящим отсюда |

## Обязательный минимум для роутинга

Без `purpose`, `topics`, `stakeholders` узел не выполняет свою функцию (аналог `contact_for`/`expertise_topics` в person-узле). Поле неизвестно → `[УТОЧНИТЬ]` в теле + пустое значение, **не выдумывать**.

## Правила заполнения

1. `node_id` — стабильный ascii-слаг `chan-<что-то>`. Кириллицу транслитерировать.
2. `stakeholders` — только реальные `node_id` из `GROUND/NEXUS/team`. Нет person-узла → создать через `/paf-nexus-create` (team) или пометить `[УТОЧНИТЬ: нет в team]`, не выдумывать людей.
3. `system_areas` / `goals` — только существующие ссылки (CORTEX-узел, KR-код из планирования). Нет — `[УТОЧНИТЬ]`.
4. `confidence` стартует 0.5 (со слов PO); 0.2–0.4 если это допущение онбординга; поднимается по мере подтверждения.
5. `sources` обязателен: откуда знаем про канал (`po:observation`, `onboarding:interview`, ссылка).
6. `ingest_action` формулируется по типам сигналов канала (см. `routing_rules.md`).

## Обновление существующего узла

`/channel-map <slug>` с уже существующим `chan-<slug>` → режим обновления: перечитать текущий узел, показать diff предложенных изменений PO, обновить `updated=today`, пересчитать `ripeness`, сохранить историю в `sources` (добавить, не затирать).
