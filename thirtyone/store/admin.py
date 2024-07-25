from django.contrib import admin
from .models import Store,Order,StoreType
# Register your models here.

#어드민페이지에서 수정할 것들 추가
admin.site.register(Store)
admin.site.register(Order)
admin.site.register(StoreType)