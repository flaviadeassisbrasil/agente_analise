import pandas as pd
from src.tools.excel_tool import ExcelTool


def test_read_returns_dataframe(sample_excel):
    df = ExcelTool().read(sample_excel)
    assert isinstance(df, pd.DataFrame)


def test_correct_columns(sample_excel):
    df = ExcelTool().read(sample_excel)
    assert "product" in df.columns
    assert "revenue" in df.columns
