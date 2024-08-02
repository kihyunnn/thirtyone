import datetime
from django.utils import timezone 
from django.db.models import Q, Sum, F 
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
    serializer_class = SelledRankSerializer
    @swagger_auto_schema(
        operation_description="지난주 떨이 상품 판매 순위를 조회합니다.",
        operation_summary="지난주 떨이 상품 판매 순위 조회",
        responses={
            200: openapi.Response('성공적으로 조회되었습니다.', SelledRankSerializer(many=True)),
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
        return SaleRecord.objects.filter(date__range=(last_week_monday, last_week_sunday),sale_product__store__id=store_pk, selled_amount__gt=0).order_by('-selled_amount')[:5]
        # 조건 : 저번주 월욜~ 일욜 / url에 pk와 같은 떨이상품 pk를 가지고있는 SaleRecord / seeld_amount가 양수일것 / 오름차순 정렬 / 5개까지만 반환

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