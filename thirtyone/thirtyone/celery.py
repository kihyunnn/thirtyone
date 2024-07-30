# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# 환경 변수에서 DJANGO_SETTINGS_MODULE 설정을 가져오거나 기본값으로 'your_project.settings.debug'를 사용
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thirtyone.settings.debug')

app = Celery('thirtyone')

# Django의 설정을 Celery에 적용
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django의 INSTALLED_APPS에서 task를 자동으로 찾아서 로드
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
