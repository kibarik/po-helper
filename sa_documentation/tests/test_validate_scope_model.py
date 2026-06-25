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


def _write(tmp_path, body):
    p = tmp_path / "scope-model.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_cell_missing_source_key(tmp_path):
    body = """
task: t
mode: enrich
sources:
  - {id: S1, kind: bft, ref: r}
trigger: {actor: a, event: e, source: S1}
end_state: {outcome: o, source: S1}
journey:
  - {step: 1, name: n, source: S1}
layers:
  - {id: L_actor, name: A}
cells:
  - {step: 1, layer: L_actor, action: x, scope: context}
"""
    errs = validate_scope_model(_write(tmp_path, body))
    assert any("source missing" in e for e in errs), errs


def test_malformed_source_entry_does_not_crash(tmp_path):
    body = """
task: t
mode: enrich
sources:
  - S1
trigger: {actor: a, event: e, source: S1}
end_state: {outcome: o, source: S1}
journey:
  - {step: 1, name: n, source: S1}
layers:
  - {id: L_actor, name: A}
cells: []
"""
    errs = validate_scope_model(_write(tmp_path, body))
    assert any("must be a mapping" in e for e in errs), errs


def test_scope_of_change_source_validated(tmp_path):
    body = """
task: t
mode: enrich
sources:
  - {id: S1, kind: bft, ref: r}
trigger: {actor: a, event: e, source: S1}
end_state: {outcome: o, source: S1}
journey:
  - {step: 1, name: n, source: S1}
layers:
  - {id: L_backstage, name: B}
cells: []
scope_of_change:
  - {layer: L_backstage, summary: s, marker: changed, source: S9}
"""
    errs = validate_scope_model(_write(tmp_path, body))
    assert any("scope_of_change" in e and "S9" in e for e in errs), errs


def test_journey_missing_step(tmp_path):
    body = """
task: t
mode: enrich
sources:
  - {id: S1, kind: bft, ref: r}
trigger: {actor: a, event: e, source: S1}
end_state: {outcome: o, source: S1}
journey:
  - {name: n, source: S1}
layers:
  - {id: L_actor, name: A}
cells: []
"""
    errs = validate_scope_model(_write(tmp_path, body))
    assert any("missing step" in e for e in errs), errs


def test_scope_of_change_bad_marker(tmp_path):
    body = """
task: t
mode: enrich
sources:
  - {id: S1, kind: bft, ref: r}
trigger: {actor: a, event: e, source: S1}
end_state: {outcome: o, source: S1}
journey:
  - {step: 1, name: n, source: S1}
layers:
  - {id: L_backstage, name: B}
cells: []
scope_of_change:
  - {layer: L_backstage, summary: s, marker: changd, source: S1}
"""
    errs = validate_scope_model(_write(tmp_path, body))
    assert any("marker invalid" in e for e in errs), errs


def test_gaps_must_be_list(tmp_path):
    body = """
task: t
mode: enrich
sources:
  - {id: S1, kind: bft, ref: r}
trigger: {actor: a, event: e, source: S1}
end_state: {outcome: o, source: S1}
journey:
  - {step: 1, name: n, source: S1}
layers:
  - {id: L_actor, name: A}
cells: []
gaps: "oops"
"""
    errs = validate_scope_model(_write(tmp_path, body))
    assert any("gaps must be a list" in e for e in errs), errs
