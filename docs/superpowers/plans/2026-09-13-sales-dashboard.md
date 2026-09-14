# E-Commerce Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit dashboard (`app.py` + `analytics.py`) that reads `data/sales-data.csv` and shows Total Sales and Total Orders KPI cards, a monthly sales trend line chart, and category/region breakdown bar charts.

**Architecture:** `analytics.py` is a Streamlit-free module (except one `@st.cache_data` decorator) holding `load_data()` plus one pure function per KPI/chart, each unit-tested with pytest against a small hand-built DataFrame fixture. `app.py` is a thin Streamlit UI layer that calls into `analytics.py` and only formats values for display.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly (`plotly.express`), pytest, plain `venv/` + `requirements.txt`.

**Spec:** [docs/superpowers/specs/2026-09-13-sales-dashboard-design.md](../specs/2026-09-13-sales-dashboard-design.md)

## Global Constraints

- Work on the current feature branch (`feature/sales-dashboard`); do not create a git worktree.
- Dependencies live in `requirements.txt`, installed into a plain `venv/` (no uv, no conda).
- All data calculations live in `analytics.py`, unit-tested with pytest; `app.py` contains no calculation logic, only formatting and layout.
- Every commit message starts with the milestone ID it belongs to (`TASK-1:` … `TASK-5:`), per `TASKS.md`'s Definition of Done.
- Trend chart granularity is **monthly**, not daily.
- A missing `data/sales-data.csv` must show a friendly `st.error()` message and call `st.stop()` — no raw traceback.
- `total_orders` counts distinct `order_id` values, not row count.
- Category and region breakdowns are **horizontal** bar charts, sorted highest-to-lowest, with currency-formatted hover tooltips.
- Deployment (Task 13) is executed by the developer after merging to `main`, not by whoever runs this plan — it is documented, not implemented, here.

---

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `app.py`

**Interfaces:**
- Produces: `app.py` runnable via `streamlit run app.py`, showing a page titled "E-Commerce Sales Dashboard". Later tasks append to this file.

- [ ] **Step 1: Create the virtual environment**

Run:
```bash
python3 -m venv venv
source venv/bin/activate
```
(Windows: `venv\Scripts\activate` instead of the `source` line.)

- [ ] **Step 2: Write `requirements.txt`**

```
streamlit
pandas
plotly
pytest
```

- [ ] **Step 3: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: all four packages install without errors.

- [ ] **Step 4: Write the minimal `app.py`**

```python
import streamlit as st

st.set_page_config(page_title="E-Commerce Sales Dashboard", layout="wide")
st.title("E-Commerce Sales Dashboard")
```

- [ ] **Step 5: Verify it runs**

Run: `streamlit run app.py`
Expected: a browser tab opens showing the title "E-Commerce Sales Dashboard"; the terminal shows no errors. Stop it with `Ctrl+C`.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt app.py
git commit -m "TASK-1: scaffold project, venv, and minimal Streamlit app"
```

---

### Task 2: `load_data()` (TDD)

**Files:**
- Create: `analytics.py`
- Create: `pytest.ini`
- Create: `tests/test_analytics.py`

**Interfaces:**
- Produces: `analytics.load_data(path: str = "data/sales-data.csv") -> pd.DataFrame`, with a `date` column parsed as `datetime64`. Raises `FileNotFoundError` for a missing path. Every later task's tests call this to build DataFrames, and `app.py` calls it directly.

- [ ] **Step 1: Write the failing tests**

Create `pytest.ini`:
```ini
[pytest]
pythonpath = .
```
(This lets `tests/test_analytics.py` `import analytics` from the project root.)

Create `tests/test_analytics.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_analytics.py -v`
Expected: FAIL/ERROR — `ModuleNotFoundError: No module named 'analytics'` (the file doesn't exist yet).

- [ ] **Step 3: Write the minimal implementation**

Create `analytics.py`:
```python
import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path: str = "data/sales-data.csv") -> pd.DataFrame:
    """Load sales transactions from CSV, parsing the date column."""
    df = pd.read_csv(path, parse_dates=["date"])
    return df
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_analytics.py -v`
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
git add analytics.py pytest.ini tests/test_analytics.py
git commit -m "TASK-1: add load_data with tests"
```

