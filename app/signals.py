from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=ViagemAssento)
@receiver(post_delete, sender=ViagemAssento)
def update_total_assentos(sender, instance, **kwargs):
    viagem = instance.viagem
    # Conta quantos assentos existem associados à viagem
    total_assentos = ViagemAssento.objects.filter(viagem=viagem).count()
    total_assentos_disponiveis = ViagemAssento.objects.filter(viagem=viagem, disponivel=True).count()
    
    # Atualiza o campo total_assento da viagem
    viagem.total_assento = total_assentos
    viagem.total_assentos_disponiveis=total_assentos_disponiveis
    viagem.save()


@receiver(post_save, sender=Bilhete)
@receiver(post_delete, sender=Bilhete)
def update_total_assentos(sender, instance, **kwargs):
    
    viagem = instance.viagem
    # Conta quantos assentos existem associados à viagem
    # ViagemAssento.objects.filter(disponivel=False).update(disponivel=True)
    total_assentos = ViagemAssento.objects.filter(viagem=viagem).count()
    total_assentos_disponiveis = ViagemAssento.objects.filter(viagem=viagem, disponivel=True).count()
    
    # Atualiza o campo total_assento da viagem
    viagem.total_assento = total_assentos
    viagem.total_assentos_disponiveis=total_assentos_disponiveis
    viagem.save()


# Sinal para deletar o usuário ao deletar o agente
@receiver(post_delete, sender=Agente)
def delete_user_with_agente(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()


# Sinal para deletar o usuário ao deletar o operador
@receiver(post_delete, sender=Operador)
def delete_user_with_operador(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()

# Sinal para deletar o usuário ao deletar o cliente
@receiver(post_delete, sender=Cliente)
def delete_user_with_cliente(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
