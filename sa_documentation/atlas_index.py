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
