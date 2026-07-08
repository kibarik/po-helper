from pathlib import Path
from engine.deckspec import load_deckspec, DeckSpec, KR

FIX = Path(__file__).parent / "fixtures" / "minimal_deck.yaml"

def test_loads_top_level():
    spec = load_deckspec(FIX)
    assert isinstance(spec, DeckSpec)
    assert spec.product == "GDS"
    assert spec.quarter == "Q3-2026"
    assert spec.footer == "GDS · Q3 · витрина Ticketland"
    assert len(spec.directions) == 1

def test_nested_kr():
    spec = load_deckspec(FIX)
    kr = spec.directions[0].objs[0].krs[0]
    assert isinstance(kr, KR)
    assert kr.id == "1.1"
    assert kr.now.startswith("Мероприятия")
    assert kr.steps[1].role == "BE"
    assert kr.sprint_cells["S2"] == ["BE·Go"]
    assert kr.owners == ["Чеботков", "Ананьев"]
    assert kr.src == "OKR-Q3-2026.md#KR-1.1"

def test_authored_block():
    spec = load_deckspec(FIX)
    assert spec.authored.market[0]["value"] == "≈227 млрд ₽"
    assert spec.authored.order_of_work["august"][0].startswith("★")
    assert spec.authored.glossary[0]["term"] == "БАЗИС"
