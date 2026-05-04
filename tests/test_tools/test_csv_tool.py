import pandas as pd
from src.tools.csv_tool import CSVTool


def test_read_returns_dataframe(sample_csv):
    tool = CSVTool()
    df = tool.read(sample_csv)
    assert isinstance(df, pd.DataFrame)


def test_correct_shape(sample_csv):
    df = CSVTool().read(sample_csv)
    assert df.shape == (5, 4)


def test_columns_detected(sample_csv):
    df = CSVTool().read(sample_csv)
    assert list(df.columns) == ["name", "age", "score", "city"]


def test_missing_value_preserved(sample_csv):
    df = CSVTool().read(sample_csv)
    assert df["age"].isnull().sum() == 1


def test_file_not_found():
    import pytest
    with pytest.raises(FileNotFoundError):
        CSVTool().read("/nao/existe.csv")
