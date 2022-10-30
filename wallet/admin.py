from django.contrib import admin

# Register your models here.
from wallet.models import User, address_book,wallet_details

admin.site.register(User)
admin.site.register(address_book)
admin.site.register(wallet_details)