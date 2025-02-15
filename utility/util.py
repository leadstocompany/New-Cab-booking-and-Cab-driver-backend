from datetime import datetime


def calculate_percentage_change(old_value, new_value):
    if old_value == 0:
        return 100 if new_value > 0 else 0
    return ((new_value - old_value) / old_value) * 100


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
