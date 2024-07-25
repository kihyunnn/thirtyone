from django.db import models

# Create your models here.

class Store(models.Model): # 판매자 모델 정의
    store_name = models.CharField(max_length=50) # 가게 이름
    store_photo = models.ImageField(upload_to='store_phothos/') # 가게 사진
    address = models.CharField(max_length=255) #가게 주소
    open_time = models.TimeField() # 가게 오픈 시간
    close_time = models.TimeField() # 가게 마감시간
    tel = models.CharField(max_length=255) # 가게 전화번호

    def __str__(self): 
        return self.name
