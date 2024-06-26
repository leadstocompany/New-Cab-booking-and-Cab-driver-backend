# Create your models here.
from base64 import b32encode

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

from utility.model import BaseModel


def create_ref_code():
    while 1:
        referral_cde = get_random_string(5).upper()
        if referral_cde not in list(User.objects.values_list('code', flat=True)):
            print(referral_cde)
            return referral_cde
            break
        else:
            continue


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

class User(AbstractUser):
    class Types(models.TextChoices):
        DRIVER = "DRIVER", "driver"
        CUSTOMER = "CUSTOMER", "customer"
        ADMIN="ADMIN", "admin"
    type = models.CharField(max_length=11, choices=Types.choices,
                            default=Types.CUSTOMER)
    username = None
    phone = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    
    code = models.CharField(max_length=74, editable=False, unique=True)
    birth_day = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=(('Male', 'Male'), ('Female', 'Female'),
                              ('Other', 'Other')), max_length=74, null=True, blank=True)



    full_address = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.PositiveIntegerField(null=True, blank=True)
    state = models.CharField(max_length=74, null=True, blank=True)
    city = models.CharField(max_length=74, null=True, blank=True)
    house_or_building = models.CharField(max_length=274, null=True, blank=True)
    road_or_area = models.CharField(max_length=274, null=True, blank=True)

    alternate_number = models.CharField(max_length=74, null=True, blank=True)
  
    photo_upload = models.TextField(null=True, blank=True)
    user_doc = models.JSONField(default=None, null=True, blank=True) 
    terms_policy = models.BooleanField(default=False)
    myride_insurance = models.BooleanField(default=False)
    driver_duty = models.BooleanField(default=False)


    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.phone

    def hash(self):
        return b32encode(("74-%s-base32secret" % self.phone).encode('utf-8'))

class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = User.Types.ADMIN
        return super().save(*args, **kwargs)
class Driver(User):
    objects = DriverManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = User.Types.DRIVER
        # self.is_driver = True
        self.driver_duty = True
        return super().save(*args, **kwargs)


class Customer(User):
    objects = CustomerManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = User.Types.CUSTOMER
        self.is_customer = True
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

@receiver(post_save, sender=Customer)
def print_only_after_deal_created(sender, instance, created, **kwargs):
    if created:
        CustomerPhoneVerify.objects.create(user=instance)


@receiver(post_save, sender=Driver)
def print_only_after_deal_created(sender, instance, created, **kwargs):
    if created:
        DriverPhoneVerify.objects.create(user=instance)



def user_directory_path(instance, filename):
    print(instance.phone)
    return 'myride/{0}/{1}'.format(instance.phone, filename)


class FileUpload(BaseModel):
    file = models.FileField(upload_to=user_directory_path, max_length=100)
    phone = models.CharField(max_length=74)


class CustomerReferral(BaseModel):
    referrer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 related_name='referreds')
    referred = models.OneToOneField(Customer, on_delete=models.CASCADE,
                                    related_name='referrers')

    class Meta:
        unique_together = (('referrer', 'referred'),)

    def __str__(self):
        return f'{self.referrer} => {self.referred}'

    def clean(self, *args, **kwargs):
        if self.referrer == self.referred:
            raise ValidationError(_('The referrer and referred are same.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(CustomerReferral, self).save(*args, **kwargs)


