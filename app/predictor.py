"""
Loads the trained Random Forest pipeline (ADR_Prediction_Model.pkl) and
reproduces the exact feature engineering used during training so that a raw
BookingInput can be turned into a single-row prediction.

The pipeline itself only does StandardScaler + OneHotEncoder + RandomForest,
so all engineered columns (season, total_guests, total_nights, is_family,
customer_history, weekend_stay, long_stay) must be computed here BEFORE the
row is handed to model.predict().
"""

import os
import urllib.request
from pathlib import Path
from functools import lru_cache

import joblib
import pandas as pd

from app.schemas import BookingInput

MODEL_PATH = Path(__file__).parent / "model" / "ADR_Prediction_Model.pkl"

# If the model isn't already at MODEL_PATH (e.g. it's not committed to git
# because of its size), it gets downloaded from this URL on startup instead.
# Set this to the direct-download URL of a GitHub Release asset:
#   https://github.com/<user>/<repo>/releases/download/<tag>/ADR_Prediction_Model.pkl
MODEL_URL = os.environ.get("MODEL_URL", "")


# def _download_model():
#     MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
#     print(f"Model not found locally. Downloading from MODEL_URL to {MODEL_PATH} ...")
#     tmp_path = MODEL_PATH.with_suffix(".pkl.tmp")
#     urllib.request.urlretrieve(MODEL_URL, tmp_path)
#     tmp_path.rename(MODEL_PATH)
#     print("Model download complete.")

def _download_model():
    print("=" * 80)
    print(f"MODEL_URL: {MODEL_URL}")
    print("=" * 80)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Model not found locally. Downloading from MODEL_URL to {MODEL_PATH} ...")

    tmp_path = MODEL_PATH.with_suffix(".pkl.tmp")
    urllib.request.urlretrieve(MODEL_URL, tmp_path)
    tmp_path.rename(MODEL_PATH)

    print("Model download complete.")

# Month -> season, matching the mapping used in the training notebook.
MONTH_TO_SEASON = {
    "December": "Winter", "January": "Winter", "February": "Winter",
    "March": "Spring", "April": "Spring", "May": "Spring",
    "June": "Summer", "July": "Summer", "August": "Summer",
    "September": "Autumn", "October": "Autumn", "November": "Autumn",
}

# Exact column order the pipeline's ColumnTransformer expects.
NUMERIC_COLS = [
    "lead_time", "arrival_date_year", "arrival_date_week_number",
    "arrival_date_day_of_month", "stays_in_weekend_nights",
    "stays_in_week_nights", "adults", "children", "babies",
    "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "booking_changes",
    "days_in_waiting_list", "required_car_parking_spaces",
    "total_of_special_requests", "total_guests", "total_nights",
    "is_family", "customer_history", "weekend_stay", "long_stay",
]

CATEGORICAL_COLS = [
    "hotel", "arrival_date_month", "meal", "country", "market_segment",
    "distribution_channel", "reserved_room_type", "deposit_type",
    "customer_type", "season",
]

ALL_COLS = NUMERIC_COLS + CATEGORICAL_COLS


@lru_cache(maxsize=1)
def get_model():
    """Load the pipeline once and cache it for the lifetime of the process.

    If the file isn't present locally, fall back to downloading it from
    MODEL_URL (e.g. a GitHub Release asset) so the 461MB .pkl never has to
    be committed to git.
    """
    if not MODEL_PATH.exists():
        if MODEL_URL:
            _download_model()
        else:
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH} and no MODEL_URL env var "
                "is set to download it from. Either place ADR_Prediction_Model.pkl "
                "in app/model/, or set MODEL_URL to a direct-download link "
                "(e.g. a GitHub Release asset URL)."
            )
    return joblib.load(MODEL_PATH)


def engineer_features(booking: BookingInput) -> dict:
    """Derive the engineered features the pipeline was trained on."""
    total_guests = booking.adults + booking.children + booking.babies
    total_nights = booking.stays_in_weekend_nights + booking.stays_in_week_nights
    is_family = 1 if (booking.children > 0 or booking.babies > 0) else 0
    customer_history = booking.previous_cancellations + booking.previous_bookings_not_canceled
    weekend_stay = 1 if booking.stays_in_weekend_nights > 0 else 0
    long_stay = 1 if total_nights > 5 else 0
    season = MONTH_TO_SEASON[booking.arrival_date_month]

    return {
        "total_guests": total_guests,
        "total_nights": total_nights,
        "is_family": is_family,
        "customer_history": customer_history,
        "weekend_stay": weekend_stay,
        "long_stay": long_stay,
        "season": season,
    }


def build_feature_row(booking: BookingInput) -> pd.DataFrame:
    """Assemble a single-row DataFrame matching the pipeline's expected schema."""
    engineered = engineer_features(booking)
    raw = booking.model_dump()

    row = {col: raw[col] for col in NUMERIC_COLS if col in raw}
    row.update({col: raw[col] for col in CATEGORICAL_COLS if col in raw})
    row.update(engineered)

    df = pd.DataFrame([row], columns=ALL_COLS)
    return df


def predict_adr(booking: BookingInput) -> dict:
    """Run the full pipeline and return the prediction plus a few derived stats."""
    model = get_model()
    df = build_feature_row(booking)
    prediction = model.predict(df)[0]
    prediction = max(0.0, float(prediction))  # ADR can't be negative

    engineered = engineer_features(booking)
    return {
        "predicted_adr": round(prediction, 2),
        "season": engineered["season"],
        "total_guests": engineered["total_guests"],
        "total_nights": engineered["total_nights"],
    }
