from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('buyer/', include('buyer.urls')), # buyer 앱의 URL 패턴 포함
    path('store/', include('store.urls')), # store 앱 url 연결
    path('dashboard/', include('dashboard.urls')) #대시보드 앱 url연결
]
