from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from app.scanner import scan_catalog

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
def upload_file(
    request: Request,
    scan_type: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        df = pd.read_csv(file_path)
        results = scan_catalog(df, scan_type)

        results_df = pd.DataFrame(results)
        report_path = "reports/latest_report.csv"
        results_df.to_csv(report_path, index=False)

        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "results": results,
                "filename": file.filename,
                "scan_type": scan_type
            }
        )
    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><pre>{str(e)}</pre>", status_code=500)

@app.get("/download-report")
def download_report():
    report_path = "reports/latest_report.csv"
    return FileResponse(report_path, media_type="text/csv", filename="scan_report.csv")
@app.get("/download-sample")
def download_sample():
    sample_path = "reports/sample_catalog.csv"
    return FileResponse(sample_path, media_type="text/csv", filename="sample_catalog.csv")