from rest_framework import serializers
from .models import Buyer
from store.models import * #store의 모델 가져옴

#구매자 시작 시리얼 라이저
class BuySerializer(serializers.ModelSerializer): 
    class Meta:
        model = Buyer
        fields = ['id','name']

#주문서 작성 시리얼 라이저
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['']

#주문서 반환 시리얼라이저
class OrderDeailSerializer(serializers.ModelSerializer):
    class Meta: