# serializers.py
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},  # Se for opcional
        }

    def create(self, validated_data):
        user = User(**validated_data)
        password = validated_data.pop('password', None)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Se o username foi alterado, verificar se já existe
        new_username = validated_data.get('username', instance.username)

        if new_username != instance.username:
            # Se o username foi alterado, verificar unicidade
            if User.objects.filter(username=new_username).exists():
                raise serializers.ValidationError({"username": "Já existes um utilizador com esse nome."})

        # Atualiza os campos restantes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance

class ConfiguracoesAppClienteSerializer(serializers.ModelSerializer):
    logotipo_url = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracoesAppCliente
        fields = ['id', 'nome_app','logotipo_url', 'descricao_app', 'politica_privacidade_app', 'termos_condicoes_app']

    def get_logotipo_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.logotipo_app.url) if obj.logotipo_app else None


class ConfiguracoesAppOperadorSerializer(serializers.ModelSerializer):
    logotipo_url = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracoesAppOperador
        fields = ['id', 'nome_app','logotipo_url', 'descricao_app', 'politica_privacidade_app', 'termos_condicoes_app']

    def get_logotipo_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.logotipo_app.url) if obj.logotipo_app else None



class ConfiguracoesAppAgenteSerializer(serializers.ModelSerializer):
    logotipo_url = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracoesAppAgente
        fields = ['id', 'nome_app','logotipo_url', 'descricao_app', 'politica_privacidade_app', 'termos_condicoes_app']

    def get_logotipo_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.logotipo_app.url) if obj.logotipo_app else None



class ClienteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cliente
        fields = ['id', 'numero_telefone', 'nome_familiar','contacto_familiar', 'endereco']
        extra_kwargs = {
            'foto_perfil': {'required': False}  # Defina como opcional caso a imagem não seja obrigatória
        }


class UserClienteSerializer(serializers.ModelSerializer):
    # cliente = ClienteSerializer(read_only=True)
    nome_familiar = serializers.SerializerMethodField()
    contacto_familiar = serializers.SerializerMethodField()
    numero_telefone = serializers.SerializerMethodField()
    foto_perfil = serializers.SerializerMethodField()
    endereco = serializers.SerializerMethodField()


    def get_numero_telefone(self,obj):
        return obj.cliente.numero_telefone if obj.cliente else ""
    
    def get_nome_familiar(self,obj):
        return obj.cliente.nome_familiar if obj.cliente else ""
    
    def get_contacto_familiar(self,obj):
        return obj.cliente.contacto_familiar if obj.cliente else ""
    
    def get_foto_perfil(self,obj):
        return obj.cliente.foto_perfil.url if obj.cliente.foto_perfil else ""
    
    def get_endereco(self,obj):
        return obj.cliente.endereco if obj.cliente else ""


    class Meta:
        model = User
        fields = ['id','numero_telefone', 'foto_perfil','endereco', 'contacto_familiar','nome_familiar','username', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}  # Para garantir que a senha só será usada para escrita

    def create(self, validated_data):
        # Usa o método set_password para garantir que a senha seja salva de forma segura
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserClienteSerializer, self).create(validated_data)


class OperadorSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Inclui o serializer do User para manipular dados do usuário

    class Meta:
        model = Operador
        fields = ['id', 'user', 'numero_telefone',  'endereco', 'data_cadastro']

    def to_representation(self, instance):
        # Serializa dados do Agente e User em uma única estrutura
        data = super().to_representation(instance)
        user_data = data.pop('user')
        
        # Mescla dados do User e Agente
        merged_data = {**user_data, **data}
        return merged_data


class EmpresaSerializer(serializers.ModelSerializer):
    logotipo_url = serializers.SerializerMethodField()

    class Meta:
        model = Empresa
        fields = ['id', 'dono','logotipo_url','numero_telefone', 'nome_empresa','nuit', 'logotipo', 'slogan', 'classificacao_media', 'sede', 'data_cadastro']
        read_only_fields = ['id', 'classificacao_media', 'data_cadastro']


    def get_logotipo_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.logotipo.url) if obj.logotipo else None


