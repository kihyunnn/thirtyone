from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import generics
from .models import Buyer
from .serializers import * # Buyer앱의 시리얼라이저 가져오기
from store.models import SaleProduct, Order # Sotre 앱에서 모델 가져옴. SaleProduct

# Create your views here.

#구매자 회원 시작 
class BuyerCreateView(generics.CreateAPIView): #제너릭 뷰 사용함
    queryset = Buyer.objects.all() # 모든 구매자 객체
    serializer_class = BuySerializer #구매자 시리얼라이저 사용
    
# 주문서 생성 
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all() #모든 주문서 객체
    serializer_class = OrderCreateSerializer #주문서 생성 시리얼라이저 사용
    
    def post(self,request,*args, **kwargs):
        sale_product_pk = self.kwargs['pk']  # URL에서 떨이 상품 pk 가져오기
        sale_product = get_object_or_404(SaleProduct, pk=sale_product_pk) #SaleProduct 모델에서 해당 pk 객체 찾기, 없으면 404 반환
        data = request.data.copy() #요청본문을 복사함
        data['sale_product'] = sale_product.pk
        serializers = self.get_serializer(data=data) #수정된 데이터로 시리얼라이저 초기화
        serializers.is_valid(raise_exception=True) # 시리얼라이저 유효성 검사
        self.perform_create(serializers) #유효한 데이터 저장
        headers = self.get_success_headers(serializers.data)
        return Response(serializers.data, status=201, headers=headers)