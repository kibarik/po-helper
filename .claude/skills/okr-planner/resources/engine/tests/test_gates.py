from engine.gates import audit
from engine.deckspec import load_deckspec
from pathlib import Path
import copy

FIX = Path(__file__).parent / "fixtures" / "minimal_deck.yaml"

def test_clean_spec_is_green_or_yellow(minimal_spec):
    rep = audit(minimal_spec)
    assert rep.level in ("🟢", "🟡")
    assert rep.red == []

def test_missing_becomes_is_red(minimal_spec):
    spec = copy.deepcopy(minimal_spec)
    spec.directions[0].objs[0].krs[0].becomes = None
    rep = audit(spec)
    assert rep.level == "🔴"
    assert any("becomes" in m or "СТАНЕТ" in m for m in rep.red)

def test_market_without_src_is_red(minimal_spec):
    spec = copy.deepcopy(minimal_spec)
    spec.authored.market = [{"value": "100", "label": "x"}]  # no src
    rep = audit(spec)
    assert rep.level == "🔴"

def test_kr_without_src_is_yellow(minimal_spec):
    spec = copy.deepcopy(minimal_spec)
    spec.directions[0].objs[0].krs[0].src = None
    rep = audit(spec)
    assert any("src" in m for m in rep.yellow)
    assert rep.level == "🟡"