class RotasSerializer(serializers.ModelSerializer):
    local_origem = serializers.SerializerMethodField()
    local_destino = serializers.SerializerMethodField()

    class Meta:
        model = Rotas
        fields = ['id', 'empresa', 'local_origem', 'local_destino', 'preco', 'duracao', 'hora_saida', 'hora_chegada']


    def get_local_origem(self, obj):
        return obj.origem.nome if obj.origem else ""
    
    def get_local_destino(self, obj):
        
        return obj.destino.nome if obj.destino else ""
    

class ViagemSerializer(serializers.ModelSerializer):
    empresa = serializers.SerializerMethodField()
    empresa_id = serializers.SerializerMethodField()
    local_origem = serializers.SerializerMethodField()
    local_destino = serializers.SerializerMethodField()
    endereco_origem = serializers.SerializerMethodField()
    endereco_destino = serializers.SerializerMethodField()
    preco = serializers.SerializerMethodField()

    # Campos de data personalizados
    data_fecho = serializers.SerializerMethodField()
    data_saida = serializers.SerializerMethodField()
    data_chegada = serializers.SerializerMethodField()
    hora_saida = serializers.SerializerMethodField()
    hora_chegada = serializers.SerializerMethodField()
    data_cadastro = serializers.SerializerMethodField()

    def get_local_origem(self, obj):
        return obj.rota.origem.nome if obj.rota else ""
    
    def get_local_destino(self, obj):
        return obj.rota.destino.nome if obj.rota else ""
    
    def get_endereco_origem(self, obj):
        return obj.rota.origem.endereco if obj.rota else ""
    
    def get_endereco_destino(self, obj):
        return obj.rota.destino.endereco if obj.rota else ""

    def get_preco(self, obj):
        return obj.rota.preco if obj.rota else 0.0

    # Formatando as datas manualmente
    def get_data_fecho(self, obj):
        return obj.data_fecho.strftime("%Y-%m-%d %H:%M:%S") if obj.data_fecho else ""

    def get_data_saida(self, obj):
        return obj.data_saida.strftime("%d-%m-%Y") if obj.data_saida else ""

    def get_data_chegada(self, obj):
        return obj.data_chegada.strftime("%d-%m-%Y") if obj.data_chegada else ""

    def get_hora_saida(self, obj):
        return obj.hora_saida.strftime("%H:%M") if obj.hora_saida else ""

    def get_hora_chegada(self, obj):
        return obj.hora_chegada.strftime("%H:%M") if obj.hora_chegada else ""


    def get_data_cadastro(self, obj):
        return obj.data_cadastro.strftime("%d-%m-%Y %H:%M:%S") if obj.data_cadastro else ""

    def get_empresa(self, obj):
        return obj.empresa.nome_empresa if obj.empresa else ""
    
    def get_empresa_id(self, obj):
        return obj.empresa.pk if obj.empresa else 0


    class Meta:
        model = Viagem
        fields = ['id','empresa', 'preco', 'empresa_id', 'duracao_viagem', 'hora_saida', 'hora_chegada', 'local_origem', 'local_destino', 'total_assento',
                  'data_fecho', 'total_assentos_disponiveis', 'data_saida', 'endereco_origem','endereco_destino',
                  'data_chegada', 'contacto', 'activo','data_cadastro']


class ClassificacaoViagemSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.user.get_full_name', read_only=True)
    data= serializers.SerializerMethodField()

    class Meta:
        model = ClassificacaoViagem
        fields = ['id', 'viagem', 'cliente', 'cliente_nome', 'rating', 'comentario', 'data']

    def get_data(self, obj):
        # Formata a data como "27 de fevereiro de 2022"
        return obj.data_classificacao.strftime('%d de %B de %Y').capitalize()

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("O rating deve ser entre 1 e 5.")
        return value

    def create(self, validated_data):
        return super().create(validated_data)

    

class ViagemAssentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViagemAssento
        fields = ['pk','assento', 'disponivel', 'data_criado']



