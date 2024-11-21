from trips.models import TripRating
from django.db.models import Avg

def get_driver_rating(driver):
    return TripRating.objects.filter(driver=driver).aggregate(Avg('star'))['star__avg'] or 0.0


# from django.utils import timezone
# import datetime

# # Get the current time
# current_time = timezone.now()
# print(current_time)  # This will print the current time in UTC

# # Convert to the local time zone (Asia/Kuala_Lumpur)
# local_time = timezone.localtime(current_time)
# print(local_time)

# print("48484848")

# print(timezone.localtime().date())
# timezone.localtime(timezone.now())
