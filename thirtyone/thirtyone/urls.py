from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg       import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="thirtyone-project",
        default_version='1.0',
        description="thirtyone-project API 문서)",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="likelion@inha.edu"), # 부가정보
        license=openapi.License(name="backend"),     # 부가정보
    ),
    public=True,
    permission_classes=(AllowAny,),
)

# 정적 파일 설정
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('buyer/', include('buyer.urls')), # buyer 앱의 URL 패턴 포함
    path('store/', include('store.urls')), # store 앱 url 연결
    path('dashboard/', include('dashboard.urls')), #대시보드 앱 url연결
    # Swagger url
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# 미디어 파일 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 정적 파일 설정 (개발 환경에서만)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # 배포에서는 STATIC_ROOT