import streamlit as st
import plotly.express as px
import yfinance as yf
import pandas as pd

# ---------------- DEVELOPER PROFILE ----------------
DEV_NAME = "Naman Khandelwal"
DEV_EMAIL = "namankhandelwal900@gmail.com"
DEV_LINKEDIN = "https://www.linkedin.com/in/naman-khandelwal09/"

# ---------------- PDF DISCLAIMER ----------------
PDF_DISCLAIMER = """
Disclaimer:
This report has been generated using AI-driven models and publicly available financial data.
While reasonable efforts have been made to ensure accuracy, Capnalyx does not guarantee
the completeness or reliability of the information.

This document is intended for educational and informational purposes only and should not
be considered as financial advice. Investors are advised to conduct their own research
and consult with a qualified financial advisor before making any investment decisions.
"""


# ---------------- INDUSTRY MAP ----------------
INDUSTRY_PEERS = {
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"],
    "BANK": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK"],
    "FMCG": ["ITC", "HUL", "NESTLEIND", "DABUR"],
    "POWER": ["NTPC", "TATAPOWER", "ADANIPOWER"],
    "AUTO": ["TATAMOTORS", "M&M", "MARUTI"],
}

# ---------------- PEER SUGGESTION ----------------
def suggest_peers(stock):

    stock = stock.upper()

    for sector, peers in INDUSTRY_PEERS.items():

        if stock in peers:

            return sector, peers

    return None, []




# ---------------- SESSION STATE ----------------
if "data" not in st.session_state:
    st.session_state.data = None
if "exchange" not in st.session_state:
    st.session_state.exchange = None
    