class BilheteSerializer(serializers.ModelSerializer):
    nome_empresa = serializers.CharField(source='empresa.nome_empresa', default="", read_only=True)
    embarque_origem = serializers.CharField(source='viagem.rota.origem.endereco', default="", read_only=True)
    desembarque_destino = serializers.CharField(source='viagem.rota.destino.endereco', default="", read_only=True)
    nuit_empresa = serializers.CharField(source='empresa.nuit', default="", read_only=True)
    sede_empresa = serializers.CharField(source='empresa.sede', default="", read_only=True)
    classif = serializers.CharField(source='empresa.classificacao_media', default="", read_only=True)
    numero_conta=serializers.CharField(source='venda.metodo_pagamento.numero_pagamento', default="", read_only=True)
    metodo_pagamento=serializers.CharField(source='venda.metodo_pagamento.agencia', default="", read_only=True)
    logotipo_empresa = serializers.SerializerMethodField()
    qrcode_url = serializers.SerializerMethodField()
    data_saida = serializers.SerializerMethodField()
    hora_saida = serializers.SerializerMethodField()
    data_criado = serializers.SerializerMethodField()
    hora_criado = serializers.SerializerMethodField()

    def get_data_criado(self, obj):
        return obj.data_criado.strftime("%d-%m-%Y") if obj.data_criado else ""
    
    def get_hora_criado(self, obj):
        return obj.hora_criado.strftime("%H:%M") if obj.hora_criado else ""
    
    def get_data_saida(self, obj):
        return obj.viagem.data_saida.strftime("%d-%m-%Y") if obj.viagem.data_saida else ""

    def get_hora_saida(self, obj):
        return obj.viagem.hora_saida.strftime("%H:%M") if obj.viagem.hora_saida else ""
    



    def get_logotipo_empresa(self, obj):
        request = self.context.get('request')
        if request and obj.empresa and obj.empresa.logotipo:
            return request.build_absolute_uri(obj.empresa.logotipo.url)
        return None
    

    def get_qrcode_url(self, obj):
        request = self.context.get('request')
        if request and obj.qrcode:
            return request.build_absolute_uri(obj.qrcode.url)
        return None


    class Meta:
        model = Bilhete
        fields = [
            'id',
            'sede_empresa',
            'embarque_origem',
            'desembarque_destino',
            'nome_empresa',
            'nuit_empresa',
            'hora_saida',
            'venda',
            'motivo',
            'viagem',
            'logotipo_empresa',
            'empresa',
            'cliente',
            'qrcode_url',
            'origem',
            'destino',
            'status_bilhete',
            'status_viagem',
            'assento',
            'nome_passageiro',
            'contacto_passageiro',
            'nome_familiar',
            'contacto_familiar',
            'metodo_pagamento',
            'numero_conta',
            'preco',
            'data_saida',
            'duracao',
            'contacto_empresa',
            'classif',
            'referencia',
            'data_criado',
            'hora_criado',
        ]



class EmpresaRotasSerializer(serializers.ModelSerializer):
    rotas = RotasSerializer(many=True, read_only=True, source='empresa_rota')
    
    class Meta:
        model = Empresa
        fields = ['rotas',]


class EmpresaViagensSerializer(serializers.ModelSerializer):
    viagens = ViagemSerializer(many=True, read_only=True, source='empresa_viagem')

    class Meta:
        model = Empresa
        fields = ['viagens',]


class AssentoViagensSerializer(serializers.ModelSerializer):
    assentos = ViagemAssentoSerializer(many=True, read_only=True, source='viagem_assento')

    class Meta:
        model = Viagem
        fields = ['assentos',]


class AppMetodoPagamentoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AppMetodoPagamento
        fields = '__all__'


class TaxaDescontoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DescontoBilhete
        fields = '__all__'


class TerminaisNacionaisSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TerminaisNaconais
        fields = '__all__'


class PerguntasFrequentesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerguntasFrequentes
        fields = '__all__'


class PerguntasFrequentesOperadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerguntasFrequentesOperador
        fields = '__all__'


class PerguntasFrequentesAgenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerguntasFrequentesAgente
        fields = '__all__'



class ClienteMetodoPagamentoUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteMetodoPagamento
        fields = ['id','cliente','agencia','default','numero_pagamento']
        read_only_fields = ['cliente', 'agencia']  # Impede a atualização de cliente e agencia


class ClienteMetodoPagamentoSerializer(serializers.ModelSerializer):
    nome_agencia = serializers.SerializerMethodField()
    nome_cliente = serializers.SerializerMethodField()
    pk_agencia = serializers.SerializerMethodField()
    logotipo_agencia = serializers.SerializerMethodField()

    class Meta:
        model = ClienteMetodoPagamento
        fields = ['id','pk_agencia','default','nome_agencia', 'logotipo_agencia', 'nome_cliente','numero_pagamento']

    # Obtém o id da agência
    def get_pk_agencia(self, obj):
        return obj.agencia.pk if obj.agencia else None
    
    # Obtém o id da agência
    def get_logotipo_agencia(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.agencia.logotipo_agencia.url) if obj.agencia.logotipo_agencia else None

    
    # Obtém o nome da agência
    def get_nome_agencia(self, obj):
        return obj.agencia.agencia if obj.agencia else None

    # Obtém o nome do cliente
    def get_nome_cliente(self, obj):
        return f'{obj.cliente.user.first_name} {obj.cliente.user.last_name}' if obj.cliente and obj.cliente.user else None

  
class VendaBilheteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendaBilhete
        fields = "__all__"


#  =========================== Fim Parte I =====================================================


#================================== Parte II ============================

#======================================= Operador ===============================

class OperadorMetodoPagamentoUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model =  OperadorMetodoPagamento
        fields = ['id','operador','agencia','default','numero_pagamento']
        read_only_fields = ['operador', 'agencia']  # Impede a atualização de cliente e agencia


class OperadorMetodoPagamentoSerializer(serializers.ModelSerializer):
    nome_agencia = serializers.SerializerMethodField()
    nome_operador = serializers.SerializerMethodField()
    pk_agencia = serializers.SerializerMethodField()
    logotipo_agencia = serializers.SerializerMethodField()

    class Meta:
        model = OperadorMetodoPagamento
        fields = ['id','pk_agencia','default','nome_agencia', 'logotipo_agencia', 'nome_operador','numero_pagamento']

    # Obtém o id da agência
    def get_pk_agencia(self, obj):
        return obj.agencia.pk if obj.agencia else None
    
    # Obtém o id da agência
    def get_logotipo_agencia(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.agencia.logotipo_agencia.url) if obj.agencia.logotipo_agencia else None

    
    # Obtém o nome da agência
    def get_nome_agencia(self, obj):
        return obj.agencia.agencia if obj.agencia else None

    # Obtém o nome do cliente
    def get_nome_operador(self, obj):
        return f'{obj.operador.user.first_name} {obj.operador.user.last_name}' if obj.operador and obj.operador.user else None
    

# Cria agente, actualiza e elimina
class OperadorAgenteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Agente
        fields = ['id', 'empresa', 'numero_telefone', 'endereco']


class OperadorAgenteCRUDSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Inclui o serializer do User para manipular dados do usuário

    class Meta:
        model = Agente
        fields = ['id', 'user', 'empresa', 'numero_telefone', 'endereco']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        agente = Agente.objects.create(user=user, **validated_data)
        return agente

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        user = instance.user
        
        if user_data:
            username = user_data.get('username', None)
            
            # Verifique se o novo username é diferente do atual e se já existe no banco
            if username != user.username and User.objects.filter(username=username).exists():
                raise serializers.ValidationError({"user": {"username": ["Já existe um utilizador com esse nome."]}})

            # Agora, atualize os dados do usuário
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Agora, atualize os dados do agente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        # Serializa dados do Agente e User em uma única estrutura
        data = super().to_representation(instance)
        user_data = data.pop('user')

        # Mescla dados do User e Agente
        merged_data = {**user_data, **data}
        return merged_data

# Busca agente
class UserAgenteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id','username', 'first_name','password', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}  # Para garantir que a senha só será usada para escrita

    def create(self, validated_data):
        # Usa o método set_password para garantir que a senha seja salva de forma segura
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserAgenteSerializer, self).create(validated_data)


