import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, timedelta
from data import (
    NIFTY50_STOCKS, SECTORS, fetch_stock_data,
    compute_rolling_average, compute_kpis,
    get_sector_performance, get_correlation_matrix,
    get_current_prices,
)

# ── Page config ───────────────────
st.set_page_config(
    page_title="NIFTY-50 Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 NIFTY-50 Stock Analytics Dashboard")
st.caption("Live NSE data via Yahoo Finance · Refreshed every 24 hours")

# ── Sidebar controls ───────────────
with st.sidebar:
    st.header("Filters")

    sector_filter = st.selectbox("Sector", ["All"] + SECTORS)

    if sector_filter == "All":
        available_tickers = list(NIFTY50_STOCKS.keys())
    else:
        available_tickers = [t for t, s in NIFTY50_STOCKS.items() if s == sector_filter]

    selected_tickers = st.multiselect(
        "Stocks",
        options=available_tickers,
        default=available_tickers[:5],
    )

    start_date = st.date_input("Start date", value=date.today() - timedelta(days=365))
    end_date = st.date_input("End date", value=date.today())

    ma_window = st.slider("Moving average window (days)", 7, 90, 30)

# ── Guard: need at least one stock 
if not selected_tickers:
    st.warning("Please select at least one stock from the sidebar.")
    st.stop()

# Fetch data ─
with st.spinner("Fetching live data from NSE..."):
    close_df = fetch_stock_data(
        selected_tickers,
        str(start_date),
        str(end_date),
    )

if close_df.empty:
    st.warning("Unable to fetch live data. Please check your connection or try again later.")
    close_df = None

    
# Live Prices
st.subheader("Live Prices")
if close_df is not None:
    price_df = get_current_prices(selected_tickers)
    cols = st.columns(len(selected_tickers))
    for i, row in price_df.iterrows():
        cols[i].metric(
            label=row["Ticker"].replace(".NS", ""),
            value=f"₹{row['Current Price']}",
            delta=f"{row['Day Change %']}%"
        )

# KPI cards
kpis = compute_kpis(close_df) if close_df is not None else {}
st.subheader("Portfolio KPIs")
if close_df is not None:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Portfolio Return", f"{kpis['return_pct']}%",
              delta=f"{kpis['return_pct']}% since {start_date}")
    k2.metric("Annualised Volatility", f"{kpis['volatility']}%")
    k3.metric("Sharpe Ratio", f"{kpis['sharpe']}")
    k4.metric("Max Drawdown", f"{kpis['max_drawdown']}%")

st.divider()

# Price trend
st.subheader("Price Trend with Moving Average")
if close_df is not None:
    ma_df = compute_rolling_average(close_df, window=ma_window)
    fig_line = go.Figure()
    for ticker in close_df.columns:
        fig_line.add_trace(go.Scatter(
            x=close_df.index, y=close_df[ticker],
            name=ticker, mode="lines", opacity=0.6,
        ))
        fig_line.add_trace(go.Scatter(
            x=ma_df.index, y=ma_df[ticker],
            name=f"{ticker} {ma_window}d MA",
            mode="lines", line=dict(dash="dash", width=2),
        ))
    fig_line.update_layout(
        xaxis_title="Date", yaxis_title="Price (INR)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=420, margin=dict(t=10),
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# Sector performance + correlation
col1, col2 = st.columns(2)
with col1:
    st.subheader("Sector Performance")
    if close_df is not None:
        sector_df = get_sector_performance(close_df, sector_filter)
        if not sector_df.empty:
            fig_bar = px.bar(
                sector_df, x="Ticker", y="Return (%)",
                color="Return (%)",
                color_continuous_scale=["#ef4444", "#f97316", "#22c55e"],
                text_auto=".1f",
            )
            fig_bar.update_layout(height=350, margin=dict(t=10))
            st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Correlation Heatmap")
    if close_df is not None:
        corr = get_correlation_matrix(close_df)
        if not corr.empty:
            fig_corr, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn",
                        center=0, ax=ax, linewidths=0.5, annot_kws={"size": 8})
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
            plt.tight_layout()
            st.pyplot(fig_corr)

st.divider()

# Raw data
with st.expander("View raw closing prices"):
    if close_df is not None:
        st.dataframe(close_df.tail(30).style.format("{:.2f}"), use_container_width=True)
    else:
        st.info("No data available.")


