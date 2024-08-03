from django.contrib import admin
from .models import *

# Register your models here.

# 어드민에서 주문서에서 세부 내역 더 보고싶어서 추가함
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk','sale_product','order_number', 'buy_step','created_at','accept_at', 'store', 'buyer','amount' )

admin.site.register(Order, OrderAdmin)

# ㅍ나매자
class StoreAdmin(admin.ModelAdmin):
    list_display = ('pk','name', 'code', 'address', 'open_time', 'close_time', 'tel')

admin.site.register(Store, StoreAdmin)

#떨이 상품
class SaleProductAdmin(admin.ModelAdmin):
    list_display = ('pk','store', 'name', 'amount', 'price', 'sale_price', 'content', 'product_type')

admin.site.register(SaleProduct, SaleProductAdmin)

# 떨이 실적
class SaleRecordAdmin(admin.ModelAdmin):
    list_display = ('pk','sale_product', 'date', 'amount', 'selled_amount')

admin.site.register(SaleRecord, SaleRecordAdmin)