# Cria um ponto de venda
class OperadorPontoVendaSerializer(serializers.ModelSerializer):
    terminal = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=TerminaisNaconais.objects.all(), required=False
    )
    nome = serializers.CharField(allow_null=True, required=False)
    endereco = serializers.CharField(allow_null=True, max_length=500, required=True)

    class Meta:
        model = PontoVenda
        fields = "__all__"
        extra_kwargs = {
            'data_cadastro': {'read_only': True},  # Somente leitura para data de cadastro
        }


# Cria uma rota
class OperadorRotaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rotas
        fields = "__all__"


# criar rota
class OperadorMinhasRotasSerializer(serializers.ModelSerializer):
    local_origem = serializers.SerializerMethodField()
    local_destino = serializers.SerializerMethodField()

    class Meta:
        model = Rotas
        fields = "__all__"

    
# Operador meus agentes
class OperadorMeusAgenteSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    totalRotas = serializers.IntegerField(default=0)

    def get_username(self,obj):
        return obj.user.username if obj.user else ""
    
    def get_first_name(self,obj):
        return obj.user.first_name if obj.user else ""
    
    def get_last_name(self,obj):
        return obj.user.last_name if obj.user else ""
    

    class Meta:
        model = Agente
        fields = ['id','numero_telefone','totalRotas','endereco','first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'foto_perfil': {'write_only': True},
        }  # Para garantir que a senha só será usada para escrita


class OperadorPontoIntermediarioSerializer(serializers.ModelSerializer):
    local_destino=serializers.CharField(source='rota.destino.nome', default="", read_only=True)
    endereco_destino=serializers.CharField(source='rota.destino.endereco', default="", read_only=True)
    class Meta:
        model = PontoIntermediario
        fields = "__all__"


# Obter reservas 
class OperadorReservasSerializer(serializers.ModelSerializer):
    agente_id = serializers.CharField(source='viagem.rota.agente.pk', default="", read_only=True)
    agente = serializers.CharField(source='viagem.rota.agente.user.get_full_name', default="", read_only=True)
    nome_empresa = serializers.CharField(source='empresa.nome_empresa', default="", read_only=True)
    embarque_origem = serializers.CharField(source='viagem.rota.origem.endereco', default="", read_only=True)
    desembarque_destino = serializers.CharField(source='viagem.rota.destino.endereco', default="", read_only=True)
    nuit_empresa = serializers.CharField(source='empresa.nuit', default="", read_only=True)
    sede_empresa = serializers.CharField(source='empresa.sede', default="", read_only=True)
    rota = serializers.CharField(source='viagem.rota.pk', default="", read_only=True)
    numero_conta=serializers.CharField(source='venda.metodo_pagamento.numero_pagamento', default="", read_only=True)
    metodo_pagamento=serializers.CharField(source='venda.metodo_pagamento.agencia.agencia', default="", read_only=True)
    logotipo_empresa = serializers.SerializerMethodField()
    qrcode_url = serializers.SerializerMethodField()
    data_saida = serializers.CharField(source='viagem.data_saida', default="", read_only=True)
    hora_saida = serializers.CharField(source='viagem.hora_saida', default="", read_only=True)
    data_criado = serializers.SerializerMethodField()
    hora_criado = serializers.SerializerMethodField()

    def get_data_criado(self, obj):
        return obj.data_criado.strftime("%d-%m-%Y") if obj.data_criado else ""
    

    def get_hora_criado(self, obj):
        return obj.hora_criado.strftime("%H:%M") if obj.hora_criado else ""
    
    
    def get_data_saida(self, obj):
        return obj.data_saida.strftime("%d-%m-%Y") if obj.data_saida else ""
    

    def get_hora_saida(self, obj):
        return obj.hora_saida.strftime("%H:%M") if obj.hora_saida else ""


    def get_logotipo_empresa(self, obj):
        request = self.context.get('request')
        if request and obj.empresa and obj.empresa.logotipo:
            return request.build_absolute_uri(obj.empresa.logotipo.url)
        return None
    

    def get_qrcode_url(self, obj):
        request = self.context.get('request')
        if request and obj.qrcode:
            return request.build_absolute_uri(obj.qrcode.url)
        return None


    class Meta:
        model = Bilhete
        fields = [
            'id',
            'sede_empresa',
            'embarque_origem',
            'desembarque_destino',
            'nome_empresa',
            'nuit_empresa',
            'rota',
            'agente',
            'agente_id',
            'nome_empresa',
            'logotipo_empresa',
            'qrcode_url',
            'origem',
            'destino',
            'status_bilhete',
            'status_viagem',
            'assento',
            'nome_passageiro',
            'contacto_passageiro',
            'nome_familiar',
            'contacto_familiar',
            'metodo_pagamento',
            'numero_conta',
            'preco',
            'hora_saida',
            'data_saida',
            'duracao',
            'contacto_empresa',
            'referencia',
            'data_criado',
            'hora_criado',
            'motivo'
        ]



