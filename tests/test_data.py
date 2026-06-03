import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock
from data import (
    compute_returns,
    compute_rolling_average,
    compute_kpis,
    get_sector_performance,
    get_correlation_matrix,
    NIFTY50_STOCKS,
)

#Fixtures

@pytest.fixture
def sample_close():
    """Realistic sample closing price dataframe for 3 stocks over 60 days."""
    dates = pd.date_range(start="2024-01-01", periods=60, freq="B")
    np.random.seed(42)
    return pd.DataFrame({
        "TCS.NS":       1000 + np.cumsum(np.random.randn(60) * 10),
        "INFY.NS":      800  + np.cumsum(np.random.randn(60) * 8),
        "HDFCBANK.NS":  600  + np.cumsum(np.random.randn(60) * 6),
    }, index=dates)


@pytest.fixture
def empty_df():
    return pd.DataFrame()


@pytest.fixture
def single_stock(sample_close):
    return sample_close[["TCS.NS"]]

# Live prices
class TestGetCurrentPrices:
    def test_returns_dataframe(self):
        """Should return a DataFrame with correct columns."""
        mock_info = MagicMock()
        mock_info.last_price = 3500.0
        mock_info.previous_close = 3450.0

        with patch("data.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = mock_info
            result = get_current_prices(["TCS.NS"])

        assert isinstance(result, pd.DataFrame)
        assert "Ticker" in result.columns
        assert "Current Price" in result.columns
        assert "Day Change %" in result.columns

    def test_price_is_positive(self):
        """Stock prices should always be positive."""
        mock_info = MagicMock()
        mock_info.last_price = 3500.0
        mock_info.previous_close = 3450.0

        with patch("data.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = mock_info
            result = get_current_prices(["TCS.NS"])

        assert (result["Current Price"] > 0).all()

    def test_multiple_tickers(self):
        """Should return one row per ticker."""
        mock_info = MagicMock()
        mock_info.last_price = 3500.0
        mock_info.previous_close = 3450.0

        with patch("data.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = mock_info
            tickers = ["TCS.NS", "INFY.NS", "HDFCBANK.NS"]
            result = get_current_prices(tickers)

        assert len(result) == len(tickers)

#compute_returns

class TestComputeReturns:
    def test_shape(self, sample_close): 
        result = compute_returns(sample_close)
        assert result.shape[1] == sample_close.shape[1]
        assert len(result) == len(sample_close) - 1  # first row dropped (NaN)

    def test_returns_are_fractions(self, sample_close):
        result = compute_returns(sample_close)
        assert (result.abs() < 1).all().all(), "Returns should be small fractions, not %"

    def test_empty_input(self, empty_df):
        result = compute_returns(empty_df)
        assert result.empty

    def test_correct_calculation(self):
        """Manually verify return calculation."""
        df = pd.DataFrame({"A": [100.0, 110.0, 99.0]})
        result = compute_returns(df)
        assert abs(result["A"].iloc[0] - 0.10) < 1e-6   # 10% gain
        assert abs(result["A"].iloc[1] + 0.10) < 1e-6  # 10% loss


# ── compute_rolling_average ─────────────────────────────────────────────────────

class TestComputeRollingAverage:
    def test_shape_preserved(self, sample_close):
        result = compute_rolling_average(sample_close, window=7)
        assert result.shape == sample_close.shape

    def test_first_rows_are_nan(self, sample_close):
        window = 7
        result = compute_rolling_average(sample_close, window=window)
        assert result.iloc[:window - 1].isna().all().all()

    def test_empty_input(self, empty_df):
        result = compute_rolling_average(empty_df, window=7)
        assert result.empty

    def test_window_30_default(self, sample_close):
        result = compute_rolling_average(sample_close)
        assert result.iloc[:29].isna().all().all()
        assert result.iloc[29].notna().all()


# ── compute_kpis ────────────────────────────────────────────────────────────────

class TestComputeKpis:
    def test_returns_dict_with_correct_keys(self, sample_close):
        kpis = compute_kpis(sample_close)
        assert set(kpis.keys()) == {"return_pct", "volatility", "sharpe", "max_drawdown"}

    def test_all_values_are_numbers(self, sample_close):
        kpis = compute_kpis(sample_close)
        for key, val in kpis.items():
            assert isinstance(val, (int, float)), f"{key} should be numeric"

    def test_volatility_is_positive(self, sample_close):
        kpis = compute_kpis(sample_close)
        assert kpis["volatility"] >= 0

    def test_max_drawdown_is_non_positive(self, sample_close):
        kpis = compute_kpis(sample_close)
        assert kpis["max_drawdown"] <= 0

    def test_empty_returns_zero_kpis(self, empty_df):
        kpis = compute_kpis(empty_df)
        assert kpis == {"return_pct": 0, "volatility": 0, "sharpe": 0, "max_drawdown": 0}

    def test_steadily_rising_stock_has_positive_return(self):
        dates = pd.date_range("2024-01-01", periods=30, freq="B")
        df = pd.DataFrame({"A.NS": [100 + i for i in range(30)]}, index=dates)
        kpis = compute_kpis(df)
        assert kpis["return_pct"] > 0


# ── get_sector_performance ──────────────────────────────────────────────────────

class TestGetSectorPerformance:
    def test_columns_present(self, sample_close):
        result = get_sector_performance(sample_close, "All")
        assert "Ticker" in result.columns
        assert "Return (%)" in result.columns
        assert "Sector" in result.columns

    def test_sector_filter(self, sample_close):
        result = get_sector_performance(sample_close, "IT")
        assert result["Sector"].unique().tolist() == ["IT"]

    def test_empty_input(self, empty_df):
        result = get_sector_performance(empty_df, "All")
        assert result.empty

    def test_sorted_descending(self, sample_close):
        result = get_sector_performance(sample_close, "All")
        returns = result["Return (%)"].tolist()
        assert returns == sorted(returns, reverse=True)


# ── get_correlation_matrix ──────────────────────────────────────────────────────

class TestGetCorrelationMatrix:
    def test_symmetric(self, sample_close):
        corr = get_correlation_matrix(sample_close)
        pd.testing.assert_frame_equal(corr, corr.T)

    def test_diagonal_is_one(self, sample_close):
        corr = get_correlation_matrix(sample_close)
        for col in corr.columns:
            assert abs(corr.loc[col, col] - 1.0) < 1e-6

    def test_values_between_minus_one_and_one(self, sample_close):
        corr = get_correlation_matrix(sample_close)
        assert (corr >= -1).all().all()
        assert (corr <= 1).all().all()

    def test_empty_input(self, empty_df):
        corr = get_correlation_matrix(empty_df)
        assert corr.empty

    def test_single_stock_returns_empty(self, single_stock):
        corr = get_correlation_matrix(single_stock)
        assert corr.empty


# ── NIFTY50_STOCKS integrity ────────────────────────────────────────────────────

class TestStockMapping:
    def test_all_tickers_end_with_ns(self):
        for ticker in NIFTY50_STOCKS:
            assert ticker.endswith(".NS"), f"{ticker} missing .NS suffix"

    def test_all_have_sectors(self):
        for ticker, sector in NIFTY50_STOCKS.items():
            assert isinstance(sector, str) and len(sector) > 0
