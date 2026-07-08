import sys
from pathlib import Path
import pytest

# put resources/ on sys.path so `import engine.*` works
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


@pytest.fixture
def minimal_spec():
    from engine.deckspec import load_deckspec  # lazy: module created in Step 5
    return load_deckspec(Path(__file__).parent / "fixtures" / "minimal_deck.yaml")
