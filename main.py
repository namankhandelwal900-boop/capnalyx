from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import black, lightgrey
from fastapi.responses import FileResponse
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pandas as pd
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)


@app.get("/")
def home():
    return {"message": "Welcome to Capnalyx API"}


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):

    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(BASE_DIR, "data", "latest.csv")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {
        "status": "Uploaded Successfully",
        "file": "latest.csv"
    }
from fastapi.responses import RedirectResponse


from datetime import datetime


@app.post("/upload-ui")
async def upload_ui(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"startup_{timestamp}.csv"

    save_path = os.path.join(BASE_DIR, "data", filename)

    df.to_csv(save_path, index=False)

    return RedirectResponse(
        url=f"/dashboard?file={filename}",
        status_code=302
    )




# ---------------- ANALYSIS ENGINE ---------------- #

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    # Unit Economics
    df["runway_months"] = df["cash"] / df["burn_rate"]
    df["ltv_cac"] = df["ltv"] / df["cac"]
    df["margin"] = (df["revenue"] - df["burn_rate"]) / df["revenue"]

    # Revenue Metrics
    df["mrr"] = df["users"] * df["monthly_price"]
    df["arr"] = df["mrr"] * 12

    # Burn
    df["burn"] = df["burn_rate"] - df["revenue"]

    # Valuation (Simple SaaS multiple)
    def valuation(row):

        multiple = 5

        if row["growth"] > 15:
            multiple = 12
        elif row["growth"] > 8:
            multiple = 8

        return row["arr"] * multiple

    df["valuation"] = df.apply(valuation, axis=1)

    # Scoring
    def score(row):

        s = 0

        if row["runway_months"] > 12: s += 20
        if row["ltv_cac"] > 3: s += 20
        if row["growth"] > 7: s += 20
        if row["margin"] > 0: s += 20
        if row["mrr"] > 200000: s += 20

        return s

    df["investment_score"] = df.apply(score, axis=1)

    # Rank
    df["rank"] = df["investment_score"].rank(
        ascending=False
    ).astype(int)

    # Recommendation
    def recommend(row):

        if row["investment_score"] >= 80:
            return "INVEST"
        if row["investment_score"] >= 55:
            return "MONITOR"
        return "REJECT"

    df["recommendation"] = df.apply(recommend, axis=1)

    return df.sort_values("rank").to_dict(orient="records")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    file_name = request.query_params.get("file")

    if not file_name:
       return HTMLResponse("No file selected", status_code=400)

    csv_path = os.path.join(BASE_DIR, "data", file_name)

    if not os.path.exists(csv_path):
       return HTMLResponse("File not found", status_code=404)

    df = pd.read_csv(csv_path)


    # ---------- Calculations ---------- #

    df["runway_months"] = df["cash"] / df["burn_rate"]
    df["ltv_cac"] = df["ltv"] / df["cac"]
    df["margin"] = (df["revenue"] - df["burn_rate"]) / df["revenue"]

    df["mrr"] = df["users"] * df["monthly_price"]
    df["arr"] = df["mrr"] * 12

    # Valuation
    def valuation(row):
        multiple = 5

        if row["growth"] > 15:
            multiple = 12
        elif row["growth"] > 8:
            multiple = 8

        return row["arr"] * multiple

    df["valuation"] = df.apply(valuation, axis=1)

    # Score
    def score(row):
        s = 0

        if row["runway_months"] > 12: s += 20
        if row["ltv_cac"] > 3: s += 20
        if row["growth"] > 7: s += 20
        if row["margin"] > 0: s += 20
        if row["mrr"] > 200000: s += 20

        return s

    df["investment_score"] = df.apply(score, axis=1)

    # Rank
    df["rank"] = df["investment_score"].rank(
        ascending=False
    ).astype(int)

    # Recommendation
    def recommend(row):

        if row["investment_score"] >= 80:
            return "INVEST"
        elif row["investment_score"] >= 55:
            return "MONITOR"
        else:
            return "REJECT"

    df["recommendation"] = df.apply(recommend, axis=1)

    data = df.to_dict(orient="records")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": data
        }
    )
@app.get("/download-report")
async def download_report(file: str):

    csv_path = os.path.join(BASE_DIR, "data", file)

    if not os.path.exists(csv_path):
        return {"error": "File not found"}

    df = pd.read_csv(csv_path)

    # Recalculate (same as dashboard)
    df["runway_months"] = df["cash"] / df["burn_rate"]
    df["ltv_cac"] = df["ltv"] / df["cac"]
    df["margin"] = (df["revenue"] - df["burn_rate"]) / df["revenue"]

    df["mrr"] = df["users"] * df["monthly_price"]
    df["arr"] = df["mrr"] * 12

    def valuation(row):
        multiple = 5
        if row["growth"] > 15: multiple = 12
        elif row["growth"] > 8: multiple = 8
        return row["arr"] * multiple

    df["valuation"] = df.apply(valuation, axis=1)

    def score(row):
        s = 0
        if row["runway_months"] > 12: s += 20
        if row["ltv_cac"] > 3: s += 20
        if row["growth"] > 7: s += 20
        if row["margin"] > 0: s += 20
        if row["mrr"] > 200000: s += 20
        return s

    df["investment_score"] = df.apply(score, axis=1)

    df["rank"] = df["investment_score"].rank(ascending=False).astype(int)

    def recommend(row):
        if row["investment_score"] >= 80:
            return "INVEST"
        elif row["investment_score"] >= 55:
            return "MONITOR"
        return "REJECT"

    df["recommendation"] = df.apply(recommend, axis=1)

    # ---------- Build PDF ---------- #

    report_name = f"Capnalyx_Report_{file}.pdf"
    report_path = os.path.join(BASE_DIR, "data", report_name)

    doc = SimpleDocTemplate(report_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Capnalyx Investment Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    table_data = [
        ["Startup", "Score", "Rank", "Runway", "LTV/CAC", "MRR", "Valuation", "Decision"]
    ]

    for _, row in df.iterrows():

        table_data.append([
            row["name"],
            row["investment_score"],
            row["rank"],
            round(row["runway_months"], 1),
            round(row["ltv_cac"], 2),
            int(row["mrr"]),
            int(row["valuation"]),
            row["recommendation"]
        ])

    table = Table(table_data, colWidths=70)

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, black),
        ("BACKGROUND", (0,0), (-1,0), lightgrey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    elements.append(table)

    doc.build(elements)

    return FileResponse(
        report_path,
        filename=report_name,
        media_type="application/pdf"
    )

