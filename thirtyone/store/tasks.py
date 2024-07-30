# tasks.py

from celery import shared_task
from django.utils import timezone
from .models import Order, SaleProduct

# check_order_status라는 비동기 작업을 정의
# 이 작업은 예약된 시간마다 실행되어 특정 조건을 만족하는 주문 처리
@shared_task
def check_order_status():
    now = timezone.now()
    time_limit = now - timezone.timedelta(minutes=30)
    # 30분 전의 시간을 계산
    
    orders = Order.objects.filter(buy_step=Order.OrderStepCategory.PICKUP_PEND, accept_at__lt=time_limit)
    # Order.accept_at 시간이 time_limit 보다 작은 객체 필터링
    for order in orders: # 해당 객체의 buy_step을 자동취소로 바꿈
        order.buy_step = Order.OrderStepCategory.AUTO_CANCEL
        sale_product_pk = order.sale_product
        sale_product = SaleProduct.objects.get(pk=sale_product_pk)
        sale_product += order.amount # 자동취소되면 해당 수량 다시 떨이상품에 업데이트 시킴
        order.save()
