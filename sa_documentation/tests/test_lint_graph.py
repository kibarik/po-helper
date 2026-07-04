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


def test_broken_wikilink_is_error():
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("broken wiki-link" in e and "precedents-nonexistent" in e for e in errs)


def test_orphan_node_is_flagged():
    # graph_bad содержит >1 узла, no-sources.md ни на кого не ссылается и никто на него
    errs = lint_graph(ROOT / "fixtures/graph_bad")
    assert any("orphan" in e for e in errs)


def test_ignores_underscore_dirs_and_frontmatterless_files():
    # graph_ok/team/_calibration/README.md (под _-директорией, без frontmatter)
    # и graph_ok/_scratch.md (без frontmatter, имя с _) не должны считаться узлами
    # и не должны попадать в отчёт как workslop.
    errs = lint_graph(ROOT / "fixtures/graph_ok")
    assert errs == [], f"unexpected: {errs}"
