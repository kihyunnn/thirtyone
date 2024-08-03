from django.contrib import admin
from .models import Buyer
# Register your models here.

class BuyerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')  

admin.site.register(Buyer, BuyerAdmin)