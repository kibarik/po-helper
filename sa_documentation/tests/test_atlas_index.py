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


def test_cli_main_runs_without_ruflo(tmp_path, monkeypatch):
    # Generation must not depend on ruflo/.swarm — simulate absent binary.
    import sa_documentation.atlas_index as ai
    _write(tmp_path / "AI-PROCESSES/om.md", NODE_OK)
    monkeypatch.setenv("PATH", "")  # no ruflo on PATH
    rc = ai.main(["--atlas", "--root", str(tmp_path), "--today", "2026-06-20"])
    assert rc == 0
    assert (tmp_path / "ATLAS/manifest.json").exists()
