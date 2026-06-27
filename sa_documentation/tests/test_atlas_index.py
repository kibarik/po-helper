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
