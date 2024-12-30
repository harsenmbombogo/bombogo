from django.contrib import admin
from .models import *


class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('pk','dono', 'nome_empresa', 'nuit', 'numero_telefone', 'slogan', 'sede', 'classificacao_media')


class ClienteClassificaoAdmin(admin.ModelAdmin):
    list_display = ('pk','viagem', 'cliente','comentario', 'rating')


class PontoIntermedioAdmin(admin.ModelAdmin):
    list_display = ('pk','terminal', 'endereco','preco')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'numero_telefone', 'data_cadastro')

class OperadorAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'numero_telefone', 'data_cadastro')

class AgenteAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'empresa', 'data_cadastro')

class RotasAdmin(admin.ModelAdmin):
    list_display = ('pk','agente','empresa', 'origem', 'destino', 'preco', 'hora_saida', 'hora_chegada')

class BilheteAdmin(admin.ModelAdmin):
    list_display = ('pk','venda','viagem', 'assento', 'cliente', 'nome_passageiro', 'status_bilhete', 'status_viagem', 'data_criado', 'hora_criado')

class ViagemAdmin(admin.ModelAdmin):
    list_display = ('pk','agente',"rota", 'data_fecho', 'total_assento', 'total_assentos_disponiveis', 'data_saida', 'data_chegada')

class ViagemAssentoAdmin(admin.ModelAdmin):
    list_display = ('pk','viagem', 'assento', 'disponivel', 'data_criado')

class PerguntasFrequentesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'pergunta', 'resposta', 'data_cadastro')



# Register your models here with ModelAdmin
admin.site.register(ClassificacaoViagem, ClienteClassificaoAdmin)
admin.site.register(PontoIntermediario, PontoIntermedioAdmin)
admin.site.register(PerguntasFrequentes, PerguntasFrequentesAdmin)
admin.site.register(PerguntasFrequentesAgente, PerguntasFrequentesAdmin)
admin.site.register(PerguntasFrequentesOperador, PerguntasFrequentesAdmin)
admin.site.register(AppMetodoPagamento)
admin.site.register(ClienteMetodoPagamento)
admin.site.register(ConfiguracoesAppCliente)
admin.site.register(ConfiguracoesAppAgente)
admin.site.register(ConfiguracoesAppOperador)
admin.site.register(VendaBilhete)
admin.site.register(DescontoBilhete)
admin.site.register(TerminaisNaconais)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(PontoVenda)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Operador, OperadorAdmin)
admin.site.register(Agente, AgenteAdmin)
admin.site.register(Rotas, RotasAdmin)
admin.site.register(Bilhete, BilheteAdmin)
admin.site.register(Viagem, ViagemAdmin)
admin.site.register(ViagemAssento,ViagemAssentoAdmin)#, ViagemAssentoAdmin)
