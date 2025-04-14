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

def get_bill_payment_mapping(payment_id, get_key = False):
    from payment.models import Bill_Payment
    from JLP_MyRide import settings

    payment = Bill_Payment.objects.get(id=payment_id) if not get_key else Bill_Payment.objects.all().order_by("-id").first()
    
    placeholder_mapping = {
        "TripID": payment.trip.id,
        "RideStartTime": payment.trip.ride_start_time,
        "RideEndTime": payment.trip.ride_end_time,
        "TripAmount": payment.amount,
        "TripDistance": payment.trip.distance,
        "TripDuration": payment.trip.time,
        "DriverName": payment.trip.driver.full_name,
        "DriverPhone": payment.trip.driver.phone,
        "DriverVehicleType": payment.trip.cab.cab_type.cab_type,
        "DriverVehicleLicence": payment.trip.cab.number_plate,
        "TripSource": payment.trip.source,
        "TripDestination": payment.trip.destination,
        "TripBillPrice": payment.trip.rent_price,
        "TripWaitingCharge": payment.trip.waiting_charge,
        "TripTotalAmount": payment.trip.total_fare,
        "SupportEmail": settings.DEFAULT_FROM_EMAIL,
    }

    return payment, placeholder_mapping