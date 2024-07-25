from rest_framework import serializers
from .models import Buyer

#구매자 시작 시리얼 라이저
class BuySerializer(serializers.ModelSerializer): 
    class Meta:
        model = Buyer
        fields = ['id','name']