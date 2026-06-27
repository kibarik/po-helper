# ATLAS Navigation Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `ATLAS/` — a committed navigation layer over existing frontmatter nodes (Nexuses), agents (Cortex) and Backlog.md tasks, driven by a generated `manifest.json` (LLM) + `INDEX.md`/Dataview (human), independent of the ruflo RAG.

**Architecture:** A pure-Python generator (`sa_documentation/atlas_index.py`) walks `GROUND/NEXUS/**`, `AI-PROCESSES/**` (frontmatter nodes), `.claude/agents/*.md` and `backlog/tasks/*.md`, parses YAML frontmatter with `yaml.safe_load`, and emits `ATLAS/manifest.json` plus a generated block inside `ATLAS/INDEX.md` (between markers). The generator never calls ruflo, so it works on a fresh checkout with no `.swarm/`. The legacy RAG indexer (`nexus_index.py`) gets a separate silent-failure fix.

**Tech Stack:** Python 3 (stdlib + PyYAML), pytest, Backlog.md (MIT, MCP already connected), Obsidian Dataview (MIT, optional human plugin).

---

## File Structure

- `sa_documentation/atlas_index.py` — **new.** Generator: frontmatter parsing, collectors (nodes/tasks/agents), ripeness aggregates, manifest builder, INDEX block renderer, `write_atlas()`, CLI `--atlas`. Pure functions; no ruflo calls.
- `sa_documentation/tests/test_atlas_index.py` — **new.** Unit tests using `tmp_path`, no committed fixtures needed.
- `ATLAS/README.md` — **new.** Human+LLM entrypoint.
- `ATLAS/INDEX.md` — **new.** MOC with generated-block markers + manual usage text + links to views.
- `ATLAS/views/by-nexus.md`, `wilting.md`, `low-cp.md`, `tasks.md` — **new.** Dataview views (optional).
- `ATLAS/manifest.json` — **generated** (committed after first run).
- `sa_documentation/nexus_index.py` — **modify.** Extract `store_ok()`, exit non-zero on failures.
- `sa_documentation/tests/test_nexus_index.py` — **new.** Tests for `store_ok` + exit semantics.
- `GROUND/README.md` — **modify.** Onboarding: `atlas` generation + RAG warm-up step.

---

## Task 1: ATLAS skeleton (static files)

**Files:**
- Create: `ATLAS/README.md`
- Create: `ATLAS/INDEX.md`
- Create: `ATLAS/views/by-nexus.md`
- Create: `ATLAS/views/wilting.md`
- Create: `ATLAS/views/low-cp.md`
- Create: `ATLAS/views/tasks.md`

- [ ] **Step 1: Create `ATLAS/README.md`**

