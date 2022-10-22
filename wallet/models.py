from django.db import models

# Create your models here.
class Details(models.Model):
    balance = models.CharField(max_length=500)
    INR_balance = models.CharField(max_length=500)
    private_key = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    phrase=models.CharField(max_length=500)


class address_book(models.Model):
    bit_id=models.CharField(max_length=50)
    Address=models.CharField(max_length=500)