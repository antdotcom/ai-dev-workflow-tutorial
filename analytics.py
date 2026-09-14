import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path: str = "data/sales-data.csv") -> pd.DataFrame:
    """Load sales transactions from CSV, parsing the date column."""
    df = pd.read_csv(path, parse_dates=["date"])
    return df
