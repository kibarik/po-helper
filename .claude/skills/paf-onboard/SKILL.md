---
name: paf-onboard
description: "Цифровизация контекста продукта в узлы Нексусов GROUND Vault по всему _registry.yaml: ингестия документов из _intake/ + интервью по seed_questions → low-CP допущения. Главный, repeatable, idempotent. Запусти после /paf-init (и опц. /paf-nexus-create)."
---

# /paf-onboard — цифровизация контекста в GROUND Vault

Skill коробки «PAF Team OS». Наполняет **все** Нексусы `GROUND/NEXUS/_registry.yaml` (дефолт + кастом) узлами-допущениями из документов клиента и интервью. Главная команда онбординга; repeatable и idempotent (upsert + дедуп). Реализует §5 спеки `docs/superpowers/specs/2026-06-21-paf-team-os-design.md`.

> Пошаговый план для LLM. Выполняй фазы по порядку. Читай перечисленные файлы перед записью. Ноль выдуманной PAF-терминологии вне `sa_documentation/naming_conventions.md`. **Узел без `sources` не пишется** — это workslop.

## 0. Контекст (прочитать перед стартом)

- `sa_documentation/nexus_schema.md` — Node schema (§2 обязательные ключи; §2.2 empirical-узлы онбординга: `kind`, `sources`, `confidence 0.2–0.4`, пометка; §3 `node_type`; §4 wilting).
- `sa_documentation/nexus_catalog.md` — seed_questions дефолтных типов (для кастомных — из их `_index.md`).
- `sa_documentation/ground_schema.md` — schema `config.yaml` и `_registry.yaml`.
- `GROUND/config.yaml` — `team.roster` (резолв owner), `onboarding.*`.
- `GROUND/NEXUS/_registry.yaml` — реестр Нексусов (по нему идёт обход).

## 1. Предусловие

- `GROUND/config.yaml` существует. Нет → **останови** и направь на `/paf-init`.
- Detect ruflo MCP: попробуй `mcp__ruflo__memory_stats`. Успех → используешь `mcp__ruflo__memory_search` для дедупа (Phase A). Ошибка/недоступен → fallback Grep по существующим узлам. Не падай без ruflo.

## 2. Определи область обхода

Прочитай `_registry.yaml` → список всех `{slug, source, onboarded}`. Работаешь по каждой записи. Для каждого Нексуса источник seed_questions:
- `source: default` → секция `## seed_questions` в `GROUND/NEXUS/<slug>/_index.md` (там уже скопированы из мастер-каталога).
- `source: custom` → секция `## seed_questions` в его `_index.md` (заполнена `/paf-nexus-create`).

## 3. Phase A — ингестия документов (`GROUND/_intake/`)

1. Перечисли файлы `GROUND/_intake/*` (кроме `.gitkeep`). Пусто → сообщи «`_intake/` пуст — пропускаю ингест, перехожу к интервью» и иди в Phase B.
2. Для каждого документа: прочитай, извлеки факты, разложи по релевантным Нексусам реестра.
3. **Дедуп** перед записью: ruflo `mcp__ruflo__memory_search` (или Grep по `GROUND/NEXUS/<slug>/*.md`). Совпало → **upsert** существующего узла (дополни `sources`, не плоди дубль). Нет → новый узел.
4. Запиши узел по Node schema (§2), `sources: ["onboarding:<имя-файла>"]`. Правила CP — Phase C.

## 4. Phase B — интервью по seed_questions

Для каждого Нексуса реестра, по одному вопросу за раз (конвенция paf-скиллов):
1. Задай его `seed_questions` (из §2). Не угадывай — переспрашивай при неоднозначности.
2. Пропуск вопроса допустим → узел не создаётся, пробел фиксируется для Phase D.
3. Ответ → узел по Node schema (§2), `sources: ["onboarding:interview"]`. Дедуп/upsert как в Phase A (ответ может дополнять узел из документа).

## 5. Phase C — verify + CP + обновление реестра

Для каждого созданного/обновлённого узла:
- `kind: empirical`; `owner` — резолв `owner_role` Нексуса → имя из `config.yaml team.roster` (роль не назначена → `"Cortex"`).
- `confidence: 0.2–0.4` (допущение онбординга, **не валидировано**). Выше не ставить — CP поднимают Steps 1–8.
- `ttl_days` по типу (`nexus_schema.md §2.2`: market/customer=90, growth=60, прочие — по каталогу/`_index.md`).
- `updated` = сегодня (ISO); `ripeness: fresh`.
- В тело узла — пометка: `> ⚠️ **допущение клиента (онбординг)**, требует валидации в Steps 1–8. CP отражает уровень доверия к допущению, не подтверждённый факт.`
- **Идемпотентность:** при upsert НЕ понижай существующий `confidence`, если он > 0.4 (значит узел уже валидирован в Steps 1–8) — только дополни `sources`/тело.

Затем обнови реестр и конфиг:
- `_registry.yaml`: для Нексуса `onboarded: todo → partial`; `→ done`, если покрыты **все** его seed_questions (интервью+документы).
- `config.yaml`: `onboarding.status: init → in_progress` (или `done`, если все Нексусы `done`); добавь обработанные документы в `onboarding.sources_ingested`; при полном покрытии — `onboarding.onboarded_at: <сегодня>`.

## 6. Phase D — readiness-отчёт GROUND Vault

Выведи в чат (не файл, если не просят сохранить):
- Таблица по всем Нексусам: `slug · узлов создано · onboarded (todo/partial/done) · Context Ripeness`.
- **Карта пробелов:** незакрытые seed_questions и Нексусы без узлов.
- **Top low-CP допущений** (для приоритетной валидации в Steps 1–8).
- Финал: «GROUND насыщен (low-CP) → Steps 1–8 валидируют и поднимают CP. Следующее: первый пайплайн (`/okr-context-gen` · `/bft-context-gen` · `/sprint-roadmap` · `/req-context`).»

## 7. Гвардраилы

- Узел без `sources` **не пишется**.
- Онбординг не валидирует; допущения не выдавать за факты.
- `sa_documentation/`, `AI-PROCESSES/`, `docs/` — read-only.
- Повторный прогон безопасен: дедуп + upsert, не затирает CP Steps 1–8.
- Без ruflo — Grep-дедуп (слабее, но работает). Без `_intake/` — только интервью.
