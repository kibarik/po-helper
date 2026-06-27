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
    """Return (frontmatter_dict, body_str). Empty dict if no/invalid frontmatter."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
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


import datetime


def freshness_score(rec, today):
    """clamp(1 - age/ttl, 0, 1) per nexus_schema.md §4."""
    u = rec.get("updated")
    ttl = rec.get("ttl_days")
    if not isinstance(u, datetime.date) or not ttl:
        return 0.0
    p = (today - u).days / float(ttl)
    return max(0.0, min(1.0, 1.0 - p))


def _completeness(nodes):
    if not nodes:
        return 0.0
    return sum(1 for n in nodes if n.get("complete")) / len(nodes)


def nexus_aggregates(nodes, today):
    """Per-nexus {slug, count, context_ripeness=completeness*weighted_freshness}."""
    by = {}
    for n in nodes:
        by.setdefault(n.get("nexus"), []).append(n)
    out = []
    for slug in sorted(by, key=lambda s: (s is None, s)):
        ns = by[slug]
        comp = _completeness(ns)
        num = sum(freshness_score(n, today) * float(n.get("confidence") or 0) for n in ns)
        den = sum(float(n.get("confidence") or 0) for n in ns)
        fresh = num / den if den else 0.0
        out.append({
            "slug": slug,
            "count": len(ns),
            "context_ripeness": round(comp * fresh, 3),
        })
    return out


def collect_tasks(tasks_dir, repo_root):
    """Backlog.md tasks (*.md with frontmatter) under tasks_dir."""
    base = pathlib.Path(repo_root) / tasks_dir
    if not base.exists():
        return []
    tasks = []
    for p in sorted(base.glob("*.md")):
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        if not fm.get("id"):
            continue
        tasks.append({
            "task_id": fm.get("id"),
            "title": fm.get("title"),
            "status": fm.get("status"),
            "nexus_nodes": fm.get("nexus_nodes") or [],
            "path": p.relative_to(repo_root).as_posix(),
        })
    return tasks


def collect_agents(agents_dir, repo_root):
    """Cortex agents (.claude/agents/*.md) — name, phase, description, path."""
    base = pathlib.Path(repo_root) / agents_dir
    if not base.exists():
        return []
    agents = []
    for p in sorted(base.glob("*.md")):
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        name = fm.get("name") or p.stem
        agents.append({
            "name": name,
            "phase": fm.get("sprint_phase"),
            "description": fm.get("description"),
            "path": p.relative_to(repo_root).as_posix(),
        })
    return agents


SCHEMA_VERSION = "1.0"


def build_manifest(nodes, tasks, agents, today):
    """Assemble the manifest dict (deterministic; `today` injected)."""
    return {
        "generated": today.isoformat(),
        "schema_version": SCHEMA_VERSION,
        "nodes": nodes,
        "tasks": tasks,
        "agents": agents,
        "nexuses": nexus_aggregates(nodes, today),
    }


import json

MARK_START = "<!-- ATLAS:GENERATED:START -->"
MARK_END = "<!-- ATLAS:GENERATED:END -->"

NODE_ROOTS = ["GROUND/NEXUS", "AI-PROCESSES"]
TASKS_DIR = "backlog/tasks"
AGENTS_DIR = ".claude/agents"


def render_index_block(m):
    """Markdown for the generated INDEX block (between markers)."""
    lines = [f"_Сгенерировано: {m['generated']}_", ""]
    lines += ["## Нексусы", "", "| Нексус | Узлов | Context Ripeness |",
              "|---|---|---|"]
    for nx in m["nexuses"]:
        lines.append(f"| {nx['slug']} | {nx['count']} | {nx['context_ripeness']} |")
    lines += ["", "## Кортекс (агенты)", "", "| Агент | Фаза |", "|---|---|"]
    for a in m["agents"]:
        lines.append(f"| {a['name']} | {a.get('phase') or '—'} |")
    counts = {}
    for t in m["tasks"]:
        counts[t.get("status")] = counts.get(t.get("status"), 0) + 1
    lines += ["", "## Задачи", "", "| Статус | Кол-во |", "|---|---|"]
    for st in sorted(counts, key=lambda s: (s is None, s)):
        lines.append(f"| {st} | {counts[st]} |")
    return "\n".join(lines)


def _replace_between_markers(text, block):
    pattern = re.compile(
        re.escape(MARK_START) + r".*?" + re.escape(MARK_END), re.S)
    replacement = f"{MARK_START}\n{block}\n{MARK_END}"
    if pattern.search(text):
        return pattern.sub(lambda _: replacement, text)
    return text.rstrip() + "\n\n" + replacement + "\n"


def _json_default(o):
    if isinstance(o, datetime.date):
        return o.isoformat()
    raise TypeError(f"not serializable: {type(o)}")


def write_atlas(repo_root, today):
    """Generate ATLAS/manifest.json + INDEX.md block. Returns the manifest."""
    repo_root = pathlib.Path(repo_root)
    nodes = collect_nodes(NODE_ROOTS, repo_root)
    tasks = collect_tasks(TASKS_DIR, repo_root)
    agents = collect_agents(AGENTS_DIR, repo_root)
    m = build_manifest(nodes, tasks, agents, today)

    atlas = repo_root / "ATLAS"
    atlas.mkdir(parents=True, exist_ok=True)
    (atlas / "manifest.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True,
                   default=_json_default) + "\n",
        encoding="utf-8")

    idx_p = atlas / "INDEX.md"
    base = idx_p.read_text(encoding="utf-8") if idx_p.exists() else (
        f"# ATLAS INDEX\n\n{MARK_START}\n{MARK_END}\n")
    idx_p.write_text(_replace_between_markers(base, render_index_block(m)),
                     encoding="utf-8")
    return m


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="ATLAS manifest/INDEX generator")
    ap.add_argument("--atlas", action="store_true", help="generate ATLAS/")
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    ap.add_argument("--today", default=None, help="ISO date override (tests)")
    args = ap.parse_args(argv)
    if not args.atlas:
        ap.error("nothing to do; pass --atlas")
    today = (datetime.date.fromisoformat(args.today) if args.today
             else datetime.date.today())
    m = write_atlas(args.root, today)
    print(f"atlas: {len(m['nodes'])} nodes | {len(m['tasks'])} tasks | "
          f"{len(m['agents'])} agents | {len(m['nexuses'])} nexuses")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
