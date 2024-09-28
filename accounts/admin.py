from django.contrib import admin

# Register your models here.
from accounts.models import User, Driver, Customer, DriverPhoneVerify, CustomerPhoneVerify,Admin, CurrentLocation, BankAccount


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, BankAccount  # Make sure to import your custom User model
class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal info'), {'fields': ('birth_day', 'gender', 'email', 'full_address', 'city', 'state', 'pincode', 'latitude', 'longitude', 'house_or_building', 'road_or_area', 'alternate_number', 'photo_upload', 'user_doc')}),
        (_('Permissions'), {'fields': ('type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Profile Status'), {'fields': ('profile_status', 'rejection_reason')}),
    )

    # Fields to be used in forms for adding or changing users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )

    # List of fields to display in the admin panel
    list_display = ('phone', 'email', 'type', 'is_staff', 'profile_status', 'birth_day')
    search_fields = ('phone', 'email')
    ordering = ('phone',)

class DriverAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'driver_duty', 'profile_status', 'birth_day')
    search_fields = ('phone', 'email')
    ordering = ('phone',)


class CurrentLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_latitude', 'current_longitude', 'timestamp')
    search_fields = ('user__phone', 'current_latitude', 'current_longitude')
    ordering = ('timestamp',)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('driver', 'name', 'account_number', 'swift_code', 'bank_name')
    search_fields = ('name', 'account_number', 'swift_code', 'bank_name')
    list_filter = ('bank_name',)

admin.site.register(User, UserAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(CurrentLocation, CurrentLocationAdmin)


# admin.site.register(User)
# admin.site.register(Driver)
admin.site.register(Admin)
admin.site.register(Customer)
admin.site.register(DriverPhoneVerify)
admin.site.register(CustomerPhoneVerify)

