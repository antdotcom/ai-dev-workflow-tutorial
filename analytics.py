import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path: str = "data/sales-data.csv") -> pd.DataFrame:
    """Load sales transactions from CSV, parsing the date column."""
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def total_sales(df: pd.DataFrame) -> float:
    """Sum of total_amount across all transactions."""
    return float(df["total_amount"].sum())


def total_orders(df: pd.DataFrame) -> int:
    """Count of unique order IDs."""
    return int(df["order_id"].nunique())
