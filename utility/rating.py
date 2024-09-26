from trips.models import TripRating
from django.db.models import Avg

def get_driver_rating(driver):
    return TripRating.objects.filter(driver=driver).aggregate(Avg('star'))['star__avg'] or 0.0