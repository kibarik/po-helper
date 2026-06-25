import shutil
from sa_documentation import blueprint_render


def test_pick_renderer_prefers_mmdc(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda c: "/bin/mmdc" if c == "mmdc" else None)
    cmd = blueprint_render.pick_renderer()
    assert cmd is not None and cmd[0] == "mmdc"


def test_pick_renderer_falls_back_to_npx(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda c: "/bin/npx" if c == "npx" else None)
    cmd = blueprint_render.pick_renderer()
    assert cmd is not None and cmd[0] == "npx" and "@mermaid-js/mermaid-cli" in cmd


def test_pick_renderer_none_available(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda c: None)
    assert blueprint_render.pick_renderer() is None


def test_block_message_contains_marker():
    msg = blueprint_render.block_message("syntax error at line 4")
    assert "Не могу продолжить" in msg and "syntax error at line 4" in msg
