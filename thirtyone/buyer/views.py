from django.shortcuts import render
from rest_framework import generics
from .models import Buyer
from .serializers import BuySerializer

# Create your views here.

#구매자 회원 시작 
class BuyerCreateView(generics.CreateAPIView): #제너릭 뷰 사용함
    queryset = Buyer.objects.all() # 모든 구매자 객체
    serializer_class = BuySerializer #구매자 시리얼라이저 사용