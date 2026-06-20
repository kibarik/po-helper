import pathlib
from sa_documentation.validate_ground import validate_ground

ROOT = pathlib.Path(__file__).parent


def test_ok():
    errs = validate_ground(ROOT / "fixtures/ground_ok")
    assert errs == [], f"unexpected errors: {errs}"


def test_bad():
    errs = validate_ground(ROOT / "fixtures/ground_bad")
    assert errs and any("product_engineer" in e or "slug" in e.lower() for e in errs)
