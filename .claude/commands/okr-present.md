---
description: 'OKR Pipeline финал квартала — deck.html (поверхность правок) → .pptx + Roadmap.xlsx из всего vault (роль: Quarter Storyteller + Consistency Auditor)'
---

## Использование

```
/okr-present <quarter>
```

Вход: **весь vault квартала** — `{okr_output_doc}`, `{sprint_roadmap_doc}`, `{sprint_output_doc}` (по каждому спринту квартала), `{kr_epic_map_doc}`, `landscape-{quarter}.md`, `GROUND/NEXUS/team/*`, `domain-profile`.
Выход: сперва `{quarter_deck_html}` (поверхность правок) → после «принято» PO — `{quarter_deck_doc}` (.pptx) + `{quarter_roadmap_xlsx}`.

## Важно

**Роль: Quarter Storyteller + Consistency Auditor.** Модель — vault→render: презентация квартала собирается из уже утверждённых артефактов (OKR, roadmap по спринтам, ФАКТ спринтов, ландшафт внешних команд, состав команды), а не придумывается заново. HTML — единственная поверхность правок: PO смотрит и просит правки на HTML, .pptx рендерится тем же движком из того же `deck-spec.yaml`, поэтому вёрстка идентична. Финал (`.pptx` + `.xlsx`) фиксируется **только после явного «принято» от PO**.

> Каждый факт на слайде ← `src:` (якорь на vault-документ) или явный `authored:` (рамка презентации: направления+цвета, рынок+источник, глоссарий, order_of_work/right_now/takeaways). Без источника — `[УТОЧНИТЬ]`, никогда не выдумывать.

---

## Инструкция для LLM

### Фаза A · Сбор + аудит

1. Прочитай `skills/okr-planner/SKILL.md`, `resources/deck_spec_schema.md`, `resources/present_gates.md`.
2. Собери данные из vault: `{okr_output_doc}` (OBJ/KR), `{sprint_roadmap_doc}` + `{sprint_output_doc}` по каждому спринту (sprint_cells, owners), `{kr_epic_map_doc}` (эпики), `landscape-{quarter}.md` (внешние зависимости), `GROUND/NEXUS/team/*` (исполнители).
3. Заполни `deck-spec.yaml` по схеме `deck_spec_schema.md` — каждый факт с `src:` (якорь на исходный документ/строку).
4. Прогони Светофор консистентности: `python3 -m engine.gates` (или вызови `engine.gates.audit(spec)` + `format_report(rep)`) → распечатай результат PO.
5. 🔴 → **СТОП**, вернуть PO на доработку фактов/vault (список нарушений — построчно). Не продолжать до 🟡/🟢.

Artifact: `{deck_spec_doc}`.

### Фаза B · Доавторинг рамки

Опроси PO **по одному вопросу за раз** (не монологом) — заполнить блок `authored:`:
1. Направления квартала + цвета (или дефолт палитры темы).
2. Рыночный контекст (`market`) — числа + обязательный `src` на каждое.
3. Глоссарий (`glossary`) — термины, которые нужно расшифровать нетехническим стейкхолдерам.
4. `order_of_work` / `right_now` / `takeaways` — рамка «сначала/к концу/дальше», «прямо сейчас», «что запомнить».

Дописать `authored:` в `deck-spec.yaml`. STOP — дождаться ответов PO по каждому пункту.

### Фаза C · deck-spec dry-run

Показать PO перечень слайдов в порядке `build_slides` (title → big_picture → why_market? → glossary? → how_to_read → по каждому направлению: divider → lifecycle table → now_becomes_detail на каждый KR → order_of_work? → right_now? → after_meeting? → takeaways?) + якоря (`src`) каждого факта. STOP — PO подтверждает состав перед рендером.

### Фаза D1 · Рендер HTML

```
cd .claude/skills/okr-planner/resources && python3 -m engine.render_html {deck_spec_doc} {quarter_deck_html}
```

Предложить PO открыть `{quarter_deck_html}` или опубликовать его как Artifact для просмотра. STOP.

### Фаза E · Коррекция

PO называет правки на HTML. В зависимости от типа правки:
- факт (число, текст, sprint-ячейка) → правь vault-источник → перенеси в `deck-spec.yaml` с тем же `src`;
- рамка (направление, рынок, глоссарий, order_of_work/right_now/takeaways) → правь `authored:` в spec;
- вёрстка (цвет, шрифт, отступ) → правь `resources/theme.md` / `present:` секцию domain-profile.

После каждой правки — перезапустить Фазу D1 (`render_html`). Цикл повторяется до явного «принято» от PO.

### Фаза D2 · Финализация

Только после «принято»:

```
cd .claude/skills/okr-planner/resources && python3 -m engine.render_pptx {deck_spec_doc} {quarter_deck_doc}
cd .claude/skills/okr-planner/resources && python3 -m engine.render_roadmap {deck_spec_doc} {quarter_roadmap_xlsx}
```

Повторно прогнать Светофор (`engine.gates.audit`) — убедиться, что цикл коррекций (фаза E) не оставил новых 🔴/🟡. Закоммитить артефакты. STOP — финал.

---

## Гигиена

- Артефакты (`deck-spec.yaml`, `.html`, `.pptx`, `.xlsx`) — под git, в `{planning_root}/presentation/` (и `{okr_workspace}/present/` для spec). Не в tmp/worktree.
- Трекер (JIRA/Confluence) — **только чтение**, `/okr-present` ничего туда не пишет.
- Не рендерить `.pptx`/`.xlsx` (фаза D2) до явного «принято» PO на HTML — только `render_html` повторяется в цикле коррекции.

## Запреты

1. НЕ рендерить финал (`.pptx`/`.xlsx`) до «принято» PO — только `render_html` в цикле E.
2. 🔴 на Светофоре (фаза A или перед D2) → СТОП, не продолжать.
3. НЕ выдумывать факты без `src:` — `[УТОЧНИТЬ]`.
4. НЕ писать в JIRA/Confluence — только чтение.
