from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError #예외처리를 위해 추가
from .models import Buyer
from .serializers import * # Buyer앱의 시리얼라이저 가져오기
from store.models import SaleProduct, Order, Store # Sotre 앱에서 모델 가져옴. SaleProduct

# Create your views here.

#구매자 회원 시작 
class BuyerCreateView(generics.CreateAPIView): #제너릭 뷰 사용함
    queryset = Buyer.objects.all() # 모든 구매자 객체
    serializer_class = BuySerializer #구매자 시리얼라이저 사용
    
# 주문서 생성 
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all() #모든 주문서 객체
    serializer_class = OrderCreateSerializer #주문서 생성 시리얼라이저 사용
    
    def post(self, request, *args, **kwargs):
        sale_product_pk = self.kwargs['pk']  # URL에서 떨이 상품 pk 가져오기
        sale_product = get_object_or_404(SaleProduct, pk=sale_product_pk)  # SaleProduct 모델에서 해당 pk 객체 찾기, 없으면 404 반환
        data = request.data.copy()  # 요청 본문을 복사함
        data['sale_product'] = sale_product.pk
        data['store'] = sale_product.store.pk  # store 필드를 자동으로 추가
        
        # 주문 수량을 정수로 변환
        order_amount = int(data['amount'])

        if order_amount > sale_product.amount: # 주문 수량이 재고보다 많으면 오류 반환
            return Response(
                {"error": "주문 수량이 재고보다 많습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 재고 감소 ->아 요거는 픽업 대기중으로 변경 될 떄 감소해야하는구나
        # sale_product.amount -= order_amount  # 주문 수량만큼 떨이 상품 수량 감소
        sale_product.save()  # 변경사항 저장

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
    
# 주문서 리스트 조회
class OrderLisetView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# 카테고리 별 떨이 상품 목록 조회
class SaleProductCateListView(generics.ListAPIView):
    serializer_class = SaleProductCategoryListSerializer

    # 유효한 product_type 값 정의
    VALID_PRODUCT_TYPES = ['FRV', 'BUT', 'BAK', 'SID', 'SEA', 'RIC', 'SNA']

    def get_queryset(self):
        product_type_par = self.kwargs['product_type']  # URL에서 product_type 가져오기
        if product_type_par not in self.VALID_PRODUCT_TYPES: # 유효성 검사 로직
            raise ValidationError(f"유효하지않은 product_type: {product_type_par}")
        return SaleProduct.objects.filter(product_type=product_type_par)

# 떨이 상품 상세 조회
class SaleProductDetailView(generics.RetrieveAPIView):
    queryset = SaleProduct.objects.all()
    serializer_class = SaleProductDetailSerializer

    def get_object(self):
        sale_product_pk = self.kwargs['pk']  # URL에서 떨이 상품 pk 가져오기
        return get_object_or_404(SaleProduct, pk=sale_product_pk)  # SaleProduct 모델에서 해당 pk 객체 찾기, 없으면 404 반환
