from django.contrib import admin
from .models import Store, Order

# Register your models here.



# 어드민에서 주문서에서 세부 내역 더 보고싶어서 추가함
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'created_at','accept_at', 'store', 'buyer', 'buy_step')

admin.site.register(Order, OrderAdmin)

# Store 모델을 admin 페이지에 등록하고, list_display 옵션을 추가하여 코드도 볼 수 있도록 설정
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'address', 'open_time', 'close_time', 'tel')

admin.site.register(Store, StoreAdmin)
