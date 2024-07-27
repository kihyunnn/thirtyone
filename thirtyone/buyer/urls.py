from django.urls import path
from .views import * #view의 모든 함수 사용

urlpatterns = [
    path('create', BuyerCreateView.as_view(), name='buyer-create'), # 구매자 생성
    path('<int:pk>/pick', OrderCreateView.as_view(), name = 'Order-create'), # 구매자 주문서 생성
    path('purchase/list', OrderLisetView.as_view(), name = 'Order-list'), # 주문서 리스트 목록 조회
    path('category/<str:product_type>/list', SaleProductCateListView.as_view(), name= 'SaleProductCate-list'), # 카테고리별 떨이상품 리스트 조회
    path('product/<int:pk>', SaleProductDetailView.as_view(), name = 'SaleProductDetail-view'), # 떨이 상품 상세조회
    path('store/<int:pk>/list', SaleProductStoreListView.as_view(), name = 'SaleProductStore - list') # 가게별 떨이 상품 리스트 조회
]
