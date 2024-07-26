from django.db import models
import string #가게 번호 코드 부여하려고 추가함
from buyer.models import Buyer #주문서에 구매자 pk넣기위해서

# Create your models here.

#판매자 코드 생성 함수
def generate_code():
    used_codes = Store.objects.values_list('code', flat=True)# 이미 사용된 코드들 집합으로 만듦
    for letter in string.ascii_uppercase:
        if letter not in used_codes:
            return letter
    raise ValueError("모든 알파벳 코드를 사용했습니다.")


# 기본 StoreType 생성 함수
#밑에 Store에서 StoreType 외래키로 받을 때 default 값을 1로 했을 떄 StoreType에 객체가 먼저 생성이 안되어서 오류가 생겨서 일케함
# def get_default_store_type_id():
#     store_type, created = StoreType.objects.get_or_create(part=StoreType.StoreCategory.FRUITS_VEGETABLES)
#     return store_type.id


#가게 업종 모델 StoreType
# class StoreType(models.Model):
#     class StoreCategory(models.TextChoices):
#         FRUITS_VEGETABLES = 'FRV', '과일 및 야채'
#         BUTCHER_SHOP = 'BUT', '정육점'
#         BAKERY = 'BAK', '베이커리'
#         SIDE_DISH_STORE = 'SID', '반찬 가게'
#         SEAFOOD_STORE = 'SEA', '수산물 가게'
#         RICE_CAKE_SHOP = 'RIC', '떡 가게'
#         PREPARED_FOOD = 'PRE', '조리 식품'
#         SNACKS = 'SNA', '간식류'

#     part = models.CharField(
#         max_length=3,  # 최대 3자까지 허용(FRV이런거)
#         choices=StoreCategory.choices, # 선택지를 StoreCategory 클래스에서 가져옴
#         default=StoreCategory.FRUITS_VEGETABLES, # 기본값을 '과일 및 야채'로 설정
#     )

#     def __str__(self):
#         return self.get_part_display()  # 선택된 값의 레이블 반환


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

    # 판매자(Store) : 가게업종(StoreType) = N : 1
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)


    #새로운 Store객체를 저장 할 때, store_code가 없으면, 다시 호출해서 설정함
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code() #고유 알파벳 코드 설정
        super().save(*args, **kwargs) # save메서드 호출해서 객체 저장


    def __str__(self): 
        return self.name


#상품 카테고리 모델 ProductType
# class ProductType(models.Model):
#     class ProductCategory(models.TextChoices):
#         BAKERY = 'BAK', '빵 & 간식류'
#         BUTCHER_SHOP = 'BUT', '정육 제품'
#         FRUITS = 'FRU', '과일류'
#         VEGETABLES = 'VEG', '채소류'
#         SIDE_DISH_STORE = 'SID', '반찬 가게'
#         SNACKS = 'ETC', '기타'

#     part = models.CharField(
#         max_length=3,  # 최대 3자까지 허용(BAK이런거)
#         choices=ProductCategory.choices, # 선택지를 ProductCategory 클래스에서 가져옴
#         default=ProductCategory.BAKERY, # 기본값을 '빵 & 간식류'로 설정
#     )


#     def __str__(self):
#         return self.name


#떨이상품 모델 SaleProduct 
class SaleProduct(models.Model):
    TYPE_CHOICES = [
        ('BAK', '빵 & 간식류'),
        ('BUT', '정육 제품'),
        ('FRU', '과일류'),
        ('VEG', '채소류'),
        ('SID', '반찬 가게'),
        ('BUT', '정육점'),
        ('ETC', '기타'),
    ]
    name = models.CharField(max_length=255) # 떨이 상품명
    amount = models.IntegerField() # 떨이 수량
    photo = models.ImageField(upload_to='SaleProduct_phothos') # 떨이 상품 사진
    price = models.IntegerField() # 상품 정가
    sale_price = models.IntegerField() # 상품 할인가
    content = models.TextField() # 상품 설명

    # 판매자(Store) : 떨이상품(SaleProduct) = 1 : N
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    #상품 카테고리(ProductType) : 떨이 상품(SaleProduct)   = 1 : N
    product_type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name  # 선택된 값의 레이블 반환



#상품 실적 모델 SaleRecord
class SaleRecord(models.Model):
    date = models.DateField() #날짜 저장 (시간 저장 안되도 ㄱㅊ으려나??)
    amount = models.IntegerField() # 상품별 당일 수량 저장

    #떨이 상품(SaleProduct) : 상품 실적(SaleRecord) = 1 : N
    sale_product = models.ForeignKey(SaleProduct, on_delete=models.CASCADE)

    def __str__(self):
        return self.amount    


#주문 모델 Order
class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # 주문서 생성 시간 작성
    # 주문서 번호, A1,A2이런거 근데 가게마다 A를 고유로 부여하고, 가게 기준 주문서가 A1,A2쌓이도록 함
    order_number = models.CharField(max_length=10, unique=True, editable=False) 
    #판매자(Store) : 주문(Order) = 1 : N
    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # 가게 외래키
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE,default=1)  # 구매자 외래키

    class OrderStepCategory(models.TextChoices): # 구매 처리 단계를 위한 클래스
        PICKUP_PEND = 'PIC', '픽업대기중'
        RES_PEND = 'RES', '예약확인중'
        AUTO_CANCEL = 'AUT', '자동취소'
        PICUP_COMP = 'COM', '픽업완료'
        ORDER_REJ = 'REJ', '주문거절'
    buy_step = models.CharField(
        max_length=3,  # 최대 3자까지 허용
        choices=OrderStepCategory.choices, # 선택지를  OrderStepCategory 클래스에서 가져옴
        default=OrderStepCategory.PICKUP_PEND, # 기본값을 '픽업대기중'으로 설정
    )

    

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
        super().save(*args, **kwargs) #객체 저장





