from django.contrib import admin

# Register your models here.
from wallet.models import Profile,address_book,wallet_details

admin.site.register(Profile)
admin.site.register(address_book)
admin.site.register(wallet_details)