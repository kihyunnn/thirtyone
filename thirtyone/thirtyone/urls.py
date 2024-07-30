from django.contrib import admin
from django.urls import path,include

# 정적 파일 설정
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('buyer/', include('buyer.urls')), # buyer 앱의 URL 패턴 포함
    path('store/', include('store.urls')) # store 앱 url 연결
]

# 미디어 파일 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 정적 파일 설정 (개발 환경에서만)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # 배포에서는 STATIC_ROOT