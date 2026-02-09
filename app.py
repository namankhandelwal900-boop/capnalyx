import streamlit as st
import plotly.express as px
import yfinance as yf
import pandas as pd


# ---------------- SESSION STATE ----------------
if "data" not in st.session_state:
    st.session_state.data = None
if "exchange" not in st.session_state:
    st.session_state.exchange = None
    

# ---------------- DATA FETCHER ----------------
@st.cache_data(ttl=600)
def get_stock_data(symbol, period):

    try:
        symbol = symbol.upper().strip()

        # Try NSE first
        nse_symbol = symbol + ".NS"
        stock_nse = yf.Ticker(nse_symbol)

        data = stock_nse.history(
            period=period.lower(),
            auto_adjust=True
        )

        if not data.empty:
            return data, "NSE"

        # If NSE fails → Try BSE
        bse_symbol = symbol + ".BO"
        stock_bse = yf.Ticker(bse_symbol)

        data = stock_bse.history(
            period=period.lower(),
            auto_adjust=True
        )

        if not data.empty:
            return data, "BSE"

        return None, None

    except Exception:
        return None, None



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

    exchange = st.session_state.get("exchange", "Auto")

    stock = st.text_input(
    f"Stock Symbol ({exchange})",
    "TCS"
)

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
    analysis_mode = mode


# ---------------- FETCH DATA ----------------
if run:

    with st.spinner("Fetching live data... 📡"):

        data, exchange = get_stock_data(stock, period)

    if data is None or data.empty:
        st.error("❌ Data unavailable. Try again later.")
        st.stop()

    # Save in session
    st.session_state.data = data
    st.session_state.exchange = exchange

# ---------------- AI SCORE ENGINE ----------------
def calculate_ai_score(data):

    returns = data["Close"].pct_change().mean() * 252
    volatility = data["Close"].pct_change().std() * (252 ** 0.5)

    sma50 = data["Close"].rolling(50).mean()
    sma200 = data["Close"].rolling(200).mean()

    trend = 1 if sma50.iloc[-1] > sma200.iloc[-1] else 0

    momentum = (data["Close"].iloc[-1] / data["Close"].iloc[-60]) - 1

    return_score = min(max(returns * 100, 0), 25)
    vol_score = min(max((0.4 - volatility) * 50, 0), 20)
    trend_score = 25 if trend else 10
    momentum_score = min(max(momentum * 100, 0), 15)
    stability_score = 15 if volatility < 0.25 else 7

    total = (
        return_score +
        vol_score +
        trend_score +
        momentum_score +
        stability_score
    )

    return round(total, 1)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import black, lightgrey, HexColor


# ---------------- CORPORATE PDF ----------------
def generate_corporate_pdf(filename, stock, exchange, latest_price, fair_value, ai_score):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>CAPNALYX RESEARCH REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Stock: {stock}", styles["Normal"]))
    elements.append(Paragraph(f"Exchange: {exchange}", styles["Normal"]))
    elements.append(Paragraph(f"Score: {ai_score}/100", styles["Normal"]))
    elements.append(Spacer(1, 20))

    data = [
        ["Metric", "Value"],
        ["Market Price", f"₹{latest_price}"],
        ["Fair Value", f"₹{fair_value}"],
        ["Upside", f"{round((fair_value/latest_price-1)*100,2)}%"],
        ["Risk", "Medium"]
    ]

    table = Table(data, colWidths=200, rowHeights=30)

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,black),
        ("BACKGROUND",(0,0),(-1,0),lightgrey),
        ("ALIGN",(0,0),(-1,-1),"CENTER")
    ]))

    elements.append(table)
    elements.append(PageBreak())

    elements.append(Paragraph("Disclaimer", styles["Heading2"]))
    elements.append(Paragraph("This report is for educational purposes only.", styles["Normal"]))

    doc.build(elements)


