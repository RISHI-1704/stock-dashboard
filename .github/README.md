# 📈 NIFTY-50 Stock Analytics Dashboard

![CI](https://github.com/RISHI-1704/stock-dashboard/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Plotly](https://img.shields.io/badge/Plotly-5.22-purple)
![Pytest](https://img.shields.io/badge/Tested-Pytest%20%2B%20Playwright-green)

A **live** stock market analytics dashboard built with Python and Streamlit, pulling real-time NSE data via the yfinance API. Features end-to-end test coverage with Pytest (unit tests) and Playwright (UI automation), integrated into a CI/CD pipeline via GitHub Actions.

🔗 **[Live Demo](https://your-app-name.streamlit.app)** ← replace after deploying

---

## Features

- **Live NSE data** — fetches real-time NIFTY-50 stock prices via yfinance, cached for 24 hours
- **Portfolio KPIs** — return %, annualised volatility, Sharpe ratio, max drawdown
- **Price trend chart** — interactive line chart with configurable moving average overlay
- **Sector performance** — bar chart comparing returns across sectors
- **Correlation heatmap** — identify diversification opportunities across selected stocks
- **Sidebar filters** — sector, stock tickers, date range, moving average window
- **Raw data table** — view last 30 days of closing prices

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, Plotly, Seaborn |
| Data | yfinance (Yahoo Finance API), Pandas, NumPy |
| Unit Testing | Pytest |
| UI Automation | Playwright |
| CI/CD | GitHub Actions |
| Deployment | Streamlit Community Cloud |

---

## Architecture

```
stock-dashboard/
├── app.py               # Streamlit UI — charts, KPIs, sidebar filters
├── data.py              # Data layer — yfinance fetch, KPI computation, caching
├── requirements.txt
├── tests/
│   ├── test_data.py     # Pytest unit tests — 20+ tests across all data functions
│   └── test_ui.py       # Playwright UI tests — dashboard load, filters, charts
└── .github/
    └── workflows/
        └── ci.yml       # GitHub Actions — runs Pytest + Playwright on every push
```

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/RISHI-1704/stock-dashboard.git
cd stock-dashboard

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the app
streamlit run app.py
```

---

## Running Tests

```bash
# Unit tests
pytest tests/test_data.py -v

# UI tests (start app first in a separate terminal)
streamlit run app.py --server.port 8501
pytest tests/test_ui.py -v
```

---

## KPIs Explained

| Metric | Description |
|---|---|
| Portfolio Return % | Avg price change across selected stocks over the date range |
| Annualised Volatility | Std deviation of daily returns scaled to 252 trading days |
| Sharpe Ratio | Risk-adjusted return assuming 6% Indian risk-free rate |
| Max Drawdown | Largest peak-to-trough decline in the portfolio |

---

Built by **Rishi Cheravath** · [LinkedIn](https://www.linkedin.com/in/rishi-cheravath) · [GitHub](https://github.com/RISHI-1704)