```markdown
# ATLAS — навигационный хаб

Слой навигации НАД существующими файлами. Файлы остаются на местах
(`GROUND/NEXUS/**`, `AI-PROCESSES/**`, `.claude/agents/**`, `backlog/**`).

## Что где
- `manifest.json` — машинный индекс для LLM (структурный/фасетный поиск). **Генерируется.**
- `INDEX.md` — человеко-MOC (Нексусы / Кортекс / задачи). Ген-блок между маркерами.
- `views/` — Dataview-вьюхи (опц. плагин Obsidian).

## Регенерация
```
python3 sa_documentation/atlas_index.py --atlas
```
Только читает исходники (не ренеймит → не ломает wikilinks). Не вызывает ruflo —
работает на свежем checkout без `.swarm/`.

## Навигация без инструментов
LLM: читай `manifest.json` (плоский JSON, любая модель). Человек: открой `INDEX.md`
(с Dataview — живые таблицы из `views/`; без него — статичный ген-блок).
```

- [ ] **Step 2: Create `ATLAS/INDEX.md` with markers**

```markdown
# ATLAS INDEX

MOC всех Нексусов, агентов Кортекса и задач. Источник истины — исходные узлы;
этот файл генерируется (`python3 sa_documentation/atlas_index.py --atlas`).

Живые вьюхи (нужен Dataview): [[views/by-nexus]] · [[views/wilting]] ·
[[views/low-cp]] · [[views/tasks]].

<!-- ATLAS:GENERATED:START -->
<!-- ATLAS:GENERATED:END -->
```

- [ ] **Step 3: Create the four `ATLAS/views/*.md` Dataview views**

`ATLAS/views/by-nexus.md`:
```markdown
# Узлы по Нексусам

```dataview
TABLE owner, confidence, ripeness, node_type
FROM "GROUND/NEXUS" OR "AI-PROCESSES"
WHERE node_id
SORT nexus ASC, confidence DESC
```
```

`ATLAS/views/wilting.md`:
```markdown
# Протухающие узлы (wilting)

```dataview
LIST
FROM "GROUND/NEXUS" OR "AI-PROCESSES"
WHERE node_id AND ripeness = "wilting"
```
```

`ATLAS/views/low-cp.md`:
```markdown
# Низкий Confidence Point (<0.5)

```dataview
TABLE nexus, owner, confidence, ripeness
FROM "GROUND/NEXUS" OR "AI-PROCESSES"
WHERE node_id AND confidence < 0.5
SORT confidence ASC
```
```

`ATLAS/views/tasks.md`:
```markdown
# Задачи по статусу

```dataview
TABLE status, nexus_nodes
FROM "backlog/tasks"
SORT status ASC
```
```

- [ ] **Step 4: Commit**

```bash
git add ATLAS/
git commit -m "feat(atlas): skeleton hub (README, INDEX markers, Dataview views)"
```

---

## Task 2: `parse_frontmatter` + body helpers

**Files:**
- Create: `sa_documentation/atlas_index.py`
- Test: `sa_documentation/tests/test_atlas_index.py`

- [ ] **Step 1: Write the failing test**

```python
# sa_documentation/tests/test_atlas_index.py
import datetime
from sa_documentation.atlas_index import (
    parse_frontmatter, extract_title, extract_links,
)


def test_parse_frontmatter_splits_fm_and_body():
    text = (
        "---\n"
        "node_id: aip-x\n"
        "confidence: 0.4\n"
        "sources: [\"[S1]\"]\n"
        "---\n"
        "# Title\n\nBody [[other-node]] text.\n"
    )
    fm, body = parse_frontmatter(text)
    assert fm["node_id"] == "aip-x"
    assert fm["confidence"] == 0.4
    assert fm["sources"] == ["[S1]"]
    assert body.startswith("# Title")


def test_parse_frontmatter_no_frontmatter():
    fm, body = parse_frontmatter("# Just body\n")
    assert fm == {}
    assert body == "# Just body\n"


def test_extract_title_and_links():
    body = "# My Title\n\nSee [[a]] and [[b|alias]].\n"
    assert extract_title(body) == "My Title"
    assert extract_links(body) == ["a", "b"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: FAIL with `ModuleNotFoundError` / `ImportError: cannot import name 'parse_frontmatter'`

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/atlas_index.py sa_documentation/tests/test_atlas_index.py
git commit -m "feat(atlas): frontmatter + title/link parsing helpers"
```

---

## Task 3: `node_record` + `collect_nodes`

**Files:**
- Modify: `sa_documentation/atlas_index.py`
- Test: `sa_documentation/tests/test_atlas_index.py`

- [ ] **Step 1: Write the failing test**

```python
def _write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


NODE_OK = (
    "---\n"
    "nexus: product\n"
    "node_id: aip-x\n"
    "node_type: operating-model\n"
    "paf_step: null\n"
    "sprint_phase: null\n"
    "kind: normative\n"
    "owner: Product Ops\n"
    "confidence: 1.0\n"
    "sources: [\"[S1]\"]\n"
    "updated: 2026-06-20\n"
    "ttl_days: 365\n"
    "ripeness: fresh\n"
    "tags: [pmf]\n"
    "---\n"
    "# Operating Model\n\nBody [[aip-y]].\n"
)


def test_collect_nodes_builds_records(tmp_path):
    from sa_documentation.atlas_index import collect_nodes
    _write(tmp_path / "AI-PROCESSES/om.md", NODE_OK)
    _write(tmp_path / "GROUND/NEXUS/_index.md", "# no frontmatter, skipped\n")
    nodes = collect_nodes(["AI-PROCESSES", "GROUND/NEXUS"], tmp_path)
    assert len(nodes) == 1
    n = nodes[0]
    assert n["node_id"] == "aip-x"
    assert n["nexus"] == "product"
    assert n["title"] == "Operating Model"
    assert n["links"] == ["aip-y"]
    assert n["tags"] == ["pmf"]
    assert n["path"] == "AI-PROCESSES/om.md"
    assert n["complete"] is True


def test_collect_nodes_marks_incomplete(tmp_path):
    from sa_documentation.atlas_index import collect_nodes
    partial = "---\nnode_id: aip-z\nnexus: market\n---\n# Z\n"
    _write(tmp_path / "AI-PROCESSES/z.md", partial)
    nodes = collect_nodes(["AI-PROCESSES"], tmp_path)
    assert nodes[0]["complete"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: FAIL with `ImportError: cannot import name 'collect_nodes'`

- [ ] **Step 3: Write minimal implementation**

Append to `sa_documentation/atlas_index.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/atlas_index.py sa_documentation/tests/test_atlas_index.py
git commit -m "feat(atlas): collect frontmatter nodes into manifest records"
```

---

## Task 4: Ripeness aggregates (`freshness_score`, `nexus_aggregates`)

**Files:**
- Modify: `sa_documentation/atlas_index.py`
- Test: `sa_documentation/tests/test_atlas_index.py`

- [ ] **Step 1: Write the failing test**

```python
def test_freshness_and_aggregates(tmp_path):
    from sa_documentation.atlas_index import (
        collect_nodes, freshness_score, nexus_aggregates,
    )
    today = datetime.date(2026, 6, 20)
    _write(tmp_path / "AI-PROCESSES/om.md", NODE_OK)  # updated today, ttl 365
    nodes = collect_nodes(["AI-PROCESSES"], tmp_path)
    # age 0 -> freshness 1.0
    assert freshness_score(nodes[0], today) == 1.0
    aggs = nexus_aggregates(nodes, today)
    assert aggs == [{"slug": "product", "count": 1, "context_ripeness": 1.0}]


def test_freshness_clamps_to_zero():
    from sa_documentation.atlas_index import freshness_score
    rec = {"updated": datetime.date(2025, 1, 1), "ttl_days": 90, "confidence": 1.0}
    # age >> ttl -> p>1 -> clamped 0
    assert freshness_score(rec, datetime.date(2026, 6, 20)) == 0.0


def test_aggregate_incomplete_lowers_completeness(tmp_path):
    from sa_documentation.atlas_index import collect_nodes, nexus_aggregates
    today = datetime.date(2026, 6, 20)
    _write(tmp_path / "AI-PROCESSES/om.md", NODE_OK)
    _write(tmp_path / "AI-PROCESSES/z.md",
           "---\nnode_id: z\nnexus: product\n---\n# Z\n")
    nodes = collect_nodes(["AI-PROCESSES"], tmp_path)
    aggs = nexus_aggregates(nodes, today)
    # 1 of 2 complete -> completeness 0.5; fresh node weight only -> fresh≈1
    assert aggs[0]["count"] == 2
    assert aggs[0]["context_ripeness"] == 0.5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: FAIL with `ImportError: cannot import name 'freshness_score'`

- [ ] **Step 3: Write minimal implementation**

Append to `sa_documentation/atlas_index.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/atlas_index.py sa_documentation/tests/test_atlas_index.py
git commit -m "feat(atlas): per-nexus Context Ripeness aggregates"
```

---

## Task 5: `collect_tasks` + `collect_agents`

**Files:**
- Modify: `sa_documentation/atlas_index.py`
- Test: `sa_documentation/tests/test_atlas_index.py`

- [ ] **Step 1: Write the failing test**

```python
def test_collect_tasks(tmp_path):
    from sa_documentation.atlas_index import collect_tasks
    _write(tmp_path / "backlog/tasks/task-10 - Add search.md",
           "---\nid: task-10\ntitle: Add search\nstatus: in-progress\n"
           "nexus_nodes: [aip-x]\n---\nbody\n")
    tasks = collect_tasks("backlog/tasks", tmp_path)
    assert tasks == [{
        "task_id": "task-10",
        "title": "Add search",
        "status": "in-progress",
        "nexus_nodes": ["aip-x"],
        "path": "backlog/tasks/task-10 - Add search.md",
    }]


def test_collect_tasks_missing_dir(tmp_path):
    from sa_documentation.atlas_index import collect_tasks
    assert collect_tasks("backlog/tasks", tmp_path) == []


def test_collect_agents(tmp_path):
    from sa_documentation.atlas_index import collect_agents
    _write(tmp_path / ".claude/agents/nexus-builder.md",
           "---\nname: nexus-builder\ndescription: Builds nodes.\n"
           "sprint_phase: cross\n---\nbody\n")
    agents = collect_agents(".claude/agents", tmp_path)
    assert agents == [{
        "name": "nexus-builder",
        "phase": "cross",
        "description": "Builds nodes.",
        "path": ".claude/agents/nexus-builder.md",
    }]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: FAIL with `ImportError: cannot import name 'collect_tasks'`

- [ ] **Step 3: Write minimal implementation**

Append to `sa_documentation/atlas_index.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: PASS (11 tests)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/atlas_index.py sa_documentation/tests/test_atlas_index.py
git commit -m "feat(atlas): collect Backlog.md tasks and Cortex agents"
```

---

## Task 6: `build_manifest`

**Files:**
- Modify: `sa_documentation/atlas_index.py`
- Test: `sa_documentation/tests/test_atlas_index.py`

- [ ] **Step 1: Write the failing test**

```python
def test_build_manifest_shape(tmp_path):
    from sa_documentation.atlas_index import (
        collect_nodes, collect_tasks, collect_agents, build_manifest,
    )
    today = datetime.date(2026, 6, 20)
    _write(tmp_path / "AI-PROCESSES/om.md", NODE_OK)
    _write(tmp_path / "backlog/tasks/task-10 - X.md",
           "---\nid: task-10\ntitle: X\nstatus: todo\nnexus_nodes: [aip-x]\n---\nb\n")
    _write(tmp_path / ".claude/agents/a.md",
           "---\nname: a\ndescription: d\n---\nb\n")
    nodes = collect_nodes(["AI-PROCESSES"], tmp_path)
    tasks = collect_tasks("backlog/tasks", tmp_path)
    agents = collect_agents(".claude/agents", tmp_path)
    m = build_manifest(nodes, tasks, agents, today)
    assert m["schema_version"] == "1.0"
    assert m["generated"] == "2026-06-20"
    assert len(m["nodes"]) == 1 and m["nodes"][0]["node_id"] == "aip-x"
    assert m["tasks"][0]["task_id"] == "task-10"
    assert m["agents"][0]["name"] == "a"
    assert m["nexuses"] == [{"slug": "product", "count": 1, "context_ripeness": 1.0}]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: FAIL with `ImportError: cannot import name 'build_manifest'`

- [ ] **Step 3: Write minimal implementation**

Append to `sa_documentation/atlas_index.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: PASS (12 tests)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/atlas_index.py sa_documentation/tests/test_atlas_index.py
git commit -m "feat(atlas): assemble manifest dict"
```

---

## Task 7: Render INDEX block + `write_atlas` (idempotent)

**Files:**
- Modify: `sa_documentation/atlas_index.py`
- Test: `sa_documentation/tests/test_atlas_index.py`

- [ ] **Step 1: Write the failing test**

```python
def test_render_index_block_contains_tables():
    from sa_documentation.atlas_index import render_index_block
    m = {
        "generated": "2026-06-20",
        "nexuses": [{"slug": "product", "count": 2, "context_ripeness": 0.7}],
        "agents": [{"name": "a", "phase": "scout", "description": "d", "path": "x"}],
        "tasks": [{"task_id": "t1", "status": "todo"},
                  {"task_id": "t2", "status": "todo"}],
    }
    block = render_index_block(m)
    assert "product" in block and "0.7" in block
    assert "| a |" in block
    assert "todo" in block and "2" in block


MARKED_INDEX = (
    "# ATLAS INDEX\n\nintro text\n\n"
    "<!-- ATLAS:GENERATED:START -->\nOLD\n<!-- ATLAS:GENERATED:END -->\n"
)


def test_write_atlas_idempotent(tmp_path):
    from sa_documentation.atlas_index import write_atlas
    import json
    today = datetime.date(2026, 6, 20)
    _write(tmp_path / "AI-PROCESSES/om.md", NODE_OK)
    _write(tmp_path / "ATLAS/INDEX.md", MARKED_INDEX)
    write_atlas(tmp_path, today)
    idx1 = (tmp_path / "ATLAS/INDEX.md").read_text()
    man1 = (tmp_path / "ATLAS/manifest.json").read_text()
    assert "intro text" in idx1            # manual text preserved
    assert "OLD" not in idx1               # generated block replaced
    assert json.loads(man1)["nodes"][0]["node_id"] == "aip-x"
    write_atlas(tmp_path, today)           # second run
    assert (tmp_path / "ATLAS/INDEX.md").read_text() == idx1   # idempotent
    assert (tmp_path / "ATLAS/manifest.json").read_text() == man1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: FAIL with `ImportError: cannot import name 'render_index_block'`

- [ ] **Step 3: Write minimal implementation**

Append to `sa_documentation/atlas_index.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: PASS (14 tests)

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/atlas_index.py sa_documentation/tests/test_atlas_index.py
git commit -m "feat(atlas): render INDEX block + idempotent write_atlas"
```

---

## Task 8: CLI wiring + first real generation

**Files:**
- Modify: `sa_documentation/atlas_index.py`
- Test: `sa_documentation/tests/test_atlas_index.py`

- [ ] **Step 1: Write the failing test (no-ruflo independence)**

```python
def test_cli_main_runs_without_ruflo(tmp_path, monkeypatch):
    # Generation must not depend on ruflo/.swarm — simulate absent binary.
    import sa_documentation.atlas_index as ai
    _write(tmp_path / "AI-PROCESSES/om.md", NODE_OK)
    monkeypatch.setenv("PATH", "")  # no ruflo on PATH
    rc = ai.main(["--atlas", "--root", str(tmp_path), "--today", "2026-06-20"])
    assert rc == 0
    assert (tmp_path / "ATLAS/manifest.json").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py::test_cli_main_runs_without_ruflo -v`
Expected: FAIL with `AttributeError: module ... has no attribute 'main'`

- [ ] **Step 3: Write minimal implementation**

Append to `sa_documentation/atlas_index.py`:

```python
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
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest sa_documentation/tests/test_atlas_index.py -v`
Expected: PASS (15 tests)

- [ ] **Step 5: Generate real ATLAS and commit**

```bash
python3 sa_documentation/atlas_index.py --atlas --root .
git add sa_documentation/atlas_index.py sa_documentation/tests/test_atlas_index.py ATLAS/INDEX.md ATLAS/manifest.json
git commit -m "feat(atlas): CLI --atlas + generated manifest/INDEX"
```

Expected stdout: `atlas: <N> nodes | 0 tasks | 6 agents | <K> nexuses` (N≈64 if AI-PROCESSES stamped).

---

## Task 9: Fix silent failures in `nexus_index.py` (RAG branch)

**Files:**
- Modify: `sa_documentation/nexus_index.py:55-65`
- Test: `sa_documentation/tests/test_nexus_index.py`

- [ ] **Step 1: Write the failing test**

```python
# sa_documentation/tests/test_nexus_index.py
from sa_documentation.nexus_index import store_ok


def test_store_ok_true_on_clean_success():
    assert store_ok(0, "stored key=aip-x ns=ai-kortex") is True


def test_store_ok_false_on_error_marker():
    assert store_ok(0, "[ERROR] boolean (true)") is False


def test_store_ok_false_on_error_word():
    assert store_ok(0, "internal error while storing") is False


def test_store_ok_false_on_nonzero_returncode():
    assert store_ok(1, "stored") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest sa_documentation/tests/test_nexus_index.py -v`
Expected: FAIL with `ImportError: cannot import name 'store_ok'`

- [ ] **Step 3: Refactor `nexus_index.py`**

Add this function above the `for p in ...` loop (after the helpers, before `stored = failed = skipped = 0`):

```python
def store_ok(returncode, output):
    """ruflo CLI returns exit 0 even on internal errors — detect real failure
    from output. Success = clean exit AND no error/fail markers in output."""
    o = (output or "").lower()
    return returncode == 0 and "[error]" not in o and "error" not in o and "fail" not in o
```

Replace the success check inside the loop:

```python
    out = (r.stdout or "") + (r.stderr or "")
    if store_ok(r.returncode, out):
        stored += 1
    else:
        print(f"FAIL {nid}: {out[:160]}", file=sys.stderr); failed += 1
```

Replace the final print line with summary + non-zero exit:

```python
print(f"indexed {stored} | failed {failed} | skipped {skipped} | ns={NS}")
sys.exit(1 if failed else 0)
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest sa_documentation/tests/test_nexus_index.py -v`
Expected: PASS (4 tests)

> NOTE for executor: verify `store_ok` against a real `ruflo memory store` run —
> if ruflo prints a benign line containing the substring "error"/"fail" on
> success, tighten to a positive marker instead. Capture one real invocation's
> stdout before relying on it in CI.

- [ ] **Step 5: Commit**

```bash
git add sa_documentation/nexus_index.py sa_documentation/tests/test_nexus_index.py
git commit -m "fix(rag): detect silent ruflo store failures + non-zero exit"
```

---

## Task 10: Onboarding docs (ATLAS generation + RAG warm-up + Backlog.md)

**Files:**
- Modify: `GROUND/README.md`

- [ ] **Step 1: Add an "ATLAS + задачи" section to `GROUND/README.md`**

Append before the final `См. спецификацию:` line:

```markdown
## ATLAS (навигация) и задачи

- **Навигация:** `python3 sa_documentation/atlas_index.py --atlas` генерирует
  `ATLAS/manifest.json` (LLM) + ген-блок `ATLAS/INDEX.md` (человек). Запускать
  после изменения узлов. Не требует ruflo/`.swarm`.
- **RAG-прогрев (опц.):** на свежем clone/worktree `.swarm/` пуст (gitignored).
  Семантический поиск агентов заработает только после
  `python3 sa_documentation/nexus_index.py` в рабочей CWD. Без прогрева навигация
  работает на `ATLAS/manifest.json`.
- **Задачи/Банчи:** Backlog.md (`backlog init`, затем `backlog board`/MCP).
  Связь задача→узел: поле `nexus_nodes: [node_id]` во frontmatter задачи.
```

- [ ] **Step 2: Run the full test suite (regression gate)**

Run: `python3 -m pytest sa_documentation/tests/ -v`
Expected: PASS (all tests: validate_ground + atlas_index + nexus_index)

- [ ] **Step 3: Commit**

```bash
git add GROUND/README.md
git commit -m "docs(atlas): onboarding — ATLAS generation, RAG warm-up, Backlog.md"
```

---

## Self-Review (completed by plan author)

**Spec coverage:**
- §1 structure (ATLAS/, backlog/) → Task 1 (skeleton), Task 8 (generated files), Task 10 (Backlog.md docs). ✓
- §2.1 manifest.json contract → Tasks 3,5,6 (records/tasks/agents/build). ✓
- §2.2 INDEX.md markers + manual text → Tasks 1,7. ✓
- §2.3 generator extends parsing, Context Ripeness, idempotent, read-only, RAG-independent → Tasks 2–8. ✓
- §2.4 task↔node link (`nexus_nodes`) → Task 5 (collect), Task 10 (docs). ✓
- §2.5 Dataview views → Task 1. ✓
- §2.6 Backlog.md → Task 10. ✓
- §3 onboarding (atlas + RAG warm-up step) + silent-fail fix → Tasks 9,10. ✓
- §5 tests (struct, aggregates, idempotency, no-ruflo, `[ERROR]`→fail→exit) → Tasks 4,7,8,9. ✓

**Placeholder scan:** No TBD/TODO; every code step shows full code. ✓

**Type consistency:** `parse_frontmatter` returns `(fm, body)` everywhere; `node_record`/`collect_nodes` fields match `render_index_block`/`build_manifest` consumers; `store_ok(returncode, output)` signature consistent across Task 9. ✓

**Note:** `ATLAS/manifest.json` (Task 8) is committed as a generated artifact (unlike `.swarm/`, it is plain JSON, diffable, and the reliable cross-checkout navigator per spec §1).
