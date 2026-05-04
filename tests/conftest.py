from pathlib import Path
import pytest
import pandas as pd

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_csv(tmp_path) -> str:
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Carol", "Dave", "Eve"],
        "age": [25, 30, 35, 40, None],
        "score": [88.5, 92.0, 78.3, 95.1, 60.0],
        "city": ["SP", "RJ", "BH", "SP", "RJ"],
    })
    path = tmp_path / "sample.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def sample_excel(tmp_path) -> str:
    df = pd.DataFrame({"product": ["A", "B", "C"], "revenue": [1000, 2000, 1500]})
    path = tmp_path / "sample.xlsx"
    df.to_excel(path, index=False)
    return str(path)


@pytest.fixture
def sample_json(tmp_path) -> str:
    import json
    data = [{"id": 1, "value": 10}, {"id": 2, "value": 20}]
    path = tmp_path / "sample.json"
    path.write_text(json.dumps(data))
    return str(path)
