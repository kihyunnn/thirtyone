from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis 사용을 예로 듭니다.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'

# 개발 단계에서 정적 파일의 위치
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 개발 환경에서 허용할 호스트 설정
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
