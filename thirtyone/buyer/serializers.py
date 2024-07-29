from rest_framework import serializers
from .models import Buyer
from store.models import * #store의 모델 가져옴

# Store 시리얼라이저
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name']

# 떨이상품 이름 중첩용 시리얼라이저
class SaleProductNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleProduct
        fields = ['name']


# 구매자 시작 시리얼 라이저
class BuySerializer(serializers.ModelSerializer): 
    class Meta:
        model = Buyer
        fields = ['id','name']

# 주문서 작성 시리얼 라이저
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['amount','store', 'sale_product',]

# 주문서 반환 시리얼라이저
class OrderDeailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

# 주문서 리스트 조회 시리얼라이저
class OrderListSerializer(serializers.ModelSerializer):
    store = StoreSerializer() #store 이름 나오도록 시리얼라이저 중첩
    sale_product = SaleProductNameSerializer() #떨이상품 이름 나오도록 시리얼라이저 중첩

    class Meta:
        model = Order
        fields = '__all__'

# 카테고리별 떨이 상품 목록 조회 시리얼 라이저 / 검색에도 사용
class SaleProductListSerializer(serializers.ModelSerializer):
    store = StoreSerializer() #store 이름 나오도록 시리얼라이저 중첩
    
    class Meta:
        model = SaleProduct
        fields = '__all__'

# 떨이 상품 상세 조회 시리얼 라이저
class SaleProductDetailSerializer(serializers.ModelSerializer):
    store = StoreSerializer() #store 이름 나오도록 시리얼라이저 중첩

    class Meta:
        model = SaleProduct
        fields = '__all__'

class StoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'