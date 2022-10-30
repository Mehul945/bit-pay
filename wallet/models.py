from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# class Profile(models.Model):
#     user=models.OneToOneField(User,on_delete=models.CASCADE)
#     email=models.EmailField(null=True)
#     is_verified =models.BooleanField(default=False)

#     token=models.CharField(max_length=100,null=True)
#     create_at=models.DateTimeField(auto_created=True,null=True)


class User(AbstractUser):
    is_verified = models.BooleanField(default=False)
    create_at=models.DateTimeField(auto_now=True)
    token=models.CharField(null=True,blank=True,max_length=30)

class address_book(models.Model):
    bit_id=models.CharField(max_length=50)
    Address=models.CharField(max_length=500)

class wallet_details(models.Model):
    balance = models.CharField(max_length=500)
    INR_balance = models.CharField(max_length=500)
    private_key = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    phrase=models.CharField(max_length=500)