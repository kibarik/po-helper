from pathlib import Path
from engine.render_html import render_html_file
from engine.render_pptx import render_pptx_file
from engine.render_roadmap import render_roadmap_file
from engine.deckspec import load_deckspec
from engine.gates import audit
from pptx import Presentation

IDEAL = Path(__file__).resolve().parents[3] / "examples" / "ideal_deck_spec.yaml"

def test_ideal_spec_loads_and_audits():
    spec = load_deckspec(IDEAL)
    assert len(spec.directions) == 4
    rep = audit(spec)
    assert rep.red == [], f"unexpected red gates: {rep.red}"

def test_end_to_end_three_artifacts(tmp_path):
    html = render_html_file(IDEAL, tmp_path / "deck.html")
    pptx = render_pptx_file(IDEAL, tmp_path / "deck.pptx")
    xlsx = render_roadmap_file(IDEAL, tmp_path / "roadmap.xlsx")
    assert html.exists() and pptx.exists() and xlsx.exists()
    prs = Presentation(str(pptx))
    assert len(prs.slides) >= 20   # эталон-scale deck
    assert "http://" not in html.read_text(encoding="utf-8")
