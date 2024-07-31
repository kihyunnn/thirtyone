from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# 가게 등록
@swagger_auto_schema(
    method="post",
    tags=["가게"],
    operation_summary="가게등록",
    operation_description="가게등록을 처리합니다.",
    request_body=CreateStoreSerializer,
    responses={
        201: '가게등록 성공',
        400: '잘못된 요청',
    }
)
@api_view(['POST'])
def create_store(request):
    serializer = CreateStoreSerializer(data=request.data)
    if serializer.is_valid():
        store = serializer.save()
        return Response({"message": "create store successful"}, status=201)
    return Response(serializer.errors, status=400)

# 판매자 페이지
@swagger_auto_schema(
    method="get",
    tags=["가게"],
    operation_summary="판매자 페이지",
    operation_description="판매자 페이지를 처리합니다.",
    responses={
        201: StoreSerializer,
        404: 'Store not found'
    }
)
@api_view(['GET'])
def view_store(request): 
    store = get_object_or_404(Store, id=1)
    # store id 값 1로 고정해줌(파리바게트 인하대점)
    serializer = StoreSerializer(store)
    return Response(serializer.data, status=200)

# 떨이 상품 등록
@swagger_auto_schema(
    method="post",
    tags=["떨이상품"],
    operation_summary="떨이상품 등록",
    operation_description="떨이상품 등록을 처리합니다.",
    request_body=CreateSaleProductSerializer,
    responses={
        201: '떨이상품 최초 등록 성공',
        200: '떨이상품 업데이트 성공',
        400: '잘못된 요청',
    }
)
@api_view(['POST'])
def create_product(request, pk):
    store = get_object_or_404(Store, pk=pk)
    name = request.data.get('name')
    sale_product, created  = SaleProduct.objects.get_or_create(store=store, name=name)
    
    if created:
        serializer = CreateSaleProductSerializer(sale_product, data=request.data)
    else :
        serializer = CreateSaleProductSerializer(sale_product, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        if created:
            return Response({'message': 'Sale product created successfully.', 'data': serializer.data}, status=201)
        else:
            return Response({'message': 'Sale product updated successfully.', 'data': serializer.data}, status=200)
        
    return Response(serializer.errors, status=400)


# 등록 상품 목록
@swagger_auto_schema(
    method="get",
    tags=["떨이상품"],
    operation_summary="등록 상품 목록",
    operation_description="등록 상품 목록을 처리합니다.",
    responses={
        200: '성공',
        404: 'Store not found'
    }
)
@api_view(['GET'])
def list_product(request, pk):
    store = get_object_or_404(Store, pk=pk)
    products = SaleProduct.objects.filter(store=store)
    return Response({'products': list(products.values()), 'store_name':store.name}, status=200)


# 판매내역
@swagger_auto_schema(
    method="get",
    tags=["판매"],
    operation_summary="판매내역",
    operation_description="판매내역을 처리합니다.",
    responses={
        200: '성공',
        404: 'Store not found'
    }
)
@api_view(['GET'])
def list_purchase(request, pk):
    store = get_object_or_404(Store, pk=pk)
    orders = Order.objects.filter(store=store)
    serializer = OrderSerializer(orders, many=True)
    return Response({'products': serializer.data, 'store_name':store.name}, status=200)


# 주문 수락 및 거절 등
@swagger_auto_schema(
    method="patch",
    tags=["판매"],
    operation_summary="주문 수락 및 거절",
    operation_description="주문 수락 및 거절을 처리합니다.",
    responses={
        200: '성공',
        400: '실패'
    }
)
@api_view(['PATCH'])
def order_update(request, pk, order_id):
    try:
        store = Store.objects.get(pk=pk)
        order = Order.objects.get(pk=order_id, store=store)
    except Store.DoesNotExist:
        return Response({"error": "Store not found"}, status=404)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        sale_product_name = order.sale_product
        sale_product = SaleProduct.objects.get(store=store, name=sale_product_name)

        if serializer.validated_data.get('buy_step') == Order.OrderStepCategory.PICKUP_PEND: # 주문수락
            order.accept_at = timezone.now()
            order.reject_at = order.accept_at + timedelta(minutes=30) # 수락시간 + 30분 = 자동 주문 취소 시간
            sale_product.amount -= order.amount # 주문수락하면 떨이 수량 감소시키기
            order.save()
            sale_product.save()

        if serializer.validated_data.get('buy_step') == Order.OrderStepCategory.PICUP_COMP: # 픽업완료
            today = datetime.date.today()
            sale_record = SaleRecord.objects.get(date=today, sale_product=sale_product)
            sale_record.selled_amount += order.amount
            sale_record.save()

        if serializer.validated_data.get('buy_step') == Order.OrderStepCategory.AUTO_CANCEL: # 주문 자동취소
            sale_product.amount += order.amount # 자동취소되면 해당 수량 다시 떨이상품에 업데이트 시킴
            sale_product.save()

        serializer.save()
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)