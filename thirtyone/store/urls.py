from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('create/', views.create_store, name='create_store'), # store 앱 url 연결
    path('home/', views.view_store, name='home'),
    # 우리가 파리바게트 판매자를 기준으로 홈화면 띄우기로 했어서 이렇게 함
]