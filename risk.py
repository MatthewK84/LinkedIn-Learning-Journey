"""
Risk Parity Portfolio Builder
A Streamlit App for constructing and analyzing risk parity portfolios.
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# Page config
st.set_page_config(
    page_title="Risk Parity Portfolio Builder",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for cleaner styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    div[data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)


def generate_sample_data(tickers: list, days: int = 504) -> pd.DataFrame:
    """Generate synthetic price data when Yahoo Finance is unavailable."""
    np.random.seed(42)
    
    # Realistic parameters for common ETFs
    params = {
        "SPY": {"mu": 0.10, "sigma": 0.18},
        "TLT": {"mu": 0.04, "sigma": 0.14},
        "GLD": {"mu": 0.05, "sigma": 0.15},
        "VNQ": {"mu": 0.08, "sigma": 0.20},
        "EFA": {"mu": 0.07, "sigma": 0.17},
    }
    default_params = {"mu": 0.06, "sigma": 0.16}
    
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="B")
    prices = {}
    
    for ticker in tickers:
        p = params.get(ticker, default_params)
        daily_mu = p["mu"] / 252
        daily_sigma = p["sigma"] / np.sqrt(252)
        returns = np.random.normal(daily_mu, daily_sigma, days)
        prices[ticker] = 100 * np.exp(np.cumsum(returns))
    
    return pd.DataFrame(prices, index=dates)


@st.cache_data(ttl=3600)
def fetch_data(tickers: list, period: str = "2y") -> pd.DataFrame:
    """Fetch historical price data from Yahoo Finance with fallback."""
    import yfinance as yf
    
    period_days = {"1y": 252, "2y": 504, "3y": 756, "5y": 1260}
    
    try:
        # Use auto_adjust=True to get adjusted prices in the "Close" column
        data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
        
        # Check if download failed (empty or error)
        if data.empty:
            raise ValueError("Empty data returned")
        
        # Handle different yfinance return formats
        if isinstance(data.columns, pd.MultiIndex):
            # Multi-ticker case with MultiIndex columns
            data = data["Close"]
        elif "Close" in data.columns:
            # Single ticker or flat columns
            data = data[["Close"]]
            data.columns = tickers
        
        # Ensure DataFrame format for single ticker
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
        
        return data
        
    except Exception as e:
        error_msg = str(e).lower()
        if "rate" in error_msg or "limit" in error_msg or "too many" in error_msg or data.empty if 'data' in dir() else True:
            st.warning("⚠️ Yahoo Finance rate limit hit. Using simulated data for demonstration.")
            return generate_sample_data(tickers, period_days.get(period, 504))
        raise e


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily returns from prices."""
    returns = prices.pct_change().dropna()
    return returns


def build_risk_parity_portfolio(returns: pd.DataFrame, min_return: float = None):
    """
    Build a risk parity portfolio using Riskfolio-Lib.
    
    Returns:
        weights: DataFrame of portfolio weights
        risk_contrib: DataFrame of risk contributions
        port: Portfolio object for further analysis
    """
    import riskfolio as rp
    
    # Create portfolio object
    port = rp.Portfolio(returns=returns)
    
    # Estimate expected returns and covariance
    port.assets_stats(method_mu="hist", method_cov="hist")
    
    # Set minimum return constraint if specified
    if min_return is not None:
        port.lowerret = min_return / 252  # Convert annual to daily
    
    # Optimize for risk parity
    weights = port.rp_optimization(
        model="Classic",
        rm="MV",  # Mean-Variance risk measure
        hist=True,
        rf=0,
        b=None
    )
    
    # Calculate risk contributions
    risk_contrib = rp.RiskFunctions.Risk_Contribution(
        weights.values.flatten(),
        returns.cov().values
    )
    risk_contrib = pd.DataFrame(
        risk_contrib,
        index=returns.columns,
        columns=["Risk Contribution"]
    )
    risk_contrib["Risk Contribution %"] = risk_contrib["Risk Contribution"] / risk_contrib["Risk Contribution"].sum() * 100
    
    return weights, risk_contrib, port


