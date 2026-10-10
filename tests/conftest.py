from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def sample_csv() -> Path:
    return DATA_DIR / "sample.csv"


@pytest.fixture
def empty_csv() -> Path:
    return DATA_DIR / "empty.csv"
