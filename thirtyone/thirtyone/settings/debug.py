from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 개발 단계에서 정적 파일의 위치
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

