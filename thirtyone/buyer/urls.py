from django.urls import path
from .views import *

urlpatterns = [
    path('create', BuyerCreateView.as_view(), name='buyer-create'),
]
