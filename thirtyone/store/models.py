from django.db import models
import string #가게 번호 코드 부여하려고 추가함
from buyer.models import Buyer #주문서에 구매자 pk넣기위해서
from django.utils import timezone #주문 수락 시간추가위해서
# Create your models here.

#판매자 코드 생성 함수
def generate_code():
    used_codes = Store.objects.values_list('code', flat=True)# 이미 사용된 코드들 집합으로 만듦
    for letter in string.ascii_uppercase:
        if letter not in used_codes:
            return letter
    raise ValueError("모든 알파벳 코드를 사용했습니다.")



# 판매자 모델 정의
class Store(models.Model): 
    # 가게업종은 생각해보니까 store에서만 쓰고 한가게에 하나의 업종만 선택 가능해서 이렇게 해줌
    # 약간 회원에서 성별 선택 같은 느낌(..?)
    # 원래 방법대로 하니까 admin에서 가게등록 오류가 뜸..
    # 혹시 몰라서 원래 모델은 주석처리 해둠
    TYPE_CHOICES = [
        ('FRV', '과일 및 야채'),
        ('BUT', '정육점'),
        ('BAK', '베이커리'),
        ('SID', '반찬 가게'),
        ('SEA', '수산물 가게'),
        ('BUT', '정육점'),
        ('RIC', '떡 가게'),
        ('SNA', '간식류'),
    ]
    name = models.CharField(max_length=50) # 가게 이름
    photo = models.ImageField(upload_to='store_phothos/') # 가게 사진
    address = models.CharField(max_length=255) #가게 주소
    open_time = models.TimeField() # 가게 오픈 시간
    close_time = models.TimeField() # 가게 마감시간
    tel = models.CharField(max_length=255) # 가게 전화번호
    latitude = models.FloatField(default=0.0)  # 위도
    longitude = models.FloatField(default=0.0)  # 경도
    code = models.CharField(max_length=1, unique=True, editable=False)  # 가게 고유 알파벳 코드
    type = models.CharField(max_length=3, choices=TYPE_CHOICES) #가게 업종


    #새로운 Store객체를 저장 할 때, store_code가 없으면, 다시 호출해서 설정함
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code() #고유 알파벳 코드 설정
        super().save(*args, **kwargs) # save메서드 호출해서 객체 저장


    def __str__(self): 
        return self.name


#떨이상품 모델 SaleProduct 
class SaleProduct(models.Model):
    TYPE_CHOICES = [
        ('BAK', '빵 & 간식류'),
        ('BUT', '정육 제품'),
        ('FRU', '과일류'),
        ('VEG', '채소류'),
        ('SID', '반찬 가게'),
        ('ETC', '기타'),
    ]
    name = models.CharField(max_length=255) # 떨이 상품명
    amount = models.IntegerField(default=0) # 떨이 수량
    photo = models.ImageField(upload_to='SaleProduct_phothos', null=True) # 떨이 상품 사진
    price = models.IntegerField(default=0) # 상품 정가
    sale_price = models.IntegerField(default=0) # 상품 할인가
    content = models.TextField() # 상품 설명
    product_type = models.CharField(max_length=3, choices=TYPE_CHOICES) #상품카테고리 선택
    # 판매자(Store) : 떨이상품(SaleProduct) = 1 : N
    store = models.ForeignKey(Store, on_delete=models.CASCADE) # 판매자 Store의 외래키


    def __str__(self):
        return self.name  # 선택된 값의 레이블 반환



#상품 실적 모델 SaleRecord
class SaleRecord(models.Model):
    date = models.DateField() #날짜 저장 
    amount = models.IntegerField(default=0) # 상품별 당일 수량 저장

    #떨이 상품(SaleProduct) : 상품 실적(SaleRecord) = 1 : N
    sale_product = models.ForeignKey(SaleProduct, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.sale_product.name} - {self.date}'    


#주문 모델 Order
class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # 주문서 생성 시간 작성
    # 주문서 번호, A1, A2이런거 근데 가게마다 A를 고유로 부여하고, 가게 기준 주문서가 A1,A2쌓이도록 함
    order_number = models.CharField(max_length=10, unique=True, editable=False) 
    #판매자(Store) : 주문(Order) = 1 : N
    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # 가게 외래키
    #구매자(Buyer) : 주문(Order) = 1 : N 
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE,default=1)  # 구매자 외래키
    #떨이상품(SaleProduct) : 주문(Order) = 1: N 
    sale_product = models.ForeignKey(SaleProduct,on_delete=models.CASCADE)
    amount = models.IntegerField(default=0) #주문 수량
    class OrderStepCategory(models.TextChoices): # 구매 처리 단계를 위한 클래스
        RES_PEND = 'RES', '예약확인중'
        PICKUP_PEND = 'PIC', '픽업대기중'
        AUTO_CANCEL = 'AUT', '자동취소'
        PICUP_COMP = 'COM', '픽업완료'
        ORDER_REJ = 'REJ', '주문거절'
    buy_step = models.CharField(
        max_length=3,  # 최대 3자까지 허용
        choices=OrderStepCategory.choices, # 선택지를  OrderStepCategory 클래스에서 가져옴
        default=OrderStepCategory.RES_PEND, # 기본값을 '예약확인중'으로 설정
    )
    accept_at = models.DateTimeField(null=True, blank=True) #픽업대기중으로 수정된 시간
    

    #주문서 번호 생성 로직
    def save(self, *args, **kwargs):
        if not self.order_number: #order_number가 없으면
            # 동일한 가게에 대한 마지막 주문서를 가져옴
            last_order = Order.objects.filter(store=self.store).order_by('-created_at').first() 
            
            if last_order: #마지막 주문이 있으면
                last_order_number = int(last_order.order_number[1:])  # 마지막 주문서 번호에서 숫자 부분 추출
                new_order_number = last_order_number + 1
            #마지막 주문서가 없는 경우 = 첫 주문 일 때
            else:
                new_order_number = 1
            # 가게의 고유 코드(store_code)와 새로운 순차 번호를 결합하여 주문서 번호 생성
            self.order_number = f"{self.store.code}{new_order_number}"

        if self.pk:  # 객체가 이미 존재하는 경우
            old_order = Order.objects.get(pk=self.pk)  # 기존 객체를 데이터베이스에서 가져옴
            # 기존 객체의 buy_step와 현재 객체의 buy_step가 다르고, 현재 buy_step가 RES_PEND인 경우
            if old_order.buy_step != self.buy_step and self.buy_step == self.OrderStepCategory.RES_PEND:
                self.accept_at = timezone.now()  # accept_at 필드에 현재 시간을 기록


        super().save(*args, **kwargs) #객체 저장
    
    #Order에 str 반환 빼먹어서 추가
    def __str__(self):
        return f"Order {self.order_number} for {self.buyer}"




