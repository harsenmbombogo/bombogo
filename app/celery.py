# app/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from decouple import config
from .tasks import agendar_viagem_diaria, fechar_agenda_viagem


# Define o ambiente de configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bombogo.settings')

REDIS_URL = config('REDIS_URL', "redis://localhost:6379")

# Cria a instância do Celery
app = Celery('app', broker=REDIS_URL)

# Carrega as configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuração de tarefas periódicas
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executar `agendar_viagem_diaria` a cada 24 horas
    sender.add_periodic_task(24 * 60 * 60, agendar_viagem_diaria.s(), name='Agendar Viagem Diária')

    # Executar `fechar_agenda_viagem` a cada 1 hora
    sender.add_periodic_task(60 * 60, fechar_agenda_viagem.s(), name='Fechar Agenda de Viagem')


app.conf.broker_connection_retry_on_startup = True  # Adiciona esta linha

# Descobre e registra automaticamente as tarefas de todos os apps do projeto Django
app.autodiscover_tasks()