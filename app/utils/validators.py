"""Small input checks shared by the form and API routes."""
import re
from datetime import datetime, date

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^[0-9]{10}$")


def valid_email(value):
    return bool(value and EMAIL_RE.match(value.strip()))


def valid_phone(value):
    return bool(value and PHONE_RE.match(value.strip()))


def valid_password(value):
    return bool(value) and len(value) >= 6


def parse_date(value):
    """'2026-10-04' -> date, or None if unusable."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate_signup(form):
    """Returns a list of human-readable problems (empty list means fine)."""
    errors = []
    if not form.get("name", "").strip():
        errors.append("Enter your name.")
    if not valid_email(form.get("email", "")):
        errors.append("Enter a valid email address.")
    if form.get("phone") and not valid_phone(form.get("phone")):
        errors.append("Phone number must be 10 digits.")
    if not valid_password(form.get("password", "")):
        errors.append("Password must be at least 6 characters.")
    if form.get("password") != form.get("confirm_password"):
        errors.append("Passwords do not match.")
    return errors


def validate_booking(seats, travel_date):
    errors = []
    if seats < 1:
        errors.append("Book at least one seat.")
    if seats > 6:
        errors.append("A single booking can hold up to 6 seats.")
    if travel_date is None:
        errors.append("Pick a travel date.")
    elif travel_date < date.today():
        errors.append("Travel date cannot be in the past.")
    return errors
