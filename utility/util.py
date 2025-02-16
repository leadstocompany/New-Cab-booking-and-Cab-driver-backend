from datetime import datetime
import uuid


def calculate_percentage_change(old_value, new_value):
    if old_value == 0:
        return "+100" if new_value > 0 else "0"

    total = ((new_value - old_value) / old_value) * 100
    total = round(total, 2)
    return f"+{total}" if total > 0 else f"{total}"


def parse_datetime(datetime_str):
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # Format: 2025-02-21T19:32:00.000Z
        "%Y-%m-%d %H:%M:%S.%f",  # Format: 2025-02-21 19:32:00.000
    ]

    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"time data '{datetime_str}' does not match any supported formats")


def generate_six_digit_uuid():
    return str(uuid.uuid4())[:7]
