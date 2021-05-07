from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.IntegerField(null=True)
    razorpay_data = models.ForeignKey('Razorpay_data', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "transaction"

    def __str__(self):
        return str(self.id)

    def get_user_transactions(self, uid):
        result = self.objects.filter(user_id=uid)
        return result


class Razorpay_data(models.Model):
    rzp_order_id = models.CharField(max_length=60, blank=True, null=True)
    status = models.BooleanField(default=False)
    paid_on = models.DateTimeField(null=True)
    rzp_payment_id = models.CharField(max_length=60, blank=True, null=True)
    method = models.CharField(max_length=20, null=True)
    payment_email = models.EmailField(null=True)
    payment_contact = models.CharField(max_length=15, null=True)

    class Meta:
        db_table = "Razorpay"

    def __str__(self):
        return str(self.id)
