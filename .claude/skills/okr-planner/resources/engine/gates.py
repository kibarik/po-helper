from __future__ import annotations
from dataclasses import dataclass, field
from .deckspec import DeckSpec


@dataclass
class Report:
    level: str
    red: list[str] = field(default_factory=list)
    yellow: list[str] = field(default_factory=list)


def audit(spec: DeckSpec) -> Report:
    red, yellow = [], []
    for d in spec.directions:
        for obj in d.objs:
            for kr in obj.krs:
                tag = f"KR {kr.id}"
                if not kr.now:
                    red.append(f"{tag}: нет СЕЙЧАС (now)")
                if not kr.becomes:
                    red.append(f"{tag}: нет СТАНЕТ (becomes)")
                if not kr.sprint_cells:
                    red.append(f"{tag}: нет ни одной sprint-ячейки (нет исполнителя/цикла)")
                if not kr.risks:
                    yellow.append(f"{tag}: без рисков")
                for sp, cells in kr.sprint_cells.items():
                    for c in cells:
                        if "·" not in c:
                            yellow.append(f"{tag} {sp}: чип '{c}' без стека")
    for m in spec.authored.market:
        if not m.get("src"):
            red.append(f"Рыночное число '{m.get('value','?')}' без источника")
    if not spec.authored.glossary:
        yellow.append("Пустой глоссарий")
    level = "🔴" if red else ("🟡" if yellow else "🟢")
    return Report(level=level, red=red, yellow=yellow)


def format_report(rep: Report) -> str:
    lines = [f"Светофор консистентности: {rep.level}"]
    for m in rep.red:
        lines.append(f"  🔴 {m}")
    for m in rep.yellow:
        lines.append(f"  🟡 {m}")
    if not rep.red and not rep.yellow:
        lines.append("  всё покрыто")
    return "\n".join(lines)
