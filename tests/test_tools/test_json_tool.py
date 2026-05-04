import pandas as pd
from src.tools.json_tool import JSONTool


def test_read_list(sample_json):
    df = JSONTool().read(sample_json)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)


def test_columns(sample_json):
    df = JSONTool().read(sample_json)
    assert "id" in df.columns
    assert "value" in df.columns