# ---------------- DATA FETCHER ----------------
@st.cache_data(ttl=900, show_spinner=False)
def get_stock_data(symbol, period):

    symbol = symbol.upper().strip()

    tickers = [
        (symbol + ".NS", "NSE"),
        (symbol + ".BO", "BSE"),
        (symbol, "GLOBAL")
    ]

    for ticker, exch in tickers:

        try:
            stock = yf.Ticker(ticker)

            data = stock.history(
                period=period.lower(),
                auto_adjust=True,
                timeout=20
            )

            if not data.empty:
                info = stock.info
                return data, exch, info

        except Exception:
            continue

    return None, None, None





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
    portfolio = st.text_area(
    "📌 Portfolio (Comma Separated)",
    "TCS,INFY,ITC"
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

        data, exchange, info = get_stock_data(stock, period)

    if data is None or data.empty:

        st.error("❌ Yahoo Finance blocked request.")
        st.warning("Try again after 2–3 minutes.")
        st.info("Tip: Don't spam Run button.")

        st.stop()

    st.session_state.data = data
    st.session_state.exchange = exchange
    st.session_state.info = info


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
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Disclaimer", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(PDF_DISCLAIMER.replace("\n", "<br/>"), styles["Normal"]))

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
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Disclaimer ⚠️", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(PDF_DISCLAIMER.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(elements)


# ---------------- HEADER ----------------
st.title("📈 Capnalyx – Intelligent Stock Analysis")
if st.session_state.exchange:
    st.caption(f"📍 Data Source: {st.session_state.exchange}")


st.caption("AI-Powered Financial Scoring & Valuation")


# ---------------- USE STORED DATA ----------------
data = st.session_state.get("data")
info = st.session_state.get("info", {})


if data is None or not isinstance(data, pd.DataFrame) or data.empty:

    st.info("👈 Enter stock and click Run Analysis")
    st.stop()

# Safe to use now
latest_price = round(float(data["Close"].iloc[-1]), 2)
# ---------------- AI SCORE (Rule-Based) ----------------

ai_score = 50  # Base score

# Trend (Price Momentum)
returns = data["Close"].pct_change().dropna()

if returns.mean() > 0.002:
    ai_score += 15
elif returns.mean() < 0:
    ai_score -= 10

# Volatility (Risk)
volatility = returns.std()

if volatility < 0.02:
    ai_score += 10
elif volatility > 0.05:
    ai_score -= 10

# Volume Strength (if available)
if "Volume" in data.columns:
    avg_vol = data["Volume"].mean()

    if avg_vol > data["Volume"].median():
        ai_score += 5

# Valuation vs Price

pe = info.get("trailingPE", 0)
industry_pe = 25   # basic benchmark

if pe and pe > 0:
    fair_value = latest_price * (industry_pe / pe)
else:
    fair_value = latest_price * 1.05

if fair_value > latest_price:
    ai_score += 10
else:
    ai_score -= 5

# Clamp between 0–100
ai_score = max(0, min(100, ai_score))


# ---------------- KPI CARDS ----------------
col1, col2, col3, col4, col5 = st.columns(5)


upside = round((fair_value/latest_price - 1)*100,2)

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
    
    # ---------------- PORTFOLIO ENGINE ----------------
def analyze_portfolio(stocks, period):

    results = []

    for s in stocks:

        data, ex = get_stock_data(s.strip(), period)

        if data is None or data.empty:
            continue

        price = round(data["Close"].iloc[-1], 2)
        score = calculate_ai_score(data)

        ret = round(
            (data["Close"].iloc[-1] / data["Close"].iloc[0] - 1) * 100,
            2
        )

        results.append({
            "Stock": s,
            "Exchange": ex,
            "Price": price,
            "Score": score,
            "Return %": ret
        })

    return pd.DataFrame(results)



# ---------------- TABS ----------------
tabs = st.tabs([
    "Overview",
    "Financials",
    "Valuation",
    "Charts",
    "Risk",
    "Portfolio",
    "Reports"
])



# ---------------- OVERVIEW ----------------
# ---------------- OVERVIEW ----------------
with tabs[0]:

    st.subheader("📌 Company Overview")

    # Peer info
    sector, peers = suggest_peers(stock)

    if sector:
        st.success(f"🏭 Sector: {sector}")
        st.write("📊 Comparable Companies:")
        st.write(", ".join(peers))
    else:
        st.info("No peer data available")

    st.divider()

    # ---------------- REAL FUNDAMENTALS ----------------

market_cap = info.get("marketCap", 0)
roe = info.get("returnOnEquity", 0)
de_ratio = info.get("debtToEquity", 0)
promoter = info.get("heldPercentInsiders", 0)
sector_name = info.get("sector", "N/A")
summary = info.get("longBusinessSummary", "Summary not available")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Market Cap",
    f"₹{market_cap/1e7:.2f} Cr" if market_cap else "N/A"
)

col2.metric(
    "ROE",
    f"{roe*100:.2f}%" if roe else "N/A"
)

col3.metric(
    "Debt / Equity",
    f"{de_ratio:.2f}" if de_ratio else "N/A"
)

col4.metric(
    "Promoter Holding",
    f"{promoter*100:.2f}%" if promoter else "N/A"
)

st.divider()

st.subheader("📄 Business Summary")

st.write(summary)




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

# ---------------- PORTFOLIO ----------------
with tabs[5]:

    st.subheader("💼 Portfolio Tracker")

    stocks = [x.strip() for x in portfolio.split(",")]

    if st.button("Analyze Portfolio 📊"):

        df = analyze_portfolio(stocks, period)

        if df.empty:
            st.error("No valid stocks found")
        else:

            st.dataframe(df, use_container_width=True)

            st.metric(
                "Best Performer",
                df.loc[df["Return %"].idxmax()]["Stock"]
            )

            st.metric(
                "Highest Score",
                df.loc[df["Score"].idxmax()]["Stock"]
            )

with tabs[6]:

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
                st.divider()

st.markdown(f"""
<div style="
text-align:center;
color:#9CA3AF;
font-size:14px;
margin-top:20px;
">

Developed by <b>{DEV_NAME}</b><br>
📧 {DEV_EMAIL}<br>
🔗 <a href="{DEV_LINKEDIN}" target="_blank">LinkedIn Profile</a>

</div>
""", unsafe_allow_html=True)

