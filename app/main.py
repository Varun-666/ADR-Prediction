"""
FastAPI backend for the ADR Prediction System.

Routes:
    GET  /            -> Home page (booking form UI)
    POST /predict      -> Accepts BookingInput JSON, returns PredictionResponse
    GET  /health        -> Simple liveness check for Render
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.schemas import BookingInput, PredictionResponse
from app.predictor import predict_adr, get_model

BASE_DIR = Path(__file__).parent

app = FastAPI(
    title="ADR Prediction System",
    description="Predicts Hotel Average Daily Rate (ADR) from booking details using a trained Random Forest model.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def load_model_on_startup():
    # Warm the model cache so the first real request isn't slow.
    get_model()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(booking: BookingInput):
    try:
        result = predict_adr(booking)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")
    return result