def plot_weights_comparison(weights_rp, weights_constrained, title_suffix=""):
    """Create side-by-side weight comparison charts."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Pure Risk Parity Weights", "Return-Constrained Weights"),
        specs=[[{"type": "pie"}, {"type": "pie"}]]
    )
    
    # Risk parity weights
    fig.add_trace(
        go.Pie(
            labels=weights_rp.index.tolist(),
            values=weights_rp.values.flatten(),
            name="Risk Parity",
            hole=0.4,
            marker_colors=px.colors.qualitative.Set2
        ),
        row=1, col=1
    )
    
    # Constrained weights
    fig.add_trace(
        go.Pie(
            labels=weights_constrained.index.tolist(),
            values=weights_constrained.values.flatten(),
            name="Constrained",
            hole=0.4,
            marker_colors=px.colors.qualitative.Set2
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text=f"Portfolio Weights Comparison{title_suffix}",
        height=400,
        showlegend=True
    )
    
    return fig


def plot_risk_contributions(risk_rp, risk_constrained):
    """Create bar chart comparing risk contributions."""
    fig = go.Figure()
    
    tickers = risk_rp.index.tolist()
    
    fig.add_trace(go.Bar(
        name="Pure Risk Parity",
        x=tickers,
        y=risk_rp["Risk Contribution %"].values,
        marker_color="#3b82f6"
    ))
    
    fig.add_trace(go.Bar(
        name="Return-Constrained",
        x=tickers,
        y=risk_constrained["Risk Contribution %"].values,
        marker_color="#f97316"
    ))
    
    fig.update_layout(
        title="Risk Contributions by Asset",
        xaxis_title="Asset",
        yaxis_title="Risk Contribution (%)",
        barmode="group",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add equal contribution reference line
    equal_contrib = 100 / len(tickers)
    fig.add_hline(
        y=equal_contrib,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Equal ({equal_contrib:.1f}%)"
    )
    
    return fig


def plot_single_portfolio(weights, risk_contrib, title="Portfolio"):
    """Create visualization for a single portfolio."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"{title} - Weights", f"{title} - Risk Contributions"),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Weights pie chart
    fig.add_trace(
        go.Pie(
            labels=weights.index.tolist(),
            values=weights.values.flatten(),
            hole=0.4,
            marker_colors=px.colors.qualitative.Set2,
            textinfo="label+percent"
        ),
        row=1, col=1
    )
    
    # Risk contributions bar chart
    fig.add_trace(
        go.Bar(
            x=risk_contrib.index.tolist(),
            y=risk_contrib["Risk Contribution %"].values,
            marker_color=px.colors.qualitative.Set2[:len(risk_contrib)],
            text=[f"{v:.1f}%" for v in risk_contrib["Risk Contribution %"].values],
            textposition="outside"
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    return fig


def calculate_portfolio_metrics(returns: pd.DataFrame, weights: pd.DataFrame) -> dict:
    """Calculate key portfolio metrics."""
    w = weights.values.flatten()
    
    # Portfolio returns
    port_returns = returns @ w
    
    # Annualized return
    ann_return = port_returns.mean() * 252
    
    # Annualized volatility
    ann_vol = port_returns.std() * np.sqrt(252)
    
    # Sharpe ratio (assuming 0 risk-free rate)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    
    # Maximum drawdown
    cum_returns = (1 + port_returns).cumprod()
    rolling_max = cum_returns.expanding().max()
    drawdowns = cum_returns / rolling_max - 1
    max_dd = drawdowns.min()
    
    return {
        "Annual Return": ann_return,
        "Annual Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd
    }


# ============== MAIN APP ==============

# Header
st.markdown('<p class="main-header">📊 Risk Parity Portfolio Builder</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Build portfolios where each asset contributes equally to total risk</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Ticker input
    st.subheader("Asset Universe")
    default_tickers = "SPY, TLT, GLD, VNQ, EFA"
    ticker_input = st.text_input(
        "Enter tickers (comma-separated)",
        value=default_tickers,
        help="Enter stock/ETF tickers separated by commas"
    )
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    
    # Data period
    st.subheader("Historical Data")
    period = st.selectbox(
        "Lookback period",
        options=["1y", "2y", "3y", "5y"],
        index=1,
        help="Historical data period for estimating covariance"
    )
    
    # Return constraint
    st.subheader("Return Constraint")
    use_constraint = st.checkbox(
        "Add minimum return constraint",
        value=True,
        help="Force the portfolio to target a minimum expected return"
    )
    
    if use_constraint:
        min_return_pct = st.slider(
            "Minimum annual return (%)",
            min_value=0.0,
            max_value=20.0,
            value=8.0,
            step=0.5,
            help="Target minimum annual return (may break equal risk contribution)"
        )
        min_return = min_return_pct / 100
    else:
        min_return = None
    
    st.divider()
    
    # Run button
    run_analysis = st.button("🚀 Build Portfolio", type="primary", use_container_width=True)

# Main content area
if len(tickers) < 2:
    st.warning("Please enter at least 2 tickers to build a portfolio.")
    st.stop()

if run_analysis or "results" in st.session_state:
    
    with st.spinner("Fetching market data..."):
        try:
            prices = fetch_data(tickers, period)
            returns = calculate_returns(prices)
            
            if returns.empty or len(returns) < 30:
                st.error("Insufficient data. Please check your tickers or try a longer period.")
                st.stop()
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.stop()
    
    with st.spinner("Building risk parity portfolio..."):
        try:
            # Pure risk parity
            weights_rp, risk_rp, port_rp = build_risk_parity_portfolio(returns, min_return=None)
            
            # Constrained portfolio (if enabled)
            if use_constraint and min_return:
                weights_con, risk_con, port_con = build_risk_parity_portfolio(returns, min_return=min_return)
            else:
                weights_con, risk_con = weights_rp.copy(), risk_rp.copy()
            
            # Store in session state
            st.session_state["results"] = {
                "returns": returns,
                "weights_rp": weights_rp,
                "risk_rp": risk_rp,
                "weights_con": weights_con,
                "risk_con": risk_con,
                "use_constraint": use_constraint
            }
            
        except Exception as e:
            st.error(f"Optimization error: {str(e)}")
            st.stop()

# Display results
if "results" in st.session_state:
    results = st.session_state["results"]
    returns = results["returns"]
    weights_rp = results["weights_rp"]
    risk_rp = results["risk_rp"]
    weights_con = results["weights_con"]
    risk_con = results["risk_con"]
    
    # Key insight callout
    st.info("""
    **💡 Key Insight:** Risk parity ensures each asset contributes equally to portfolio risk, 
    not just equal dollar weights. Adding a return constraint typically breaks this equality—
    the visualization below shows you exactly how.
    """)
    
    # Metrics row
    st.subheader("📈 Portfolio Metrics")
    
    metrics_rp = calculate_portfolio_metrics(returns, weights_rp)
    metrics_con = calculate_portfolio_metrics(returns, weights_con)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Annual Return (RP)",
            f"{metrics_rp['Annual Return']:.1%}",
            delta=f"{(metrics_con['Annual Return'] - metrics_rp['Annual Return']):.1%}" if results["use_constraint"] else None
        )
    with col2:
        st.metric(
            "Annual Volatility (RP)",
            f"{metrics_rp['Annual Volatility']:.1%}",
            delta=f"{(metrics_con['Annual Volatility'] - metrics_rp['Annual Volatility']):.1%}" if results["use_constraint"] else None,
            delta_color="inverse"
        )
    with col3:
        st.metric(
            "Sharpe Ratio (RP)",
            f"{metrics_rp['Sharpe Ratio']:.2f}",
            delta=f"{(metrics_con['Sharpe Ratio'] - metrics_rp['Sharpe Ratio']):.2f}" if results["use_constraint"] else None
        )
    with col4:
        st.metric(
            "Max Drawdown (RP)",
            f"{metrics_rp['Max Drawdown']:.1%}",
            delta=f"{(metrics_con['Max Drawdown'] - metrics_rp['Max Drawdown']):.1%}" if results["use_constraint"] else None,
            delta_color="inverse"
        )
    
    st.divider()
    
    # Visualizations
    if results["use_constraint"]:
        # Comparison view
        st.subheader("⚖️ Weights Comparison")
        fig_weights = plot_weights_comparison(weights_rp, weights_con)
        st.plotly_chart(fig_weights, use_container_width=True)
        
        st.subheader("📊 Risk Contribution Analysis")
        fig_risk = plot_risk_contributions(risk_rp, risk_con)
        st.plotly_chart(fig_risk, use_container_width=True)
        
        st.caption("""
        The dashed line shows equal risk contribution. In pure risk parity, all bars should 
        align with this line. When you add a return constraint, the optimizer must deviate 
        from equal risk to chase higher expected returns.
        """)
        
    else:
        # Single portfolio view
        st.subheader("📊 Risk Parity Portfolio")
        fig_single = plot_single_portfolio(weights_rp, risk_rp, "Pure Risk Parity")
        st.plotly_chart(fig_single, use_container_width=True)
    
    # Detailed tables
    st.divider()
    st.subheader("📋 Detailed Allocations")
    
    tab1, tab2 = st.tabs(["Pure Risk Parity", "Return-Constrained"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Weights**")
            weights_display = weights_rp.copy()
            weights_display.columns = ["Weight"]
            weights_display["Weight %"] = weights_display["Weight"] * 100
            st.dataframe(
                weights_display.style.format({"Weight": "{:.4f}", "Weight %": "{:.2f}%"}),
                use_container_width=True
            )
        with col2:
            st.write("**Risk Contributions**")
            st.dataframe(
                risk_rp.style.format({
                    "Risk Contribution": "{:.6f}",
                    "Risk Contribution %": "{:.2f}%"
                }),
                use_container_width=True
            )
    
    with tab2:
        if results["use_constraint"]:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Weights**")
                weights_display = weights_con.copy()
                weights_display.columns = ["Weight"]
                weights_display["Weight %"] = weights_display["Weight"] * 100
                st.dataframe(
                    weights_display.style.format({"Weight": "{:.4f}", "Weight %": "{:.2f}%"}),
                    use_container_width=True
                )
            with col2:
                st.write("**Risk Contributions**")
                st.dataframe(
                    risk_con.style.format({
                        "Risk Contribution": "{:.6f}",
                        "Risk Contribution %": "{:.2f}%"
                    }),
                    use_container_width=True
                )
        else:
            st.info("Enable the return constraint in the sidebar to see the comparison.")

# Educational footer
with st.expander("📚 About Risk Parity"):
    st.markdown("""
    ### What is Risk Parity?
    
    Risk parity is a portfolio construction method that sizes positions so each asset 
    contributes equally to total portfolio risk. Unlike equal-weight portfolios (where 
    each asset gets the same dollar allocation), risk parity accounts for the fact that 
    different assets have different volatilities and correlations.
    
    ### Why It Matters
    
    - **Diversification**: Having 10 stocks doesn't mean you're diversified if one 
      volatile stock drives 50% of your portfolio's variance.
    - **Interpretable Backtests**: When each asset contributes equally to risk, your 
      backtest results reflect your signals, not accidental concentration.
    - **Explicit Tradeoffs**: Adding return constraints shows you how much risk 
      equality you're sacrificing to chase higher returns.
    
    ### The Math
    
    For a portfolio with weights $w$ and covariance matrix $\\Sigma$, the risk contribution 
    of asset $i$ is:
    
    $$RC_i = w_i \\cdot (\\Sigma w)_i$$
    
    Risk parity finds weights where all $RC_i$ values are equal.
    
    ### References
    
    - Qian, E. (2005). "Risk Parity Portfolios"
    - Maillard, S., Roncalli, T., & Teïletche, J. (2010). "The Properties of Equally Weighted Risk Contribution Portfolios"
    """)

# Footer
st.divider()
st.caption("Built with Streamlit • Data from Yahoo Finance • Optimization via Riskfolio-Lib")
