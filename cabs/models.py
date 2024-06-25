from django.db import models
from accounts.models import *
from utility.model import BaseModel
# Create your models here.
def vehicle_model_directory_path(instance, filename):
    print(instance.model, "file_name", filename)
    return 'myride/{0}/{1}'.format(instance.model, filename)
class CabType(BaseModel):
    cab_type = models.CharField(max_length=74)
    
    def __str__(self):
        return self.cab_type
class CabClass(BaseModel):
    cab_class = models.CharField(max_length=74)
    cab_type = models.ForeignKey(CabType, on_delete=models.PROTECT)
    icon = models.ImageField(upload_to=vehicle_model_directory_path, null=True, blank=True)
    # price = models.FloatField()

    def __str__(self):
        return self.cab_class
class VehicleMaker(BaseModel):
    maker = models.CharField(max_length=74)
    cab_type = models.ForeignKey('cabs.CabType', on_delete=models.PROTECT)

    def __str__(self):
        return self.maker


class VehicleModel(BaseModel):
    model = models.CharField(max_length=74)
    maker = models.ForeignKey(VehicleMaker, on_delete=models.PROTECT)
    model_image=models.ImageField(upload_to=vehicle_model_directory_path, null=True, blank=True)
    # Add image 
    def __str__(self):
        return self.model
    
    
class Vehicle(BaseModel):
    # id=models.AutoField()
    driver = models.ForeignKey(Driver, related_name='vehicles',
                               on_delete=models.PROTECT)
    maker = models.ForeignKey(VehicleMaker, related_name='vehicles',
                              on_delete=models.PROTECT, null=True, blank=True)
    model = models.ForeignKey(VehicleModel, related_name='vehicles',
                              on_delete=models.PROTECT, null=True, blank=True)
    number_plate = models.CharField(
        max_length=74, unique=True)
        
    # insurance_certiifcate = models.TextField(null=True, blank=True)
    # registration_certiifcate = models.TextField(null=True, blank=True)
    # mot_certiifcate = models.TextField(null=True, blank=True)
    # addtional_document = models.TextField(null=True, blank=True)

    front = models.TextField(null=True, blank=True)
    back = models.TextField(null=True, blank=True)
    right = models.TextField(null=True, blank=True)
    left = models.TextField(null=True, blank=True)
    inside_driver_seat = models.TextField(null=True, blank=True)
    inside_passanger_seat = models.TextField(null=True, blank=True)
    front_head_light = models.TextField(null=True, blank=True)
    back_head_light = models.TextField(null=True, blank=True)
    vehicle_certiifcate= models.JSONField(default=None)
    # sound = models.TextField(null=True, blank=True)
    # pollution = models.TextField(null=True, blank=True)

    cab_type = models.ForeignKey(
        CabType, on_delete=models.PROTECT, related_name='vehicles', null=True, blank=True)
    cab_class = models.ForeignKey(
        CabClass, on_delete=models.PROTECT, related_name='vehicles', null=True, blank=True)
    last_location = models.CharField(max_length=174, null=True, blank=True)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.number_plate