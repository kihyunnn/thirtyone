from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('summary/<int:pk>', views.SalesSummaryView, name="sale_summary") # 맨위에 요약 4개 조회
]