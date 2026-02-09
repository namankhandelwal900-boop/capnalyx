import streamlit as st
import plotly.express as px

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

    stock = st.text_input("Stock Symbol", "TCS")

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

    st.button("Run Analysis 🚀")

    st.download_button(
        "Download Report",
        "Coming Soon"
    )

# ---------------- HEADER ----------------
st.title("📈 Capnalyx – Intelligent Stock Analysis")

st.caption("AI-Powered Financial Scoring & Valuation")

# ---------------- KPI CARDS ----------------
col1,col2,col3,col4,col5 = st.columns(5)

metrics = [
    ("Score","82/100"),
    ("Fair Value","₹1240"),
    ("Market Price","₹1150"),
    ("Upside","+7.8%"),
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

    data = {
        "Year":["2020","2021","2022","2023","2024"],
        "Price":[500,720,890,1020,1150]
    }

    fig = px.line(
        data,
        x="Year",
        y="Price",
        title="Stock Price Growth"
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
a
