from rest_framework import serializers
from store.models import SaleProduct, SaleRecord

# 판매순위 시리얼라이저
class SelledRankSerializer(serializers.ModelSerializer):
    selled_product_name= serializers.CharField(source='sale_product.name',read_only=True) # 떨이 상품의 이름 직접 가져오기
    
    class Meta:
        model = SaleRecord
        fields = ['selled_product_name', 'selled_amount']   

# 중첩용 salerecord 시리얼라이저
class SaleRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecord
        fields = '__all__'
        
# 떨이 판매 추이 조회 시리얼라이저
class SaleTrendSerializer(serializers.ModelSerializer):
    selled_product_name= serializers.CharField(source='sale_product.name',read_only=True) # 떨이 상품의 이름 직접 가져오기
    remove_total = serializers.SerializerMethodField()  # 계산된 필드 추가
    class Meta:
        model = SaleRecord
        fields = ['selled_product_name','date','amount','selled_amount','remove_total']  
        
    def get_remove_total(self, obj):
        # amount에서 selld_amoubt뺸값
        return obj.amount - obj.selled_amount

        