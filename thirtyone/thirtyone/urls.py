from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('buyer/', include('buyer.urls'))  # buyer 앱의 URL 패턴 포함
]