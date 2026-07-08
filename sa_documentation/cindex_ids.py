"""Детерминированная генерация node_id для Confluence Indexator.

node_id = "<nexus>-<slug(title)>", ascii, паттерн [a-z][a-z0-9-]*, <= 60 символов.
См. docs/superpowers/specs/2026-07-04-confluence-indexator-design.md §6, §8.
"""
import re

# Практичная таблица транслитерации ГОСТ-подобная (нижний регистр).
_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(text: str) -> str:
    text = text.strip().lower()
    out = []
    for ch in text:
        if ch in _TRANSLIT:
            out.append(_TRANSLIT[ch])
        elif ch.isascii() and (ch.isalnum()):
            out.append(ch)
        else:
            out.append(" ")
    slug = "".join(out)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def make_node_id(nexus: str, title: str, max_len: int = 60) -> str:
    slug = slugify(title)
    nid = f"{nexus}-{slug}" if slug else nexus
    if not re.match(r"[a-z]", nid):
        nid = "n-" + nid
    return nid[:max_len].rstrip("-")
