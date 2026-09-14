# E-Commerce Sales Dashboard: Design

**Status:** Approved
**Source:** [prd/ecommerce-analytics.md](../../../prd/ecommerce-analytics.md)
**Milestones tracked in:** [TASKS.md](../../../TASKS.md) (TASK-1 through TASK-5)

## Summary

A single-page Streamlit dashboard that reads `data/sales-data.csv` and
shows: two KPI scorecards (Total Sales, Total Orders), a monthly sales
trend line chart, and two sorted bar charts (sales by category, sales
by region). Built with Streamlit + Pandas + Plotly per the PRD's
Technical Approach section, on the current feature branch, with a
plain `venv/` + `requirements.txt` for dependencies. Deployment to
Streamlit Community Cloud is out of scope for this design and plan —
the PRD assigns it (NFR-5), but it's executed by the developer after
merge, not by the plan.

## Architecture & data flow

```
┌──────────────────┐     ┌────────────────────┐     ┌──────────────────┐
│ data/sales-data  │ ──> │   analytics.py      │ ──> │     app.py       │
│      .csv        │     │  (load + calculate) │     │ (Streamlit UI)   │
└──────────────────┘     └────────────────────┘     └──────────────────┘
                                                              │
                                                              ▼
                                                     Browser (KPI cards,
                                                     line chart, 2 bar charts)
```

- `analytics.py` owns everything data-related: reading the CSV into a
  Pandas DataFrame and every aggregation the dashboard needs. It has
  no Streamlit imports except the `@st.cache_data` decorator on
  `load_data()` — every other function takes an already-loaded
  DataFrame and returns a plain value, so pytest can call them
  directly with a small in-memory DataFrame.
- `app.py` owns everything visual: page config, layout, KPI cards, and
  the three Plotly charts. It calls into `analytics.py` for numbers
  and only formats for display; it does not compute anything itself.
- `load_data()` is decorated with `@st.cache_data` so the CSV is
  parsed once per session and reused across Streamlit reruns (a
  Streamlit app reruns its whole script on every user interaction),
  keeping the app responsive per NFR-1 (5s load, 2s chart render).

## Calculations (`analytics.py`)

```python
load_data(path="data/sales-data.csv") -> pd.DataFrame
    # @st.cache_data. Parses 'date' as datetime.
    # Missing file: pandas' own read_csv raises FileNotFoundError;
    # not caught here — app.py handles the user-facing message.

total_sales(df) -> float          # df['total_amount'].sum()
total_orders(df) -> int           # df['order_id'].nunique()
monthly_trend(df) -> pd.DataFrame # total_amount summed per calendar month, chronological
sales_by_category(df) -> pd.DataFrame  # summed per category, sorted descending
sales_by_region(df) -> pd.DataFrame    # summed per region, sorted descending
```

Notes:
- `total_orders` counts distinct `order_id`, not row count. They're
  equal in the current dataset (482 rows, 482 unique IDs), but
  counting the ID is the version that stays correct if the data ever
  gains multiple line items per order.
- Sorting for the category/region breakdowns happens in these
  functions, not in `app.py` — FR-3/FR-4 both require "sorted by
  sales value, highest to lowest," and putting it here means pytest
  pins the order down rather than a human eyeballing the rendered
  chart.
- Trend granularity is **monthly** (12 points), not daily. With ~40
  orders/month and several days having 0-1 orders, a monthly line
  reads as a clean trend; a daily line would be noisy and doesn't
  serve the CEO user story ("is the business growing").

## UI layout (`app.py`)

Top to bottom, matching the PRD's own mockup:

```
st.set_page_config(page_title="E-Commerce Sales Dashboard", layout="wide")
st.title("E-Commerce Sales Dashboard")

col1, col2 = st.columns(2)
col1: st.metric("Total Sales", f"${total_sales:,.0f}")
col2: st.metric("Total Orders", f"{total_orders:,}")

st.plotly_chart(line chart — monthly_trend, x=month, y=total_amount)

col1, col2 = st.columns(2)
col1: st.plotly_chart(horizontal bar — sales_by_category)
col2: st.plotly_chart(horizontal bar — sales_by_region)
```

