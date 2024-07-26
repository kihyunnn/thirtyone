from django.shortcuts import render
from rest_framework import generics
from .models import Buyer
from .serializers import * # Buyer앱의 시리얼라이저 가져오기
from store.models import SaleProduct # Sotre 앱에서 모델 가져옴. SaleProduct

# Create your views here.

#구매자 회원 시작 
class BuyerCreateView(generics.CreateAPIView): #제너릭 뷰 사용함
    queryset = Buyer.objects.all() # 모든 구매자 객체
    serializer_class = BuySerializer #구매자 시리얼라이저 사용
    
# 주문서 생성 
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all() #모든 주문서 객체
    serializer_class = OrderCreateSerializer #주문서 생성 시리얼라이저 사용
    
    def Post(self):
        sale_product_id = self.kwargs['pk']  # URL에서 게시물 ID 가져오기
        