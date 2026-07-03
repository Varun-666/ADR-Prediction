"""
Loads the trained Random Forest pipeline (ADR_Prediction_Model.pkl) and
reproduces the exact feature engineering used during training so that a raw
BookingInput can be turned into a single-row prediction.

The pipeline itself only does StandardScaler + OneHotEncoder + RandomForest,
so all engineered columns (season, total_guests, total_nights, is_family,
customer_history, weekend_stay, long_stay) must be computed here BEFORE the
row is handed to model.predict().
"""

from pathlib import Path
from functools import lru_cache

import joblib
import pandas as pd

from app.schemas import BookingInput

# Local model path
MODEL_PATH = Path(__file__).parent / "model" / "ADR_Prediction_Model.pkl"


# Month -> season mapping
MONTH_TO_SEASON = {
    "December": "Winter", "January": "Winter", "February": "Winter",
    "March": "Spring", "April": "Spring", "May": "Spring",
    "June": "Summer", "July": "Summer", "August": "Summer",
    "September": "Autumn", "October": "Autumn", "November": "Autumn",
}


NUMERIC_COLS = [
    "lead_time",
    "arrival_date_year",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "booking_changes",
    "days_in_waiting_list",
    "required_car_parking_spaces",
    "total_of_special_requests",
    "total_guests",
    "total_nights",
    "is_family",
    "customer_history",
    "weekend_stay",
    "long_stay",
]

CATEGORICAL_COLS = [
    "hotel",
    "arrival_date_month",
    "meal",
    "country",
    "market_segment",
    "distribution_channel",
    "reserved_room_type",
    "deposit_type",
    "customer_type",
    "season",
]

ALL_COLS = NUMERIC_COLS + CATEGORICAL_COLS


@lru_cache(maxsize=1)
def get_model():
    """
    Load the trained pipeline once and cache it for the lifetime
    of the application.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found at:\n{MODEL_PATH}\n\n"
            "Ensure ADR_Prediction_Model.pkl exists inside app/model/."
        )

    return joblib.load(MODEL_PATH)


def engineer_features(booking: BookingInput) -> dict:
    """Generate engineered features used during model training."""

    total_guests = booking.adults + booking.children + booking.babies
    total_nights = (
        booking.stays_in_weekend_nights +
        booking.stays_in_week_nights
    )

    is_family = int(
        booking.children > 0 or booking.babies > 0
    )

    customer_history = (
        booking.previous_cancellations +
        booking.previous_bookings_not_canceled
    )

    weekend_stay = int(
        booking.stays_in_weekend_nights > 0
    )

    long_stay = int(total_nights > 5)

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
    """Build a DataFrame matching the pipeline's expected schema."""

    engineered = engineer_features(booking)
    raw = booking.model_dump()

    row = {
        col: raw[col]
        for col in NUMERIC_COLS
        if col in raw
    }

    row.update({
        col: raw[col]
        for col in CATEGORICAL_COLS
        if col in raw
    })

    row.update(engineered)

    return pd.DataFrame([row], columns=ALL_COLS)


def predict_adr(booking: BookingInput) -> dict:
    """Predict ADR for a booking."""

    model = get_model()

    df = build_feature_row(booking)

    prediction = float(model.predict(df)[0])
    prediction = max(0.0, prediction)

    engineered = engineer_features(booking)

    return {
        "predicted_adr": round(prediction, 2),
        "season": engineered["season"],
        "total_guests": engineered["total_guests"],
        "total_nights": engineered["total_nights"],
    }