---

### Task 3: Wire data loading into `app.py`

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `analytics.load_data() -> pd.DataFrame` (Task 2).
- Produces: a module-level `df` in `app.py` that later tasks (4-11) read from.

- [ ] **Step 1: Update `app.py`**

```python
import streamlit as st

import analytics

st.set_page_config(page_title="E-Commerce Sales Dashboard", layout="wide")
st.title("E-Commerce Sales Dashboard")

try:
    df = analytics.load_data()
except FileNotFoundError:
    st.error("Data file not found at `data/sales-data.csv`. Add it and reload the app.")
    st.stop()
```

- [ ] **Step 2: Verify the happy path**

Run: `streamlit run app.py`
Expected: no error shown (`data/sales-data.csv` already exists in the repo), no traceback in the terminal.

- [ ] **Step 3: Verify the missing-file path**

Run: `mv data/sales-data.csv data/sales-data.csv.bak`, then reload the browser tab.
Expected: a red error box reading "Data file not found at `data/sales-data.csv`. Add it and reload the app." and nothing else on the page — no chart placeholders, no traceback.
Then restore the file: `mv data/sales-data.csv.bak data/sales-data.csv`, reload, and confirm the error is gone.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "TASK-1: wire data loading into app with missing-file handling"
```

---

### Task 4: `total_sales()` (TDD)

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`

**Interfaces:**
- Produces: `analytics.total_sales(df: pd.DataFrame) -> float`. Also introduces the shared `sample_df` pytest fixture that Tasks 5, 7, 9, and 10 reuse.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_analytics.py` (fixture goes above the first test that uses it):
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analytics.py::test_total_sales_sums_total_amount -v`
Expected: FAIL — `AttributeError: module 'analytics' has no attribute 'total_sales'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `analytics.py`:
```python
def total_sales(df: pd.DataFrame) -> float:
    """Sum of total_amount across all transactions."""
    return float(df["total_amount"].sum())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analytics.py::test_total_sales_sums_total_amount -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add analytics.py tests/test_analytics.py
git commit -m "TASK-2: add total_sales with tests"
```

---

### Task 5: `total_orders()` (TDD)

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`

**Interfaces:**
- Consumes: the `sample_df` fixture (Task 4).
- Produces: `analytics.total_orders(df: pd.DataFrame) -> int`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_analytics.py`:
```python
def test_total_orders_counts_unique_order_ids(sample_df):
    assert analytics.total_orders(sample_df) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analytics.py::test_total_orders_counts_unique_order_ids -v`
Expected: FAIL — `AttributeError: module 'analytics' has no attribute 'total_orders'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `analytics.py`:
```python
def total_orders(df: pd.DataFrame) -> int:
    """Count of unique order IDs."""
    return int(df["order_id"].nunique())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analytics.py::test_total_orders_counts_unique_order_ids -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add analytics.py tests/test_analytics.py
git commit -m "TASK-2: add total_orders with tests"
```

---

### Task 6: Display KPI scorecards

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `analytics.total_sales(df) -> float` (Task 4), `analytics.total_orders(df) -> int` (Task 5), the `df` from Task 3.

- [ ] **Step 1: Add the KPI row to `app.py`**

Append after the `try`/`except` block:
```python
col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${analytics.total_sales(df):,.0f}")
col2.metric("Total Orders", f"{analytics.total_orders(df):,}")
```

- [ ] **Step 2: Verify against the PRD's expected values**

Run: `streamlit run app.py`
Expected: "Total Sales" reads **$116,500** and "Total Orders" reads **482**, matching the PRD's Expected Output table.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-2: display KPI scorecards in app"
```

---

### Task 7: `monthly_trend()` (TDD)

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`

