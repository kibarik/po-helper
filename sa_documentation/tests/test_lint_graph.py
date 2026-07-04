import pathlib
from sa_documentation.lint_graph import lint_graph

ROOT = pathlib.Path(__file__).parent


def test_graph_ok():
    errs = lint_graph(ROOT / "fixtures/graph_ok")
    assert errs == [], f"unexpected: {errs}"


def test_missing_sources_is_error():
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("sources" in e for e in errs)


def test_invalid_node_type_is_error():
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("node_type" in e and "banana" in e for e in errs)
