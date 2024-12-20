import os
import django

# Defina a variável de ambiente para o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bomboapi.settings') # Ajuste para o caminho correto do seu projeto

# Inicie o Django
django.setup()

# Agora você pode importar o FCMDevice
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification

# Use o FCMDevice para enviar notificações
device = FCMDevice.objects.all().first()
if device:
    message = Message(notification=Notification(title='Título', body='Corpo da Mensagem'))
    device.send_message(message)
else:
    print("Nenhum dispositivo encontrado.")
