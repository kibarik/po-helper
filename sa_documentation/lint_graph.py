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

    nodes = {}      # node_id -> frontmatter
    out_links = {}  # node_id -> set(target node_id)
    in_links = {}   # target node_id -> count

    for md in sorted(nexus_root.rglob("*.md")):
        if md.name.startswith("_"):
            continue
        text = md.read_text()
        fm = _parse_frontmatter(text)
        nid = fm.get("node_id", md.stem)
        nodes[nid] = fm
        targets = set(re.findall(r"\[\[([a-z0-9-]+)\]\]", text))
        out_links[nid] = targets
        for t in targets:
            in_links[t] = in_links.get(t, 0) + 1

    for nid, fm in nodes.items():
        if not fm.get("sources"):
            errs.append(f"{nid}: empty sources[] (workslop)")
        nt = fm.get("node_type")
        if nt not in VALID_NODE_TYPES:
            errs.append(f"{nid}: invalid node_type {nt!r}")
        nx = fm.get("nexus")
        if valid_nexus and nx not in valid_nexus:
            errs.append(f"{nid}: nexus {nx!r} not in registry")
        for t in out_links[nid]:
            if t not in nodes:
                errs.append(f"{nid}: broken wiki-link [[{t}]]")
        if len(nodes) > 1 and not out_links[nid] and in_links.get(nid, 0) == 0:
            errs.append(f"{nid}: orphan (no wiki-links in or out)")
    return errs


if __name__ == "__main__":
    import sys
    errs = lint_graph(sys.argv[1] if len(sys.argv) > 1 else "GROUND/NEXUS")
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
