import plotly.express as px
import streamlit as st

import analytics

st.set_page_config(page_title="E-Commerce Sales Dashboard", layout="wide")
st.title("E-Commerce Sales Dashboard")

try:
    df = analytics.load_data()
except FileNotFoundError:
    st.error("Data file not found at `data/sales-data.csv`. Add it and reload the app.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${analytics.total_sales(df):,.0f}")
col2.metric("Total Orders", f"{analytics.total_orders(df):,}")

trend = analytics.monthly_trend(df)
fig_trend = px.line(
    trend, x="month", y="total_amount", markers=True,
    labels={"month": "Month", "total_amount": "Sales"},
)
fig_trend.update_traces(hovertemplate="%{x}: $%{y:,.0f}<extra></extra>")
st.plotly_chart(fig_trend, use_container_width=True)
