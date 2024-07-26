from rest_framework import serializers
from .models import *
import datetime

class CreateStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'photo', 'address', 'open_time', 'close_time', 'tel', 'latitude', 'longitude', 'type']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class CreateSaleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleProduct
        fields = ['photo', 'name', 'product_type', 'price', 'sale_price', 'amount', 'content']

    # update랑 create는 instance(떨이상품)을 가지고 update_sale_record에 사용하기 위해서 있는 함수 느낌..?
    def update(self, instance, validated_data):
        # 떨이 상품이 새로 업데이트 될때 수행됨
        instance = super().update(instance, validated_data)
        self.update_sale_record(instance)
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        self.update_sale_record(instance)
        return instance

    def update_sale_record(self, sale_product):
        today = datetime.date.today()
        sale_record, created = SaleRecord.objects.get_or_create(date=today, sale_product=sale_product)
            
        if created:
            sale_record.amount = sale_product.amount
        else:
            sale_record.amount += sale_product.amount
        sale_record.save()