# sa_documentation/atlas_index.py
"""ATLAS generator: committed navigation layer over frontmatter nodes,
agents and Backlog.md tasks. Emits ATLAS/manifest.json + INDEX.md block.

Pure-Python, does NOT call ruflo — works on a fresh checkout without .swarm/.
Usage: python3 sa_documentation/atlas_index.py --atlas [--root <repo_root>]
"""
import re
import yaml

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str). Empty dict if no frontmatter."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    fm = yaml.safe_load(m.group(1)) or {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, text[m.end():]


def extract_title(body):
    """First markdown H1 heading, or empty string."""
    m = re.search(r"^#\s+(.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def extract_links(body):
    """Wikilink targets ([[target]] / [[target|alias]]), de-duped, in order."""
    out = []
    for tgt in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", body):
        t = tgt.strip()
        if t and t not in out:
            out.append(t)
    return out


import pathlib

# Required Node-schema keys (nexus_schema.md §2). paf_step value may be null,
# but the key must be present for the node to count as "complete".
REQUIRED_KEYS = [
    "nexus", "node_id", "node_type", "paf_step", "kind", "owner",
    "confidence", "sources", "updated", "ttl_days", "ripeness",
]


def node_record(fm, body, rel_path):
    """Build a manifest node entry from frontmatter + body."""
    return {
        "node_id": fm.get("node_id"),
        "title": extract_title(body),
        "kind": fm.get("kind"),
        "nexus": fm.get("nexus"),
        "node_type": fm.get("node_type"),
        "owner": fm.get("owner"),
        "confidence": fm.get("confidence"),
        "ripeness": fm.get("ripeness"),
        "paf_step": fm.get("paf_step"),
        "sprint_phase": fm.get("sprint_phase"),
        "updated": fm.get("updated"),
        "ttl_days": fm.get("ttl_days"),
        "path": rel_path,
        "links": extract_links(body),
        "tags": fm.get("tags") or [],
        "complete": all(k in fm for k in REQUIRED_KEYS),
    }


def collect_nodes(roots, repo_root):
    """Walk roots for *.md frontmatter nodes (those with node_id)."""
    repo_root = pathlib.Path(repo_root)
    nodes = []
    for root in roots:
        base = repo_root / root
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            fm, body = parse_frontmatter(p.read_text(encoding="utf-8"))
            if not fm.get("node_id"):
                continue
            rel = p.relative_to(repo_root).as_posix()
            nodes.append(node_record(fm, body, rel))
    return nodes