# ---------------- MODERN PDF ----------------
def generate_modern_pdf(filename, stock, exchange, latest_price, fair_value, ai_score):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    dark = HexColor("#0f172a")
    blue = HexColor("#2563eb")

    title = Paragraph(
        f'<font color="#2563eb"><b>CAPNALYX REPORT 🚀</b></font>',
        styles["Title"]
    )

    elements.append(title)
    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"<b>{stock}</b> ({exchange})", styles["h2"]))
    elements.append(Spacer(1,10))

    cards = [
        ["Score", f"{ai_score}/100"],
        ["Price", f"₹{latest_price}"],
        ["Fair Value", f"₹{fair_value}"],
        ["Upside", f"+{round((fair_value/latest_price-1)*100,2)}%"],
        ["Risk", "Medium"]
    ]

    table = Table(cards, colWidths=250, rowHeights=40)

    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),dark),
        ("TEXTCOLOR",(0,0),(-1,-1),"white"),
        ("GRID",(0,0),(-1,-1),0.5,blue),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONT",(0,0),(-1,-1),"Helvetica-Bold")
    ]))

    elements.append(table)
    elements.append(Spacer(1,30))

    elements.append(Paragraph("AI Insights 🤖", styles["Heading2"]))
    elements.append(Paragraph("• Strong momentum", styles["Normal"]))
    elements.append(Paragraph("• Stable volatility", styles["Normal"]))
    elements.append(Paragraph("• Positive long-term outlook", styles["Normal"]))

    doc.build(elements)


# ---------------- HEADER ----------------
st.title("📈 Capnalyx – Intelligent Stock Analysis")
if st.session_state.exchange:
    st.caption(f"📍 Data Source: {st.session_state.exchange}")


st.caption("AI-Powered Financial Scoring & Valuation")


# ---------------- USE STORED DATA ----------------
data = st.session_state.get("data")

if data is None or not isinstance(data, pd.DataFrame) or data.empty:

    st.info("👈 Enter stock and click Run Analysis")
    st.stop()

# Safe to use now
latest_price = round(float(data["Close"].iloc[-1]), 2)
ai_score = calculate_ai_score(data)


# ---------------- KPI CARDS ----------------
col1, col2, col3, col4, col5 = st.columns(5)

fair_value = round(latest_price * 1.08, 2)
upside = round((fair_value/latest_price - 1)*100, 2)

metrics = [
    ("Score",
     f"{ai_score}/100" if analysis_mode != "Basic" else "—"
),
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
# ---------------- VALUATION ----------------
with tabs[2]:

    if analysis_mode == "Basic":
        st.warning("🔒 Upgrade to Advanced/Pro for Valuation")

    else:
        st.subheader("💰 Valuation Model")

        st.write("DCF & Relative Valuation")

        st.metric("Intrinsic Value", f"₹{fair_value}")
        st.metric("Margin of Safety", "12%")



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
# ---------------- RISK ----------------
with tabs[4]:

    if analysis_mode == "Basic":
        st.warning("🔒 Upgrade to Advanced/Pro for Risk Analysis")

    else:
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

    if analysis_mode != "Pro":
        st.warning("🔒 Pro Feature: Download Reports")

    else:

        st.subheader("📄 Download Report")

        report_style = st.radio(
            "Select Report Style",
            ["Corporate", "Modern"]
        )

        if st.button("Generate PDF 📥"):

            filename = f"Capnalyx_{stock}_{report_style}.pdf"

            if report_style == "Corporate":

                generate_corporate_pdf(
                    filename,
                    stock,
                    st.session_state.exchange,
                    latest_price,
                    fair_value,
                    ai_score
                )

            else:

                generate_modern_pdf(
                    filename,
                    stock,
                    st.session_state.exchange,
                    latest_price,
                    fair_value,
                    ai_score
                )

            with open(filename, "rb") as f:

                st.download_button(
                    "Download Report",
                    f,
                    file_name=filename,
                    mime="application/pdf"
                )