#-----------------------------------------/////////////////////-----------------------------------

#========================================== Agente ===============================================

class AgenteSerializer(serializers.ModelSerializer):
    nome_empresa=serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    logotipo = serializers.SerializerMethodField()
    nuit = serializers.SerializerMethodField()
    sede = serializers.SerializerMethodField()
    contacto = serializers.SerializerMethodField()
    classificacao=serializers.SerializerMethodField()
    slogan=serializers.SerializerMethodField()


    def get_logotipo(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.empresa.logotipo.url) if obj.empresa.logotipo else None

    def get_username(self,obj):
        return obj.user.username if obj.user else ""
    
    def get_first_name(self,obj):
        return obj.user.first_name if obj.user else ""
    
    def get_last_name(self,obj):
        return obj.user.last_name if obj.user else ""
    
    def get_nome_empresa(self,obj):
        return obj.empresa.nome_empresa if obj.empresa else ""
    
    def get_sede(self,obj):
        return obj.empresa.sede if obj.empresa else ""
    
    def get_nuit(self,obj):
        return obj.empresa.nuit if obj.empresa.nuit else 0
    
    def get_contacto(self,obj):
        return obj.empresa.numero_telefone if obj.empresa.numero_telefone else 0
    
    def get_classificacao(self,obj):
        return obj.empresa.classificacao_media if obj.empresa.classificacao_media else 0.0

    def get_slogan(self,obj):
        return obj.empresa.slogan if obj.empresa.slogan else ""
    

    class Meta:
        model = Agente
        fields = ['id','numero_telefone',
                  'slogan',
                  'logotipo','classificacao','sede','nuit','contacto', 'nome_empresa','endereco','username', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'foto_perfil': {'write_only': True},
        }  # Para garantir que a senha só será usada para escrita


class AgenteRotasSerializer(serializers.ModelSerializer):
    local_origem=serializers.CharField(source='origem.nome', default="", read_only=True)
    local_destino = serializers.CharField(source='destino.nome', default="", read_only=True)
    endereco_origem=serializers.CharField(source='origem.endereco', default="", read_only=True)
    endereco_destino = serializers.CharField(source='destino.endereco', default="", read_only=True)
    data_cadastro = serializers.SerializerMethodField()
    hora_saida = serializers.SerializerMethodField()
    hora_chegada = serializers.SerializerMethodField()
    responsavel = serializers.SerializerMethodField()

    total_aprovados = serializers.IntegerField()
    total_pendentes = serializers.IntegerField()
    total_cancelados = serializers.IntegerField()


    def get_data_cadastro(self, obj):
        return obj.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if obj.data_cadastro else ""
    
    def get_hora_saida(self, obj):
        return obj.hora_saida.strftime("%H:%M") if obj.hora_saida else ""
    
    def get_hora_chegada(self, obj):
        return obj.hora_chegada.strftime("%H:%M") if obj.hora_chegada else ""
    
    def get_responsavel(self, obj):
        return f'{obj.agente.user.get_full_name()}' if obj.agente else ""


    class Meta:
        model = Rotas
        fields = [
            'id',
            'local_origem',
            'data_cadastro',
            'endereco_origem',
            'endereco_destino',
            'local_destino',
            'duracao',
            'hora_saida',
            'hora_chegada',
            'preco',
            'capacidade_assentos',
            'total_aprovados', 
            'total_pendentes', 
            'total_cancelados',
            'responsavel'
        ]
    

