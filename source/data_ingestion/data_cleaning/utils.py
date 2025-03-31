from typing import Dict, Any, List
import re
from datetime import datetime


def convert_to_24h(time_str):
    time_str = time_str.strip().upper()
    if time_str == "NONE":
        return None
    match = re.match(r"^(\d{1,2}):(\d{2})(AM|PM)$", time_str)
    if not match:
        return None
    hour, minute, ampm = match.groups()
    hour = int(hour)
    minute = int(minute)
    if ampm == "AM" and hour == 12:
        hour = 0
    elif ampm == "PM" and hour != 12:
        hour += 12
    return f"{hour:02d}:{minute:02d}:00"


def clean_spaces(text):
    return " ".join(text.split())


def clean_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def clean_string_common(value):
    if value is None or not isinstance(value, str):
        return None
    value = value.strip()
    if value == "" or value.lower() == "none":
        return None
    return value
