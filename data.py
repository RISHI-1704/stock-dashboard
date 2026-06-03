import yfinance as yf
import pandas as pd
import streamlit as st

# NIFTY-50 stocks with sector mapping
NIFTY50_STOCKS = {
    "RELIANCE.NS": "Energy",
    "TCS.NS": "IT",
    "INFY.NS": "IT",
    "WIPRO.NS": "IT",
    "HCLTECH.NS": "IT",
    "HDFCBANK.NS": "Banking",
    "ICICIBANK.NS": "Banking",
    "KOTAKBANK.NS": "Banking",
    "AXISBANK.NS": "Banking",
    "SBIN.NS": "Banking",
    "BAJFINANCE.NS": "Finance",
    "BAJAJFINSV.NS": "Finance",
    "HINDUNILVR.NS": "FMCG",
    "ITC.NS": "FMCG",
    "NESTLEIND.NS": "FMCG",
    "MARUTI.NS": "Auto",
    "TATAMOTORS.NS": "Auto",
    "HEROMOTOCO.NS": "Auto",
    "SUNPHARMA.NS": "Pharma",
    "DRREDDY.NS": "Pharma",
    "CIPLA.NS": "Pharma",
    "ONGC.NS": "Energy",
    "NTPC.NS": "Energy",
    "POWERGRID.NS": "Energy",
    "LT.NS": "Infrastructure",
    "ULTRACEMCO.NS": "Infrastructure",
    "ASIANPAINT.NS": "Consumer",
    "TITAN.NS": "Consumer",
    "BHARTIARTL.NS": "Telecom",
    "TECHM.NS": "IT",
}

SECTORS = sorted(set(NIFTY50_STOCKS.values()))

@st.cache_data(ttl=300)  # Refresh every 5 minutes for current price
def get_current_prices(tickers: list) -> pd.DataFrame:
    """Fetch current/latest price and daily change for each stock."""
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        data.append({
            "Ticker": ticker,
            "Current Price": round(info.last_price, 2),
            "Day Change %": round(((info.last_price - info.previous_close) / info.previous_close) * 100, 2),
        })
    return pd.DataFrame(data)


@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_stock_data(tickers, start_date, end_date):
    """Fetch historical stock data from Yahoo Finance."""
    raw = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True,threads=False)
    if raw.empty:
        return pd.DataFrame()

    # Extract Close prices only
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]]

    close = close.dropna(how="all")
    return close


def compute_returns(close_df):
    """Compute daily percentage returns."""
    if close_df.empty:
        return pd.DataFrame()
    return close_df.pct_change().dropna()


def compute_rolling_average(close_df, window=30):
    """Compute rolling average for each stock."""
    if close_df.empty:
        return pd.DataFrame()
    return close_df.rolling(window=window).mean()


def compute_kpis(close_df: pd.DataFrame) -> dict:
    """Compute portfolio-level KPIs from closing prices."""
    if close_df.empty:
        return {"return_pct": 0, "volatility": 0, "sharpe": 0, "max_drawdown": 0}

    returns = compute_returns(close_df)
    avg_returns = returns.mean(axis=1)

    # Portfolio return %
    total_return = ((close_df.iloc[-1] - close_df.iloc[0]) / close_df.iloc[0]).mean() * 100

    # Annualised volatility
    volatility = avg_returns.std() * (252 ** 0.5) * 100

    # Sharpe ratio (assuming risk-free rate of 6% for India)
    risk_free = 0.06 / 252
    excess = avg_returns - risk_free
    sharpe = (excess.mean() / avg_returns.std()) * (252 ** 0.5) if avg_returns.std() != 0 else 0

    # Max drawdown
    cumulative = (1 + avg_returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100

    return {
        "return_pct": round(total_return, 2),
        "volatility": round(volatility, 2),
        "sharpe": round(sharpe, 2),
        "max_drawdown": round(max_drawdown, 2),
    }


def get_sector_performance(close_df: pd.DataFrame, sector_filter: str = "All"):
    """Compute return % per stock, optionally filtered by sector."""
    if close_df.empty:
        return pd.DataFrame()

    returns_pct = ((close_df.iloc[-1] - close_df.iloc[0]) / close_df.iloc[0] * 100).reset_index()
    returns_pct.columns = ["Ticker", "Return (%)"]
    returns_pct["Sector"] = returns_pct["Ticker"].map(NIFTY50_STOCKS)

    if sector_filter != "All":
        returns_pct = returns_pct[returns_pct["Sector"] == sector_filter]

    return returns_pct.sort_values("Return (%)", ascending=False)


def get_correlation_matrix(close_df: pd.DataFrame) -> pd.DataFrame:
    """Compute correlation matrix of daily returns."""
    if close_df.empty or close_df.shape[1] < 2:
        return pd.DataFrame()
    return compute_returns(close_df).corr()
