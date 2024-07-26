from django.urls import path
from .views import * #view의 모든 함수 사용

urlpatterns = [
    path('create', BuyerCreateView.as_view(), name='buyer-create'),
    path('<int:pk>/pick', OrderCreateView.as_view, name='Order-create')
]
