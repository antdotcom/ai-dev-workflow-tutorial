# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page Streamlit dashboard (`app.py` + `analytics.py`) that reads
`data/sales-data.csv` and shows Total Sales / Total Orders KPI cards, a
monthly sales trend line chart, and category/region breakdown bar charts.
The requirements live in `prd/ecommerce-analytics.md`; the approved design
and implementation plan live in `docs/superpowers/specs/` and
`docs/superpowers/plans/`.

This repo also doubles as tutorial course material (see `README.md`,
`pre-work-setup.md`, `workshop-build-deploy.md`) — those files document the
workflow for a student, not the app itself, and aren't relevant to editing
`app.py`/`analytics.py`.

## Commands

```bash
source venv/bin/activate          # activate the existing venv (already created)
pip install -r requirements.txt   # streamlit, pandas, plotly, pytest

streamlit run app.py              # run the dashboard locally
pytest -v                         # run the full test suite
pytest tests/test_analytics.py::test_total_sales_sums_total_amount -v  # single test
```

`pytest.ini` sets `pythonpath = .` so `tests/test_analytics.py` can `import
analytics` from the project root without packaging.

## Architecture

The split between the two top-level files is a hard boundary, not just a
convention:

- **`analytics.py`** owns everything data-related: `load_data()` (decorated
  with `@st.cache_data`, the module's only Streamlit dependency) and one
  pure function per KPI/chart (`total_sales`, `total_orders`,
  `monthly_trend`, `sales_by_category`, `sales_by_region`). Every function
  besides `load_data` takes an already-loaded DataFrame and returns a plain
  value/DataFrame, with no Streamlit calls — that's what lets
  `tests/test_analytics.py` call them directly against a small in-memory
  fixture instead of driving the UI.
- **`app.py`** owns everything visual: page config, layout, KPI cards via
  `st.metric`, and the three Plotly charts. It calls into `analytics.py`
  for every number and only formats for display (currency, separators,
  hover templates) — it must never compute anything itself.
- Sorting for the category/region breakdowns happens inside `analytics.py`,
  not in `app.py`, so the sort order is pinned down by a test rather than
  eyeballed in the rendered chart.
- `total_orders` counts distinct `order_id` values, not row count, so it
  stays correct if the data ever gains multiple line items per order.
- Trend granularity is monthly (12 points), not daily.
- A missing `data/sales-data.csv` is caught once, in `app.py`, around the
  `load_data()` call: `st.error(...)` + `st.stop()`. `load_data()` itself
  lets `FileNotFoundError` propagate uncaught.

## Testing

`tests/test_analytics.py` covers every function in `analytics.py`,
written test-first. All functions besides `load_data` share one
hand-built `sample_df` fixture (5 rows, 2 categories, 2 regions, 2 months,
values chosen so expected sums/counts can be checked by hand) — extend
that fixture rather than adding a new one when testing another aggregation
over the same shape of data. Chart rendering in `app.py` is not unit
tested (Streamlit/Plotly components aren't meaningfully testable in
isolation); that layer is verified by running the app locally against the
PRD's Acceptance Criteria and Expected Output table.

## Progress tracking (TASKS.md)

`TASKS.md` is the versioned source of truth for milestone progress, not
just documentation — it's a Markdown board with `To Do` / `In Progress` /
`Done` sections. Every commit message starts with the milestone ID it
belongs to (`TASK-1:`, `TASK-2:`, etc.), including commits that only move
a milestone between board sections, so `git log` traces the full chain
from requirement to code. A milestone's `Done` entry records the hash of
its last *code* commit (not the board-move commit) on its `Commit:` line.

TASK-5 ("Test and deploy") includes Streamlit Community Cloud deployment,
which is executed by the developer from `main` after merge — it is not
part of implementation work done on a feature branch and should stay in
`To Do` until then.

## Lessons

Rules earned from mistakes caught during development, one line per
correction, added when a milestone's `Notes:` line in `TASKS.md` records
something Claude got wrong or the developer changed.

TASK-1 through TASK-4 all record `Notes: clean` — no corrections were
needed during the initial build, so there are no rules here yet. Add one
the first time a Notes line says otherwise.
