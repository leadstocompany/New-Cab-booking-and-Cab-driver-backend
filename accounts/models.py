# Create your models here.
from base64 import b32encode
from importlib import import_module

# from django.contrib.auth.base_user import BaseUserManager
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError, transaction
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.crypto import get_random_string

from utility.util import calculate_percentage_change
from utility.model import BaseModel, CloudinaryBaseModelUser, CloudinaryBaseModel
from cloudinary.models import CloudinaryField

def create_ref_code():
    while True:
        # Generate a random 5-character string
        referral_cde = get_random_string(5).upper()
        try:
            # Try to save it to the database inside a transaction
            with transaction.atomic():
                # Ensure that the referral code is unique at the time of insertion
                if not User.objects.filter(code=referral_cde).exists():
                    return referral_cde
        except IntegrityError:
            # Handle the case where a race condition caused a duplicate entry
            continue  # Retry with a new code

# def create_ref_code():
#     while True:
#         referral_cde = get_random_string(5).upper()
#         print(referral_cde)
#         if referral_cde not in list(User.objects.values_list('code', flat=True)):
#             print(referral_cde)
#             # break
#             return referral_cde
#             # break
#         else:
#             continue


class UserManager(UserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, phone, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not phone:
            raise ValueError(_("The Phone must be set"))
        user = self.model(phone=phone, **extra_fields)
        user.code = create_ref_code()
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        """
        Create and save a SuperUser with the given phone and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("type", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone, password, **extra_fields)


class DriverManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(type=User.Types.DRIVER)
        return queryset


class CustomerManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(type=User.Types.CUSTOMER)
        return queryset
class AdminManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(type=User.Types.ADMIN)
        return queryset

class User(AbstractUser, CloudinaryBaseModelUser):
    class Types(models.TextChoices):
        DRIVER = "DRIVER", "driver"
        CUSTOMER = "CUSTOMER", "customer"
        ADMIN="ADMIN", "admin"
    type = models.CharField(max_length=11, choices=Types.choices,
                            default=Types.CUSTOMER)
    username = None
    date_joined = models.DateTimeField(_("date joined"), default=timezone.localtime(timezone.now()))
    phone = models.CharField(max_length=21, unique=True)
    email = models.EmailField(max_length=254)

    code = models.CharField(max_length=74, editable=False, unique=True)
    birth_day = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=(('Male', 'Male'), ('Female', 'Female'),
                              ('Other', 'Other')), max_length=74, null=True, blank=True)

    full_address = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=74, null=True, blank=True)
    state = models.CharField(max_length=74, null=True, blank=True)
    city = models.CharField(max_length=74, null=True, blank=True)
    pincode = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(max_length=274, null=True, blank=True)
    house_or_building = models.CharField(max_length=274, null=True, blank=True)
    road_or_area = models.CharField(max_length=274, null=True, blank=True)
    landmark = models.CharField(max_length=274, null=True, blank=True)

    alternate_number = models.CharField(max_length=74, null=True, blank=True)

    photo_upload = CloudinaryField(null=True, blank=True)
    user_doc = models.JSONField(default=None, null=True, blank=True) 
    terms_policy = models.BooleanField(default=False)
    myride_insurance = models.BooleanField(default=False)
    driver_duty = models.BooleanField(default=False)
    profile_status = models.CharField(choices=(('Pending', 'Pending'), ('Approve', 'Approve'), ('Rejected', 'Rejected'),
                              ('Block', 'Block')), max_length=74, default="Pending")
    rejection_reason = models.TextField(null=True, blank=True)
    fcm_token=models.TextField(null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.full_name

    def get_cloudinary_folder(self, field_name):
        return f"accounts/{self.phone}"

    def get_file_fields(self):
        return ['photo_upload']

    @property
    def full_name(self):
        return self.phone

    def hash(self):
        return b32encode(("74-%s-base32secret" % self.phone).encode('utf-8'))

    def get_driver_rating(self):
        TripRating = import_module("trips.models").TripRating
        return TripRating.objects.filter(driver=self).aggregate(models.Avg('star'))['star__avg'] or 0.0

    @classmethod
    def get_recent_drivers(cls):
        drivers = cls.objects.filter(type=cls.Types.DRIVER).order_by("-date_joined")[:3]

        driver_data = []
        for driver in drivers:
            from importlib import import_module

            Vehicle = import_module("cabs.models").Vehicle
            vehicle = Vehicle.objects.filter(driver=driver).first()
            driver_info = {
                "id": driver.id,
                "name": f"{driver.first_name} {driver.last_name}",
                "join_date": driver.date_joined.strftime("%d/%m/%Y"),
                "vehicle_type": (
                    vehicle.cab_type.cab_type if vehicle and vehicle.cab_type else None
                ),
                "status": driver.profile_status,
                "phone": driver.phone,
                "vehicle_number": vehicle.number_plate if vehicle else None,
            }
            driver_data.append(driver_info)

        return driver_data

    @classmethod
    def get_new_customer_stats(cls):
        today = timezone.now()
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)

        current_users = cls.objects.filter(
            date_joined__gte=current_month_start, type=cls.Types.CUSTOMER
        ).count()

        last_month_users = cls.objects.filter(
            date_joined__gte=last_month_start,
            date_joined__lt=current_month_start,
            type=cls.Types.CUSTOMER,
        ).count()

        return {
            "count": current_users,
            "percentage": calculate_percentage_change(last_month_users, current_users),
        }

    @classmethod
    def get_new_driver_stats(cls):
        today = timezone.now()
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)

        current_drivers = cls.objects.filter(
            date_joined__gte=current_month_start, type=cls.Types.DRIVER
        ).count()
        last_month_drivers = cls.objects.filter(
            date_joined__gte=last_month_start,
            date_joined__lt=current_month_start,
            type=cls.Types.DRIVER,
        ).count()
        return {
            "count": current_drivers,
            "percentage": calculate_percentage_change(
                last_month_drivers, current_drivers
            ),
        }


class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = User.Types.ADMIN
        if not self.code:
            self.code = create_ref_code()
        return super().save(*args, **kwargs)
class Driver(User):
    objects = DriverManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = User.Types.DRIVER
        # self.is_driver = True
        self.driver_duty = True
        if not self.code:
            self.code = create_ref_code()
        return super().save(*args, **kwargs)


class Customer(User):
    objects = CustomerManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = User.Types.CUSTOMER
        if not self.code:
            self.code = create_ref_code()
        return super().save(*args, **kwargs)


class DriverPhoneVerify(models.Model):
    user = models.OneToOneField(Driver, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return str(self.count)


class CustomerPhoneVerify(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return str(self.count)

# @receiver(pre_save)
# def callback(sender, instance, *args, **kwargs):
#     if sender.__name__ in ['Customer', 'Driver', 'CarOwner' ] and \
#          not instance.email and not instance.pk:
#             instance.email = instance.code.lower() + "@jps.myride.com"


def user_directory_path(instance, filename):
    print(instance.phone)
    return 'myride/{0}/{1}'.format(instance.phone, filename)


class FileUpload(CloudinaryBaseModel):
    file = CloudinaryField(null=True, blank=True)
    phone = models.CharField(max_length=74)

    def get_cloudinary_folder(self, field_name):
        return f"accounts/{self.phone}/documents"

    def get_file_fields(self):
        return ['file']


# class CustomerReferral(BaseModel):
#     referrer = models.ForeignKey(Customer, on_delete=models.CASCADE,
#                                  related_name='referreds')
#     referred = models.OneToOneField(Customer, on_delete=models.CASCADE,
#                                     related_name='referrers')

#     class Meta:
#         unique_together = (('referrer', 'referred'),)

#     def __str__(self):
#         return f'{self.referrer} => {self.referred}'

#     def clean(self, *args, **kwargs):
#         if self.referrer == self.referred:
#             raise ValidationError(_('The referrer and referred are same.'))

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         return super(CustomerReferral, self).save(*args, **kwargs)


class BankAccount(BaseModel):
    driver = models.ForeignKey(Driver, related_name='backaccount',
                               on_delete=models.PROTECT)
    name=models.CharField(max_length=200)
    account_number=models.CharField(max_length=25, unique=True)
    swift_code=models.CharField(max_length=35, unique=True)
    routing_number=models.CharField(_("routing number"), max_length=100, blank=True)
    bank_name=models.CharField(max_length=200)
    account_id=models.CharField(max_length=1000,null=True, blank=True)
    def __str__(self):
        return f'{self.name} - {self.bank_name}'


class CurrentLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_latitude = models.CharField(max_length=50, null=True, blank=True)
    current_longitude = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone} - {self.current_latitude}, {self.current_longitude} at {self.timestamp}"


@receiver(post_save, sender=Customer)
def print_only_after_deal_created(sender, instance, created, **kwargs):
    if created:
        CustomerPhoneVerify.objects.create(user=instance)


@receiver(post_save, sender=Driver)
def print_only_after_deal_created(sender, instance, created, **kwargs):
    if created:
        DriverPhoneVerify.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def create_user_current_location(sender, instance, created, **kwargs):
#     if created:
#         CurrentLocation.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_current_location(sender, instance, **kwargs):
#     instance.current_location.save()
