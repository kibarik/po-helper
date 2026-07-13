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


def test_no_absolute_tools_path_outside_adapter():
    # skill bodies must not carry absolute ~/tools или ~/.mts-link-sync пути;
    # адаптер (tools/adapters/mts-link/) намеренно вне scope этой проверки
    hits = []
    for p in _skill_files():
        text = p.read_text(encoding="utf-8")
        if "~/tools" in text or "~/.mts-link-sync" in text:
            hits.append(str(p.relative_to(REPO)))
    assert not hits, f"абсолютные ~/tools-пути в скиллах: {hits}"