**Interfaces:**
- Consumes: the `sample_df` fixture (Task 4).
- Produces: `analytics.monthly_trend(df: pd.DataFrame) -> pd.DataFrame` with columns `month` (string `"YYYY-MM"`) and `total_amount`, sorted chronologically.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_analytics.py`:
```python
def test_monthly_trend_sums_by_month_chronologically(sample_df):
    result = analytics.monthly_trend(sample_df)
    assert list(result["month"]) == ["2024-01", "2024-02"]
    assert list(result["total_amount"]) == [150.0, 270.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analytics.py::test_monthly_trend_sums_by_month_chronologically -v`
Expected: FAIL — `AttributeError: module 'analytics' has no attribute 'monthly_trend'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `analytics.py`:
```python
def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Total sales summed per calendar month, sorted chronologically."""
    result = (
        df.assign(month=df["date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)["total_amount"]
        .sum()
        .sort_values("month")
        .reset_index(drop=True)
    )
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analytics.py::test_monthly_trend_sums_by_month_chronologically -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add analytics.py tests/test_analytics.py
git commit -m "TASK-3: add monthly_trend with tests"
```

---

### Task 8: Render the sales trend chart

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `analytics.monthly_trend(df) -> pd.DataFrame` (Task 7).

- [ ] **Step 1: Add the import and the chart**

Add `import plotly.express as px` to the top of `app.py` (alongside the other imports).

Append after the KPI row (Task 6):
```python
trend = analytics.monthly_trend(df)
fig_trend = px.line(
    trend, x="month", y="total_amount", markers=True,
    labels={"month": "Month", "total_amount": "Sales"},
)
fig_trend.update_traces(hovertemplate="%{x}: $%{y:,.0f}<extra></extra>")
st.plotly_chart(fig_trend, use_container_width=True)
```

- [ ] **Step 2: Verify**

Run: `streamlit run app.py`
Expected: a line chart with 12 points (Jan-Dec 2024) appears below the KPI cards; hovering over a point shows a tooltip like `2024-03: $9,842` (currency-formatted, not a raw float).

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-3: render sales trend chart"
```

---

### Task 9: `sales_by_category()` (TDD)

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`

**Interfaces:**
- Consumes: the `sample_df` fixture (Task 4).
- Produces: `analytics.sales_by_category(df: pd.DataFrame) -> pd.DataFrame` with columns `category` and `total_amount`, sorted highest to lowest.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_analytics.py`:
```python
def test_sales_by_category_sorted_descending(sample_df):
    result = analytics.sales_by_category(sample_df)
    assert list(result["category"]) == ["Electronics", "Accessories", "Audio"]
    assert list(result["total_amount"]) == [300.0, 80.0, 40.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analytics.py::test_sales_by_category_sorted_descending -v`
Expected: FAIL — `AttributeError: module 'analytics' has no attribute 'sales_by_category'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `analytics.py`:
```python
def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Total sales per category, sorted highest to lowest."""
    result = (
        df.groupby("category", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False)
        .reset_index(drop=True)
    )
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analytics.py::test_sales_by_category_sorted_descending -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add analytics.py tests/test_analytics.py
git commit -m "TASK-4: add sales_by_category with tests"
```

---

### Task 10: `sales_by_region()` (TDD)

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`

**Interfaces:**
- Consumes: the `sample_df` fixture (Task 4).
- Produces: `analytics.sales_by_region(df: pd.DataFrame) -> pd.DataFrame` with columns `region` and `total_amount`, sorted highest to lowest.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_analytics.py`:
```python
def test_sales_by_region_sorted_descending(sample_df):
    result = analytics.sales_by_region(sample_df)
    assert list(result["region"]) == ["North", "South", "West", "East"]
    assert list(result["total_amount"]) == [300.0, 50.0, 40.0, 30.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analytics.py::test_sales_by_region_sorted_descending -v`
Expected: FAIL — `AttributeError: module 'analytics' has no attribute 'sales_by_region'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `analytics.py`:
```python
def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Total sales per region, sorted highest to lowest."""
    result = (
        df.groupby("region", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False)
        .reset_index(drop=True)
    )
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analytics.py::test_sales_by_region_sorted_descending -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add analytics.py tests/test_analytics.py
git commit -m "TASK-4: add sales_by_region with tests"
```

---

### Task 11: Render category and region breakdown charts

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `analytics.sales_by_category(df) -> pd.DataFrame` (Task 9), `analytics.sales_by_region(df) -> pd.DataFrame` (Task 10).

- [ ] **Step 1: Add the charts**

Append after the trend chart (Task 8):
```python
category_df = analytics.sales_by_category(df)
region_df = analytics.sales_by_region(df)

col1, col2 = st.columns(2)
with col1:
    fig_cat = px.bar(
        category_df, x="total_amount", y="category", orientation="h",
        labels={"total_amount": "Sales", "category": "Category"},
    )
    fig_cat.update_traces(hovertemplate="%{y}: $%{x:,.0f}<extra></extra>")
    # Rows are already sorted highest-to-lowest; reverse the axis so the
    # first (highest) row renders at the top of the chart.
    fig_cat.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    fig_region = px.bar(
        region_df, x="total_amount", y="region", orientation="h",
        labels={"total_amount": "Sales", "region": "Region"},
    )
    fig_region.update_traces(hovertemplate="%{y}: $%{x:,.0f}<extra></extra>")
    fig_region.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_region, use_container_width=True)
```

- [ ] **Step 2: Verify**

Run: `streamlit run app.py`
Expected: two side-by-side horizontal bar charts appear below the trend chart. The category chart shows Electronics as the longest (topmost) bar; the region chart shows its regions ordered highest to lowest, top to bottom. Hovering over any bar shows a currency-formatted tooltip (e.g. `Electronics: $34,210`).

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "TASK-4: render category and region breakdown charts"
```

---

### Task 12: Full test suite and acceptance walkthrough

**Files:** none (verification only)

**Interfaces:** none — this task exercises everything built in Tasks 1-11.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: all 7 tests pass (`test_load_data_reads_csv`, `test_load_data_missing_file_raises`, `test_total_sales_sums_total_amount`, `test_total_orders_counts_unique_order_ids`, `test_monthly_trend_sums_by_month_chronologically`, `test_sales_by_category_sorted_descending`, `test_sales_by_region_sorted_descending`).

- [ ] **Step 2: Walk the PRD's Acceptance Criteria against the running app**

Run: `streamlit run app.py`, then check each item yourself in the browser (not by asking Claude):
- KPIs visible: Total Sales and Total Orders shown prominently.
- Trend chart works: line chart shows sales over time with correct data.
- Category chart works: bar chart sorted highest to lowest.
- Region chart works: bar chart sorted highest to lowest.
- Data loads correctly: Total Sales reads **$116,500**, Total Orders reads **482** (PRD Expected Output table).
- No errors: terminal and browser show no errors or warnings.
- Professional appearance: suitable for an executive presentation.

If anything fails, fix it in the relevant file and commit under the milestone it belongs to (e.g. "the region chart isn't sorted, fix it and commit under TASK-4") before moving on. If everything passes, there's nothing to commit for this task.

---

### Task 13: Deploy to Streamlit Community Cloud

**Executed by: you, the developer — not part of running this plan.** This task is documented so the milestone is complete and traceable, but it happens after Tasks 1-12 are merged to `main`, using your own GitHub and Streamlit Cloud accounts.

**Files:** none (deployment only)

- [ ] **Step 1:** Push the merged `main` branch to GitHub (if not already pushed).
- [ ] **Step 2:** Go to [share.streamlit.io](https://share.streamlit.io), sign in, and create a new app pointing at this repository, `main` branch, with `app.py` as the entry point.
- [ ] **Step 3:** Deploy and wait for the build to finish. Streamlit Cloud installs from `requirements.txt` automatically.
- [ ] **Step 4:** Open the live URL and re-check the Acceptance Criteria from Task 12 against the deployed app (not just the local one).
- [ ] **Step 5:** Update `TASKS.md`: check off TASK-5's acceptance criteria, record the live URL, move TASK-5 to Done, and commit the board update.

---

## Milestone-to-task map

| Milestone (`TASKS.md`) | Plan tasks |
|---|---|
| TASK-1: Project setup and data loading | Tasks 1-3 |
| TASK-2: KPI scorecards | Tasks 4-6 |
| TASK-3: Sales trend chart | Tasks 7-8 |
| TASK-4: Category and region breakdowns | Tasks 9-11 |
| TASK-5: Test and deploy | Tasks 12-13 |
