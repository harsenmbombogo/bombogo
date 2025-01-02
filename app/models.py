from queue import Full
from django.db import models
from django.contrib.auth.models import User
import datetime
from django.db import transaction  # Importante para usar transações
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction  # Importante para usar transações
from django.db.models.signals import post_delete
from django.dispatch import receiver
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile
from cloudinary.models import CloudinaryField

class ConfiguracoesAppCliente(models.Model):
    nome_app=models.CharField(max_length=150, blank=True, null=True, unique=True)
    descricao_app=models.CharField(max_length=150, blank=True, null=True,)
    politica_privacidade_app=models.TextField(blank=True, null=True)
    termos_condicoes_app=models.TextField(blank=True, null=True)
    logotipo_app = CloudinaryField('logotipo_app_cliente')
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'App cliente {self.nome_app}'


class ConfiguracoesAppOperador(models.Model):
    nome_app=models.CharField(max_length=150, blank=True, null=True, unique=True)
    descricao_app=models.CharField(max_length=150, blank=True, null=True,)
    politica_privacidade_app=models.TextField(blank=True, null=True, )
    termos_condicoes_app=models.TextField(blank=True, null=True,)
    logotipo_app = CloudinaryField('logotipo_app_oerador')
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'App operador {self.nome_app}'
    

class ConfiguracoesAppAgente(models.Model):
    nome_app=models.CharField(max_length=150, blank=True, null=True, unique=True)
    descricao_app=models.CharField(max_length=150, blank=True, null=True, )
    politica_privacidade_app=models.TextField(blank=True, null=True,)
    termos_condicoes_app=models.TextField(blank=True, null=True,)
    logotipo_app = CloudinaryField('logotipo_app_agente')
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'App agente {self.nome_app}'

class AppMetodoPagamento(models.Model):
    agencia=models.CharField(max_length=150, blank=True, null=True, unique=True)
    numero_conta=models.CharField(max_length=150, blank=True, null=True, unique=True)
    logotipo_agencia = CloudinaryField('logotipo_agencia')
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.agencia}'


class PerguntasFrequentes(models.Model):
    
    pergunta=models.CharField(max_length=255, null=True, blank=True, unique=True)
    resposta=models.TextField()
    activo=models.BooleanField(default=True)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pergunta}  {self.resposta}'


class PerguntasFrequentesOperador(models.Model):
    
    pergunta=models.CharField(max_length=255, null=True, blank=True, unique=True)
    resposta=models.TextField()
    activo=models.BooleanField(default=True)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pergunta}  {self.resposta}'
    

class PerguntasFrequentesAgente(models.Model):
    
    pergunta=models.CharField(max_length=255, null=True, blank=True, unique=True)
    resposta=models.TextField()
    activo=models.BooleanField(default=True)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pergunta}  {self.resposta}'

class DescontoBilhete(models.Model):
    taxa_desconto= models.DecimalField(decimal_places=2, max_digits=10, unique=True)
    activo=models.BooleanField(default=True)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Taxa de desconto {self.taxa_desconto} - activo: {self.activo}'

    def save(self, *args, **kwargs):
        if self.activo:
            DescontoBilhete.objects.filter(activo=True).update(activo=False)
        
        super(DescontoBilhete, self).save(*args, **kwargs)


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    numero_telefone = models.CharField(max_length=15, blank=True, null=True)
    nome_familiar = models.CharField(max_length=15, blank=True, null=True)
    contacto_familiar = models.IntegerField(blank=True, null=True)
    foto_perfil = CloudinaryField('profile_images')
    token=models.CharField(max_length=1000, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    activo=models.BooleanField(default=True)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name


class ClienteMetodoPagamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cliente_metodo_pagamento')
    agencia = models.ForeignKey(AppMetodoPagamento, on_delete=models.CASCADE, related_name='cliente_agencia')
    numero_pagamento = models.CharField(max_length=15, blank=True, null=True)
    data_cadastro=models.DateTimeField(auto_now=True)
    default=models.BooleanField(default=True)

    def __str__(self):
        return f'{self.cliente.user.first_name} - {self.agencia} - {self.numero_pagamento}'

    def save(self, *args, **kwargs):
        if self.default:
            ClienteMetodoPagamento.objects.filter(cliente=self.cliente, default=True).update(default=False)
        agencia=ClienteMetodoPagamento.objects.filter(cliente=self.cliente, default=True)
        
        if not agencia.exists():
            self.default=True
        
        
        super(ClienteMetodoPagamento, self).save(*args, **kwargs)

    class Meta:
        ordering=['-default']


class Operador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operador')
    numero_telefone = models.CharField(max_length=15, blank=True, null=True)
    foto_perfil = CloudinaryField('operdaor_images')
    endereco = models.TextField(blank=True, null=True)
    token=models.CharField(max_length=1000, blank=True, null=True)
    activo=models.BooleanField(default=True)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name


class OperadorMetodoPagamento(models.Model):
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name='operador_metodo_pagamento')
    agencia = models.ForeignKey(AppMetodoPagamento, on_delete=models.CASCADE, related_name='operador_agencia')
    numero_pagamento = models.CharField(max_length=15, blank=True, null=True)
    data_cadastro=models.DateTimeField(auto_now=True)
    default=models.BooleanField(default=True)
    activo=models.BooleanField(default=True)

    def __str__(self):
        return f'{self.operador.user.first_name} - {self.agencia} - {self.numero_pagamento}'

    def save(self, *args, **kwargs):
        if self.default:
            OperadorMetodoPagamento.objects.filter(operador=self.operador, default=True).update(default=False)
        
        super(OperadorMetodoPagamento, self).save(*args, **kwargs)


