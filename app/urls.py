# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'operadores', OperadorViewSet)
router.register(r'empresas', EmpresaViewSet)
router.register(r'pontovendas', PontoVendaViewSet)
router.register(r'rotas', RotasViewSet)
router.register(r'operador_agente_crud', OperadorAgenteViewSet)
router.register(r'viagens', ViagemViewSet)
router.register(r'viagem-assentos', ViagemAssentoViewSet)
router.register(r'terminais', TerminaisNacionaisViewSet)
router.register(r'metodos-pagamentos', AppMetodoPagamentoViewSet)
router.register(r'taxas-descontos', DescontoBilheteViewSet)
router.register(r'vendas', VendaBilheteViewSet)
router.register(r'bilhetes', BilheteViewSet)
router.register(r'perguntas-frequentes', PerguntasFrequentesViewSet)
router.register(r'perguntas_frequentes_agente', PerguntasFrequentesAgenteViewSet)
router.register(r'perguntas_frequentes_operador', PerguntasFrequentesOperadorViewSet)


urlpatterns = [
    path('', home.index, name='index'),
    path('app_operador/', ConfiguracoesAppOperadorView.as_view(), name='app_operador'),
    path('app_agente/', ConfiguracoesAppAgenteView.as_view(), name='app_agente'),
    path('app_cliente/', ConfiguracoesAppClienteView.as_view(), name='app_cliente'),
    path('buscar_viagens/', ViagemListView.as_view(), name='viagem_list'),
    path('', include(router.urls)),  # Inclui as URLs do router
    path('empresa/<int:empresa_id>/rotas/', EmpresaRotasView.as_view(), name='empresa_rotas'),
    path('empresa/<int:empresa_id>/viagens/', EmpresaViagensView.as_view(), name='empresa_viagens'),
    path('empresa/<int:pk>/avaliacoes_estatisticas/', ClassificacaoEmpresaStatisticsView.as_view(), name='valiacoes_estatisticas'),
    path('empresa/<int:pk>/avaliacoes/', ClassificacaoEmpresaListView.as_view(), name='empresa_avaliacoes'),
    path('viagem/<int:viagem_id>/assentos/', AssentoViagemView.as_view(), name='viagem_assentos'),

    # Bilhetes
    path('viagem/vender_bilhete/', VenderBilheteListCreateView.as_view(), name='vendabilhete_create'),
    path('viagem/comprar_bilhete/', BilheteListCreateView.as_view(), name='bilhete_list_create'),
    path('viagem/bilhete/<int:pk>/', BilheteDetailView.as_view(), name='bilhete_detail'),
    path('viagem/obter_bilhetes/', BilhetesClienteView.as_view(), name='obter_bilhetes'),
    path('cliente/metodos-pagamentos/', ClienteMetodosPagamantos.as_view(), name='cliente_metodos_pagamantos'),

    # Verificar se já classificou a viagem
    path('cliente/classificacao_viagem_create/', ClassificarViagemCreate.as_view(), name='cliente_classif_create'),
    path('cliente/<int:pk>/verificacao_classificacao/', ClassificarViagemExiste.as_view(), name='cliente_metodos_pagamantos'),
    # Fim classificacao
    
    path('cliente/metodos-pagamentos-create/', ClienteMetodosPagamantosCreateView.as_view(), name='cliente_metodos_pagamantos-create'),
    path('cliente/<int:pk>/metodo-pagamento-update/', ClienteMetodoPagamentoUpdateView.as_view(), name='cliente_metodo_pagamento_update'),
    path('cliente/<int:pk>/metodo-pagamento-delete/', ClienteMetodoPagamentoDeleteView.as_view(), name='cliente_metodo_pagamento_delete'),
    path('update-token-device/', UpdateTokenDeviceView.as_view(), name='update_token_device'),



    # Fim Bilhetes
    path('user/check_exists_username/', VerificarUserNameView.as_view(), name='check_exists_username'),
    path('user/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('user/new_password/', NewPasswordView.as_view(), name='new_password'),
    path('login/', LoginView.as_view(), name='login'),  # Endpoint para login
    path('register/', UserCreateView.as_view(), name='cadastrar_usuario'),  # Endpoint para cadastro de usuário
    path('user/', UserDetailView.as_view(), name='user-detail'),  # Nova rota
    path('user/update/', UserUpdateClienteView.as_view(), name='user-update'),  # Nova rota

    # ================================Profissional==============================
    
    path('profissional/login/', LoginProfissView.as_view(), name='login_profissional'),  # Endpoint para login
    path('agente/register/', UserCreateView.as_view(), name='cadastrar_usuario'),  # Endpoint para cadastro de usuário
    path('agente/user/', UserDetailView.as_view(), name='user-detail'),  # Nova rota
    path('agente/user/update/', UpdateUserAgenteView.as_view(), name='user_agente_update'),  # Nova rota
    path('operador/user/update/', UpdateUserOperadorView.as_view(), name='user_operador_update'),  # Nova rota
    
    
    # Dashboard Operador
    path('operador/empresa/', EmpresaOperadorView.as_view(), name='operador_empresa'),
    path('operador/estatisticas/', EstatisticasOperadorView.as_view(), name='operador_empresa_estatisticas'),

    path('operador/agente/venda_semanais/', OperadorVendasAgentesSemanaisView.as_view(), name='operador_agente_venda_semanais'),
    path('operador/agente/venda_mensais/', OperadorVendasAgentesMensaisView.as_view(), name='operador_agente_venda_mensais'),

    path('operador/rota/venda_semanais/', OperadorVendasRotasSemanaisView.as_view(), name='operador_rota_venda_semanais'),
    path('operador/rota/venda_mensais/', OperadorVendasRotasMensaisView.as_view(), name='operador_rota_venda_mensais'),
    
    # Fim Dashboard

    path('operador/meus_agentes/', MeusAgentesOperadorView.as_view(), name='operador_empresa_meus_agentes'),
    path('operador/ponto_venda/create/', OperadorPontosVendaCreateView.as_view(), name='operador_ponto_venda_create'),
    path('operador/<int:pk>/ponto_venda/', OperadorPontosVendaUpdateDeleteView.as_view(), name='operador_ponto_venda_create_update'),
    path('operador/pontos_vendas/', OperadorPontosVendaListView.as_view(), name='operador_pontos_vendas'),
    path('operador/rotas/', OperadorRotasListView.as_view(), name='operador_rotas'),
    path('operador/agentes/rotas/', OperadorAgentesRotasView.as_view(), name='operador_agentes_rotas'),
    path('operador/rota/create/', OperadorRotaCreateView.as_view(), name='operador_rota_create'),
    path('operador/<int:pk>/rota/', OperadorRotaRetrieveUpdateDestroyView.as_view(), name='operador_rota_detail_update_delete'),
    
    path('operador/ponto_intermedio/create/', OperadorPontoIntermedioCreateView.as_view(), name='operador_ponto_intermedio_create'),
    path('operador/<int:pk>/ponto_intermedio/', OperadorPontoIntermedioRetrieveUpdateDestroyView.as_view(), name='operador_ponto_intermedio_detail_update_delete'),
    path('operador/<int:pk>/rota/pontos_intermediarios/', OperadorPontoIntermediarioListView.as_view(), name='operador_pontos_intermediarios'),

    # Obter numero de rotas por agente
    path('operador/<int:pk>/agente/rotas/', OperadorAgenteRotasView.as_view(), name='agente_rota'),

    # Obter actividades dos agentes
    path('operador/<int:pk>/agente/actividades/', OperadorAgenteRotasView.as_view(), name='operador_agente_rota'),
    path('operador/<int:pk>/agente/estatistica_ontem/', OperadorEstatisticasAgenteOntemView.as_view(), name='operador_estatisticas_ontem_agente'),
    path('operador/<int:pk>/agente/estatisticas/', OperadorEstatisticasAgenteView.as_view(), name='operador_estatisticas_agente'),
    path('operador/<int:pk>/agente/estatistica_semanal/', OperadorEstatisticasAgenteSemanalView.as_view(), name='operador_estatisticas_semanal_agente'),
    path('operador/<int:pk>/agente/estatistica_mensal/', OperadorEstatisticasAgenteMensalView.as_view(), name='operador_estatisticas_mensal_agente'),

    # Reservas por agente
    path('operador/<int:pk>/agente/reservas_ontem/', OperadorReservasBilhetesAgenteOntemView.as_view(), name='operador_reserva_ontem_agente'),
    path('operador/<int:pk>/agente/reservas/', OperadorReservasBilhetesAgenteDiarioView.as_view(), name='operador_reservas_agente'),
    path('operador/<int:pk>/agente/reservas_semanal/', OperadorReservasBilhetesAgenteSemanalView.as_view(), name='operador_reserva_semanal_agente'),
    path('operador/<int:pk>/agente/reservas_mensal/', OperadorReservasBilhetesAgenteMensalView.as_view(), name='operador_reserva_mensal_agente'),
    # Fim reservas por agente

    path('operador/<int:pk>/agente/estatisticas_semanais/', OperadorEstatisticaAgenteVendasSemanaisView.as_view(), name='operador_estatisticas_agente_semanais'),
    path('operador/<int:pk>/agente/reservas_estatisticas/', OperadorEstatisticasAgenteReservasView.as_view(), name='operador_agente_reservas_estatisticas'),  # Endpoint para login
    path('operador/<int:pk>/agente/proximas_reservas/', OperadorAgenteProximasReservasBilhetesView.as_view(), name='operador_agente_proximas_reservas'),  # Endpoint para login
    path('operador/<int:pk>/agente/viagens_anteriores/', OperdaorAgenteProximaViagemOntemView.as_view(), name='operador_agente_viagens_anteriores'),
    path('operador/<int:pk>/agente/proximas_viagens/', OperdaorAgenteProximaViagemView.as_view(), name='operador_agente_proximas_viagens'),  # Endpoint para login
    path('operador/<int:pk>/agente/viagens_posteriores/', OperdaorAgenteProximaViagemAmanhaView.as_view(), name='operador_agente_viagens_posteriores'),  # Endpoint para login
    # Reservas
    path('operador/reservas/estatistica_diaria/', EstatisticasReservasDiariasOperadorView.as_view(), name='operador_reservas_estatisticas'),
    path('operador/reservas/estatistica_semanal/', EstatisticasReservasSemanalOperadorView.as_view(), name='operador_reservas_estatisticas'),
    path('operador/reservas/estatistica_mensal/', EstatisticasReservasMensalOperadorView.as_view(), name='operador_reservas_estatisticas'),
    path('operador/reservas_diarias/', OperadorReservasBilhetesDiarioView.as_view(), name='operador_reservas_diarias'),
    path('operador/reservas_semanais/', OperadorReservasBilhetesSemanalView.as_view(), name='operador_reservas_semanal'),
    path('operador/reservas_mensais/', OperadorReservasBilhetesMensalView.as_view(), name='operador_reservas_mensal'),

    # Fim reservas


    path('operador/<int:pk>/agente/checkin_viagens/', OperadorAgenteCheckinViagensView.as_view(), name='operador_agente_checkin_viagens'),  # Endpoint para login
    path('viagem/<int:pk>/classificacoes/', ClassificacaoViagemListCreateView.as_view(), name='classificacao-viagem-list-create'),
    path('viagem/<int:pk>/estatisticas/', ClassificacaoViagemStatisticsView.as_view(), name='classificacao-viagem-statistics'),
    path('viagem/<int:pk>/classificacao/', ClassificacaoViagemDetailUpdateView.as_view(), name='classificacao-viagem-detail-update'),

    # 
    path('operador/metodos_pagamentos/', OperadorMetodosPagamantos.as_view(), name='cliente_metodos_pagamantos'),
    path('operador/metodos_pagamentos_create/', OperadorMetodosPagamantosCreateView.as_view(), name='cliente_metodos_pagamantos-create'),
    path('operador/<int:pk>/metodo_pagamento_update/', OperadorMetodoPagamentoUpdateView.as_view(), name='cliente_metodo_pagamento_update'),
    path('operador/<int:pk>/metodo_pagamento_delete/', OperadorMetodoPagamentoDeleteView.as_view(), name='cliente_metodo_pagamento_delete'),
   

    #==================================== Agente==================================
    path('agente/rotas/', AgenteRotasView.as_view(), name='agente_rota'),
    path('agente/rota/<int:pk>/viagens/', AgenteRotaViagensView.as_view(), name='agente_rota_viagens'),
    path('agente/rota/<int:pk>/viagem/', AgenteRotaViagemView.as_view(), name='agente_rota_viagem'),

    # Inicio estatisticas de agente
    path('agente/estatisticas/', EstatisticasReservasDiariasAgenteView.as_view(), name='estatisticas_diarias'),
    path('agente/estatisticas_semanais/', EstatisticasReservasSemanalAgenteView.as_view(), name='estatisticas_semanais'),
    path('agente/estatisticas_mensais/', EstatisticasReservasMensalAgenteView.as_view(), name='estatisticas_mensais'),
    # Fim estatisticas de agente

    path('agente/rota/viagem/<int:pk>/bilhetes/', AgenteRotaViagemBilhetesView.as_view(), name='agente_rota_viagem-bilhetes'),
    path('agente/rota/viagem/<int:pk>/bilhete/', AgenteRotaViagemBilheteView.as_view(), name='agente_rota_viagem-bilhete'),
    path('agente/rota/viagem/<int:pk>/assentos/', AgenteRotaViagemAssentosView.as_view(), name='agente_rota_viagem_assentos'),
    path('agente/rota/viagem/assento/update/', AgenteRotaViagemAssentoUpdateView.as_view(), name='agente_rota_viagem_assento_update'),
    path('agente/rota/viagem/bilhete/update/', AgenteRotaViagemBilheteUpdateView.as_view(), name='agente_rota_viagem_bilhete_update'),
    path('agente/vendas_diarias_bilhetes/', AgenteVendasDiariasBilhetesView.as_view(), name='agente_venda_diarias'),  # Endpoint para login
    path('agente/proximas_viagens/', AgenteProximaViagemView.as_view(), name='agente_proximas_viagens'), 
    path('agente/<int:pk>/viagem_vendas_diarias/', AgenteViagemReservaBilhetesView.as_view(), name='agente_viagem_vendas_diarias'),  # Endpoint para login
    path('agente/relatorio_vendas/', AgenteRelatoriosBilhetesView.as_view(), name='agente_relatorio_vendas'),  # Endpoint para login
    path('agente/proximas_reservas/', AgenteProximasReservasBilhetesView.as_view(), name='agente_proximas_reservas'),  # Endpoint para login
    path('agente/reservas_estatisticas/', EstatisticasAgenteReservasView.as_view(), name='agente_reservas_estatisticas'),  # Endpoint para login
    path('agente/<int:pk>/viagem/', AgenteReservaViagemGetView.as_view(), name='agente_viagem_reserva'),  # Endpoint para login
    path('agente/<int:pk>/agenda_viagem/', AgenteAgendaViagemGetView.as_view(), name='agente_viagem_reserva'),
    path('agente/checkin_viagens/', AgenteCheckinViagensView.as_view(), name='agente_checkin_viagens'),  # Endpoint para login
    path('agente/<int:pk>/checkin_viagem/', AgenteCheckinViagemPassageiroView.as_view(), name='agente_checkin_viagem'),  # Endpoint para login
    path('agente/checkin_list_passageiros/', AgenteCheckinListPassageiroView.as_view(), name='agente_checkin_list_passageiros'),  # Endpoint para login
    path('agente/bilhete/checkin_passageiro_update/', AgenteCheckinPassageiroUpdateView.as_view(), name='agente_checkin_passageiro_update'),  # Endpoint para login



]
