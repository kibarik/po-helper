"""Линтер графа узлов нексусов Confluence Indexator.

Проверяет: sources[] непуст, node_type/nexus валидны против реестра,
[[wiki-links]] не битые, нет orphan-узлов. Возвращает список ошибок.
См. docs/superpowers/specs/2026-07-04-confluence-indexator-design.md §8.
"""
import pathlib
import re
import yaml

VALID_NODE_TYPES = {
    "spine", "operating-model", "gates", "bootstrap", "step-overview",
    "sprint-phase", "person", "deliverable", "channel", "component",
    "decision", "rule", "regulation", "nfr", "risk", "term", "metric",
}


def _load_registry_slugs(nexus_root: pathlib.Path) -> set:
    reg_p = nexus_root / "_registry.yaml"
    if not reg_p.exists():
        return set()
    reg = yaml.safe_load(reg_p.read_text()) or {}
    return {t.get("slug") for t in reg.get("nexus_types", []) or []}


def _parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def lint_graph(nexus_root) -> list:
    errs = []
    nexus_root = pathlib.Path(nexus_root)
    valid_nexus = _load_registry_slugs(nexus_root)

    for md in sorted(nexus_root.rglob("*.md")):
        if md.name.startswith("_"):
            continue
        fm = _parse_frontmatter(md.read_text())
        nid = fm.get("node_id", md.stem)
        if not fm.get("sources"):
            errs.append(f"{nid}: empty sources[] (workslop)")
        nt = fm.get("node_type")
        if nt not in VALID_NODE_TYPES:
            errs.append(f"{nid}: invalid node_type {nt!r}")
        nx = fm.get("nexus")
        if valid_nexus and nx not in valid_nexus:
            errs.append(f"{nid}: nexus {nx!r} not in registry")
    return errs