class Logs(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')
    accao = models.CharField(max_length=255, blank=True, null=True)
    detalhes = models.TextField(blank=True, null=True)
    data_cadastro=models.DateField(auto_now=True)
    hora_cadastro=models.TimeField(auto_now=True)

    def __str__(self):
        return f'Log do usuário {self.user.first_name} -> {self.accao}'


class Empresa(models.Model):
    dono = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name='operador_empresa')
    nome_empresa = models.CharField(max_length=100, null=True)
    nuit = models.CharField(max_length=100, null=True, blank=True)
    numero_telefone = models.CharField(max_length=100, null=True, blank=True)
    slogan = models.CharField(max_length=500, null=True)
    logotipo = CloudinaryField('logotipo-empresa')
    sede = models.TextField(blank=True, null=True)
    activo=models.BooleanField(default=True)
    classificacao_media = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_empresa

    def atualizar_classificacao_media(self):
        # Calcula a média das classificações com base nas viagens associadas à empresa
        media = self.empresa_viagem.aggregate(models.Avg('classificacoes_viagem__rating'))['classificacoes_viagem__rating__avg']
        
        # Se a média não for None, arredonde e atribua ao campo de média
        if media is not None:
            self.classificacao_media = round(media, 2)
        else:
            self.classificacao_media = 0.0  # Se não houver classificações

        self.save()


class TerminaisNaconais(models.Model):
    terminal = models.CharField(max_length=100, null=True, unique=True)
    activo=models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Terminal {self.terminal}'


class PontoVenda(models.Model):
    terminal = models.ForeignKey(TerminaisNaconais, null=True, blank=True, on_delete=models.CASCADE, related_name='ponto_venda_terminal')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresa_pontovenda')
    nome = models.CharField(max_length=100, null=True, blank=True, editable=False)
    endereco = models.CharField(max_length=500, null=True)
    activo=models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.empresa.nome_empresa} terminal {self.nome}, endereco {self.endereco}'
    
    class Meta:
        unique_together = (('empresa', 'nome', 'endereco'),)

    def save(self, *args, **kwargs):
        # Verifica se 'terminal' foi passado e está presente
        if self.terminal:
            # Atualiza o nome com base no terminal existente
            self.nome = self.terminal.terminal
        elif self.nome:
            # Cria ou busca um terminal baseado no 'nome' se o terminal não foi passado
            terminal, created = TerminaisNaconais.objects.get_or_create(terminal=self.nome)
            self.terminal = terminal  # Atualiza o campo 'terminal' com o terminal criado ou existente
        else:
            # Se nenhum nome ou terminal for fornecido, deixe como None
            self.nome = None

        # Chamar o método save da superclasse
        super(PontoVenda, self).save(*args, **kwargs)


