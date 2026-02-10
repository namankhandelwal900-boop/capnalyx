import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Capnalyx",
    page_icon="📊",
    layout="wide"
)

# ---------------- DEVELOPER PROFILE ----------------
DEV_NAME = "Naman Khandelwal"
DEV_EMAIL = "namankhandelwal900@gmail.com"
DEV_LINKEDIN = "https://www.linkedin.com/in/namankhandelwal09/"

# ---------------- DISCLAIMER ----------------
PDF_DISCLAIMER = """
This report is generated using AI models and publicly available data.
It is for informational purposes only and not financial advice.
Please consult a certified financial advisor before investing.
"""

# ---------------- CSS ----------------
st.markdown("""
<style>
.metric-card {
    background:#111827;
    padding:15px;
    border-radius:12px;
    text-align:center;
    color:white;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SCREENER SCRAPER ----------------
def get_screener_data(symbol):

    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return {}

        soup = BeautifulSoup(r.text, "html.parser")

        data = {}

        ratios = soup.select("li.flex")

        for item in ratios:
            key = item.select_one("span.name").text.strip()
            val = item.select_one("span.value").text.strip()
            data[key] = val

        return data

    except:
        return {}


# ---------------- YAHOO FETCHER ----------------
@st.cache_data(ttl=900)
def get_stock_data(symbol, period):

    ticker = symbol.upper() + ".NS"

    try:
        stock = yf.Ticker(ticker)

        data = stock.history(period=period.lower())

        if data.empty:
            return None, None

        info = stock.info

        return data, info

    except:
        return None, None


# ---------------- AI SCORE ----------------
def calculate_ai_score(data):

    returns = data["Close"].pct_change().dropna()
    volatility = returns.std()

    sma50 = data["Close"].rolling(50).mean()
    sma200 = data["Close"].rolling(200).mean()

    trend = sma50.iloc[-1] > sma200.iloc[-1]

    momentum = (data["Close"].iloc[-1] / data["Close"].iloc[-60]) - 1

    score = 50

    if returns.mean() > 0:
        score += 15

    if volatility < 0.03:
        score += 10

    if trend:
        score += 10

    if momentum > 0:
        score += 10

    return max(0, min(100, score))


# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.title("📊 Capnalyx")

    stock = st.text_input("Stock Symbol (NSE)", "TCS")

    portfolio = st.text_area(
        "📌 Portfolio",
        "TCS,INFY,ITC"
    )

    period = st.selectbox(
        "Time Period",
        ["1Y","3Y","5Y","10Y"]
    )

    mode = st.radio(
        "Analysis Mode",
        ["Basic","Advanced","Pro"]
    )

    run = st.button("Run Analysis 🚀")


# ---------------- HEADER ----------------
st.title("📈 Capnalyx – Intelligent Stock Analysis")
st.caption("📍 Data Source: Yahoo Finance + Screener.in")


# ---------------- FETCH DATA ----------------
if not run:

    st.info("👈 Enter stock and click Run Analysis")
    st.stop()


with st.spinner("Fetching data... 📡"):

    data, info = get_stock_data(stock, period)

    screener = get_screener_data(stock)


if data is None or data.empty:

    st.error("❌ Failed to fetch Yahoo data")
    st.stop()


# ---------------- BASIC VALUES ----------------
latest_price = round(float(data["Close"].iloc[-1]),2)

pe = info.get("trailingPE",0)

market_cap = info.get("marketCap",0)


# ---------------- FAIR VALUE ----------------
industry_pe = 25

if pe and pe < 200:
    fair_value = latest_price * (industry_pe/pe)
else:
    fair_value = latest_price * 1.10


# ---------------- AI SCORE ----------------
ai_score = calculate_ai_score(data)


# ---------------- KPI CARDS ----------------
upside = round((fair_value/latest_price - 1)*100,2)

cols = st.columns(5)

metrics = [
    ("Score", f"{ai_score}/100" if mode!="Basic" else "—"),
    ("Fair Value", f"₹{round(fair_value,2)}"),
    ("Market Price", f"₹{latest_price}"),
    ("Upside", f"+{upside}%"),
    ("Risk","Medium")
]

for col,(t,v) in zip(cols,metrics):

    col.markdown(f"""
    <div class="metric-card">
        <h4>{t}</h4>
        <h2>{v}</h2>
    </div>
    """, unsafe_allow_html=True)


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


# ================= OVERVIEW =================
with tabs[0]:

    st.subheader("📌 Company Overview")

    roe = screener.get("ROE","N/A")
    de = screener.get("Debt to equity","N/A")
    promoter = screener.get("Promoter holding","N/A")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Market Cap", f"₹{market_cap/1e7:.2f} Cr" if market_cap else "N/A")
    c2.metric("ROE", roe)
    c3.metric("Debt/Equity", de)
    c4.metric("Promoter Holding", promoter)

    st.divider()

    st.subheader("📄 Summary")

    st.write(info.get("longBusinessSummary","Not Available"))


# ================= FINANCIALS =================
with tabs[1]:

    st.subheader("📑 Financials (Sample)")

    st.dataframe({
        "Year":["2022","2023","2024"],
        "Revenue":[100,120,145],
        "Profit":[18,22,27]
    })


# ================= VALUATION =================
with tabs[2]:

    if mode=="Basic":
        st.warning("🔒 Upgrade Required")

    else:

        st.subheader("💰 Valuation")

        st.metric("Intrinsic Value",f"₹{round(fair_value,2)}")
        st.metric("Margin of Safety","12%")


# ================= CHARTS =================
with tabs[3]:

    st.subheader("📊 Price Chart")

    fig = px.line(
        data,
        x=data.index,
        y="Close",
        title=f"{stock.upper()} Trend"
    )

    st.plotly_chart(fig,use_container_width=True)


# ================= RISK =================
with tabs[4]:

    if mode=="Basic":
        st.warning("🔒 Upgrade Required")

    else:

        st.subheader("⚠️ Risk Analysis")

        st.progress(70)

        st.write("""
        ✔ Market Risk: Medium  
        ✔ Business Risk: Low  
        ✔ Financial Risk: Low  
        ✔ Valuation Risk: Medium
        """)


# ================= PORTFOLIO =================
with tabs[5]:

    st.subheader("💼 Portfolio")

    stocks = [x.strip() for x in portfolio.split(",")]

    if st.button("Analyze Portfolio 📊"):

        rows = []

        for s in stocks:

            d,_ = get_stock_data(s,"1Y")

            if d is None:
                continue

            price = round(d["Close"].iloc[-1],2)
            score = calculate_ai_score(d)

            ret = round((d["Close"].iloc[-1]/d["Close"].iloc[0]-1)*100,2)

            rows.append([s,price,score,ret])

        if rows:

            df = pd.DataFrame(
                rows,
                columns=["Stock","Price","Score","Return %"]
            )

            st.dataframe(df,use_container_width=True)

        else:
            st.error("No valid stocks found")


# ================= REPORTS =================
with tabs[6]:

    if mode!="Pro":
        st.warning("🔒 Pro Feature")

    else:

        st.subheader("📄 Reports")

        st.success("PDF Engine Ready (Next Phase)")


# ---------------- FOOTER ----------------
st.markdown(f"""
<div style="text-align:center;color:#9CA3AF;font-size:14px;margin-top:30px;">

Developed by <b>{DEV_NAME}</b><br>
📧 {DEV_EMAIL}<br>
🔗 <a href="{DEV_LINKEDIN}" target="_blank">LinkedIn</a>

</div>
""", unsafe_allow_html=True)
