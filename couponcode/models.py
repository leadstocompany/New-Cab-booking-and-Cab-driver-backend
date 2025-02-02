from django.db import models
import string
import random
from accounts.models import User
# Create your models here.
class Coupon(models.Model):
    name=models.CharField(max_length=1000, null=True, blank=True)
    title=models.CharField(max_length=1000, null=True, blank=True)
    terms_conditions=models.TextField(null=True, blank=True)
    code = models.CharField(max_length=10, unique=True, editable=False)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    use_count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_unique_code()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        length = 10
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not Coupon.objects.filter(code=code).exists():
                return code



class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"

    class Meta:
        db_table = 'couponusage'
        unique_together = ('user', 'coupon')