class Agente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agente')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresa_agente')
    numero_telefone = models.IntegerField(blank=True, null=True)
    foto_perfil = CloudinaryField('agente_images')
    endereco = models.TextField(blank=True, null=True)
    token=models.CharField(max_length=1000, blank=True, null=True)
    activo=models.BooleanField(default=True)
    data_cadastro=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.empresa}"


class AgenteMetodoPagamento(models.Model):
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='agente_metodo_pagamento')
    agencia = models.ForeignKey(AppMetodoPagamento, on_delete=models.CASCADE, related_name='agente_agencia')
    numero_pagamento = models.CharField(max_length=15, blank=True, null=True)
    data_cadastro=models.DateTimeField(auto_now=True)
    default=models.BooleanField(default=True)
    activo=models.BooleanField(default=True)

    def __str__(self):
        return f'{self.agente.user.first_name} - {self.agencia} - {self.numero_pagamento}'

    def save(self, *args, **kwargs):
        if self.default:
            AgenteMetodoPagamento.objects.filter(agente=self.agente, default=True).update(default=False)
        
        super(AgenteMetodoPagamento, self).save(*args, **kwargs)


class Rotas(models.Model):
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, blank=True,null=True, related_name='rota_agente')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresa_rota')
    origem = models.ForeignKey(PontoVenda, on_delete=models.CASCADE, related_name='empresa_rota_origem')
    destino = models.ForeignKey(PontoVenda, on_delete=models.CASCADE, related_name='empresa_rota_destino')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    duracao = models.IntegerField( blank=True, null=True)
    hora_saida = models.TimeField()
    hora_chegada = models.TimeField()
    capacidade_assentos = models.IntegerField(default=61)
    activo=models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.empresa.nome_empresa}: {self.origem.nome} - {self.destino.nome} - {self.preco} MT'


class PontoIntermediario(models.Model):
    rota = models.ForeignKey(Rotas, on_delete=models.CASCADE, related_name='rota_ponto_intermedio')   
    terminal = models.CharField(max_length=255)
    endereco = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Preço extra até esta parada
    activo=models.BooleanField(default=True)


    def __str__(self):
        return f'{self.terminal} - Preço : {self.preco}'
    

    class Meta:
        # unique_together = (('rota', 'terminal', 'endereco'),)
        ordering=['-pk']
    

    def save(self, *args, **kwargs):
        terminal, created = TerminaisNaconais.objects.get_or_create(terminal=self.terminal)
        super(PontoIntermediario, self).save(*args, **kwargs)


