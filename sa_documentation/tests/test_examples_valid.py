import pathlib
import shutil
from sa_documentation.validate_ground import validate_loop_artifacts

REPO = pathlib.Path(__file__).resolve().parents[2]
EXAMPLE_DIRS = [
    REPO / ".claude/skills/sprint-planner/examples/loop",
    REPO / ".claude/skills/okr-planner/examples/loop",
]
PHASE_TO_FOLDER = {"pulse": "PULSE", "bunch": "BUNCH", "harvest": "RESULTS"}


def test_shipped_examples_are_schema_valid(tmp_path):
    """Golden-примеры скиллов не могут разойтись со схемой."""
    copied = 0
    for ed in EXAMPLE_DIRS:
        if not ed.is_dir():
            continue
        for p in ed.glob("*.md"):
            # разложить пример по нужной папке по имени файла (S-pulse/Q-bunch/...)
            for phase, folder in PHASE_TO_FOLDER.items():
                if phase in p.stem.lower():
                    dest = tmp_path / folder
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy(p, dest / p.name)
                    copied += 1
                    break
    assert copied > 0, "no example loop artifacts found"
    errs = validate_loop_artifacts(tmp_path)
    assert errs == [], f"shipped examples invalid: {errs}"
