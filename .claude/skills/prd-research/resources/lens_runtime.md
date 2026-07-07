# prd-research — Wrap: единый исполнитель линзы

Любая линза (шаговая или cross-cutting) исполняется одинаково. Промт-тело (`resources/lenses/<id>.md`) — read-only, НЕ редактируется; Wrap добавляет только вход и персист.

## PULSE — собрать вход
1. По `lenses.yaml` найти линзу по `id`; прочитать `prompt_file`, `host_steps`, `harvest`.
2. Прочитать `GROUND/NEXUS/_registry.yaml` + существующие узлы шага-хозяина и узлы-первопричины (по теме).
3. Собрать **input-пак** и заполнить входную форму промта (`input_request`/Input Block/Context): `product_description`, `target_audience`, `problem_or_hypothesis`, прошлые находки (Step 1 узлы и т.д.). Пусто → `[УТОЧНИТЬ]`, не выдумывать.

## SCOUT — запустить промт дословно
4. Исполнить промт линзы **как есть**: его роль, стадийность, структурный вывод (YAML/карточки), его правила `[Assumption]`.
5. **Нормализация гейт-языка (обёртка, не правка тела):** перед запуском объяви PO: «переход между стадиями — командой `продолжить`/`далее`; правка — `ревизия`». Разные сигналы промтов (`start`/`next`/`continue`) трактуй как эти команды. Тело промта не меняем.
6. **Язык:** если промт англ. по умолчанию — инструктируй «отвечай по-русски» (промты это допускают).
7. `data_needed`/недостаток данных → показать PO список недостающего, пауза (как предписывает промт).

## HARVEST — персист выходов в узлы
8. По `harvest`-мапу линзы: каждый указанный `output` → узел в `nexus` с `node_type`, `cp_policy` (см. node_conventions «CP-политики»). Frontmatter — строго по node_conventions (обяз. ключи + hyp_status/CP по политике + sources + depends_on на input-узлы + ttl_days по нексусу + ripeness: fresh).

8a. **Мультихост-линзы** (`host_steps` из ≥2 шагов, напр. odi/rory-interrogation/aarrr/distribution-channels): harvest-нексус/тип задаёт **host-команда** текущего шага; блок `harvest` в реестре — дефолт первого хоста. Команда приоритетна.

9. Уважать разметку допущений промта: помеченное `[Assumption]`/оценка → `estimate`/`judgment`, не `validated`.
10. Узел без `sources` не создавать.
11. Обновить `{discovery_workspace(step)}/state.yaml` (nodes/cp/status/open_questions/last_touched) + дописать `journal.md` (какая линза, какие выходы, ссылки).

## STOP
Отчёт: линза, создано узлов N по типам, средний CP, `[estimate]`-узлов k. Пауза PO.

> Cross-cutting линза (`host_steps: []`) исполняется тем же Wrap, но HARVEST-нексус берётся из контекста текущего шага (диспетчер `/prd-lens` передаёт `step`).
