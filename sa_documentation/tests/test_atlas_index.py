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
