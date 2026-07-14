import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
SKILLS = REPO / ".claude/skills"
CMDS = REPO / ".claude/commands"

PULSE_SKILLS = ["chat-watch", "chat-sync", "pulse-radar", "pulse-promote"]
PULSE_COMMANDS = ["chat-watch", "chat-sync", "pulse-radar", "pulse-promote"]
FORBIDDEN = ["link-radar", "radar-promote", "mts-po-workspace",
             "Ишманов", "team-ishmanov-aleksej", "Парфило", "GDS Daily"]


def _skill_files():
    for s in PULSE_SKILLS:
        for p in (SKILLS / s).rglob("*.md"):
            yield p


def test_all_pulse_skills_present():
    for s in PULSE_SKILLS:
        assert (SKILLS / s / "SKILL.md").is_file(), f"нет скилла {s}"


def test_all_pulse_commands_present():
    for c in PULSE_COMMANDS:
        assert (CMDS / f"{c}.md").is_file(), f"нет команды {c}"


def test_no_forbidden_tokens_in_pulse_skills():
    hits = []
    for p in _skill_files():
        text = p.read_text(encoding="utf-8")
        for tok in FORBIDDEN:
            if tok in text:
                hits.append(f"{p.relative_to(REPO)}: {tok}")
    assert not hits, f"запрещённые токены: {hits}"


def test_contract_defines_chat_dump():
    contract = SKILLS / "chat-sync/resources/chat_dump_contract.md"
    assert contract.is_file()
    assert "type: chat-dump" in contract.read_text(encoding="utf-8")


def test_adapters_emit_contract_type():
    adapters = REPO / "tools/adapters"
    if not adapters.is_dir():
        return
    hits = []
    for p in adapters.rglob("*"):
        if p.is_file() and p.suffix in {".mjs", ".js", ".md"}:
            if "type: mts-chat" in p.read_text(encoding="utf-8"):
                hits.append(str(p.relative_to(REPO)))
    assert not hits, f"адаптер пишет устаревший type: mts-chat вместо contract type: chat-dump: {hits}"


def test_no_stale_radar_notes_key_in_pulse_skills():
    # канонический ключ каталога радар-нот — paths.pulse_radar_dir;
    # старое имя radar_notes из исходного link-radar не должно остаться (рассинхрон с профилем)
    hits = []
    for p in _skill_files():
        if "radar_notes" in p.read_text(encoding="utf-8"):
            hits.append(str(p.relative_to(REPO)))
    assert not hits, f"стейл-ключ radar_notes (нужен pulse_radar_dir): {hits}"


def test_pulse_docs_have_no_absolute_home_path():
    # план/спека шиппятся через install.sh — не должны нести абсолютный путь с именем ОС-пользователя
    docs = [
        REPO / "docs/superpowers/plans/2026-07-13-pulse-pipeline-port.md",
        REPO / "docs/superpowers/specs/2026-07-13-pulse-pipeline-port-design.md",
    ]
    hits = []
    for p in docs:
        if p.is_file() and "/Users/" in p.read_text(encoding="utf-8"):
            hits.append(str(p.relative_to(REPO)))
    assert not hits, f"абсолютный /Users/-путь (PII) в pulse-доках: {hits}"


def test_no_absolute_tools_path_outside_adapter():
    # skill bodies must not carry absolute ~/tools или ~/.mts-link-sync пути;
    # адаптер (tools/adapters/mts-link/) намеренно вне scope этой проверки
    hits = []
    for p in _skill_files():
        text = p.read_text(encoding="utf-8")
        if "~/tools" in text or "~/.mts-link-sync" in text:
            hits.append(str(p.relative_to(REPO)))
    assert not hits, f"абсолютные ~/tools-пути в скиллах: {hits}"
