# app/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from decouple import config


# Define o ambiente de configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bombogo.settings')

REDIS_URL = config('REDIS_URL', "redis://localhost:6379")

# Cria a instância do Celery
app = Celery('bombogo', broker=REDIS_URL)

# Carrega as configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.broker_connection_retry_on_startup = True  # Adiciona esta linha

# Descobre e registra automaticamente as tarefas de todos os apps do projeto Django
app.autodiscover_tasks()