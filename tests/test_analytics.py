import pandas as pd
import pytest

import analytics


def test_load_data_reads_csv(tmp_path):
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price,total_amount\n"
        "2024-01-05,ORD-001,Widget A,Electronics,North,1,100.0,100.0\n"
    )
    df = analytics.load_data(str(csv_path))
    assert len(df) == 1
    assert df.loc[0, "order_id"] == "ORD-001"
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_data_missing_file_raises(tmp_path):
    missing_path = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError):
        analytics.load_data(str(missing_path))
