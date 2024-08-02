from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError, NotFound #예외처리를 위해 추가
from django.db.models import Q #검색기능에 Q객체 기능 사용

from .models import Buyer
from .serializers import * # Buyer앱의 시리얼라이저 가져오기
from store.models import SaleProduct, Order, Store # Sotre 앱에서 모델 가져옴. SaleProduct
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

#구매자 회원 시작 
class BuyerCreateView(generics.CreateAPIView):
    queryset = Buyer.objects.all()  # 모든 구매자 객체
    serializer_class = BuySerializer  # 구매자 시리얼라이저 사용
    @swagger_auto_schema(
        operation_description="구매자 등록",
        operation_summary="구매자를 생성합니다",
        request_body=BuySerializer,
        responses={
            201: openapi.Response('구매자가 성공적으로 생성되었습니다.', BuySerializer),
            400: "잘못된 요청입니다.",
            500: "서버 오류입니다."
        },
        tags=["구매자"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    
# 주문서 생성 
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all() #모든 주문서 객체
    serializer_class = OrderCreateSerializer #주문서 생성 시리얼라이저 사용
    @swagger_auto_schema(
        operation_description="새로운 주문서를 생성합니다.",
        operation_summary="주문서 생성",
        request_body=OrderCreateSerializer,
        responses={
            201: openapi.Response('주문서가 성공적으로 생성되었습니다.', OrderCreateSerializer),
            400: "잘못된 요청입니다.",
            500: "서버 오류입니다."
        },
        tags=["주문"]
    )
    def post(self, request, *args, **kwargs):
        data = request.data.copy() # 요청 본분 data 변수에 복사
        # json 본문에서 SaleProduct id와 Buyer id 가져오기
        sale_product_pk = data.get('sale_product')
        buyer_id = data.get('buyer')
        # SaleProduct 모델에서 해당 pk 객체 찾기, 없으면 404 반환
        sale_product = get_object_or_404(SaleProduct, pk=sale_product_pk)

        # 주문 수량을 정수로 변환
        order_amount = int(data['amount'])

        if order_amount > sale_product.amount: # 주문 수량이 재고보다 많으면 오류 반환
            return Response(
                {"error": "주문 수량이 재고보다 많습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data['store'] = sale_product.store.pk  # store 필드를 자동으로 추가

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=201, headers=headers)
    
# 주문서 리스트 조회
class OrderLisetView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    queryset = Order.objects.none()  # 기본 빈 쿼리셋 설정

    @swagger_auto_schema(
        operation_description="특정 구매자의 주문서 리스트를 조회합니다.",
        operation_summary="주문서 리스트 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', OrderListSerializer(many=True)),
            400: "잘못된 요청입니다.",
            404: "구매자를 찾을 수 없습니다.",
            500: "서버 오류입니다."
        },
        tags=["주문"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="구매자의 ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # Swagger 스키마 생성 중일 때 빈 쿼리셋 반환
            return Order.objects.none()
        
        buyer_pk = self.kwargs.get('pk')  # URL에서 구매자 pk 가져오기
        if buyer_pk is None:
            return Order.objects.none()
        return Order.objects.filter(buyer__id=buyer_pk)

@swagger_auto_schema(
    method='patch',
    operation_description="주문을 취소합니다.",
    operation_summary="주문 취소",
    responses={
        200: openapi.Response('주문이 성공적으로 취소되었습니다.', OrderCancelSerializer),
        400: "잘못된 요청입니다.",
        404: "구매자 또는 주문을 찾을 수 없습니다.",
        500: "서버 오류입니다."
    },
    tags=["주문"],
    manual_parameters=[
        openapi.Parameter('pk', openapi.IN_PATH, description="구매자의 ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('order_id', openapi.IN_PATH, description="주문의 ID", type=openapi.TYPE_INTEGER),
    ],
    request_body=OrderCancelSerializer,
)
# 주문 취소
@api_view(['PATCH'])
def cancel_order(request, pk, order_id):
    try:
        buyer = Buyer.objects.get(pk=pk)
        order = Order.objects.get(pk=order_id, buyer=buyer)
    except Store.DoesNotExist:
        return Response({"error": "Byer not found"}, status=404)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    serializer = OrderCancelSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        sale_product_name = order.sale_product
        store_name = order.store
        sale_product = SaleProduct.objects.get(store=store_name, name=sale_product_name)
        if serializer.validated_data.get('buy_step') == Order.OrderStepCategory.BUYER_CANCEL: # 주문 취소
            sale_product.amount += order.amount # 자동취소되면 해당 수량 다시 떨이상품에 업데이트 시킴
            sale_product.save()
        
        serializer.save()
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)
        


# 카테고리별 떨이 상품 목록 조회
class SaleProductCateListView(generics.ListAPIView):
    serializer_class = SaleProductListSerializer
    queryset = Order.objects.none()  # 기본 빈 쿼리셋 설정
    # 유효한 product_type 값 정의
    VALID_PRODUCT_TYPES = ['FRV', 'BUT', 'BAK', 'SID', 'SEA', 'RIC', 'SNA']
    @swagger_auto_schema(
        operation_description="카테고리별 떨이 상품 목록을 조회합니다.",
        operation_summary="카테고리별 떨이 상품 목록 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', SaleProductListSerializer(many=True)),
            400: "유효하지 않은 product_type입니다.",
            500: "서버 오류입니다."
        },
        tags=["떨이상품"],
        manual_parameters=[
            openapi.Parameter('product_type', openapi.IN_PATH, description="상품 카테고리 타입", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    def get_queryset(self):
        # Swagger 스키마 생성 중일 때는 빈 쿼리셋 반환
        if getattr(self, 'swagger_fake_view', False):
            return SaleProduct.objects.none()

        product_type_par = self.kwargs.get('product_type')  # URL에서 product_type 가져오기
        if product_type_par not in self.VALID_PRODUCT_TYPES:  # 유효성 검사 로직
            raise ValidationError(f"유효하지 않은 product_type: {product_type_par}")
        return SaleProduct.objects.filter(product_type=product_type_par)  # 필터링해서 변수에 담아둔 type과 일치하는 것만 반환

# 떨이 상품 상세 조회
class SaleProductDetailView(generics.RetrieveAPIView):
    queryset = SaleProduct.objects.all()
    serializer_class = SaleProductDetailSerializer
    @swagger_auto_schema(
        operation_description="특정 떨이 상품의 상세 정보를 조회합니다.",
        operation_summary="떨이 상품 상세 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', SaleProductDetailSerializer),
            404: "해당 상품을 찾을 수 없습니다.",
            500: "서버 오류입니다."
        },
        tags=["떨이상품"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="떨이 상품의 ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        # Swagger 스키마 생성 중일 때는 빈 쿼리셋 반환
        if getattr(self, 'swagger_fake_view', False):
            return SaleProduct.objects.none()

        sale_product_pk = self.kwargs['pk']  # URL에서 떨이 상품 pk 가져오기
        return get_object_or_404(SaleProduct, pk=sale_product_pk)  # SaleProduct 모델에서 해당 pk 객체 찾기, 없으면 404 반환


# 가게별 떨이 상품 목록 조회
class SaleProductStoreListView(generics.ListAPIView):
    serializer_class = SaleProductListSerializer
    queryset = Order.objects.none()  # 기본 빈 쿼리셋 설정
    @swagger_auto_schema(
        operation_description="특정 가게의 떨이 상품 목록을 조회합니다.",
        operation_summary="가게별 떨이 상품 목록 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', SaleProductListSerializer(many=True)),
            404: "해당 가게를 찾을 수 없습니다.",
            500: "서버 오류입니다."
        },
        tags=["떨이상품"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="가게의 ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)    
    def get_queryset(self): #오버라이딩
        # Swagger 스키마 생성 중일 때는 빈 쿼리셋 반환
        if getattr(self, 'swagger_fake_view', False):
            return SaleProduct.objects.none()
        store_pk_par = self.kwargs['pk']  # URL에서 store pk 가져오기
        
        # Store 모델에 해당 pk가 존재하는지 확인
        store = get_object_or_404(Store, pk=store_pk_par)
        queryset = SaleProduct.objects.filter(store=store)
        
        if not queryset.exists():
            raise NotFound(detail="해당 가게에 대한 떨이 상품이 존재하지 않습니다.")
        
        return queryset
    
# 검색 기능
class SearchView(generics.ListAPIView):
    @swagger_auto_schema(
        operation_description="가게 이름, 타입 또는 떨이 상품 이름으로 검색 결과를 반환합니다.",
        operation_summary="검색 결과",
        responses={
            200: openapi.Response('검색 결과를 성공적으로 반환했습니다.', StoreListSerializer(many=True)),
            404: "검색 결과가 없습니다.",
            500: "서버 오류입니다."
        },
        tags=["구매자"],
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="검색어", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)    
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Store.objects.none()
        query = self.request.GET.get('q')  # 검색에서 파라미터 가져오기
        if query:
            results = []
            if Store.objects.filter(name__icontains=query).exists(): #가게이름과 부분일치 하는 것이 있으면
                stores = Store.objects.filter(name__icontains=query) #기본적으로 가게 리스트를 반환함
                results = list(stores) 
            elif Store.objects.filter(type__icontains=query).exists(): #가게에 일치하는게 없는데, 가게 타입과 일치해도 가게 리스트 반환
                stores = Store.objects.filter(type__icontains=query)
                results = list(stores)
            elif SaleProduct.objects.filter(name__icontains=query).exists(): #마지막으로 떨이 상품 이름과 비교
                saleproducts = SaleProduct.objects.filter(name__icontains=query)
                results = list(saleproducts)
            return results
        else:
            return []

    def get_serializer_class(self):
        query = self.request.GET.get('q')  # 검색에서 파라미터 가져오기
        if query:
            if Store.objects.filter(Q(name__icontains=query) | Q(type__icontains=query)).exists():  # Store 모델에서 검색어와 일치하는 항목이 있는지 확인
                return StoreListSerializer  # Store 모델의 시리얼라이저 반환
            elif SaleProduct.objects.filter(Q(name__icontains=query)).exists():  # SaleProduct 모델에서 검색어와 일치하는 항목이 있는지 확인
                return SaleProductListSerializer  # SaleProduct 모델의 시리얼라이저 반환
        return StoreListSerializer  # 기본적으로 StoreSerializer 반환
    
    def list(self, request, *args, **kwargs): # 검색 결과 없음 반환
        queryset = self.get_queryset()  
        if not queryset:
            return Response({"detail": "검색결과 없음"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)