class Viagem(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresa_viagem')
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='agente_viagem')
    rota = models.ForeignKey(Rotas, on_delete=models.CASCADE, related_name='agente_viagem_rota')
    data_saida = models.DateField(null=True)
    data_chegada = models.DateField(null=True)
    hora_saida = models.TimeField(null=True)
    hora_chegada = models.TimeField(null=True)
    total_assento = models.IntegerField(default=61)
    total_assentos_disponiveis = models.IntegerField(default=61)
    contacto = models.CharField(max_length=15, blank=True, null=True)
    data_fecho = models.DateTimeField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now=True)
    activo=models.BooleanField(default=True)
    duracao_viagem = models.CharField(max_length=20, blank=True, null=True)
    #paradas_disponiveis = models.ManyToManyField(PontoIntermediario, blank=True,null=True, related_name='viagem_paradas')

    class Meta:
        ordering = ['-data_saida']

    def save(self, *args, **kwargs):
        # Define a data_fecho para o próximo dia às 3:30, se não for fornecida
        if not self.data_fecho:
            tomorrow = timezone.now() + timedelta(days=1)
            self.data_fecho = tomorrow.replace(hour=3, minute=30, second=0, microsecond=0)

        # Calcular a duração da viagem
        self.duracao_viagem = self.calcular_duracao()
        
        super(Viagem, self).save(*args, **kwargs)
        # self.agendar_viagens_diarias()
    
    
    def calcular_duracao(self):
        if self.data_saida and self.data_chegada and self.hora_saida and self.hora_chegada:
            # Cria objetos datetime combinando data e hora
            datetime_saida = datetime.combine(self.data_saida, self.hora_saida)
            datetime_chegada = datetime.combine(self.data_chegada, self.hora_chegada)

            # Calcula a diferença entre a data/hora de saída e a de chegada
            duracao = datetime_chegada - datetime_saida
            
            # Extrai a duração em dias, horas e minutos
            dias = duracao.days
            horas, resto = divmod(duracao.seconds, 3600)
            minutos = resto // 60
            
            # Formata a duração em uma string legível
            partes = []
            
            if dias >= 30:
                meses = dias // 30
                partes.append(f"{meses} mês{'es' if meses > 1 else ''}")
                dias %= 30  # Resto dos dias após contar os meses

            if dias > 0:
                partes.append(f"{dias} dia{'s' if dias > 1 else ''}")
            if horas > 0 or minutos > 0:
                horas_minutos = f"{horas}h"
                if minutos > 0:
                    horas_minutos += f":{minutos:02d}min"
                partes.append(horas_minutos)

            return ' '.join(partes) if partes else "Duração desconhecida"

        return "Duração desconhecida"

    def __str__(self):
        return f"Viagem {self.agente} - {self.data_saida} - ({self.data_chegada})"


    def agendar_viagens_diarias(self):
    
        # Obtém a data atual
        data_atual = timezone.now().date()
        msg=''
        # Itera sobre cada rota
        rotas = Rotas.objects.all()
        
        with transaction.atomic():  # Garante que as operações sejam tratadas como uma única transação
            for rota in rotas:
                # Obtém os agentes responsáveis pela rota
                agentes = Agente.objects.filter(rota=rota)

                for agente in agentes:
                    for i in range(3):  # Cria uma viagem para os próximos 7 dias
                        data_viagem = data_atual + timedelta(days=i)
                       
                        # Cria um objeto datetime para a data de fechamento
                        data_fecho = datetime.combine(data_viagem, datetime.min.time()).replace(hour=3, minute=30)

                        
                        # Cria uma nova viagem
                        viagem = Viagem.objects.create(
                            empresa=rota.empresa,
                            agente=agente,
                            rota=rota,
                            data_saida=data_viagem,
                            hora_saida=rota.hora_saida,
                            data_chegada=data_viagem,
                            hora_chegada=rota.hora_chegada,
                            data_fecho= data_fecho
                        )

                        if viagem:
                            msg='Viagem criada com sucesso: '
                        else: 
                            msg= "Erro ao criar viagem"

                        # Adiciona assentos disponíveis
                        for assento_num in range(1, rota.capacidade_assentos + 1):
                            ViagemAssento.objects.create(viagem=viagem, assento=assento_num)

        return f"{msg} -  message"


class ViagemAssento(models.Model):
    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE, related_name='viagem_assento')
    assento = models.IntegerField()
    disponivel = models.BooleanField(default=True)
    activo = models.BooleanField(default=False)
    data_criado=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.viagem} - assento: {self.assento} ({self.disponivel})"

    def save(self, *args, **kwargs):
        total_assentos_disponiveis = ViagemAssento.objects.filter(viagem=self.viagem, disponivel=True).count()
        
        # Atualiza o campo total_assento da viagem
        self.viagem.total_assentos_disponiveis=total_assentos_disponiveis
        self.viagem.save()

        super(ViagemAssento, self).save(*args, **kwargs)


class VendaBilhete(models.Model):
    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Aprovado", "Aprovado"),
        ("Cancelado", "Cancelado"),
    ]

    # Relacionamento com o modelo Cliente
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='venda_bilhete_cliente',)
    # Relacionamento com o modelo Agente
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='venda_bilhete_agente', blank=True, null=True)
    # Relacionamento com o modelo Empresa
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='venda_bilhete_emoresa', blank=True, null=True)
    # Relacionamento com o modelo Viagem
    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE, related_name='venda_bilhete_viagem', blank=True, null=True)
    metodo_pagamento = models.ForeignKey(ClienteMetodoPagamento, on_delete=models.CASCADE, related_name='venda_bilhete_metodo_pagamento', blank=True, null=True)
    
    preco_total= models.DecimalField(decimal_places=2, max_digits=10)
    quantidade= models.IntegerField()
    subtotal= models.DecimalField(decimal_places=2, max_digits=10)
    desconto= models.DecimalField(decimal_places=2, max_digits=10)
    total_pago= models.DecimalField(decimal_places=2, max_digits=10)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pendente")
    data_venda = models.DateField(auto_now_add=True)
    hora_venda = models.TimeField(auto_now_add=True)


    def __str__(self):
        return f"Venda {self.pk} - Cliente: {self.cliente} - Status: {self.status}"

    def save(self, *args, **kwargs):
        self.agente=self.viagem.agente
        self.empresa=self.viagem.agente.empresa

        super(VendaBilhete, self).save(*args, **kwargs)
    
    class Meta:
        ordering=['-pk']



