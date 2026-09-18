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


@pytest.fixture
def sample_df():
    data = {
        "date": pd.to_datetime([
            "2024-01-05", "2024-01-20", "2024-02-10", "2024-02-15", "2024-02-20",
        ]),
        "order_id": ["ORD-001", "ORD-002", "ORD-003", "ORD-004", "ORD-005"],
        "product": ["Widget A", "Widget B", "Widget C", "Widget D", "Widget E"],
        "category": ["Electronics", "Accessories", "Electronics", "Accessories", "Audio"],
        "region": ["North", "South", "North", "East", "West"],
        "quantity": [1, 2, 1, 3, 1],
        "unit_price": [100.0, 25.0, 200.0, 10.0, 40.0],
        "total_amount": [100.0, 50.0, 200.0, 30.0, 40.0],
    }
    return pd.DataFrame(data)


def test_total_sales_sums_total_amount(sample_df):
    assert analytics.total_sales(sample_df) == 420.0


def test_total_orders_counts_unique_order_ids(sample_df):
    assert analytics.total_orders(sample_df) == 5


def test_monthly_trend_sums_by_month_chronologically(sample_df):
    result = analytics.monthly_trend(sample_df)
    assert list(result["month"]) == ["2024-01", "2024-02"]
    assert list(result["total_amount"]) == [150.0, 270.0]


def test_sales_by_category_sorted_descending(sample_df):
    result = analytics.sales_by_category(sample_df)
    assert list(result["category"]) == ["Electronics", "Accessories", "Audio"]
    assert list(result["total_amount"]) == [300.0, 80.0, 40.0]
