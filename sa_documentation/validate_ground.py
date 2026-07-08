"""Валидатор GROUND Vault: config.yaml + NEXUS/_registry.yaml.

См. sa_documentation/ground_schema.md и spec
docs/superpowers/specs/2026-06-21-paf-team-os-design.md (§7).
"""
import pathlib
import re
import yaml

LOOP_PHASES = ("pulse", "bunch", "harvest")
LOOP_DIRS = {"PULSE": "pulse", "BUNCH": "bunch", "RESULTS": "harvest"}
_LOOP_BASE_REQUIRED = (
    "nexus", "node_id", "node_type", "sprint_phase", "kind", "owner",
    "confidence", "sources", "updated", "ttl_days", "ripeness",
    "level", "cycle_ref",
)


def _parse_frontmatter(text):
    """YAML-frontmatter между первыми --- ... ---. None если нет/битый."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _validate_loop_node(fm, rel):
    errs = []
    for k in _LOOP_BASE_REQUIRED:
        if fm.get(k) in (None, "", []):
            errs.append(f"{rel}: missing required field {k!r}")
    # paf_step обязателен как ключ (для loop-узлов значение = null) — см. node/loop schema.
    if "paf_step" not in fm:
        errs.append(f"{rel}: missing required field 'paf_step' (null for loop)")
    if fm.get("node_type") != "sprint-phase":
        errs.append(f"{rel}: node_type must be 'sprint-phase'")
    if fm.get("kind") != "empirical":
        errs.append(f"{rel}: kind must be 'empirical'")
    conf = fm.get("confidence")
    if (
        isinstance(conf, bool)
        or not isinstance(conf, (int, float))
        or not (0 <= conf <= 1)
    ):
        errs.append(f"{rel}: confidence must be float 0..1")
    level = fm.get("level")
    if level not in ("quarter", "sprint"):
        errs.append(f"{rel}: level must be quarter|sprint")

    phase = fm.get("sprint_phase")
    if phase not in LOOP_PHASES:
        errs.append(f"{rel}: sprint_phase must be pulse|bunch|harvest")
        return errs
    if phase == "pulse":
        if not isinstance(fm.get("nexus_snapshot"), dict):
            errs.append(f"{rel}: pulse requires nexus_snapshot (map)")
        if not fm.get("intent"):
            errs.append(f"{rel}: pulse requires intent")
        if fm.get("lens") not in ("product", "business", "strategy"):
            errs.append(f"{rel}: pulse lens must be product|business|strategy")
    elif phase == "bunch":
        if not fm.get("bunch_size"):
            errs.append(f"{rel}: bunch requires bunch_size")
        if not fm.get("bunch_window"):
            errs.append(f"{rel}: bunch requires bunch_window")
        items = fm.get("items")
        if not isinstance(items, list) or not items:
            errs.append(f"{rel}: bunch requires non-empty items")
        else:
            for i, it in enumerate(items):
                if not isinstance(it, dict) or not it.get("ref") or not it.get("kind") or not it.get("trace"):
                    errs.append(f"{rel}: item[{i}] requires ref, kind and trace")
        gate = fm.get("gate")
        if not isinstance(gate, dict) or gate.get("decision") not in ("commit", "defer", "refuse"):
            errs.append(f"{rel}: bunch requires gate.decision in commit|defer|refuse")
        if level == "sprint" and not fm.get("parent_bunch"):
            errs.append(f"{rel}: sprint bunch requires parent_bunch")
    elif phase == "harvest":
        wb = fm.get("nexus_writeback")
        if not isinstance(wb, list) or not wb:
            errs.append(f"{rel}: harvest requires non-empty nexus_writeback")
        else:
            for i, w in enumerate(wb):
                if not isinstance(w, dict) or not all(
                    w.get(k) for k in ("nexus", "node", "change", "source")
                ):
                    errs.append(f"{rel}: writeback[{i}] requires nexus,node,change,source")
        if not fm.get("insights"):
            errs.append(f"{rel}: harvest requires insights")
        if level == "sprint" and not fm.get("rolls_up_to"):
            errs.append(f"{rel}: sprint harvest requires rolls_up_to")
        if (fm.get("outcomes") or {}).get("cp_change") is None:
            errs.append(f"{rel}: harvest requires outcomes.cp_change")
    return errs


def validate_loop_artifacts(ground_dir):
    """Валидировать loop-артефакты в PULSE/BUNCH/RESULTS. Список ошибок (пустой = OK)."""
    ground_dir = pathlib.Path(ground_dir)
    errs = []
    for folder in LOOP_DIRS:
        d = ground_dir / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            fm = _parse_frontmatter(p.read_text())
            # не loop-артефакт (init-pulse, summary, без frontmatter) → пропустить.
            # Классифицируем по node_type, а не по sprint_phase — иначе
            # артефакт с отсутствующим/опечатанным sprint_phase молча
            # пропускается вместо того, чтобы упасть на валидации.
            if not fm or fm.get("node_type") != "sprint-phase":
                continue
            rel = f"{folder}/{p.name}"
            errs.extend(_validate_loop_node(fm, rel))
            expected_phase = LOOP_DIRS[folder]
            phase = fm.get("sprint_phase")
            if phase in LOOP_PHASES and phase != expected_phase:
                errs.append(
                    f"{rel}: sprint_phase {phase!r} does not match folder {folder}"
                )
    return errs


def validate_loop_references(ground_dir):
    """Проверить referential integrity вложенности loop-артефактов на весь свод.

    В отличие от validate_loop_artifacts (изолированная валидация одного
    файла), здесь проверяется, что parent_bunch/rolls_up_to спринтовых
    артефактов резолвятся в node_id, реально присутствующий среди всех
    loop-артефактов. Список ошибок (пустой = OK).
    """
    ground_dir = pathlib.Path(ground_dir)
    nodes = []  # (rel, fm)
    node_ids = set()
    for folder in LOOP_DIRS:
        d = ground_dir / folder
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            fm = _parse_frontmatter(p.read_text())
            if not fm or fm.get("node_type") != "sprint-phase":
                continue
            if fm.get("sprint_phase") not in LOOP_PHASES:
                continue
            rel = f"{folder}/{p.name}"
            nodes.append((rel, fm))
            nid = fm.get("node_id")
            if nid:
                node_ids.add(nid)

    errs = []
    for rel, fm in nodes:
        if fm.get("level") != "sprint":
            continue
        phase = fm.get("sprint_phase")
        if phase == "bunch":
            parent = fm.get("parent_bunch")
            if parent and parent not in node_ids:
                errs.append(
                    f"{rel}: parent_bunch {parent!r} does not resolve to any loop node_id"
                )
        elif phase == "harvest":
            rolls_up_to = fm.get("rolls_up_to")
            if rolls_up_to and rolls_up_to not in node_ids:
                errs.append(
                    f"{rel}: rolls_up_to {rolls_up_to!r} does not resolve to any loop node_id"
                )
    return errs


def validate_ground(ground_dir):
    """Проверить GROUND-каталог. Возвращает список строк-ошибок (пустой = OK)."""
    errs = []
    ground_dir = pathlib.Path(ground_dir)
    cfg_p = ground_dir / "config.yaml"
    reg_p = ground_dir / "NEXUS/_registry.yaml"

    if not cfg_p.exists():
        return [f"missing {cfg_p}"]

    try:
        cfg = yaml.safe_load(cfg_p.read_text()) or {}
    except yaml.YAMLError as e:
        return [f"{cfg_p}: invalid YAML ({e})"]

    # product.slug — ascii-slug
    slug = (cfg.get("product") or {}).get("slug", "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(slug)):
        errs.append(f"product.slug invalid ascii-slug: {slug!r}")

    # team.roster.product_engineer — обязателен
    roster = (cfg.get("team") or {}).get("roster") or {}
    if not roster.get("product_engineer"):
        errs.append("team.roster.product_engineer is required")

    # NEXUS/_registry.yaml (опционально, но если есть — валидируем)
    if reg_p.exists():
        try:
            reg = yaml.safe_load(reg_p.read_text()) or {}
        except yaml.YAMLError as e:
            errs.append(f"{reg_p}: invalid YAML ({e})")
            reg = {}
        for t in reg.get("nexus_types", []) or []:
            s = t.get("slug", "")
            if not re.fullmatch(r"[a-z][a-z0-9-]*", str(s)):
                errs.append(f"nexus slug invalid: {s!r}")
            if t.get("source") not in ("default", "custom"):
                errs.append(f"nexus {s!r} source must be default|custom")

    errs.extend(validate_loop_artifacts(ground_dir))
    errs.extend(validate_loop_references(ground_dir))

    return errs


if __name__ == "__main__":
    import sys
    e = validate_ground(sys.argv[1])
    print("\n".join(e) or "OK")
