"""Валидатор GROUND Vault: config.yaml + NEXUS/_registry.yaml.

См. sa_documentation/ground_schema.md и spec
docs/superpowers/specs/2026-06-21-paf-team-os-design.md (§7).
"""
import pathlib
import re
import yaml


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

    return errs


if __name__ == "__main__":
    import sys
    e = validate_ground(sys.argv[1])
    print("\n".join(e) or "OK")
