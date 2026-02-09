import streamlit as st
import plotly.express as px
import yfinance as yf
import pandas as pd
if "data" not in st.session_state:
    st.session_state.data = None

if "info" not in st.session_state:
    st.session_state.info = None


@st.cache_data(ttl=300)
def get_stock_data(symbol, period):
    if ".NS" not in symbol and ".BO" not in symbol:
        symbol = symbol + ".NS"   # NSE by default

    stock = yf.Ticker(symbol)

    data = stock.history(
        period=period.lower()
    )

    info = stock.info

    return data, info


# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Capnalyx",
    page_icon="📊",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.metric-card {
    background-color:#111827;
    padding:15px;
    border-radius:12px;
    text-align:center;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("📊 Capnalyx")

    stock = st.text_input("Stock Symbol (NSE)", "TCS")

    period = st.selectbox(
        "Time Period",
        ["1Y","3Y","5Y","10Y"]
    )

    risk = st.selectbox(
        "Risk Profile",
        ["Low","Medium","High"]
    )

    mode = st.radio(
        "Analysis Mode",
        ["Basic","Advanced","Pro"]
    )

    run = st.button("Run Analysis 🚀")

    st.download_button(
        "Download Report",
        "Coming Soon"
    )
    if run:
      with st.spinner("Fetching live data... 📡"):
        data, info = get_stock_data(stock, period)

      if data.empty:
        st.error("❌ No data found. Check stock symbol.")
        st.stop()

    # Save in session
    st.session_state.data = data
    st.session_state.info = info


# ---------------- HEADER ----------------
st.title("📈 Capnalyx – Intelligent Stock Analysis")

st.caption("AI-Powered Financial Scoring & Valuation")

# Use stored data
data = st.session_state.data

if data is not None:
    latest_price = round(data["Close"].iloc[-1], 2)
else:
    st.info("👈 Enter stock and click Run Analysis")
    st.stop()


# ---------------- KPI CARDS ----------------
col1,col2,col3,col4,col5 = st.columns(5)

fair_value = round(latest_price * 1.08, 2)  # Demo valuation
upside = round((fair_value/latest_price - 1)*100, 2)

metrics = [
    ("Score","82/100"),
    ("Fair Value",f"₹{fair_value}"),
    ("Market Price",f"₹{latest_price}"),
    ("Upside",f"+{upside}%"),
    ("Risk","Medium")
]


for col,(title,val) in zip(
    [col1,col2,col3,col4,col5],metrics
):
    col.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{val}</h2>
    </div>
    """, unsafe_allow_html=True)

# ---------------- TABS ----------------
tabs = st.tabs([
    "Overview",
    "Financials",
    "Valuation",
    "Charts",
    "Risk",
    "Reports"
])

# ---------------- OVERVIEW ----------------
with tabs[0]:
    st.subheader("📌 Company Overview")

    st.write("""
    - Sector: IT Services  
    - Market Cap: ₹12T  
    - ROE: 28%  
    - Debt/Equity: 0.12  
    """)

# ---------------- FINANCIALS ----------------
with tabs[1]:
    st.subheader("📑 Financial Statements")

    st.dataframe({
        "Year":["2022","2023","2024"],
        "Revenue":[100,120,145],
        "Profit":[18,22,27]
    })

# ---------------- VALUATION ----------------
with tabs[2]:
    st.subheader("💰 Valuation Model")

    st.write("DCF & Relative Valuation")

    st.metric("Intrinsic Value","₹1240")
    st.metric("Margin of Safety","12%")

# ---------------- CHARTS ----------------
with tabs[3]:
    st.subheader("📊 Performance Chart")

    fig = px.line(
        data,
        x=data.index,
        y="Close",
        title=f"{stock.upper()} Price Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- RISK ----------------
with tabs[4]:
    st.subheader("⚠️ Risk Analysis")

    st.progress(70)

    st.write("""
    ✔ Market Risk: Medium  
    ✔ Business Risk: Low  
    ✔ Financial Risk: Low  
    ✔ Valuation Risk: Medium  
    """)

# ---------------- REPORTS ----------------
with tabs[5]:
    st.subheader("📄 Reports")

    st.write("PDF & Excel reports coming soon.")