class Bilhete(models.Model):
    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Aprovado", "Aprovado"),
        ("Cancelado", "Cancelado"),
    ]

    STATUS_VIAGEM_CHOICES = [
        ("Pendente", "Pendente"),
        ("Confirmado", "Confirmado"),
        ("Adamento", "Adamento"),
        ("Realizada", "Realizada"),
    ]

    venda = models.ForeignKey(VendaBilhete, on_delete=models.CASCADE, related_name='bilhete_vendido')
    referencia = models.CharField(unique=True, max_length=100)
    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE, related_name='bilhetes_viagem')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='bilhetes_empresa')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='bilhetes_cliente')

    origem = models.CharField(max_length=500, blank=True, null=True)
    destino = models.CharField(max_length=500, blank=True, null=True)
    motivo = models.CharField(max_length=500, blank=True, null=True)
    assento = models.IntegerField()

    nome_passageiro = models.CharField(max_length=500)
    contacto_passageiro = models.CharField(max_length=500)
    nome_familiar = models.CharField(max_length=500)
    contacto_familiar = models.CharField(max_length=500)
    status_bilhete = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pendente")
    status_viagem = models.CharField(max_length=10, choices=STATUS_VIAGEM_CHOICES, default="Pendente")
    preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    duracao = models.CharField(max_length=500, blank=True, null=True)
    contacto_empresa = models.CharField(max_length=500, blank=True, null=True)
    qrcode = CloudinaryField('bilhete_qr_code')

    data_criado = models.DateField(auto_now_add=True)
    hora_criado = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"Bilhete {self.referencia} - passageiro: {self.nome_passageiro} status: ({self.status_bilhete})"

    def save(self, *args, **kwargs):
        if not self.referencia:
            self.referencia = self.gerar_referencia_unica()

        self.hora_saida = self.viagem.hora_saida
        self.data_saida = self.viagem.data_saida
        self.duracao = self.viagem.duracao_viagem
        self.empresa = self.viagem.rota.empresa

        self.contacto_empresa = self.viagem.agente.numero_telefone

        if self.venda:
            self.venda.status = "Aprovado"

        # Gerar o QR code
        qr_data = f"Bilhete: {self.referencia} | Passageiro: {self.nome_passageiro} | Destino: {self.destino}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Salvar a imagem do QR code como arquivo em memória
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)  # Garantir que o ponteiro do buffer está no início

        # Nome do arquivo para o campo `qrcode`
        file_name = f"bilhete_{self.referencia}.png"

        # Salvar o arquivo no campo `qrcode` usando ContentFile
        self.qrcode.save(file_name, ContentFile(buffer.read()), save=False)

        # Agora, salve o modelo com o arquivo do QR code já incluído
        super(Bilhete, self).save(*args, **kwargs)

    def gerar_referencia_unica(self):
        data_formatada = timezone.now().strftime('%Y%m%d')
        rota_id = self.viagem.rota.id
        
        while True:
            codigo_unico = uuid.uuid4().hex[:6].upper()  
            referencia = f"{rota_id}-{data_formatada}-{codigo_unico}"
            if not Bilhete.objects.filter(referencia=referencia).exists():
                return referencia

    class Meta:
        ordering = ['-pk']


class ClassificacaoViagem(models.Model):
    bilhete = models.ForeignKey(Bilhete, on_delete=models.CASCADE, related_name='classificacoes_bilhete',blank=True, null=True)
    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE, related_name='classificacoes_viagem')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='classificacoes_cliente')
    comentario = models.TextField(blank=True, null=True)
    rating = models.DecimalField(decimal_places=2, max_digits=10)  # rating entre 1 a 5, por exemplo
    data_classificacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Classificação de {self.cliente.user.first_name} para Viagem {self.viagem} - Rating: {self.rating}"
    
    class Meta:
        unique_together = ('viagem', 'cliente')  # Cada cliente pode classificar uma viagem apenas uma vez

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualizar a média de classificação da empresa relacionada
        self.viagem.empresa.atualizar_classificacao_media()



