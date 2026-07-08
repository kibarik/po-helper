from __future__ import annotations
from .deckspec import DeckSpec, Direction
from .theme import Theme
from .archetypes import ARCHETYPES
from .layout import Slide

_LIFECYCLE_STAGES = ["Дизайн и данные", "Разработка", "Отладка и выкатка"]


def _kr_detail_data(kr) -> dict:
    # group образ действия steps into a single "stages" block (simple: one stage)
    stages = [{"label": "Образ действия", "steps": [{"role": s.role, "text": s.text}
                                                    for s in kr.steps]}]
    return {"kicker": f"KR {kr.id}", "title": kr.title,
            "now": kr.now or "[УТОЧНИТЬ]", "becomes": kr.becomes or "[УТОЧНИТЬ]",
            "stages": stages, "risks": [r.text for r in kr.risks]}


def _lifecycle_rows(direction: Direction) -> list[dict]:
    rows = []
    for obj in direction.objs:
        for kr in obj.krs:
            rows.append({"label": kr.title, "cells": kr.sprint_cells})
    return rows


def _collect_sprints(spec: DeckSpec) -> list[str]:
    seen = []
    for d in spec.directions:
        for o in d.objs:
            for kr in o.krs:
                for sp in kr.sprint_cells:
                    if sp not in seen:
                        seen.append(sp)
    return sorted(seen, key=lambda s: int(s.lstrip("S") or 0))


def build_slides(spec: DeckSpec, theme: Theme) -> list[Slide]:
    sprints = _collect_sprints(spec)
    plan: list[tuple[str, dict]] = []

    plan.append(("title", {"kicker": f"КВАРТАЛ {spec.product} · {spec.quarter}",
                           "headline": f"Что мы делаем\nс {spec.subtitle}",
                           "sub": "Общая картина квартала простым языком."}))
    cards = [{"n": d.number, "title": d.name,
              "note": d.blurb, "color": d.color or theme.direction_color(i)}
             for i, d in enumerate(spec.directions)]
    plan.append(("big_picture", {"kicker": "ОБЩАЯ КАРТИНА",
                                 "headline": "Что мы делаем в этом квартале", "cards": cards}))
    if spec.authored.market:
        plan.append(("why_market", {"kicker": "ЗАЧЕМ ЭТО ВСЁ", "headline": "Контекст рынка",
                                    "stats": spec.authored.market,
                                    "shift": spec.authored.quarter_shift}))
    if spec.authored.glossary:
        plan.append(("glossary", {"kicker": "СЛОВАРЬ", "headline": "Что есть что — простыми словами",
                                  "terms": spec.authored.glossary}))
    plan.append(("how_to_read", {"kicker": "КАК ЧИТАТЬ ДАЛЬШЕ",
                                 "headline": "По одной задаче на слайд: что сейчас и что станет",
                                 "footnote": "Как устроено внутри — здесь не разбираем. Только результат."}))

    for i, d in enumerate(spec.directions):
        color = d.color or theme.direction_color(i)
        plan.append(("direction_divider", {"number": f"{d.number:02d}", "kicker": "НАПРАВЛЕНИЕ",
                                            "title": d.name, "blurb": d.blurb, "color": color}))
        plan.append(("sprint_lifecycle_table",
                     {"kicker": f"НАПРАВЛЕНИЕ {d.number} · КАК РАБОТАЕМ",
                      "headline": "Как двигаемся по спринтам", "sprints": sprints,
                      "rows": _lifecycle_rows(d), "owners": ""}))
        for obj in d.objs:
            for kr in obj.krs:
                plan.append(("now_becomes_detail", _kr_detail_data(kr)))

    if spec.authored.order_of_work:
        plan.append(("order_of_work", {"kicker": "КАК ДВИГАЕМСЯ", "headline": "Порядок работ",
                                       "order": spec.authored.order_of_work}))
    if spec.authored.right_now:
        plan.append(("right_now", {"kicker": "ПРЯМО СЕЙЧАС", "headline": "Что делаем в первую очередь",
                                   "items": spec.authored.right_now}))
    if spec.authored.after_meeting:
        plan.append(("after_meeting", {"kicker": "ЧТО ПОСЛЕ ЭТОЙ ВСТРЕЧИ",
                                       "headline": "Детальные задачи распишем в JIRA",
                                       "body": spec.authored.after_meeting}))
    if spec.authored.takeaways:
        plan.append(("takeaways", {"kicker": "ЧТО ЗАПОМНИТЬ", "headline": "Главное",
                                   "items": spec.authored.takeaways}))

    slides: list[Slide] = []
    page = 0
    for name, data in plan:
        els = ARCHETYPES[name](data, theme)
        if name == "title":
            slides.append(Slide(name, els, footer="", page=0))
        else:
            page += 1
            slides.append(Slide(name, els, footer=spec.footer, page=page))
    return slides
