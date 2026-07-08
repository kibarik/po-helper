import json
import pathlib
import shutil
from sa_documentation.lint_graph import lint_graph, _parse_frontmatter
from sa_documentation.cindex_ids import make_node_id

REPO = pathlib.Path(__file__).resolve().parents[2]
EX = REPO / ".claude/skills/confluence-indexator/examples"


def test_ideal_node_passes_linter(tmp_path):
    # собрать мини-волт: реестр + ideal_node в папке нексуса
    (tmp_path / "precedents").mkdir()
    shutil.copy(REPO / "GROUND/NEXUS/_registry.yaml", tmp_path / "_registry.yaml")
    shutil.copy(EX / "ideal_node.md", tmp_path / "precedents/ideal_node.md")
    # плюс узел-цель, чтобы wiki-link не был битым и не было orphan
    (tmp_path / "system-landscape").mkdir()
    tgt = tmp_path / "system-landscape/payment-gateway.md"
    tgt.write_text(
        "---\nnexus: system-landscape\nnode_id: system-landscape-payment-gateway\n"
        "node_type: component\npaf_step: null\nkind: empirical\nowner: Cortex\n"
        "confidence: 0.3\nsources: [\"confluence:https://wiki/131099\"]\n"
        "updated: 2026-07-04\nttl_days: 180\nripeness: fresh\ntags: []\n---\n"
        "Шлюз. См. [[precedents-vybor-sinhronnogo-platezhnogo-potoka]].\n"
    )
    errs = lint_graph(tmp_path)
    assert errs == [], f"ideal_node не проходит линтер: {errs}"


def test_ideal_node_id_matches_generator():
    fm = _parse_frontmatter((EX / "ideal_node.md").read_text())
    assert fm["node_id"] == make_node_id(fm["nexus"], "Выбор синхронного платёжного потока")


def test_ideal_routing_is_valid_jsonl():
    lines = (EX / "ideal_routing.jsonl").read_text().strip().splitlines()
    recs = [json.loads(l) for l in lines]
    assert any(r["action"] == "auto" for r in recs)
    assert any(r["action"] == "queue" for r in recs)