- KPI cards use `st.metric`, Streamlit's built-in scorecard widget —
  no custom CSS needed, satisfies NFR-2 (no training required,
  professional appearance).
- Category and region charts are **horizontal** bars (category/region
  names on the y-axis), matching the PRD's ASCII mockup
  (`Electronics ████████`) and reading better than vertical bars once
  labels get long.
- All three charts use `plotly.express` with a `hovertemplate` set so
  tooltips show currency-formatted values (e.g. `$99,980`) rather
  than Plotly's raw float default — satisfies FR-2/FR-3/FR-4's
  "interactive tooltips showing exact values."
- No sidebar, no filters, no date-range picker — Phase 2 of the PRD
  explicitly puts those out of scope.

## Error handling

Missing `data/sales-data.csv` (wrapping the `load_data()` call in `app.py`):

```python
try:
    df = analytics.load_data()
except FileNotFoundError:
    st.error("Data file not found at `data/sales-data.csv`. Add it and reload the app.")
    st.stop()
```

`st.stop()` halts the script at that point so nothing downstream tries
to render a chart against data that doesn't exist. This is the one
error path the app needs: FR-5's format guarantees (date, numeric,
categorical columns) are assumed to hold for the sample data, so no
additional schema validation is built for this phase.

## Testing

`tests/test_analytics.py` covers every function in `analytics.py`,
written test-first (TDD):

- A small hand-built DataFrame fixture (4-5 rows across 2 categories,
  2 regions, 2 months) with values chosen so expected sums/counts can
  be checked by hand.
- `total_sales`, `total_orders`, `monthly_trend`, `sales_by_category`,
  `sales_by_region` are each asserted against that fixture, including
  that the category/region results come back sorted descending.
- `load_data` gets its own tests: a happy path using pytest's
  `tmp_path` fixture to write a temp CSV, and a `FileNotFoundError`
  assertion for a missing path.

Chart rendering in `app.py` is not unit tested — Streamlit/Plotly
components are hard to test meaningfully in isolation, so that layer
is verified by running the app locally and checking it against the
PRD's Acceptance Criteria and Expected Output table by eye.

## Project layout

```
app.py                    # Streamlit UI
analytics.py              # data loading + calculations
requirements.txt          # streamlit, pandas, plotly, pytest
venv/                     # gitignored (already covered in .gitignore)
tests/
  test_analytics.py
data/
  sales-data.csv          # already present
TASKS.md                  # already present
prd/
  ecommerce-analytics.md  # already present
docs/superpowers/
  specs/                  # this file
  plans/                  # implementation plan
```

`requirements.txt` holds `pytest` alongside the runtime libraries
(streamlit, pandas, plotly) rather than a separate dev-requirements
file — splitting them buys nothing at this size, and Streamlit Cloud
only reads the one file at deploy time anyway.

## Out of scope (per PRD Phase 2 and this design)

- User authentication, real-time database integration, export
  (PDF/Excel), email alerts, filtering/date-range selection,
  transaction-level drill-down, mobile-responsive design.
- Deployment execution: the plan's last step describes the deploy
  procedure but is marked as developer-executed, run from `main`
  after merge, per the workflow's ground rules.

## Milestone mapping

| Milestone | Design elements it covers |
|---|---|
| TASK-1: Project setup and data loading | `venv/`, `requirements.txt`, `analytics.load_data()`, missing-file error handling |
| TASK-2: KPI scorecards | `total_sales()`, `total_orders()`, `st.metric` cards |
| TASK-3: Sales trend chart | `monthly_trend()`, Plotly line chart |
| TASK-4: Category and region breakdowns | `sales_by_category()`, `sales_by_region()`, horizontal bar charts |
| TASK-5: Test and deploy | Full `tests/test_analytics.py` suite, local run against Acceptance Criteria, deployment (developer-executed) |
