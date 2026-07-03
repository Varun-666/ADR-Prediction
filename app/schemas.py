"""
Pydantic schemas for the ADR Prediction API.

BookingInput mirrors the raw booking fields collected from the user (or a
front-desk system) *before* feature engineering. predictor.py is responsible
for deriving season / total_guests / total_nights / is_family /
customer_history / weekend_stay / long_stay from these raw fields before
handing the row to the trained pipeline.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal

# Exact category values the model's OneHotEncoder was fit on.
HOTEL_VALUES = ("City Hotel", "Resort Hotel")
MEAL_VALUES = ("BB", "FB", "HB", "SC", "Undefined")
MARKET_SEGMENT_VALUES = (
    "Aviation", "Complementary", "Corporate", "Direct",
    "Groups", "Offline TA/TO", "Online TA", "Undefined",
)
DISTRIBUTION_CHANNEL_VALUES = ("Corporate", "Direct", "GDS", "TA/TO", "Undefined")
RESERVED_ROOM_TYPE_VALUES = ("A", "B", "C", "D", "E", "F", "G", "H", "L", "P")
DEPOSIT_TYPE_VALUES = ("No Deposit", "Non Refund", "Refundable")
CUSTOMER_TYPE_VALUES = ("Contract", "Group", "Transient", "Transient-Party")
MONTH_VALUES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


class BookingInput(BaseModel):
    hotel: Literal[HOTEL_VALUES] = Field(..., description="Hotel type")

    lead_time: int = Field(..., ge=0, le=800, description="Days between booking and arrival")
    arrival_date_year: int = Field(..., ge=2015, le=2035)
    arrival_date_month: Literal[MONTH_VALUES]
    arrival_date_week_number: int = Field(..., ge=1, le=53)
    arrival_date_day_of_month: int = Field(..., ge=1, le=31)

    stays_in_weekend_nights: int = Field(..., ge=0, le=20)
    stays_in_week_nights: int = Field(..., ge=0, le=40)

    adults: int = Field(..., ge=0, le=10)
    children: int = Field(0, ge=0, le=10)
    babies: int = Field(0, ge=0, le=10)

    meal: Literal[MEAL_VALUES] = "BB"
    country: str = Field(..., description="ISO 3166-1 alpha-3 country code, e.g. 'USA', 'GBR', 'IND'")
    market_segment: Literal[MARKET_SEGMENT_VALUES]
    distribution_channel: Literal[DISTRIBUTION_CHANNEL_VALUES]

    is_repeated_guest: int = Field(0, ge=0, le=1)
    previous_cancellations: int = Field(0, ge=0, le=30)
    previous_bookings_not_canceled: int = Field(0, ge=0, le=80)

    reserved_room_type: Literal[RESERVED_ROOM_TYPE_VALUES]
    booking_changes: int = Field(0, ge=0, le=25)
    deposit_type: Literal[DEPOSIT_TYPE_VALUES] = "No Deposit"
    days_in_waiting_list: int = Field(0, ge=0, le=400)
    customer_type: Literal[CUSTOMER_TYPE_VALUES]

    required_car_parking_spaces: int = Field(0, ge=0, le=8)
    total_of_special_requests: int = Field(0, ge=0, le=10)

    @field_validator("country")
    @classmethod
    def uppercase_country(cls, v: str) -> str:
        return v.strip().upper()

    class Config:
        json_schema_extra = {
            "example": {
                "hotel": "City Hotel",
                "lead_time": 45,
                "arrival_date_year": 2026,
                "arrival_date_month": "July",
                "arrival_date_week_number": 28,
                "arrival_date_day_of_month": 10,
                "stays_in_weekend_nights": 2,
                "stays_in_week_nights": 3,
                "adults": 2,
                "children": 1,
                "babies": 0,
                "meal": "BB",
                "country": "USA",
                "market_segment": "Online TA",
                "distribution_channel": "TA/TO",
                "is_repeated_guest": 0,
                "previous_cancellations": 0,
                "previous_bookings_not_canceled": 0,
                "reserved_room_type": "A",
                "booking_changes": 0,
                "deposit_type": "No Deposit",
                "days_in_waiting_list": 0,
                "customer_type": "Transient",
                "required_car_parking_spaces": 0,
                "total_of_special_requests": 1,
            }
        }


class PredictionResponse(BaseModel):
    predicted_adr: float
    currency_note: str = "ADR is in the same currency/unit as the training data (EUR, per the original Hotel Booking Demand dataset)."
    season: str
    total_guests: int
    total_nights: int
