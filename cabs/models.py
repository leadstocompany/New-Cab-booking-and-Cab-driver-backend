from django.db import models
from accounts.models import *
from utility.model import BaseModel
# Create your models here.
def vehicle_model_directory_path(instance, filename):
    print(instance.model, "file_name", filename)
    return 'myride/{0}/{1}'.format(instance.model, filename)
def vehicle_class_directory_path(instance, filename):
    
    return 'myride/{0}/{1}'.format(instance.cab_class, filename)
def vehicle_type_directory_path(instance, filename):
    
    return 'myride/{0}/{1}'.format(instance.type, filename)

def vehicle_maker_directory_path(instance, filename):
    return 'myride/{0}/{1}'.format(instance.maker, filename)
class CabType(BaseModel):
    cab_type = models.CharField(max_length=74, unique=True)
    icon = models.TextField(null=True, blank=True)
    # icon = models.FileField(upload_to=vehicle_type_directory_path, null=True, blank=True)
    def __str__(self):
        return str(self.cab_type)
    
class CabClass(BaseModel):
    cab_class = models.CharField(max_length=200, unique=True)
    cab_type = models.ForeignKey(CabType, on_delete=models.PROTECT)
    icon = models.TextField(null=True, blank=True)
    # icon = models.FileField(upload_to=vehicle_class_directory_path, null=True, blank=True)
    def __str__(self):
        return str(self.cab_class)
class VehicleMaker(BaseModel):
    maker = models.CharField(max_length=200, unique=True)
    cab_type = models.ForeignKey(CabType, on_delete=models.PROTECT, null=True, blank=True)
    icon = models.TextField(null=True, blank=True)
    # icon = models.FileField(upload_to=vehicle_maker_directory_path, null=True, blank=True)
    def __str__(self):
        return self.maker


class VehicleModel(BaseModel):
    model = models.CharField(max_length=200, unique=True)
    cabtype=models.ForeignKey(CabType, on_delete=models.PROTECT, null=True, blank=True)
    cabclass=models.ForeignKey(CabClass, on_delete=models.PROTECT, null=True, blank=True)
    maker = models.ForeignKey(VehicleMaker, on_delete=models.PROTECT)
    model_image = models.TextField(null=True, blank=True)
    # model_image=models.FileField(upload_to=vehicle_model_directory_path, null=True, blank=True)
    
    # Add image 
    def __str__(self):
        return self.model
    
    
class Vehicle(BaseModel):
    driver = models.ForeignKey(Driver, related_name='vehicles',
                               on_delete=models.PROTECT)
    maker = models.ForeignKey(VehicleMaker, related_name='vehicles',
                              on_delete=models.PROTECT, null=True, blank=True)
    model = models.ForeignKey(VehicleModel, related_name='vehicles',
                              on_delete=models.PROTECT, null=True, blank=True)
    number_plate = models.CharField(max_length=74, unique=True)
   
    vehicle_photo=  models.JSONField(default=None, null=True, blank=True) 
    vehicle_certiifcate=  models.JSONField(default=None, null=True, blank=True) 
   

    cab_type = models.ForeignKey(
        CabType, on_delete=models.PROTECT, related_name='vehicles', null=True, blank=True)
    cab_class = models.ForeignKey(
        CabClass, on_delete=models.PROTECT, related_name='vehicles', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    # last_latitude = models.DecimalField(max_digits=21, decimal_places=18, null=True, blank=True)
    # last_longitude = models.DecimalField(max_digits=21, decimal_places=18, null=True, blank=True)
    last_latitude = models.CharField(max_length=50, null=True, blank=True)
    last_longitude = models.CharField(max_length=50, null=True, blank=True)

     # front = models.TextField(null=True, blank=True)
    # back = models.TextField(null=True, blank=True)
    # right = models.TextField(null=True, blank=True)
    # left = models.TextField(null=True, blank=True)
    # inside_driver_seat = models.TextField(null=True, blank=True)
    # inside_passanger_seat = models.TextField(null=True, blank=True)
    # front_head_light = models.TextField(null=True, blank=True)
    # back_head_light = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.number_plate
   







class CabBookingPrice(models.Model):
    cab_class = models.ForeignKey(CabClass, on_delete=models.PROTECT)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="base fare for per kms")
    # extra_km_fare = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="extra km fare")
    waiting_fare_per_minute = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="waiting fare per minute")
    class Meta:
        db_table = 'cabbookingprice'
    objects=models.Manager()
    def __str__(self):
        return self.base_fare





    