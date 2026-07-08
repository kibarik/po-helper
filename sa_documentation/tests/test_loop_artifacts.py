import pathlib
from sa_documentation.validate_ground import validate_loop_artifacts

VALID_PULSE = """---
nexus: product
node_id: pulse-s14
node_type: sprint-phase
sprint_phase: pulse
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.5
sources: ["sprint-sync:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
level: sprint
cycle_ref: S14
nexus_snapshot:
  product: {ripeness: 0.72, gaps: ["mNSM не валидирована"]}
intent: "закрыть гэп по гипотезе X"
lens: product
---
# Pulse
"""

VALID_BUNCH = """---
nexus: product
node_id: bunch-s14
node_type: sprint-phase
sprint_phase: bunch
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.4
sources: ["OKR-Q3", "sprint-deliver:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
level: sprint
cycle_ref: S14
parent_bunch: bunch-q3
bunch_size: 5
bunch_window: sprint-14
items:
  - {ref: PROJ-123, kind: hypothesis, trace: "GROUND/NEXUS/product/feature-x.md", initial_cp: 3}
gate: {final_cp: 0.5, cost_of_risk: "переоценка объёма", decision: commit}
---
# Bunch
"""

VALID_HARVEST = """---
nexus: product
node_id: harvest-s14
node_type: sprint-phase
sprint_phase: harvest
paf_step: null
kind: empirical
owner: Product Engineer
confidence: 0.6
sources: ["sprint-fact:S14"]
updated: 2026-07-08
ttl_days: 14
ripeness: fresh
level: sprint
cycle_ref: S14
rolls_up_to: harvest-q3
outcomes: {cp_change: "+0.2", mNSM_delta: "[УТОЧНИТЬ]", npv_actual: "[УТОЧНИТЬ]"}
insights: ["пилот подтвердил ценность для SMB"]
nexus_writeback:
  - {nexus: product, node: feature-x, change: "cp 0.4->0.6", source: harvest-s14}
---
# Harvest
"""


def _mk(tmp_path, folder, name, text):
    d = tmp_path / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(text)


def test_valid_artifacts_pass(tmp_path):
    _mk(tmp_path, "PULSE", "S14-pulse.md", VALID_PULSE)
    _mk(tmp_path, "BUNCH", "S14-bunch.md", VALID_BUNCH)
    _mk(tmp_path, "RESULTS", "S14-harvest.md", VALID_HARVEST)
    assert validate_loop_artifacts(tmp_path) == []


def test_harvest_missing_writeback_fails(tmp_path):
    broken = VALID_HARVEST.replace(
        'nexus_writeback:\n  - {nexus: product, node: feature-x, change: "cp 0.4->0.6", source: harvest-s14}\n',
        "",
    )
    _mk(tmp_path, "RESULTS", "S14-harvest.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("nexus_writeback" in e for e in errs), errs


def test_bunch_bad_decision_fails(tmp_path):
    broken = VALID_BUNCH.replace("decision: commit", "decision: maybe")
    _mk(tmp_path, "BUNCH", "S14-bunch.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("gate.decision" in e for e in errs), errs


def test_sprint_bunch_without_parent_fails(tmp_path):
    broken = VALID_BUNCH.replace("parent_bunch: bunch-q3\n", "")
    _mk(tmp_path, "BUNCH", "S14-bunch.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("parent_bunch" in e for e in errs), errs


def test_pulse_missing_lens_fails(tmp_path):
    broken = VALID_PULSE.replace("lens: product\n", "")
    _mk(tmp_path, "PULSE", "S14-pulse.md", broken)
    errs = validate_loop_artifacts(tmp_path)
    assert any("lens" in e for e in errs), errs


def test_non_loop_pulse_note_skipped(tmp_path):
    # init-pulse / summary без sprint_phase не должны падать
    _mk(tmp_path, "PULSE", "00-init-pulse.md", "# просто заметка без frontmatter\n")
    assert validate_loop_artifacts(tmp_path) == []
