from sa_documentation.cindex_ids import make_node_id, slugify


def test_slugify_cyrillic():
    assert slugify("Выбор синхронного потока") == "vybor-sinhronnogo-potoka"


def test_slugify_strips_punctuation_and_case():
    assert slugify("SLA / Доступность 99.9%!") == "sla-dostupnost-99-9"


def test_make_node_id_is_deterministic():
    a = make_node_id("precedents", "Выбор синхронного платёжного потока")
    b = make_node_id("precedents", "Выбор синхронного платёжного потока")
    assert a == b == "precedents-vybor-sinhronnogo-platezhnogo-potoka"


def test_make_node_id_matches_pattern():
    import re
    nid = make_node_id("system-landscape", "Payment Gateway")
    assert re.fullmatch(r"[a-z][a-z0-9-]*", nid)


def test_make_node_id_truncates_to_60():
    nid = make_node_id("market", "оч" * 100)
    assert len(nid) <= 60
