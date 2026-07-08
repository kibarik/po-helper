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
    if fm.get("node_type") != "sprint-phase":
        errs.append(f"{rel}: node_type must be 'sprint-phase'")
    if fm.get("kind") != "empirical":
        errs.append(f"{rel}: kind must be 'empirical'")
    conf = fm.get("confidence")
    if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
        errs.append(f"{rel}: confidence must be float 0..1")
    level = fm.get("level")
    if level not in ("quarter", "sprint"):
        errs.append(f"{rel}: level must be quarter|sprint")

    phase = fm.get("sprint_phase")
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
                if not isinstance(it, dict) or not it.get("ref") or not it.get("trace"):
                    errs.append(f"{rel}: item[{i}] requires ref and trace")
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
            # не loop-артефакт (init-pulse, summary, без frontmatter) → пропустить
            if not fm or fm.get("sprint_phase") not in LOOP_PHASES:
                continue
            errs.extend(_validate_loop_node(fm, f"{folder}/{p.name}"))
    return errs


def validate_ground(ground_dir):
    """Проверить GROUND-каталог. Возвращает список строк-ошибок (пустой = OK)."""
    errs = []
    ground_dir = pathlib.Path(ground_dir)
    cfg_p = ground_dir / "config.yaml"
    reg_p = ground_dir / "NEXUS/_registry.yaml"

    if not cfg_p.exists():
        return [f"missing {cfg_p}"]

    cfg = yaml.safe_load(cfg_p.read_text()) or {}

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
        reg = yaml.safe_load(reg_p.read_text()) or {}
        for t in reg.get("nexus_types", []) or []:
            s = t.get("slug", "")
            if not re.fullmatch(r"[a-z][a-z0-9-]*", str(s)):
                errs.append(f"nexus slug invalid: {s!r}")
            if t.get("source") not in ("default", "custom"):
                errs.append(f"nexus {s!r} source must be default|custom")

    errs.extend(validate_loop_artifacts(ground_dir))

    return errs


if __name__ == "__main__":
    import sys
    e = validate_ground(sys.argv[1])
    print("\n".join(e) or "OK")
