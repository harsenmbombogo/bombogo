from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from datetime import timedelta, datetime
from celery import shared_task
from .models import Rotas, Viagem, ViagemAssento, Agente
import logging

logger = logging.getLogger(__name__)

# Função principal para agendar viagens diárias
def agendar_viagem_diaria():
    data_atual = timezone.now().date()
    messages = []
    agentes = Agente.objects.all()

    logger.debug("Iniciando o agendamento de viagens diárias.")

    with transaction.atomic():
        for agente in agentes:
            logger.debug(f"Processando agente {agente}.")
            rotas = agente.rota_agente.all()  # Verifique o nome correto do campo de relação

            mensagens_novas = criar_novas_viagens(rotas, agente, data_atual)
            messages.extend(mensagens_novas)

    return "\n".join(messages)


def criar_novas_viagens(rotas, agente, data_atual):
    mensagens = []
    novas_viagens = []

    viagens_existentes = Viagem.objects.filter(
        rota__in=[rota.id for rota in rotas],
        data_saida__gte=data_atual,
        data_saida__lte=data_atual + timedelta(days=7)
    ).values_list('rota_id', 'data_saida')

    viagens_existentes_set = set(viagens_existentes)

    for rota in rotas:
        for i in range(7):
            data_viagem = data_atual + timedelta(days=i)
            data_chegada = data_viagem + timedelta(days=rota.duracao) if rota.duracao > 1 else data_viagem
            data_fecho = timezone.make_aware(datetime.combine(data_viagem, datetime.min.time()).replace(hour=3, minute=30))

            if (rota.id, data_viagem) in viagens_existentes_set:
                viagens_para_deletar = Viagem.objects.filter(rota=rota, data_saida=data_viagem)
                if viagens_para_deletar.exists():
                    viagens_para_deletar.delete()
                    print("Viagens deletadas com sucesso.")

                mensagens.append(f"Viagem já existe para a rota {rota.id} na data {data_viagem}.")
                logger.debug(f"Viagem já existente para rota {rota.id} na data {data_viagem}.")
                continue

            try:
                viagem = Viagem(
                    empresa=rota.empresa,
                    agente=agente,
                    rota=rota,
                    data_saida=data_viagem,
                    hora_saida=rota.hora_saida,
                    data_chegada=data_chegada,
                    hora_chegada=rota.hora_chegada,
                    data_fecho=data_fecho,
                    total_assento=61,
                    total_assentos_disponiveis=61,
                    duracao_viagem=calcular_duracao(data_viagem, data_chegada, rota.hora_saida, rota.hora_chegada)
                )
                
                novas_viagens.append(viagem)
                
            except Exception as e:
                mensagens.append(f"Erro ao criar viagem para a rota {rota.id} na data {data_viagem}: {str(e)}")
                logger.error(f"Erro ao criar viagem para a rota {rota.id} na data {data_viagem}: {str(e)}")

        Assentos(novas_viagens, mensagens)

    return mensagens


def Assentos(novas_viagens, mensagens):
    try:
        # Cria as viagens em lote
        viagens = Viagem.objects.bulk_create(novas_viagens, batch_size=30)
        print("Viagens", viagens)
        mensagens.append("Viagens criadas com sucesso.")
        

        # Busca novamente as viagens para garantir IDs consistentes
        novas_viagens_criadas = Viagem.objects.filter(
            empresa__in=[viagem.empresa for viagem in viagens],
            agente__in=[viagem.agente for viagem in viagens],
            data_saida__in=[viagem.data_saida for viagem in viagens]
        )

        # Cria os assentos para cada viagem
        for viagem in novas_viagens_criadas:
            try:
                criar_assentos(viagem, viagem.rota.capacidade_assentos)
                mensagens.append(f"Assentos criados para a viagem {viagem.pk}.")
            except Exception as e:
                mensagens.append(f"Erro ao criar assentos para a viagem {viagem.pk}: {str(e)}")
                logger.error(f"Erro ao criar assentos para a viagem {viagem.pk}: {str(e)}")
    except Exception as e:
        mensagens.append(f"Erro ao criar viagens em lote: {str(e)}")
        logger.error(f"Erro ao criar viagens em lote: {str(e)}")


def criar_assentos(viagem, capacidade_assentos, batch_size=30):
    if capacidade_assentos <= 0:
        logger.error(f"Capacidade de assentos inválida para a viagem {viagem.id}: {capacidade_assentos}")
        raise ValueError(f"Capacidade de assentos inválida para a viagem {viagem.id}")
    
    # Criando os assentos
    assentos = [ViagemAssento(viagem=viagem, assento=assento_num) for assento_num in range(1, capacidade_assentos + 1)]
    
    # Agora realizando a criação em lotes
    try:
        for i in range(0, len(assentos), batch_size):
            ViagemAssento.objects.bulk_create(assentos[i:i + batch_size])
            logger.debug(f"Assentos {i} a {i + batch_size} criados para a viagem {viagem.id}.")
    except Exception as e:
        logger.error(f"Erro ao criar assentos em lote para a viagem {viagem.id}: {str(e)}")
        raise


def calcular_duracao(data_saida, data_chegada, hora_saida, hora_chegada):
    if not (data_saida and data_chegada and hora_saida and hora_chegada):
        return "Duração inválida"

    datetime_saida = datetime.combine(data_saida, hora_saida)
    datetime_chegada = datetime.combine(data_chegada, hora_chegada)
    duracao = datetime_chegada - datetime_saida

    dias, segundos = duracao.days, duracao.seconds
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60

    if dias == 0 and horas == 0 and minutos == 0:
        return "Menos de um minuto"

    partes = []
    if dias > 0:
        partes.append(f"{dias} dia{'s' if dias > 1 else ''}")
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}min")

    return " ".join(partes)


if __name__ == "__main__":
    agendar_viagem_diaria()
