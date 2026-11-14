import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spaimadincarpat_djangochallenge_hard.settings')

app = Celery('spaimadincarpat_djangochallenge_hard')
# Configurează Celery să ia setările din settings.py care încep cu 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')
# Descoperă automat task-urile din toate aplicațiile
app.autodiscover_tasks()