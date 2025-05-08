from datetime import datetime
import json
import uuid

import requests

from admin_api.models import EmailTemplate



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

def get_notification_mapping(trip_id=None, payment_id=None, driver = None, extra_mapping = None):
    from trips.models import Trip
    from payment.models import Bill_Payment

    mapping = {}

    if trip_id:
        trip = Trip.objects.get(id=trip_id)
        mapping = {
            "TripID": trip.id,
            "TripSource": trip.source,
            "TripDestination": trip.destination,
            "TripDistance": trip.distance,
            "TripDuration": trip.time,
            "TripAmount": trip.rent_price if trip.rent_price else get_custom_ride_amount(trip, driver),
            "DriverName": f"{trip.driver.first_name} {trip.driver.last_name}" if trip.driver else f"{driver.first_name} {driver.last_name}",
            "DriverPhone": trip.driver.phone if trip.driver else driver.phone,
            "PassengerName": f"{trip.customer.first_name} {trip.customer.last_name}",
            "PassengerPhone": trip.customer.phone,
        }

    if payment_id:
        payment = Bill_Payment.objects.get(id=payment_id)
        mapping.update({
            "PaymentAmount": payment.amount,
            "PaymentType": payment.payment_type,
        })
    if extra_mapping and trip.rent_price is None:
        extra_mapping['PaymentAmount'] = mapping['TripAmount']

    return mapping if extra_mapping is None else {**mapping, **extra_mapping}


def get_custom_ride_amount(trip, driver):
    from cabs.models import CabBookingPrice, Vehicle
    if trip.ride_type is None or trip.rent_price is None or trip.rent_price <= 0:
        vehicle = Vehicle.objects.get(driver_id=driver.id)
        cabclass_value = CabBookingPrice.objects.get(cab_class_id=vehicle.cab_class.id)
        cab_custom_price = cabclass_value.base_fare * trip.distance
        if trip.coupon_code:
            from couponcode.models import Coupon
            coupon = Coupon.objects.get(code=trip.coupon_code)
            cab_custom_price -= cab_custom_price * (coupon.discount / 100)
        return cab_custom_price

from django.template import Template, Context
from notifications.models import NotificationTemplate

def render_notification_template(notification_type, mapping):
    try:
        template = NotificationTemplate.objects.get(type=notification_type, is_active=True)
        title_template = Template(template.title)
        body_template = Template(template.body)

        context = Context(mapping)
        rendered_title = title_template.render(context)
        rendered_body = body_template.render(context)

        return rendered_title, rendered_body
    except NotificationTemplate.DoesNotExist:
        return None, None
    

from django.core.mail import send_mail
from JLP_MyRide import settings
def send_dynamic_email(email_type, recipient_email, context_data):
    subject, content = EmailTemplate.render_template(email_type, context_data)
    
    if not subject or not content:
        return False
    
    try:
        payload = {
            "to": recipient_email,
            "subject": subject,
            "body": content,
            # "subscribed": True,
            "from": settings.DEFAULT_FROM_EMAIL,
        }
        response = requests.post(
            url="https://api.useplunk.com/v1/send",
            headers={
                "Authorization": f"Bearer sk_1f2426383c99fae254cc8e6ccc4286d71ec298c1fba0dabc",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        print("sening emial")
        if response.status_code == 200:
            print("Email sent successfully!")
            return True
        else:
            print(f"Plunk API error: {response.status_code} - {response.text}")
            return False
        # send_mail(
        #     subject=subject,
        #     message="",  # Plain text version (empty)
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[recipient_email],
        #     html_message=content,
        #     fail_silently=False,
        # )
        # return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False