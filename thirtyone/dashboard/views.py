import datetime
from django.utils import timezone 
from django.db.models import Q, Sum, F, FloatField, ExpressionWrapper
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
# Create your views here.
from store.serializers import *
from store.models import SaleProduct, SaleRecord
from .serializers import *
#스웨거를 위한 import
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# 대시보드 요약 4개정보 반환 
class SalesSummaryView(APIView):
    @swagger_auto_schema(
        operation_description="특정 가게의 대시보드 요약 정보를 반환합니다.",
        operation_summary="대시보드 요약 정보 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'today_sales_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='오늘 판매한 떨이 개수'),
                    'today_sales_income': openapi.Schema(type=openapi.TYPE_INTEGER, description='오늘 판매 수익'),
                    'month_sales_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='지난달 판매한 떨이 개수'),
                    'month_sales_income': openapi.Schema(type=openapi.TYPE_INTEGER, description='지난달 판매 수익'),
                }
            )),
            400: "잘못된 요청입니다.",
            404: "가게를 찾을 수 없습니다.",
            500: "서버 오류입니다."
        },
        tags=["대시보드"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="가게의 ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        store_pk_par = self.kwargs['pk']  # URL에서 store pk 가져오기


        # 오늘 날짜
        today = datetime.datetime.now().date()
        # 지난달 시작 날짜 계산
        start_date = today.replace(day=1) - datetime.timedelta(days=1)
        start_date = start_date.replace(day=1)
        # 지난달 마지막 날짜 계산
        end_date = today.replace(day=1) - datetime.timedelta(days=1)
                
        # 오늘의 판매 실적 필터링 및 total_income 필드 추가
        today_sales_query = SaleRecord.objects.filter(date=today, sale_product__store__pk=store_pk_par).annotate(
            sale_product_income=F('selled_amount') * F('sale_product__sale_price')
        )
        # 오늘 판매한 떨이 개수 총합
        today_sales_count =today_sales_query.aggregate(Sum('selled_amount'))['selled_amount__sum'] or 0
        # 임시 필드를 만들어서 그 필드 안에 그 상품의 팔린개수 x 할인판매금액을 넣어둠 / 하루계산용
        today_sales_income = today_sales_query.aggregate(total_income=Sum('sale_product_income'))['total_income'] or 0
        # 임시 필드를 만들어서 그 필드 안에 그 상품의 팔린개수 x 할인판매금액을 넣어둠 / 한달 계산용
        month_sales_query = SaleRecord.objects.filter(date__range=(start_date, end_date),sale_product__store__pk=store_pk_par).annotate(
            sale_product_income_m=F('selled_amount') * F('sale_product__sale_price')
        )
        # 지난달 판매한 떨이 개수와 수입 계산
        month_sales_count = month_sales_query.aggregate(Sum('selled_amount'))['selled_amount__sum'] or 0
        month_sales_income = month_sales_query.aggregate(total_income=Sum('sale_product_income_m'))['total_income'] or 0


        print(today_sales_query)  # 쿼리셋 확인
        for record in today_sales_query:
            print(record.selled_amount, record.sale_product.sale_price, record.sale_product_income)  # 각 필드 확인
        print(today_sales_count)  # 총 판매 개수 확인
        print(today_sales_income)  # 총 판매 금액 확인

        
        # 결과 반환
        data = {
            'today_sales_count': today_sales_count,
            'today_sales_income': today_sales_income,
            'month_sales_count': month_sales_count,
            'month_sales_income': month_sales_income
        }
        # 정리된 데이터를 HTTP 200 OK 상태와 함께 반환
        return Response(data, status=status.HTTP_200_OK)
    
# 지난주 떨이 상품 판매 순위 조회
class SelledRankListView(generics.ListAPIView):
    queryset = SaleRecord.objects.all()
    serializer_class = TopSoldProductSerializer
    @swagger_auto_schema(
        operation_description="지난주 떨이 상품 판매 순위를 조회합니다.",
        operation_summary="지난주 떨이 상품 판매 순위 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', TopSoldProductSerializer(many=True)),
            400: "잘못된 요청입니다.",
            404: "가게를 찾을 수 없습니다.",
            500: "서버 오류입니다."
        },
        tags=["대시보드"],
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="가게의 ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # Swagger 스키마 생성 중일 때 빈 쿼리셋 반환
            return SaleRecord.objects.none()
        
        # 현재 날짜 가져오기
        today = datetime.datetime.now().date()
        # 이번 주 월요일 계산
        this_week_monday = today - datetime.timedelta(days=today.weekday())
        # 지난주 월요일 계산
        last_week_monday = this_week_monday - datetime.timedelta(days=7)
        # 지난주 일요일 계산
        last_week_sunday = last_week_monday + datetime.timedelta(days=6)
        
        store_pk = self.kwargs['pk'] # url에서 구매자 pk 가져오기
        last_week_sales = SaleRecord.objects.filter(
        date__gte = last_week_monday,
        date__lte = last_week_sunday,
        sale_product__store__id=store_pk
        ).values('sale_product').annotate(total_selled=Sum('selled_amount')).order_by('-total_selled')[:5]
        
        return last_week_sales

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # SaleProduct 인스턴스 가져오기 및 직렬화
        sale_product_ids = [sale['sale_product'] for sale in queryset]
        sale_products = SaleProduct.objects.filter(id__in=sale_product_ids)
        
        # 각 상품에 대한 정보를 직렬화하고, total_selled 값을 추가
        ranked_products = []
        for sale_data in queryset:
            product = next((p for p in sale_products if p.id == sale_data['sale_product']), None)
            if product:
                product_data = TopSoldProductSerializer(product).data
                product_data['total_selled'] = sale_data['total_selled']
                ranked_products.append(product_data)
                
        return Response(ranked_products)

# 판매 추이 조회
class SaleTrendListView(generics.ListAPIView):
    serializer_class = SaleTrendSerializer
    queryset = SaleRecord.objects.none()  # 기본 빈 쿼리셋 설정
    
    @swagger_auto_schema(
        operation_description="특정 가게와 제품의 판매 추이를 조회합니다.",
        operation_summary="판매 추이 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', SaleTrendSerializer(many=True)),
            400: "잘못된 요청입니다.",
            404: "가게 또는 제품을 찾을 수 없습니다.",
            500: "서버 오류입니다."
        },
        tags=["대시보드"],
        manual_parameters=[
            openapi.Parameter('storepk', openapi.IN_PATH, description="가게의 ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('productpk', openapi.IN_PATH, description="제품의 ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # Swagger 스키마 생성 중일 때 빈 쿼리셋 반환
            return SaleRecord.objects.none()
        
        store_pk = self.kwargs['storepk']  # URL에서 store_pk 가져오기
        product_pk = self.kwargs['productpk']  # URL에서 sale_product_pk 가져오기

        # 현재 날짜 가져오기
        today = datetime.datetime.now().date()
        # 7일 전 날짜
        last_week_day = today - datetime.timedelta(days=7)
        # 어제 날짜
        yesterday = today - datetime.timedelta(days=1)

        return SaleRecord.objects.filter(
            date__range=(last_week_day, yesterday),
            sale_product__store__id=store_pk,
            sale_product__pk=product_pk,
        ).order_by('date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # 필터링된 쿼리셋 가져오기

        # 시리얼라이저 인스턴스 생성
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data  # 시리얼라이즈된 데이터 가져오기
        print(data)  # 쿼리셋 확인
        return Response(data, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method="get",
    tags=["대시보드"],
    operation_summary="가장 많이(적게), 떨이 등록대비 많이(적게) 팔린 상품",
    operation_description="가장 많이(적게), 떨이 등록대비 많이(적게) 팔린 상품을 처리합니다.",
    responses={
        200: '성공'
    }
)
@api_view(['GET'])
def advice_product(request, store_pk):
    # 현재 날짜 가져오기
    today = datetime.datetime.now().date()
    # 이번 주 월요일 계산
    this_week_monday = today - datetime.timedelta(days=today.weekday())
    # 지난주 월요일 계산
    last_week_monday = this_week_monday - datetime.timedelta(days=7)
    # 지난주 일요일 계산
    last_week_sunday = last_week_monday + datetime.timedelta(days=6)

    last_week_sales = SaleRecord.objects.filter(
        date__gte = last_week_monday,
        date__lte = last_week_sunday,
        sale_product__store__id=store_pk
    ).values('sale_product').annotate(total_selled=Sum('selled_amount')).order_by('-total_selled')
    # 지난주 월-일: 팔린 수량의 총합으로 많은순으로 정렬
    most_sold_product = last_week_sales.first() # 가장 많이 팔린 상품
    least_sold_product = last_week_sales.last() # 가장 적게 팔린 상품

    # 각 sale_product의 SaleProduct 인스턴스 가져오기
    most_sold_product_instance = SaleProduct.objects.get(pk=most_sold_product['sale_product'])
    least_sold_product_instance = SaleProduct.objects.get(pk=least_sold_product['sale_product'])

    # 각 상품에 대한 정보를 직렬화하고, total_selled 값을 추가
    most_sold_product_data = AdviceSaleProductSerializer(most_sold_product_instance).data
    most_sold_product_data['total_selled'] = most_sold_product['total_selled']

    least_sold_product_data = AdviceSaleProductSerializer(least_sold_product_instance).data
    least_sold_product_data['total_selled'] = least_sold_product['total_selled']


    last_week_sales_based_post = SaleRecord.objects.filter(
        date__gte = last_week_monday,
        date__lte = last_week_sunday,
        sale_product__store__id=store_pk
    ).values('sale_product').annotate(
        total_selled=Sum('selled_amount'),
        total_posted=Sum('amount'),
        selled_based_post=ExpressionWrapper(
            (Sum('selled_amount') * 100.0) / Sum('amount'),
            output_field=FloatField()
        )
    ).order_by('-selled_based_post')
    # 떨이 등록 대비 가장 많이(적게) 팔린 상품들 정렬
    most_based_post_product = last_week_sales_based_post.first()
    least_based_post_product = last_week_sales_based_post.last()

    most_based_post_instance = SaleProduct.objects.get(pk=most_based_post_product['sale_product'])
    least_based_post_instance = SaleProduct.objects.get(pk=least_based_post_product['sale_product'])

    most_sold_based_post_data = SelledAmountBasedPostSerializer(most_based_post_instance).data
    most_sold_based_post_data['total_selled'] = most_based_post_product['total_selled']
    most_sold_based_post_data['total_posted'] = most_based_post_product['total_posted']
    most_sold_based_post_data['percent_selled'] = most_based_post_product['selled_based_post']

    least_sold_based_post_data = SelledAmountBasedPostSerializer(least_based_post_instance).data
    least_sold_based_post_data['total_selled'] = least_based_post_product['total_selled']
    least_sold_based_post_data['total_posted'] = least_based_post_product['total_posted']
    least_sold_based_post_data['percent_selled'] = least_based_post_product['selled_based_post']

    response_data = {
        "most_selled": most_sold_product_data,
        "least_selled": least_sold_product_data,
        "most_based_post": most_sold_based_post_data,
        "least_based_post": least_sold_based_post_data,
    }

    return Response(response_data, status=200)