from rest_framework import serializers
from .models import *
from buyer.models import *
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
    #photo_url = serializers.SerializerMethodField()

    class Meta:
        model = SaleProduct
        fields = ['id', 'photo', 'name', 'product_type', 'price', 'sale_price', 'amount', 'content']


    def save(self, **kwargs): # save 함수 오버라이딩
        # 새 인스턴스가 생성되거나 기존 인스턴스가 업데이트될 때 호출됨
        sale_product = super().save(**kwargs)
        # **kwargs : keyword arguments 예상하지 못한 키워드 인수도 받을 수 있음
    
        # SaleRecord 업데이트
        self.update_sale_record(sale_product)

        return sale_product

    def update_sale_record(self, sale_product):
        today = datetime.date.today()
        sale_record, created = SaleRecord.objects.get_or_create(date=today, sale_product=sale_product)
        if created: # 해당 상품에 대해 처음 떨이 기록 생성됐을 경우
            sale_record.amount = sale_product.amount
        else: # 원래 있던 경우는 누적합으로
            sale_record.amount += sale_product.amount
        sale_record.save()

    # 안쓰는거여서 일단 주석처리 해둠
    # def get_image_url(self, obj):
    #     request = self.context.get('request')
    #     if obj.photo and hasattr(obj.photo, 'url'):
    #         return request.build_absolute_uri(obj.photo.url)
    #     return None

# 가게 목록 조회
class StoreMapListSerializer(serializers.ModelSerializer):
    sale_products = CreateSaleProductSerializer(many=True, read_only=True, source='saleproduct_set')
    # 해당 가게에 있는 떨이 상품 목록

    class Meta:
        model = Store
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    sale_product_name = serializers.CharField(source='sale_product.name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.name', read_only=True)
    class Meta:
        model = Order
        fields = '__all__'

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['buy_step']