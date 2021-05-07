from django.urls import path
from .views import *

urlpatterns = [
    path('', payment, name='make_payment'),
    path('payment_status', payment_status, name='payment_status'),
]
