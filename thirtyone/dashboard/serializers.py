from rest_framework import serializers
from store.models import SaleProduct, SaleRecord

# 판매순위 시리얼라이저
class SelledRankSerializer(serializers.ModelSerializer):
    selled_name = serializers.CharField(source='sale_product.name',read_only=True) # 떨이 상품의 이름 직접 가져오기
    
    class Meta:
        model = SaleRecord
        fields = ['selled_name', 'selled_amount']   