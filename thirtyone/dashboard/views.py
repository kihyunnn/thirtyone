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


class SalesSummaryView(APIView):
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