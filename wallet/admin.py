from django.contrib import admin

# Register your models here.
from wallet.models import Details,address_book

admin.site.register(Details)
admin.site.register(address_book)