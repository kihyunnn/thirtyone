from django.contrib import admin
from django.urls import path, include
from .views import * #view의 모든 함수 사용

urlpatterns = [
    path('summary/<int:pk>', SalesSummaryView.as_view(), name="sale_summary"), # 맨위에 요약 4개 조회
    path('rank/<int:pk>', SelledRankListView.as_view(), name="selled_rank") # 저번주 판매내역 순위 조회
]
