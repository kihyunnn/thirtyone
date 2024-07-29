from django.utils import timezone, timedelta #시간 함수 사용
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
        today = datetime.today()
        # 지난달 시작 날짜 계산
        start_date = today.replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
        # 지난달 마지막 날짜 계산
        end_date = today.replace(day=1) - timedelta(days=1)
        
        
        # 오늘의 판매 실적 필터링
        today_sales = SaleRecord.objects.filter(date=today,sale_product__store__pk=store_pk_par)
        # 오늘 판매한 떨이 개수와 수입 계산
        today_sales_count = today_sales.aggregate(Sum('amount'))['amount__sum'] or 0
        today_sales_income = today_sales.aggregate(total_income=Sum(F('amount') * F('sale_product__sale_price')))['total_income'] or 0

        # 지정된 날짜(1일~30일) 범위 내의 판매 실적 필터링
        sales_date_range = SaleRecord.objects.filter(date__range=(start_date, end_date),sale_product__store__pk=store_pk_par)
        # 지난달 판매한 떨이 개수와 수입 계산
        month_sales_count = sales_date_range.aggregate(Sum('amount'))['amount__sum'] or 0
        month_sales_income = sales_date_range.aggregate(total_income=Sum(F('amount') * F('sale_product__sale_price')))['total_income'] or 0

        # 결과 반환
        data = {
            'today_sales_count': today_sales_count,
            'today_sales_income': today_sales_income,
            'month_sales_count': month_sales_count,
            'month_sales_income': month_sales_income,
        }
        # 정리된 데이터를 HTTP 200 OK 상태와 함께 반환
        return Response(data, status=status.HTTP_200_OK)