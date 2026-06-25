import pathlib
from sa_documentation.validate_scope_model import validate_scope_model

ROOT = pathlib.Path(__file__).parent


def test_ok():
    errs = validate_scope_model(ROOT / "fixtures/scope_model_ok/scope-model.yaml")
    assert errs == [], f"unexpected errors: {errs}"


def test_bad_unknown_source():
    errs = validate_scope_model(ROOT / "fixtures/scope_model_bad/scope-model.yaml")
    assert any("source" in e.lower() and "S9" in e for e in errs), errs


def test_bad_scope_value():
    errs = validate_scope_model(ROOT / "fixtures/scope_model_bad/scope-model.yaml")
    assert any("scope" in e.lower() for e in errs), errs


def test_missing_file():
    errs = validate_scope_model(ROOT / "fixtures/nope/scope-model.yaml")
    assert errs and "missing" in errs[0]