class AgenteViagemBilheteStatusSerializer(serializers.ModelSerializer):
    total_realizados = serializers.IntegerField()
    total_aprovados = serializers.IntegerField()
    total_pendentes = serializers.IntegerField()
    total_cancelados = serializers.IntegerField()

    # Campos de data personalizados
    data_fecho = serializers.SerializerMethodField()
    data_saida = serializers.SerializerMethodField()
    data_chegada = serializers.SerializerMethodField()
    hora_saida = serializers.SerializerMethodField()
    hora_chegada = serializers.SerializerMethodField()

    # Formatando as datas manualmente
    def get_data_fecho(self, obj):
        return obj.data_fecho.strftime("%Y-%m-%d %H:%M:%S") if obj.data_fecho else ""

    def get_data_saida(self, obj):
        return obj.data_saida.strftime("%d-%m-%Y") if obj.data_saida else ""

    def get_data_chegada(self, obj):
        return obj.data_chegada.strftime("%d-%m-%Y") if obj.data_chegada else ""

    def get_hora_saida(self, obj):
        return obj.hora_saida.strftime("%H:%M") if obj.hora_saida else ""

    def get_hora_chegada(self, obj):
        return obj.hora_chegada.strftime("%H:%M") if obj.hora_chegada else ""
    

    local_origem = serializers.SerializerMethodField()
    local_destino = serializers.SerializerMethodField()
    preco = serializers.SerializerMethodField()
    endereco_origem = serializers.SerializerMethodField()
    endereco_destino = serializers.SerializerMethodField()


    def get_local_origem(self, obj):
        return obj.rota.origem.nome if obj.rota else ""
    
    def get_local_destino(self, obj):
        return obj.rota.destino.nome if obj.rota else ""
    
    def get_endereco_origem(self, obj):
        return obj.rota.origem.endereco if obj.rota else ""
    
    def get_endereco_destino(self, obj):
        return obj.rota.destino.endereco if obj.rota else ""

    def get_preco(self, obj):
        return obj.rota.preco if obj.rota else 0.0

    

    class Meta:
        model = Viagem
        fields =   [
            'id', 
            'rota', 
            'data_saida', 
            'data_chegada', 
            'local_destino',
            'local_origem',
            'hora_saida', 
            'preco',
            "endereco_origem",
            "endereco_destino",
            'data_fecho',
            'hora_chegada', 
            'total_assento', 
            'duracao_viagem',
            'total_assentos_disponiveis',
            'total_realizados', 
            'total_aprovados', 
            'total_pendentes', 
            'total_cancelados'
        ]


class AgenteRotaViagensSerializer(serializers.ModelSerializer):
    reservas = serializers.SerializerMethodField()
    pendentes = serializers.SerializerMethodField()
    aprovados = serializers.SerializerMethodField()
    cancelados = serializers.SerializerMethodField()

    # Campos de data personalizados
    data_fecho = serializers.SerializerMethodField()
    data_saida = serializers.SerializerMethodField()
    data_chegada = serializers.SerializerMethodField()
    hora_saida = serializers.SerializerMethodField()
    hora_chegada = serializers.SerializerMethodField()
    data_cadastro = serializers.SerializerMethodField()

    def get_reservas(self, obj):

        return obj.rota.origem.nome if obj.rota else ""
    
    def get_local_destino(self, obj):
        return obj.rota.destino.nome if obj.rota else ""

    def get_preco(self, obj):
        return obj.rota.preco if obj.rota else 0.0

    # Formatando as datas manualmente
    def get_data_fecho(self, obj):
        return obj.data_fecho.strftime("%Y-%m-%d %H:%M:%S") if obj.data_fecho else ""

    def get_data_saida(self, obj):
        return obj.data_saida.strftime("%d-%m-%Y") if obj.data_saida else ""

    def get_data_chegada(self, obj):
        return obj.data_chegada.strftime("%d-%m-%Y") if obj.data_chegada else ""

    def get_hora_saida(self, obj):
        return obj.hora_saida.strftime("%H:%M") if obj.hora_saida else ""

    def get_hora_chegada(self, obj):
        return obj.hora_chegada.strftime("%H:%M") if obj.hora_chegada else ""


    def get_data_cadastro(self, obj):
        return obj.data_cadastro.strftime("%d-%m-%Y %H:%M:%S") if obj.data_cadastro else ""

    def get_empresa(self, obj):
        return obj.empresa.nome_empresa if obj.empresa else ""


    class Meta:
        model = Viagem
        fields = ['id','empresa', 'preco', 'duracao_viagem','hora_saida','hora_chegada', 'local_origem', 'local_destino', 'total_assento',
                  'data_fecho', 'total_assentos_disponiveis', 'data_saida', 
                  'data_chegada', 'contacto', 'activo','data_cadastro']
        

class AgenteRotaViagemAssentosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ViagemAssento
        fields = ['id','assento','disponivel','viagem','activo']
        extra_kwargs = {
            'viagem': {'required': False}  # Defina como opcional caso a imagem não seja obrigatória
        }


# Reservas de bilhetes
class ReservasBilheteSerializer(serializers.ModelSerializer):
    nnome_empresa = serializers.CharField(source='empresa.nome_empresa', default="", read_only=True)
    embarque_origem = serializers.CharField(source='viagem.rota.origem.endereco', default="", read_only=True)
    desembarque_destino = serializers.CharField(source='viagem.rota.destino.endereco', default="", read_only=True)
    nuit_empresa = serializers.CharField(source='empresa.nuit', default="", read_only=True)
    sede_empresa = serializers.CharField(source='empresa.sede', default="", read_only=True)

    numero_conta=serializers.CharField(source='vendabilhete.metodo_pagamento.numero_pagamento', default="", read_only=True)
    metodo_pagamento=serializers.CharField(source='vendabilhete.metodo_pagamento.numero_pagamento', default="", read_only=True)
    logotipo_empresa = serializers.SerializerMethodField()
    qrcode_url = serializers.SerializerMethodField()
    data_saida = serializers.SerializerMethodField()
    hora_saida = serializers.SerializerMethodField()
    data_criado = serializers.SerializerMethodField()
    hora_criado = serializers.SerializerMethodField()

    def get_data_criado(self, obj):
        return obj.data_criado.strftime("%d-%m-%Y") if obj.data_criado else ""
    
    def get_hora_criado(self, obj):
        return obj.hora_criado.strftime("%H:%M") if obj.hora_criado else ""
    
    def get_data_saida(self, obj):
        return obj.data_saida.strftime("%d-%m-%Y") if obj.data_saida else ""

    def get_hora_saida(self, obj):
        return obj.viagem.hora_saida.strftime("%H:%M") if obj.viagem.hora_saida else ""

    def get_logotipo_empresa(self, obj):
        request = self.context.get('request')
        if request and obj.empresa and obj.empresa.logotipo:
            return request.build_absolute_uri(obj.empresa.logotipo.url)
        return None
    
    def get_qrcode_url(self, obj):
        request = self.context.get('request')
        if request and obj.qrcode:
            return request.build_absolute_uri(obj.qrcode.url)
        return None

    class Meta:
        model = Bilhete
        fields = [
            'id',
            'sede_empresa',
            'embarque_origem',
            'desembarque_destino',
            'nome_empresa',
            'nuit_empresa',
            'hora_saida',
            'venda',
            'viagem',
            'nome_empresa',
            'logotipo_empresa',
            'empresa',
            'cliente',
            'qrcode_url',
            'origem',
            'destino',
            'status_bilhete',
            'status_viagem',
            'assento',
            'nome_passageiro',
            'contacto_passageiro',
            'nome_familiar',
            'contacto_familiar',
            'metodo_pagamento',
            'numero_conta',
            'motivo'
            'preco',
            'data_saida',
            'duracao',
            'contacto_empresa',
            'referencia',
            'data_criado',
            'hora_criado',
        ]


    

