# 🚀 Онбординг po-helper — с чего начать

> Ты только что установил po-helper и не знаешь, за что взяться. Этот файл — пошаговый план. Открой доску `backlog board` — там те же шаги как задачи (label `onboarding`), отмечай их по мере прохождения.

**Главный результат онбординга — настроенная система:** заполнен `.claude/domain-profile.md` и насыщены **все Нексусы** GROUND Vault (`GROUND/NEXUS/_registry.yaml` → у всех `onboarded ≠ todo`). После этого po-helper персонализирован под твой продукт и готов к пайплайнам (OKR / БФТ / спринты / запросы).

Модель доски — «1 задача = 1 артефакт» (см. `backlog/docs/operational-hq.md`). Источники истины живут в артефактах (`GROUND/`, `bft_documentation/`, трекер, wiki), не на доске.

---

## Шаг 1 — Старт (понять устройство)
Прочитай этот файл и `operational-hq.md`. Пойми: доска — операционный штаб; цель онбординга — насыщенный GROUND Vault.
**Готово когда:** понимаешь, куда идёшь (config + domain-profile + заполненные Нексусы).

## Шаг 2 — Персонализируй domain-profile
```bash
cp .claude/domain-profile.template.md .claude/domain-profile.md
```
Заполни: пути планирования, трекер, wiki, глоссарий, стейкхолдеров, `landscape.ext_teams`. Затем **Reload Window** в IDE — команды появятся в чате.
**Готово когда:** `.claude/domain-profile.md` заполнен под твой продукт.

## Шаг 3 — Инициализируй GROUND Vault: `/paf-init`
Запусти навык `/paf-init` — one-shot интервью (компания, продукт, Product Engineer, роли). Создаёт `GROUND/config.yaml` + скелет + `_registry.yaml` с 13 дефолтными Нексусами.
**Готово когда:** есть `GROUND/config.yaml`, в `_registry.yaml` — дефолтный каталог.

## Шаг 4 — (опц.) Кастомные Нексусы: `/paf-nexus-create`
Нужны Нексусы сверх дефолта (`team`, `channels`, `landscape` или доменные `sellers`/`buyers`)? Запусти `/paf-nexus-create` — по одному на Нексус.
**Готово когда:** нужные кастомные Нексусы в `_registry.yaml` (`source: custom`).

## Шаг 5 — Сложи материалы в `GROUND/_intake/`
Положи документы продукта (стратегия, аналитика, PRD, транскрипты интервью) в `GROUND/_intake/` — `/paf-onboard` их проингестит. Нет документов — пропусти, наполнение пойдёт из интервью.
**Готово когда:** доки в `_intake/` (или осознанный пропуск).

## Шаг 6 — 🎯 Наполни Нексусы: `/paf-onboard` (ГЛАВНОЕ)
Запусти `/paf-onboard`. Он пройдёт по всему реестру: Phase A — ингест `_intake/`; Phase B — интервью по `seed_questions` каждого Нексуса; Phase C — запишет допущения (low-CP) и обновит `onboarded`; Phase D — выдаст readiness-отчёт и карту пробелов.
**Готово когда:** в `_registry.yaml` у всех Нексусов `onboarded ≠ todo` — **система настроена**.

## Шаг 7 — (опц.) Команда и карта людей
`/people-links` (опиши отношения PO), `/people-map` (навигация: кто по каким вопросам), `/radar-calibrate` (качество People Graph).
**Готово когда:** `team`-нексус насыщен, контур PO описан.

## Шаг 8 — Первый реальный проход
Система настроена — примени её. Выбери сценарий:
- **OKR:** `/okr-context-gen <quarter>` … `/okr-deliver`
- **БФТ:** `/bft-context-gen <epic>` … `/bft-deliver`
- **Спринт:** `/sprint-roadmap <quarter>` → `/sprint-sync <sprint>`
- **Внешний запрос:** `/req-context` … `/req-handoff`

Заведи первый артефакт задачей на доске (label `bft`/`okr`/`sprint`/`request`) — см. `operational-hq.md`.
**Готово когда:** первый артефакт в работе, зафиксирован на доске.

---

> Застрял? Полный список сценариев — в корневом `README.md`. Recall «на чём остановился» — `entire search "<тема>"`.
