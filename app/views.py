from decimal import Decimal
from django.db.models import Q, Count,Sum,Avg,Max
from django.forms import ValidationError
from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.response import Response
from django.contrib.auth import authenticate, logout
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from .models import *
from rest_framework import status
from .serializers import *
from django_filters import rest_framework as filters
from django.http import JsonResponse
from firebase_admin import messaging # type: ignore
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
import locale
from django.contrib.auth.password_validation import validate_password
from .twilio_config import *


# Definindo a localidade para português do Brasil
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')  # Tente configurar para Português de Portugal
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'C')  # Fallback para uma localidade padrão (genérica)

# from .firebase_config import initializeApp
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification

# verificar se o usuario ainda tem auterizacao para o acesso usando token
class VerifyTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": "Token is valid."}, status=status.HTTP_200_OK)


def sendMessage(id, title, body, bilhete):
    devices = FCMDevice.objects.filter(user=id)
    if not devices:
        return False
    try:
        send=devices.send_message(
            message =Message(
                notification=Notification(
                    title=title,
                    body=body
                ),
                data={
                    'bilhete_id': str(bilhete),  # Inclua o ID do pedido nos dados
                }
            ),
            # this is optional
            # app=settings.FCM_DJANGO_SETTINGS['DEFAULT_FIREBASE_APP']
        )
        
        deactivated_ids = send.deactivated_registration_ids  # Pega os IDs desativados

        for device_id in deactivated_ids:
            FCMDevice.objects.filter(registration_id=device_id).delete()  # Remove do banco de dados
        

        return send.registration_ids_sent.count >= 0
    
    except Exception as e:
        print("Error", e)
        return False
    
class home:
    def index(request):
        # verification("+258873686545")
        # code=input("Digite o codigo")
        # check_verification("+258873686545", code)
        # send_sms()
        return render(request, "index.html")

class VerificarUserNameView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username')

        if not username:
            return Response({"error": "O campo 'username' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"exists": True, "message": "O username já existe."}, status=status.HTTP_200_OK)

        return Response({"exists": False, "message": "O username não existe."}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        # Verifica a senha antiga
        old_password = data.get('old_password')
        if not user.check_password(old_password):
            return Response({"error": "Senha antiga incorreta."}, status=status.HTTP_400_BAD_REQUEST)

        # Valida e altera a nova senha
        new_password = data.get('new_password')

        try:
            validate_password(new_password, user=user)
        except Exception as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)
    

class NewPasswordView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        # Valida e altera a nova senha
        new_password = data.get('new_password')

        try:
            validate_password(new_password, user=user)
        except Exception as e:
            print(e)
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)
   

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class UpdateTokenDeviceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            # Obtém o token do corpo da requisição
            token = request.data.get('token')
            if not token:
                return Response({'error': 'Token é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

            # Verifica se o cliente está relacionado ao usuário
            user = request.user

            if hasattr(user, 'cliente'):
                # Atualiza e salva o token do cliente
                user.cliente.token = token
                user.cliente.save()
                # Verificar se o dispositivo já está registrado
                device = FCMDevice.objects.filter(user=user, registration_id=token).exists()
                if not device:
                    FCMDevice.objects.create(
                        user=user,  # Associar ao usuário correto
                        registration_id=token,  # Token do dispositivo
                        type='android'  # Tipo de dispositivo (pode ser 'android' ou 'ios')
                    )
                
                return Response({'token': user.cliente.token}, status=status.HTTP_200_OK)

            elif hasattr(user, 'agente'):
                # Atualiza e salva o token do agente
                user.agente.token = token
                user.agente.save()
                # Verificar se o dispositivo já está registrado
                device = FCMDevice.objects.filter(user=user, registration_id=token).exists()
                if not device:
                    FCMDevice.objects.create(
                        user=user,  # Associar ao usuário correto
                        registration_id=token,  # Token do dispositivo
                        type='android'  # Tipo de dispositivo (pode ser 'android' ou 'ios')
                    )
                return Response({'token': user.agente.token}, status=status.HTTP_200_OK)

            elif hasattr(user, 'operador'):
                # Atualiza e salva o token do operador
                user.operador.token = token
                user.operador.save()
                # Verificar se o dispositivo já está registrado
                device = FCMDevice.objects.filter(user=user, registration_id=token).exists()
                if not device:
                    FCMDevice.objects.create(
                        user=user,  # Associar ao usuário correto
                        registration_id=token,  # Token do dispositivo
                        type='android'  # Tipo de dispositivo (pode ser 'android' ou 'ios')
                    )

                return Response({'token': user.operador.token}, status=status.HTTP_200_OK)

            else:
                return Response({'error': 'Não tem permissão para alterar dados aqui.'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendaBilheteViewSet(viewsets.ModelViewSet):
    queryset = VendaBilhete.objects.all()
    serializer_class = VendaBilheteSerializer


class OperadorViewSet(viewsets.ModelViewSet):
    queryset = Operador.objects.all()
    serializer_class = OperadorSerializer


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer


class ConfiguracoesAppClienteView(APIView):
    serializer_class = ConfiguracoesAppClienteSerializer

    def get(self, request,):
        try:
            queryset_ =ConfiguracoesAppCliente.objects.all()
            serializer = ConfiguracoesAppClienteSerializer(queryset_,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ConfiguracoesAppCliente.DoesNotExist as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)


class ConfiguracoesAppOperadorView(APIView):
    serializer_class = ConfiguracoesAppOperadorSerializer

    def get(self, request,):
        try:
            queryset_ =ConfiguracoesAppOperador.objects.all()
            serializer = ConfiguracoesAppOperadorSerializer(queryset_,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)


class ConfiguracoesAppAgenteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConfiguracoesAppAgenteSerializer

    def get(self, request,):
        try:
            queryset_ =ConfiguracoesAppAgente.objects.all()
            serializer = ConfiguracoesAppAgenteSerializer(queryset_,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        


class EmpresaRotasView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, empresa_id):
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            serializer = RotasSerializer(empresa.empresa_rota.all(),many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa não encontrada'}, status=status.HTTP_404_NOT_FOUND)


class EmpresaViagensView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, empresa_id):
        data_atual = timezone.now()
        data_fecho = timezone.make_aware(datetime.combine(data_atual, datetime.min.time())).replace(hour=3, minute=30)

        # Desativa viagens ativas que precisam ser fechadas
        Viagem.objects.filter(Q(data_fecho__lte=data_fecho) & Q(activo=True)).update(activo=False)
        
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            viagem=Viagem.objects.filter(empresa=empresa).exclude(activo=False)
            serializer = ViagemSerializer(viagem, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa não encontrada'}, status=status.HTTP_404_NOT_FOUND)


# Classificacoes da empresa
class ClassificacaoEmpresaStatisticsView(APIView):
    """
    View para retornar as estatísticas de avaliação de uma empresa.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        empresa = Empresa.objects.get(pk=pk)
        empresa.atualizar_classificacao_media()
        classificacoes = ClassificacaoViagem.objects.filter(viagem__rota__empresa=empresa)

        # Cálculo das estatísticas de avaliações
        estatisticas = classificacoes.aggregate(
            total=Count('rating'),
            media_rating=Avg('rating'),
            total_rating_1=Count('rating', filter=Q(rating=1)),
            total_rating_2=Count('rating', filter=Q(rating=2)),
            total_rating_3=Count('rating', filter=Q(rating=3)),
            total_rating_4=Count('rating', filter=Q(rating=4)),
            total_rating_5=Count('rating', filter=Q(rating=5)),
        ) 

        # Total de avaliações
        total_avaliacoes = estatisticas['media_rating'] or 0

        # Cálculo das porcentagens de cada avaliação
        if total_avaliacoes > 0:
            estatisticas['total_rating_1'] = estatisticas['total_rating_1'] / total_avaliacoes
            estatisticas['total_rating_2'] = estatisticas['total_rating_2'] / total_avaliacoes
            estatisticas['total_rating_3'] = estatisticas['total_rating_3'] / total_avaliacoes
            estatisticas['total_rating_4'] = estatisticas['total_rating_4'] / total_avaliacoes
            estatisticas['total_rating_5'] = estatisticas['total_rating_5'] / total_avaliacoes
        else:
            estatisticas['total_rating_1'] = 0.0
            estatisticas['total_rating_2'] = 0.0
            estatisticas['total_rating_3'] = 0.0
            estatisticas['total_rating_4'] = 0.0
            estatisticas['total_rating_5'] = 0.0

        return Response(estatisticas)


class ClassificacaoEmpresaListView(APIView):
    """
    View para listar as classificações de uma viagem específica e criar novas classificações.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,pk,):
        empresa = Empresa.objects.get(pk=pk)
        classificacoes = ClassificacaoViagem.objects.filter(viagem__rota__empresa=empresa).order_by('-pk')[:5]
       

        # Serializando as classificações
        serializer = ClassificacaoViagemSerializer(classificacoes, many=True)

        # Respondendo com as classificações
        return Response(serializer.data)

# Fim classificacoes da empresa

class ClassificarViagemCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        viagem=Viagem.objects.get(pk=request.data.get('viagem'))
        cliente=request.user.cliente
        bilhete=Bilhete.objects.get(pk=request.data.get('bilhete'))
        rating=request.data.get('rating')
        comentario=request.data.get('comentario')

        ClassificacaoViagem.objects.create(
            viagem=viagem,
            cliente=cliente,
            bilhete=bilhete,
            rating=rating,
            comentario=comentario
        )
        return Response({"message":"Observação concebida"}, status=status.HTTP_201_CREATED)


class ClassificarViagemExiste(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request,pk):
        classifbilhete=ClassificacaoViagem.objects.filter(
            bilhete__pk=pk,
            viagem__bilhetes_viagem__status_viagem='Realizada',
        )
        
        if not classifbilhete.exists():
            bilhete=Bilhete.objects.filter(
                pk=pk,
            )
            serializers= BilheteSerializer(bilhete,many=True, context={"request": request})
            return Response(serializers.data, status=status.HTTP_200_OK)
        
        return Response({"message":"Já classificou a viagem"}, status=status.HTTP_201_CREATED)


def verificar_e_atualizar_todos_bilhetes():
    # Obtém todos os bilhetes aprovados
    bilhetes = Bilhete.objects.filter(status_bilhete="Aprovado")

    if not bilhetes.exists():
        return {"message": "Nenhum bilhete aprovado encontrado."}

    # Data atual para comparação
    data_atual = timezone.localdate()

    # Itera sobre cada bilhete e atualiza o status da viagem
    for bilhete in bilhetes:
        viagem = bilhete.viagem

        # Atualiza o status da viagem com base na data de saída e chegada
        if viagem.data_saida == data_atual:
            bilhete.status_viagem = "Adamento"  # Viagem em andamento
        elif viagem.data_chegada == data_atual:
            bilhete.status_viagem = "Realizada"  # Viagem concluída
        else:
            bilhete.status_viagem = "Pendente"  # Status padrão fora do intervalo

        # Salva as alterações no bilhete
        bilhete.save()

    return {"message": "Status de todos os bilhetes atualizados com sucesso."}


class AssentoViagemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, viagem_id):
        try:
            viagem = Viagem.objects.get(id=viagem_id)
            serializer = AssentoViagensSerializer(viagem)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Viagem.DoesNotExist:
            return Response({'error': 'Viagem não encontrada'}, status=status.HTTP_404_NOT_FOUND)


# Cliente=========================
class PontoVendaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PontoVenda.objects.all()
    serializer_class = OperadorPontoVendaSerializer


# Fim cliente==============================
class PontoVendaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PontoVenda.objects.all()
    serializer_class = OperadorPontoVendaSerializer


class RotasViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Rotas.objects.all()
    serializer_class = RotasSerializer


class AgenteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Agente.objects.all()
    serializer_class = AgenteSerializer


class ViagemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Viagem.objects.all()
    serializer_class = ViagemSerializer


# Filtros para o modelo Viagem
class ViagemFilter(filters.FilterSet):
    #ponto_intermedio = filters.CharFilter(field_name='rota__rota_ponto_intermedio__terminal', lookup_expr='icontains', label='Terminal de Parada')

    empresa_id=filters.CharFilter(method='isNull', lookup_expr='icontains', label='Empresa')
    origem = filters.CharFilter(field_name='rota__origem__nome', lookup_expr='icontains')  # Filtra por origem
    destino = filters.CharFilter(field_name='rota__destino__nome', lookup_expr='icontains')  # Filtra por destino
    data_saida = filters.DateFilter(method='filter_data_saida_volta', label='Data de Saída')
    
    class Meta:
        model = Viagem
        fields = ['origem','destino','data_saida','empresa_id']

 
    def filter_data_saida_volta(self, queryset, name, value):
        # Obtemos a data de volta diretamente dos parâmetros da requisição
        data_volta = self.request.query_params.get('data_volta', None)

        try:
            data_saida = value
            if data_volta:
                # Filtro que considera tanto data de saída quanto data de volta
                return queryset.filter(data_saida__range=(data_saida, data_volta))
            return queryset.filter(data_saida__gte=data_saida)
        except ValueError:
            return queryset.none()  # Retorna queryset vazio caso as datas sejam inválidas


    def isNull(self, queryset, name, value):
        pk = value
        try:
            if pk !='null':
                # Filtro que considera tanto data de saída quanto data de volta
                return queryset.filter(rota__empresa__pk=pk)
            return queryset.all()
        except ValueError:
            return queryset.none()  # Retorna queryset vazio caso as datas sejam inválidas



# View para listar as viagens com filtros aplicados
class ViagemListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Viagem.objects.all().exclude(activo=False)
    serializer_class = ViagemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ViagemFilter
    

class ViagemAssentoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ViagemAssento.objects.all()
    serializer_class = ViagemAssentoSerializer


class BilheteViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Bilhete.objects.all()
    serializer_class = BilheteSerializer


class PerguntasFrequentesViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = PerguntasFrequentes.objects.all().exclude(activo=False)
    serializer_class = PerguntasFrequentesSerializer


class PerguntasFrequentesAgenteViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = PerguntasFrequentesAgente.objects.all().exclude(activo=False)
    serializer_class = PerguntasFrequentesAgenteSerializer


class PerguntasFrequentesOperadorViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = PerguntasFrequentesOperador.objects.all().exclude(activo=False)
    serializer_class = PerguntasFrequentesOperadorSerializer



class BilheteListCreateView(generics.ListCreateAPIView):

    serializer_class = BilheteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get('viagem', None)
        viagem_id= Viagem.objects.get(pk=id)
        if viagem_id is not None:
            return Bilhete.objects.filter(viagem=viagem_id)
        return Bilhete.objects.all()

    def create(self, request, *args, **kwargs):
        # Obtém os dados da requisição
        
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=False)

        id = request.data.get('viagem')
        idvenda = request.data.get('venda')
        assento = request.data.get('assento')
        venda=VendaBilhete.objects.get(pk=idvenda)
        viagem_id= Viagem.objects.get(pk=id)


        # Verifica se já existe um bilhete para a viagem e o cliente (baseado em algum dado relevante, como nome)
        if Bilhete.objects.filter(viagem=viagem_id, assento=assento, status_bilhete='Aprovado').exists():
            print("Já existe um bilhete comprado para essa viagem.")
            raise ValidationError("Já existe um bilhete comprado para essa viagem.")
        try:

            bilhete=Bilhete.objects.create(
                cliente=request.user.cliente,
                venda=venda,
                viagem=viagem_id,
                origem=request.data.get('origem'),
                destino=request.data.get('destino'),

                assento=request.data.get('assento'),
                preco=request.data.get('preco'),
                nome_passageiro=request.data.get('nome_passageiro'),
                nome_familiar=request.data.get('nome_familiar'),

                contacto_passageiro=request.data.get('contacto_passageiro'),
                contacto_familiar=request.data.get('contacto_familiar'),
            )
            
            sendMessage(viagem_id.agente.user.pk, "Pedido de Reserva ", f"""Rota {viagem_id.rota.origem.nome} - {viagem_id.rota.destino.nome} ({viagem_id.data_saida})
            """,1)

            return Response({'message': 'Criado com sucesso.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Erro: ",e)
            return Response({'message': f'Erro:( {e}'}, status=status.HTTP_400_BAD_REQUEST)

class BilheteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Bilhete.objects.all()
    serializer_class = BilheteSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        # Adicionar lógica para atualizar se necessário
        return super().update(request, *args, **kwargs)


class BilhetesClienteView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        cliente = request.user.cliente  # Obtém o cliente autenticado
        bilhetes = Bilhete.objects.filter(cliente=cliente)
        serializer = BilheteSerializer(bilhetes, many=True, context={'request': request})
        return Response(serializer.data)


# Cliente
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserClienteSerializer

    def create(self, request, *args, **kwargs):
        # Serializa os dados
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Cria o usuário
        user = serializer.save()
        
        # Cria o objeto Cliente com base nas informações do cadastro
        cliente = Cliente.objects.create(
            user=user,
            numero_telefone=request.data.get('phone_number'),
            endereco='',
            foto_perfil=None
        )
        
        # Gera o token JWT para o novo usuário
        refresh = RefreshToken.for_user(user)
        
        
        # Dados do cliente e token de resposta
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'cliente': ClienteSerializer(cliente).data
        }
        
        return Response(response_data, status=201)  


class UserUpdateClienteView(generics.UpdateAPIView):
    serializer_class = UserClienteSerializer

    def get_object(self):
        # Retorna o usuário autenticado
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Obtem o usuário atual
        user = self.get_object()  # Obtém o objeto do usuário com base no queryset

        # Serializa os dados sem incluir o username
        serializer = self.get_serializer(user, data=request.data, partial=True)  # Permite atualizações parciais
        serializer.is_valid(raise_exception=True)
        
       

        if 'foto_perfil' in serializer.validated_data:
            serializer.validated_data.pop('foto_perfil')
            

        # Atualiza o usuário (exceto o username)
        user = serializer.save()

        # Atualiza o objeto Cliente com base nas informações do cadastro
        cliente = Cliente.objects.get(user=user)
        cliente.numero_telefone = request.data.get('phone_number')
        cliente.endereco = request.data.get('endereco')
        if request.data.get('contacto_familiar') !="":
            cliente.contacto_familiar = request.data.get('contacto_familiar') 
        cliente.nome_familiar = request.data.get('nome_familiar')
        cliente.foto_perfil = None  # Pode ser tratado separadamente
        cliente.save()

        if cliente:
            return Response({'message': "Seus dados foram actualzados com sucesso."}, status=201)
    
        return Response({'message': "Erro ao actualizar seus dados."}, status=400)


# Login do cliente
class LoginView(generics.GenericAPIView):
    serializer_class = UserClienteSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('phone_number')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            match user:
                case _ if hasattr(user, 'cliente'):
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'type_user':"cliente"
                    })

                case _:
                    return Response({'error': 'Usuário não é cliente, agente ou operador'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Credenciais inválidas'}, status=400)


class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Usando 'match' para verificar diferentes tipos de usuário
        match user:
            case _ if hasattr(user, 'cliente'):
                serializer = UserClienteSerializer(user)
                return Response(serializer.data)
            
            case _ if hasattr(user, 'agente'):
                serializer = AgenteSerializer(user.agente, context={'request': request})
                return Response(serializer.data)

            case _ if hasattr(user, 'operador'):
                serializer = OperadorSerializer(user.operador)
                return Response(serializer.data)

            case _:
                return Response({'error': 'Usuário não é cliente, agente ou operador'}, status=status.HTTP_400_BAD_REQUEST)


# Novas informacooes
class TerminaisNacionaisViewSet(viewsets.ModelViewSet):
    queryset = TerminaisNaconais.objects.all()
    serializer_class = TerminaisNacionaisSerializer


class AppMetodoPagamentoViewSet(viewsets.ModelViewSet):
    queryset = AppMetodoPagamento.objects.all()
    serializer_class = AppMetodoPagamentoSerializer


class DescontoBilheteViewSet(viewsets.ModelViewSet):
    queryset = DescontoBilhete.objects.all()
    serializer_class = TaxaDescontoSerializer


class ClienteMetodosPagamantos(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,format=None):
        # Verifica se o usuário tem um perfil de cliente
        if hasattr(request.user, 'cliente'):
            cliente = request.user.cliente
            # Filtra métodos de pagamento pelo cliente
            cliente_metodo_pagamento = ClienteMetodoPagamento.objects.filter(cliente=cliente)

            if cliente_metodo_pagamento.exists():
                # Passa o queryset completo com many=True para o serializer
                serializer = ClienteMetodoPagamentoSerializer(cliente_metodo_pagamento, many=True,context={'request': request})
                return Response(serializer.data)
            else:
                return Response({'error': 'Cliente ainda não selecionou método'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Não tem permissão'}, status=status.HTTP_401_UNAUTHORIZED)


class ClassificacaoViagemStatisticsView(generics.GenericAPIView):
    """
    View para retornar as estatísticas de avaliação de uma viagem.
    """
    def get(self, request, *args, **kwargs):
        viagem_id = self.kwargs.get('pk')
        classificacoes = ClassificacaoViagem.objects.filter(viagem_id=viagem_id)

        # Cálculo das estatísticas de avaliações
        
        estatisticas = classificacoes.aggregate(
            media_rating=Avg('rating'),
            total_rating_1=Count('rating', filter=Q(rating=1)),
            total_rating_2=Count('rating', filter=Q(rating=2)),
            total_rating_3=Count('rating', filter=Q(rating=3)),
            total_rating_4=Count('rating', filter=Q(rating=4)),
            total_rating_5=Count('rating', filter=Q(rating=5)),
        )

        # Verifique se a média é None, caso contrário defina como 0.0
        media_rating = estatisticas['media_rating'] if estatisticas['media_rating'] is not None else 0.0

        # Atualizando o dicionário com a média ajustada
        estatisticas['media_rating'] = media_rating

        return Response(estatisticas)


class ClassificacaoViagemListCreateView(generics.ListCreateAPIView):
    """
    View para listar as classificações de uma viagem específica e criar novas classificações.
    """
    serializer_class = ClassificacaoViagemSerializer

    def get_queryset(self):
        viagem_id = self.kwargs.get('pk')
        return ClassificacaoViagem.objects.filter(viagem_id=viagem_id)

    def get(self, request, *args, **kwargs):
        viagem_id = self.kwargs.get('pk')
        classificacoes = self.get_queryset()

        # Serializando as classificações
        serializer = self.get_serializer(classificacoes, many=True)

        # Respondendo com as classificações
        return Response(serializer.data)

    def perform_create(self, serializer, request):
        """
        Cria uma nova classificação associada a uma viagem específica.
        """
        viagem=Viagem.objects.get(pk=request.data.get('viagem'))
        cliente=request.user.cliente
        bilhete=request.data.get('bilhete')
        rating=request.data.get('rating')
        comentario=request.data.get('comentario')

        ClassificacaoViagem.objects.create(
            viagem=viagem,
            cliente=cliente,
            bilhete__pk=bilhete,
            rating=rating,
            comentario=comentario
        )


class ClassificacaoViagemDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    View para recuperar, atualizar ou deletar uma classificação de viagem existente usando o ID da classificação.
    """
    queryset = ClassificacaoViagem.objects.all()
    serializer_class = ClassificacaoViagemSerializer
    lookup_field = 'pk'  # Usando o ID da classificação para lookup

    def perform_update(self, serializer):
        """
        Atualiza a classificação, preservando a associação com a viagem, se necessário.
        """
        # Aqui, não é necessário associar uma viagem, pois a classificação já está associada
        serializer.save()


# Create 
class ClienteMetodosPagamantosCreateView(generics.ListCreateAPIView):
    serializer_class = ClienteMetodoPagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        agencia_id = self.request.query_params.get('agencia_id', None)
        if agencia_id:
            try:
                agencia_id = AppMetodoPagamento.objects.get(pk=agencia_id)
                return agencia_id
            except AppMetodoPagamento.DoesNotExist:
                return AppMetodoPagamento.objects.none()  # Retorna uma queryset vazia se a viagem não existir
        return AppMetodoPagamento.objects.all()

    def create(self, request, *args, **kwargs):
        # Obtém os dados da requisição
        agencia_id = request.data.get('agencia_id')
        numero_pagamento = request.data.get('numero_pagamento')
        default = request.data.get('default')
        cliente = Cliente.objects.get(user=request.user)
        

        try:
            # Obtém a viagem com base no ID fornecido
            agencia = AppMetodoPagamento.objects.get(pk=agencia_id)
        except AppMetodoPagamento.DoesNotExist:
            return Response({"message": 'Tipo de agência não foi selecionado.'},status=status.HTTP_400_BAD_REQUEST)


        # Verifica se já existe uma venda de bilhete para a viagem e o cliente
        if ClienteMetodoPagamento.objects.filter(agencia=agencia, numero_pagamento=numero_pagamento, cliente__user=request.user).exists():
            return Response({"message": 'Este método já foi cadastardo.'},status=status.HTTP_400_BAD_REQUEST)


        # Cria a venda do bilhete
        venda_bilhete = ClienteMetodoPagamento(
            cliente=cliente,
            agencia=agencia,
            numero_pagamento=numero_pagamento,
            default=default,
        )
        venda_bilhete.save()

        return Response({"message": 'Método adicionado com sucesso.'},status=status.HTTP_201_CREATED)


# update
class ClienteMetodoPagamentoUpdateView(APIView):
    def patch(self, request, pk):
        try:
            metodo_pagamento = ClienteMetodoPagamento.objects.get(pk=pk)
            serializer = ClienteMetodoPagamentoUpdateDeleteSerializer(metodo_pagamento, data=request.data, partial=True)  # partial=True para atualizações parciais
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ClienteMetodoPagamento.DoesNotExist:
            return Response({'error': 'Método de pagamento não encontrado'}, status=status.HTTP_404_NOT_FOUND)


class ClienteMetodoPagamentoDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        try:
            metodo_pagamento = ClienteMetodoPagamento.objects.get(pk=pk)
            metodo_pagamento.delete()
            return Response({'message': 'Método de pagamento deletado com sucesso!'}, status=status.HTTP_204_NO_CONTENT)
        except ClienteMetodoPagamento.DoesNotExist:
            return Response({'error': 'Método de pagamento não encontrado'}, status=status.HTTP_404_NOT_FOUND)


# Vender Bilhete
class VenderBilheteListCreateView(generics.ListCreateAPIView):
    serializer_class = VendaBilheteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        id_viagem = self.request.query_params.get('id_viagem', None)
        if id_viagem:
            try:
                viagem_id = Viagem.objects.get(pk=id_viagem)
                return VendaBilhete.objects.filter(viagem=viagem_id)
            except Viagem.DoesNotExist:
                return VendaBilhete.objects.none()  # Retorna uma queryset vazia se a viagem não existir
        return VendaBilhete.objects.all()

    def create(self, request, *args, **kwargs):
        # Obtém os dados da requisição
        id_viagem = request.data.get('id_viagem')
        id_metodopagamento = request.data.get('id_metodopagamanto')
        preco_bilhete = request.data.get('preco_total')
        desconto_bilhete = request.data.get('desconto')
        subtotal_bilhete = request.data.get('subtotal')
        total_pago_bilhete = request.data.get('total_pago')
        quantidade_bilhete = request.data.get('quantidade')

        try:
            # Obtém a viagem com base no ID fornecido
            viagem_id = Viagem.objects.get(pk=id_viagem)
        except Viagem.DoesNotExist:
            raise ValidationError("Viagem não encontrada.")

        # Verifica se o método de pagamento existe
        try:
            metodo_pagamento = ClienteMetodoPagamento.objects.get(pk=id_metodopagamento, cliente__user=request.user)
        except ClienteMetodoPagamento.DoesNotExist:
            raise ValidationError("Método de pagamento não encontrado.")

        # Verifica se já existe uma venda de bilhete para a viagem e o cliente
        if VendaBilhete.objects.filter(viagem=viagem_id, data_venda__iexact=viagem_id.data_saida ,cliente__user=request.user).exists():
            raise ValidationError("Já existe um bilhete comprado para essa viagem.")

        # Obtém o cliente baseado no usuário autenticado
        cliente = Cliente.objects.get(user=request.user)

        # Cria a venda do bilhete
        venda_bilhete = VendaBilhete(
            cliente=cliente,
            viagem=viagem_id,
            metodo_pagamento=metodo_pagamento,
            preco_total=preco_bilhete,
            desconto=desconto_bilhete,
            subtotal=subtotal_bilhete,
            total_pago=total_pago_bilhete,
            quantidade=quantidade_bilhete,
        )
        venda_bilhete.save()

        # Retorna o ID da venda criada
        serializer = VendaBilheteSerializer(venda_bilhete)
        return Response(serializer.data,status=status.HTTP_201_CREATED)














# ==========================Parte II Agente & Operador ================================

# Login dos profissionais
class LoginProfissView(generics.GenericAPIView):
    serializer_class = UserClienteSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('phone_number')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            
            match user:
                
                case _ if hasattr(user, 'agente'):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'type_user':"agente"
                    })

                case _ if hasattr(user, 'operador'):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'type_user':"operador"
                    })

                case _:
                    logout(request)
                    return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_400_BAD_REQUEST)



class AgenteRotasView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):

        try:
            data_atual = timezone.now() + timedelta(days=1)
            agente = request.user.agente  # Obtém o cliente autenticado
            # Filtra as viagens do agente específico
            rotas = Rotas.objects.filter(agente=agente).annotate(
                total_aprovados=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Aprovado')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                total_pendentes=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Pendente')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                total_cancelados=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Cancelado')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                
            )
        
            serializer = AgenteRotasSerializer(rotas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class EstatisticasAgenteView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        data_atual = timezone.now()
        data_ontem = data_atual - timedelta(days=1)
        

        # Estatísticas de bilhetes hoje
        total_bilhetes = Bilhete.objects.filter(
            viagem__agente=request.user.agente, data_criado__exact=data_atual
        ).count()

        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__exact=data_atual, viagem__agente=request.user.agente, status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__exact=data_atual, viagem__agente=request.user.agente, status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__exact=data_atual, viagem__agente=request.user.agente, status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            viagem__agente=request.user.agente, data_criado__exact=data_atual, status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')


        receita_ontem = Bilhete.objects.filter(
            viagem__agente=request.user.agente, data_criado__exact=data_ontem, status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Cálculo da porcentagem de variação
        def calcular_variacao_percentual(valor_atual, valor_anterior):
            if valor_anterior == 0:
                return 100 if valor_atual > 0 else 0
            return ((valor_atual - valor_anterior) / valor_anterior) * 100

        variacao_receita = calcular_variacao_percentual(receita_diaria, receita_ontem)

        # Resumo das informações para o agente
        estatisticas = {
            "total_bilhetes": total_bilhetes,
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "variacao_receita": f'{variacao_receita:.2f}',  # Variação percentual da receita
        }
        
        
        # Retorna as informações em formato JSON
        return Response(estatisticas)


class EstatisticaAgenteVendasSemanaisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        data_atual = timezone.now() +timedelta(days=1)

        # Dados de vendas diárias para os últimos 7 dias
        vendas_semanais = []
        
        for i in range(7):
            dia = (data_atual - timedelta(days=i)).date()
            
            bilhete=Bilhete.objects.filter(Q(viagem__agente=request.user.agente) & Q(viagem__data_saida__exact=dia) & (Q(status_bilhete='Aprovado') | Q( status_bilhete='realizado')) )
            
            # if bilhete:
            receita_dia = bilhete.aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

            vendas_semanais.append({
                'dia': dia.strftime('%A'),
                'receita': float(receita_dia)  # Convertendo para float para JSON
            })

        # Inverte a lista para que os dias mais antigos apareçam primeiro
        vendas_semanais.reverse()

        # Resumo da receita semanal total
        # receita_total_semanal = sum([venda['receita'] for venda in vendas_semanais])
        

        return JsonResponse(vendas_semanais, safe=False, json_dumps_params={'ensure_ascii': False})
    

class AgenteRotaViagensView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, pk, format=None):
        

        # Filtra as viagens do agente específico
        viagens = Viagem.objects.filter(rota__pk=pk).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return Response(serializer.data)


class AgenteRotaViagemView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, pk, format=None):
        # Filtra as viagens do agente específico
        viagens = Viagem.objects.filter(pk=pk).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return Response(serializer.data)


class AgenteRotaViagemBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, pk, format=None):
        
        bilhetes = Bilhete.objects.filter(viagem__pk=pk)
        serializer = BilheteSerializer(bilhetes, many=True, context={'request': request})
        
        return Response(serializer.data)


class AgenteRotaViagemBilheteView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado
    def get(self, request, pk, format=None):
        
        bilhetes = Bilhete.objects.filter(pk=pk)
        serializer = BilheteSerializer(bilhetes, many=True, context={'request': request})
        return Response(serializer.data)


class AgenteRotaViagemAssentosView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            viagemAssento= ViagemAssento.objects.filter(viagem__pk=pk)
            
            serializer = AgenteRotaViagemAssentosSerializer(viagemAssento, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ViagemAssento.DoesNotExist:
            return Response({'error': 'Assentos não encontrados'}, status=status.HTTP_404_NOT_FOUND)


class AgenteRotaViagemAssentoUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgenteRotaViagemAssentosSerializer
    def put(self, request):
        try:
            pk=request.data['id']
            disponivel=request.data['disponivel']
            assento=ViagemAssento.objects.get(pk=pk)
            assento.disponivel=disponivel
            assento.save()
            serializer = AgenteRotaViagemAssentosSerializer(assento)
            return Response({"":serializer.data,'message': 'Assento actualizado com sucesso.',}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': 'Assento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class AgenteRotaViagemBilheteUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BilheteSerializer

    def put(self, request):
        try:
            pk = request.data['id']
            status_bilhete = request.data['status_bilhete']
            motivo = request.data['motivo']
            
            # Obtendo o bilhete existente
            bilhete = Bilhete.objects.get(pk=pk)
            bilhete.status_bilhete = status_bilhete
            bilhete.motivo = motivo

            # Atualizando o status e realizando ações associadas
            match status_bilhete:
                case 'Aprovado':
                    
                    assento = ViagemAssento.objects.filter(viagem=bilhete.viagem, assento=bilhete.assento).first()
                    assento.activo = True
                    assento.disponivel = False
                    assento.save()
                    sendMessage(bilhete.cliente.user.pk, "Reserva", "Seu pedido de reserva foi aprovado.", bilhete.pk)
                    
                case 'Cancelado':
                    assento = ViagemAssento.objects.filter(viagem=bilhete.viagem, assento=bilhete.assento).first()
                    assento.activo = False
                    assento.disponivel = True
                    assento.save()
                    sendMessage(bilhete.cliente.user.pk, "Reserva", "Seu pedido de reserva foi cancelado.", bilhete.pk)

            # Salvar as alterações no modelo Bilhete
            bilhete.save()  # Isso salvará o modelo, incluindo qualquer campo de mídia automaticamente

            # Serializando a resposta
            serializer = BilheteSerializer(bilhete)
            return Response({
                'data': serializer.data,
                'message': 'Bilhete atualizado com sucesso.',
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({
                'error': f'Bilhete não encontrado ou erro durante atualização. {e}'
            }, status=status.HTTP_404_NOT_FOUND)

# Vendas diarias de bilhetes
class AgenteVendasDiariasBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        data_actual=timezone.now() + timedelta(days=1)

        try:

            bilhetes = Bilhete.objects.filter(viagem__agente=request.user.agente,viagem__data_saida__exact=data_actual)
            serializer = BilheteSerializer(bilhetes, many=True, context={'request': request})
            return Response(serializer.data)
        
        except Exception as e:
            return Response({"error":e}, status=status.HTTP_401_UNAUTHORIZED)


# proximas viagens
class AgenteProximaViagemView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        proxima_viagem=timedelta(days=1)+ timezone.now()
        # Filtra as viagens do agente específico
        agente=request.user.agente
        viagens = Viagem.objects.filter(data_saida__exact=proxima_viagem, agente=agente).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})


# buscar dados de uma viagem
class AgenteReservaViagemGetView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, pk, format=None):
        
        viagens = Viagem.objects.filter(pk=pk, activo=True).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Realizada')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})


class AgenteAgendaViagemGetView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, pk, format=None):
        
        viagens = Viagem.objects.filter(pk=pk).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Realizada')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})


# Reservas das proximas viagens
class AgenteViagemReservaBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, pk, format=None):
        data_proxima=timedelta(days=1)+timezone.now()

        try:

            bilhetes = Bilhete.objects.filter(viagem__agente=request.user.agente, viagem__pk=pk, viagem__data_saida__exact=data_proxima)
            serializer = ReservasBilheteSerializer(bilhetes, many=True, context={'request': request})
            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


# todas reservas de bilhetes
class AgenteRelatoriosBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:
            proxima_viagem=timedelta(days=2)+ timezone.now()

            viagens = Bilhete.objects.filter(viagem__agente=request.user.agente, viagem_data_saida__lte=proxima_viagem).values('viagem')
            serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)
        

# Proximas reservas
class AgenteProximasReservasBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:

            proxima_viagem=timedelta(days=2)+ timezone.now()

            bilhetes = Bilhete.objects.filter(viagem__agente=request.user.agente, viagem__data_saida__gte=proxima_viagem)
            viagens=[
                Viagem.objects.filter(pk=bilhete.viagem.pk).annotate(
                    total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
                    total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
                    total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
                    total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
                ) 
                     
                    for bilhete in bilhetes ]
            
            
            serializers = list(AgenteViagemBilheteStatusSerializer(viagem, many=True).data[0] for viagem in viagens)
            
            return JsonResponse(serializers,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            print(e)
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


# Estatisticas das proximas viagens marcadas
class EstatisticasAgenteReservasView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        data_atual = timezone.now() + timedelta(days=2)
        data_ontem = data_atual + timedelta(days=1)
        

        # Estatísticas de bilhetes hoje
        total_bilhetes = Bilhete.objects.filter(
            viagem__agente=request.user.agente, viagem__data_saida__gte=data_atual
        ).count()

        bilhetes_aprovados = Bilhete.objects.filter(
            viagem__data_saida__gte=data_atual, viagem__agente=request.user.agente, status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            viagem__data_saida__gte=data_atual, viagem__agente=request.user.agente, status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            viagem__data_saida__gte=data_atual, viagem__agente=request.user.agente, status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            viagem__agente=request.user.agente, viagem__data_saida__gte=data_atual, status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Comparações com o dia anterior (ontem)
        total_bilhetes_ontem = Bilhete.objects.filter(
            viagem__agente=request.user.agente, viagem__data_saida__gte=data_ontem
        ).count()

        receita_ontem = Bilhete.objects.filter(
            viagem__agente=request.user.agente, viagem__data_saida__gte=data_ontem, status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Cálculo da porcentagem de variação
        def calcular_variacao_percentual(valor_atual, valor_anterior):
            if valor_anterior == 0:
                return 100 if valor_atual > 0 else 0
            return ((valor_atual - valor_anterior) / valor_anterior) * 100

        variacao_receita = calcular_variacao_percentual(receita_diaria, receita_ontem)

        # Resumo das informações para o agente
        estatisticas = {
            "total_bilhetes": total_bilhetes,
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "variacao_receita": f'{variacao_receita:.2f}',  # Variação percentual da receita
        }

        # Retorna as informações em formato JSON
        return Response(estatisticas)


class AgenteCheckinViagensView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:
            proxima_viagem= timezone.now()
            agente=request.user.agente
            viagens=Viagem.objects.filter(agente=agente,data_saida__exact=proxima_viagem).order_by('-data_saida').annotate(
                total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
                total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
                total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
                total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
            ) 
            
            
            serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
            
            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            print(e)
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class AgenteCheckinViagemPassageiroView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:
            proxima_viagem= timezone.now()
            viagem=Viagem.objects.get(pk=pk)
            bilhetes = Bilhete.objects.filter(viagem__rota=viagem.rota,viagem__data_saida__lte=proxima_viagem).exclude(status_bilhete='Cancelado').exclude(status_bilhete='Pendente')
            
            serializer = BilheteSerializer(bilhetes, many=True, context={'request': request})

            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            print(e)
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class AgenteCheckinListPassageiroView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:
            data_actual= timezone.now()
            agente=request.user.agente
            bilhetes = Bilhete.objects.filter(viagem__agente=agente,viagem__data_saida__exact=data_actual,status_bilhete='Aprovado') 
            
            serializer = BilheteSerializer(bilhetes, many=True, context={'request': request})

            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            print(e)
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)
        

class AgenteCheckinPassageiroUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado
    serializer_class = BilheteSerializer
    def put(self, request):
        try:
            pk=request.data.get('id')
            bilhete = Bilhete.objects.get(pk=pk)
            bilhete.status_viagem="Confirmado"
            bilhete.save()
            print(bilhete.status_viagem)
            return Response({'message':'actualizado com sucesso.'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e, )
            return Response({"error":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)


# Estatisiticas de reservas
class EstatisticasReservasDiariasAgenteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_bilhetes_statistics(self, agente, start_date):
        
        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__agente=agente,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__agente=agente,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__agente=agente,
            status_bilhete='Cancelado'
        ).count()

        total_bilhetes = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__agente=agente,
        ).count()

        receita_total = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__agente=agente,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        return {
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "total_bilhetes": total_bilhetes,
            "variacao_receita":f'{receita_total:.2f}',
            "receita_diaria": f'{receita_total:.2f}',
        }

    def get(self, request, format=None):
        agente = request.user.agente
        if not agente:
            return Response({"error": "Agente não encontrado."}, status=404)
        
        data_atual = timezone.localdate()
        
        estatisticas_diarias = self.get_bilhetes_statistics(agente, data_atual)
        return Response(estatisticas_diarias)


class EstatisticasReservasSemanalAgenteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_bilhetes_statistics(self, agente, start_date, end_date):
        # Contagem dos bilhetes por status
        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Cancelado'
        ).count()

        total_bilhetes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
        ).count()

        receita_total = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        return {
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "total_bilhetes": total_bilhetes,
            "variacao_receita":f'{receita_total:.2f}',
            "receita_diaria": f'{receita_total:.2f}',
        }

    def get(self, request, format=None):
        agente = request.user.agente
        if not agente:
            return Response({"error": "Agente não encontrado."}, status=404)

        data_atual = timezone.localdate()

        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim da semana
        inicio_da_semana = ultimo_pedido_data - timedelta(days=7)
        inicio_da_semana = timezone.make_aware(datetime.combine(inicio_da_semana, datetime.min.time()))  # Início do dia (00:00)
        fim_da_semana = ultimo_pedido_data  # Fim do dia (23:59:59)
        fim_da_semana = timezone.make_aware(datetime.combine(fim_da_semana, datetime.max.time()))

        # Obtém as estatísticas semanais
        estatisticas_semanais = self.get_bilhetes_statistics(agente, inicio_da_semana, fim_da_semana)
        return Response(estatisticas_semanais)


class EstatisticasReservasMensalAgenteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_agente(self, request):
        try:
            return request.user.agente
        except Exception:
            return None

    def get_bilhetes_statistics(self, agente, start_date, end_date):
        # Contagem dos bilhetes por status
        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Cancelado'
        ).count()

        total_bilhetes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
        ).count()

        receita_total = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__agente=agente,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        return {
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "total_bilhetes": total_bilhetes,
            "variacao_receita":f'{receita_total:.2f}',
            "receita_diaria": f'{receita_total:.2f}',
        }

    def get(self, request, format=None):
        agente = self.get_agente(request)
        if not agente:
            return Response({"error": "Agente não encontrado."}, status=404)

        data_atual = timezone.localdate()

        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim do mês
        inicio_do_mes = ultimo_pedido_data - timedelta(days=30)
        inicio_do_mes = timezone.make_aware(datetime.combine(inicio_do_mes, datetime.min.time()))  # Início do dia (00:00)
        fim_do_mes = ultimo_pedido_data  # Fim do dia (23:59:59)
        fim_do_mes = timezone.make_aware(datetime.combine(fim_do_mes, datetime.max.time()))

        # Obtém as estatísticas mensais
        estatisticas_mensais = self.get_bilhetes_statistics(agente, inicio_do_mes, fim_do_mes)
        return Response(estatisticas_mensais)

# =============================Fim estatisticas reservas============================
















# ======================================= Operador ========================================

class OperadorMetodosPagamantos(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,format=None):
        # Verifica se o usuário tem um perfil de cliente
        if hasattr(request.user, 'operador'):
            operador = request.user.operador
            # Filtra métodos de pagamento pelo cliente
            cliente_metodo_pagamento = OperadorMetodoPagamento.objects.filter(operador=operador)

            if cliente_metodo_pagamento.exists():
                # Passa o queryset completo com many=True para o serializer
                serializer = OperadorMetodoPagamentoSerializer(cliente_metodo_pagamento, many=True,context={'request': request})
                return Response(serializer.data)
            else:
                return Response({'message': 'Ainda não cadastrou nenhum método'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Não tem permissão'}, status=status.HTTP_401_UNAUTHORIZED)



# Create 
class OperadorMetodosPagamantosCreateView(generics.ListCreateAPIView):
    serializer_class = OperadorMetodoPagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]


    def create(self, request, *args, **kwargs):
        # Obtém os dados da requisição
        agencia_id = request.data.get('agencia_id')
        numero_pagamento = request.data.get('numero_pagamento')
        default = request.data.get('default')
        operador = Operador.objects.get(user=request.user)
        

        try:
            # Obtém a viagem com base no ID fornecido
            agencia = AppMetodoPagamento.objects.get(pk=agencia_id)
        except AppMetodoPagamento.DoesNotExist:
            return Response({"message": 'Tipo de agência não foi selecionado.'},status=status.HTTP_400_BAD_REQUEST)


        # Verifica se já existe uma venda de bilhete para a viagem e o cliente
        if OperadorMetodoPagamento.objects.filter(agencia=agencia, numero_pagamento=numero_pagamento, operador__user=request.user).exists():
            return Response({"message": 'Este método já foi cadastardo.'},status=status.HTTP_400_BAD_REQUEST)


        # Cria a venda do bilhete
        venda_bilhete = OperadorMetodoPagamento(
            operador=operador,
            agencia=agencia,
            numero_pagamento=numero_pagamento,
            default=default,
        )
        venda_bilhete.save()

        return Response({"message": 'Método adicionado com sucesso.'},status=status.HTTP_201_CREATED)


# update
class OperadorMetodoPagamentoUpdateView(APIView):
    def patch(self, request, pk):
        try:
            metodo_pagamento = OperadorMetodoPagamento.objects.get(pk=pk)
            serializer = OperadorMetodoPagamentoUpdateDeleteSerializer(metodo_pagamento, data=request.data, partial=True)  # partial=True para atualizações parciais
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except OperadorMetodoPagamento.DoesNotExist:
            return Response({'error': 'Método de pagamento não encontrado'}, status=status.HTTP_404_NOT_FOUND)


class OperadorMetodoPagamentoDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        try:
            metodo_pagamento = OperadorMetodoPagamento.objects.get(pk=pk)
            metodo_pagamento.delete()
            return Response({'message': 'Método de pagamento deletado com sucesso!'}, status=status.HTTP_204_NO_CONTENT)
        except OperadorMetodoPagamento.DoesNotExist:
            return Response({'error': 'Método de pagamento não encontrado'}, status=status.HTTP_404_NOT_FOUND)



class EmpresaOperadorView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request, format=None):
        try:
            # Obtém a empresa do operador autenticado
            empresa = request.user.operador.operador_empresa
            
            # Verifica se empresa é uma instância de Empresa
            if not isinstance(empresa, Empresa):
                return Response({"message": "Empresa não encontrada."}, status=status.HTTP_404_NOT_FOUND)
            
            # Serializa a empresa
            serializer = EmpresaSerializer(empresa, context={'request': request})
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def put(self, request, *args, **kwargs):
        """Atualiza uma Empresa existente."""
        try:
            empresa = request.user.operador.operador_empresa
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa não encontrada"}, status=status.HTTP_404_NOT_FOUND)
        # Atualizar os dados do request com informações do operador
        data = request.data.copy()
        data["dono"] = request.user.operador.pk
        serializer = EmpresaSerializer(empresa, data=data, context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(request.data,serializer.errors, data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Informacoes gerais 
class EstatisticasOperadorView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request, format=None):
        # Obtém a empresa associada ao operador
        try:
            empresa = request.user.operador.operador_empresa
        except Exception as e:
            return Response({"error": "Operador não encontrado."}, status=404)

        # Data atual e data de ontem
        data_atual = timezone.localdate()
        

        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__exact=data_atual,
            viagem__empresa=empresa, 
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__exact=data_atual,
            viagem__empresa=empresa, 
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__exact=data_atual,
            viagem__empresa=empresa, 
            status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            data_criado__exact=data_atual,
            empresa=empresa, 
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Contagem de agentes e rotas
        total_agentes = Agente.objects.filter(empresa=empresa).count()
        total_rotas = Rotas.objects.filter(empresa=empresa).count()

        # Resumo das informações para o operador
        estatisticas = {
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "total_agentes": total_agentes,
            "total_rotas": total_rotas,
        }

        # Retorna as informações em formato JSON
        return Response(estatisticas)


# Vendas dos agentes e rotas
class OperadorVendasAgentesSemanaisView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request, format=None):
        # Obtém a empresa associada ao operador
        try:
            empresa = request.user.operador.operador_empresa
        except Exception as e:
            return Response({"error": "Operador não encontrado."}, status=404)

        data_atual = timezone.localdate()
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim do mês (últimos 7 dias)
        inicio_do_mes = ultimo_pedido_data - timedelta(days=7)

        relatorioAgente = []
        for agente in Agente.objects.filter(empresa=empresa).exclude(activo=False):
            receita_total = Bilhete.objects.filter(
                data_criado__range=(inicio_do_mes, ultimo_pedido_data),
                viagem__agente=agente,
                status_bilhete='Aprovado'
            ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

            relatorioAgente.append({
                "Agente": agente.user.get_full_name(),  # Corrigido para chamar o método
                "receita": receita_total
            })

        # Retorna as informações em formato JSON
        return Response(relatorioAgente)
  

class OperadorVendasAgentesMensaisView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request, format=None):
        # Obtém a empresa associada ao operador
        try:
            empresa = request.user.operador.operador_empresa
        except Exception as e:
            return Response({"error": "Operador não encontrado."}, status=404)
        data_atual = timezone.localdate()

        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim do mês
        inicio_do_mes = ultimo_pedido_data - timedelta(days=30)

        relatorioAgente = []
        for agente in Agente.objects.filter(empresa=empresa).exclude(activo=False):
            receita_total = (Bilhete.objects.filter(
                data_criado__range=(inicio_do_mes, ultimo_pedido_data),
                viagem__agente=agente,
                status_bilhete='Aprovado'
            ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')).quantize(Decimal('0.00'))

            relatorioAgente.append({
                "Agente": agente.user.get_full_name(),  
                "receita": f"{receita_total:.2f}"
            })

        # Retorna as informações em formato JSON
        return Response(relatorioAgente)
    

class OperadorVendasRotasSemanaisView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request, format=None):
        # Obtém a empresa associada ao operador
        try:
            empresa = request.user.operador.operador_empresa
        except Exception as e:
            return Response({"error": "Operador não encontrado."}, status=404)

        data_atual = timezone.localdate()
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim do mês (últimos 7 dias)
        inicio_do_mes = ultimo_pedido_data - timedelta(days=7)
        relatorioRota = []
        for rota in Rotas.objects.filter(empresa=empresa).exclude(activo=False):
            receita_total = (Bilhete.objects.filter(
                data_criado__range=(inicio_do_mes, ultimo_pedido_data),
                viagem__rota=rota,
                status_bilhete='Aprovado'
            ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')).quantize(Decimal('0.00'))

            relatorioRota.append({
                "origem": f"{rota.origem.nome}",
                "destino": f"{rota.destino.nome}",
                "receita": f"{receita_total:.2f}"
            })

        # Retorna as informações em formato JSON
        return Response(relatorioRota)
  

class OperadorVendasRotasMensaisView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request, format=None):
        # Obtém a empresa associada ao operador
        try:
            empresa = request.user.operador.operador_empresa
        except Exception as e:
            return Response({"error": "Operador não encontrado."}, status=404)
        data_atual = timezone.localdate()

        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim do mês
        inicio_do_mes = ultimo_pedido_data - timedelta(days=30)

        relatorioRota = []
        for rota in Rotas.objects.filter(empresa=empresa).exclude(activo=False):
            receita_total = (Bilhete.objects.filter(
                data_criado__range=(inicio_do_mes, ultimo_pedido_data),
                viagem__rota=rota,
                status_bilhete='Aprovado'
            ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')).quantize(Decimal('0.00'))

            relatorioRota.append({
                "origem": f"{rota.origem.nome}",
                "destino": f"{rota.destino.nome}",
                "receita": f"{receita_total:.2f}"
            })

        # Retorna as informações em formato JSON
        return Response(relatorioRota)
    
# Fim vendas de agentes e rotas

# Estatisiticas de reservas
class EstatisticasReservasDiariasOperadorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_empresa(self, request):
        try:
            return request.user.operador.operador_empresa
        except Exception:
            return None

    def get_bilhetes_statistics(self, empresa, start_date):
        
        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__empresa=empresa,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__empresa=empresa,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__empresa=empresa,
            status_bilhete='Cancelado'
        ).count()

        total_bilhetes = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__empresa=empresa
        ).count()

        receita_total = Bilhete.objects.filter(
            data_criado__exact=start_date,
            viagem__empresa=empresa,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        return {
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "total_bilhetes": total_bilhetes,
            "receita_total": f'{receita_total:.2f}',
        }

    def get(self, request, format=None):
        empresa = self.get_empresa(request)
        if not empresa:
            return Response({"error": "Operador não encontrado."}, status=404)
        
        data_atual = timezone.localdate()
        
        estatisticas_diarias = self.get_bilhetes_statistics(empresa, data_atual)
        return Response(estatisticas_diarias)


class EstatisticasReservasSemanalOperadorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_empresa(self, request):
        try:
            return request.user.operador.operador_empresa
        except Exception:
            return None

    def get_bilhetes_statistics(self, empresa, start_date, end_date):
        # Contagem dos bilhetes por status
        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Cancelado'
        ).count()

        total_bilhetes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa
        ).count()

        receita_total = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        return {
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "total_bilhetes": total_bilhetes,
            "receita_total": f'{receita_total:.2f}',
        }

    def get(self, request, format=None):
        empresa = self.get_empresa(request)
        if not empresa:
            return Response({"error": "Operador não encontrado."}, status=404)

        data_atual = timezone.localdate()

        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim da semana
        inicio_da_semana = ultimo_pedido_data - timedelta(days=7)
        inicio_da_semana = timezone.make_aware(datetime.combine(inicio_da_semana, datetime.min.time()))  # Início do dia (00:00)
        fim_da_semana = ultimo_pedido_data  # Fim do dia (23:59:59)
        fim_da_semana = timezone.make_aware(datetime.combine(fim_da_semana, datetime.max.time()))

        # Obtém as estatísticas semanais
        estatisticas_semanais = self.get_bilhetes_statistics(empresa, inicio_da_semana, fim_da_semana)
        return Response(estatisticas_semanais)


class EstatisticasReservasMensalOperadorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_empresa(self, request):
        try:
            return request.user.operador.operador_empresa
        except Exception:
            return None

    def get_bilhetes_statistics(self, empresa, start_date, end_date):
        # Contagem dos bilhetes por status
        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Cancelado'
        ).count()

        total_bilhetes = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa
        ).count()

        receita_total = Bilhete.objects.filter(
            data_criado__range=(start_date, end_date),
            viagem__empresa=empresa,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        return {
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "total_bilhetes": total_bilhetes,
            "receita_total": f'{receita_total:.2f}',
        }

    def get(self, request, format=None):
        empresa = self.get_empresa(request)
        if not empresa:
            return Response({"error": "Operador não encontrado."}, status=404)

        data_atual = timezone.localdate()

        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = data_atual

        # Calcula o início e o fim do mês
        inicio_do_mes = ultimo_pedido_data - timedelta(days=30)
        inicio_do_mes = timezone.make_aware(datetime.combine(inicio_do_mes, datetime.min.time()))  # Início do dia (00:00)
        fim_do_mes = ultimo_pedido_data  # Fim do dia (23:59:59)
        fim_do_mes = timezone.make_aware(datetime.combine(fim_do_mes, datetime.max.time()))

        # Obtém as estatísticas mensais
        estatisticas_mensais = self.get_bilhetes_statistics(empresa, inicio_do_mes, fim_do_mes)
        return Response(estatisticas_mensais)

# =============================Fim estatisticas reservas============================

# Carregar todas as reservas
class OperadorReservasBilhetesDiarioView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:
            dataAtual = timezone.now().date()
            empresa = request.user.operador.operador_empresa
            
            reservas = Bilhete.objects.filter(
                data_criado__exact=dataAtual,
                empresa=empresa,
            ).order_by('-pk')
            serializer = OperadorReservasSerializer(reservas, many=True, context={"request": request})
            return Response(serializer.data)
        
        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class OperadorReservasBilhetesSemanalView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:
            empresa = request.user.operador.operador_empresa
            
            dataAtual = timezone.localdate()

            # Obter o último pedido da empresa
            ultimo_pedido_data = dataAtual

            # Cálculo do início e fim da semana
            inicio_da_semana = ultimo_pedido_data - timedelta(days=7)
            inicio_da_semana = timezone.make_aware(datetime.combine(inicio_da_semana, datetime.min.time()))  # Início do dia (00:00)
            fim_da_semana = ultimo_pedido_data
            fim_da_semana = timezone.make_aware(datetime.combine(fim_da_semana, datetime.max.time()))  # Fim do dia (23:59:59)

            # Filtra as reservas da última semana
            reservas = Bilhete.objects.filter(
                viagem__empresa=empresa,
                data_criado__range=(inicio_da_semana, fim_da_semana)  # Última semana
            ).order_by('-pk')

            # Serializa os dados
            serializer = OperadorReservasSerializer(reservas, many=True, context={"request": request})
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class OperadorReservasBilhetesMensalView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:
            empresa = request.user.operador.operador_empresa
            dataAtual = timezone.localdate()

            # Obter o último pedido da empresa
            ultimo_pedido_data = dataAtual

            # Cálculo do início e fim do mês
            inicio_do_mes = ultimo_pedido_data - timedelta(days=30)
            inicio_do_mes = timezone.make_aware(datetime.combine(inicio_do_mes, datetime.min.time()))  # Início do dia (00:00)
            fim_do_mes = ultimo_pedido_data
            fim_do_mes = timezone.make_aware(datetime.combine(fim_do_mes, datetime.max.time()))  # Fim do dia (23:59:59)

            # Filtra as reservas do último mês
            reservas = Bilhete.objects.filter(
                viagem__empresa=empresa,
                status_bilhete__in=['Aprovado', 'Cancelado', 'Pendente'],
                data_criado__range=(inicio_do_mes, fim_do_mes)  # Últimos 30 dias
            ).order_by('-data_criado')

            # Serializa os dados
            serializer = OperadorReservasSerializer(reservas, many=True, context={"request": request})
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)

# Fim carregamento de reservas


class EstatisticaAgentesVendasSemanaisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        data_atual = timezone.now() +timedelta(days=1)

        # Dados de vendas diárias para os últimos 7 dias
        vendas_semanais = []
        
        for i in range(7):
            dia = (data_atual - timedelta(days=i)).date()
            
            bilhete=Bilhete.objects.filter(Q(viagem__agente=request.user.agente) & Q(viagem__data_saida__exact=dia) & (Q(status_bilhete='Aprovado') | Q( status_bilhete='realizado')) )
            
            # if bilhete:
            receita_dia = bilhete.aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

            vendas_semanais.append({
                'dia': dia.strftime('%A'),
                'receita': float(receita_dia)  # Convertendo para float para JSON
            })

        # Inverte a lista para que os dias mais antigos apareçam primeiro
        vendas_semanais.reverse()

        # Resumo da receita semanal total
        # receita_total_semanal = sum([venda['receita'] for venda in vendas_semanais])
        

        return JsonResponse(vendas_semanais, safe=False, json_dumps_params={'ensure_ascii': False})


# Meus Agentes
class MeusAgentesOperadorView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request, format=None):
        # Obtém a empresa associada ao operador
        try:
            agentes = request.user.operador.operador_empresa.empresa_agente.annotate(totalRotas=Count('rota_agente'))
            
            serializers=OperadorMeusAgenteSerializer(agentes,many=True)
            return Response(serializers.data, status=200)
        except Exception as e:
            
            return Response({"error": f"Operador não encontrado. {e}"}, status=404)


class MeuAgenteRotaOperadorView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o operador esteja logado

    def get(self, request,pk, format=None):
        # Obtém a empresa associada ao operador
        try:
            agentes = request.user.operador.operador_empresa.empresa_agente.all()
            data_atual = timezone.now() + timedelta(days=1)
            agente = Agente.objects.get(pk=pk)  # Obtém o cliente autenticado
            # Filtra as viagens do agente específico
            rotas = Rotas.objects.filter(agente=agente).annotate(
                total_aprovados=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Aprovado')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                total_pendentes=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Pendente')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                total_cancelados=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Cancelado')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                
            )
        
            serializer = AgenteRotasSerializer(rotas, many=True)
            return Response(serializer.data)
        except Exception as e:
            
            return Response({"error": f"Operador não encontrado. {e}"}, status=404)


# Obter minhas rotas por agente
class OperadorAgentesRotasView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):

        try:
            data_atual = timezone.now() + timedelta(days=1)
            empresa_rota= request.user.operador.operador_empresa.empresa_rota.all()  # Obtém o cliente autenticado
            # Filtra as viagens do agente específico
            rotas = empresa_rota.annotate(
                total_aprovados=Count('empresa__bilhetes_empresa', filter=Q(empresa__bilhetes_empresa__status_bilhete='Aprovado')
                                    & Q(empresa__bilhetes_empresa__viagem__data_saida__gte=data_atual)),
                total_pendentes=Count('empresa__bilhetes_empresa', filter=Q(empresa__bilhetes_empresa__status_bilhete='Pendente')
                                    & Q(empresa__bilhetes_empresa__viagem__data_saida__gte=data_atual)),
                total_cancelados=Count('empresa__bilhetes_empresa', filter=Q(empresa__bilhetes_empresa__status_bilhete='Cancelado')
                                    & Q(empresa__bilhetes_empresa__viagem__data_saida__gte=data_atual)),
                
            )
        
            serializer = AgenteRotasSerializer(rotas, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



# CRUD AGENTE
class OperadorAgenteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Agente.objects.all()
    serializer_class = OperadorAgenteCRUDSerializer

    def perform_create(self, serializer):
        # Salva o agente ao criar
        serializer.save()

    def perform_update(self, serializer):
        try:
            # Recupera a instância do Agente
            instance = serializer.instance
            user_data = self.request.data.get('user', None)
            
            # Se houver dados de 'user', tentamos atualizar o usuário
            if user_data:
                username = user_data.get('username', None)
                # Verifica se o username é diferente do atual e se já existe outro usuário com o mesmo username
                if username and username != instance.user.username:
                    if User.objects.filter(username=username).exists():
                        raise serializers.ValidationError({"user": {"username": ["Já h existe um utilizador com esse nome."]}})
                
                # Agora, cria o serializer para o usuário e tenta salvar
                user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
                if user_serializer.is_valid():
                    user_serializer.save()  # Atualiza o usuário
                else:
                    raise serializers.ValidationError(user_serializer.errors)

            # Salva os dados do Agente após atualizar o usuário
            serializer.save()
        except Exception as e:
            print(f"Erro ao atualizar o agente: {str(e)}")
            raise

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data=request.data
        agente=Agente.objects.get(pk=data['id'])
        username=data['user']['username']
        agente_username = agente.user.username
        
        if username!= agente_username and User.objects.filter(username=username).exclude(username=agente_username).exists():
            return Response({"error": "este username já existe"}, status=400)
        # Retira os dados do 'user' antes de passar para o serializer

        user_data = request.data.pop('user', None)

        # Atualiza os dados do 'user' separadamente, se necessário
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()  # Atualiza o usuário
            else:
                # Se houver erro ao salvar os dados do usuário, levanta uma exceção
                return Response(user_serializer.errors, status=400)
            
        agente.numero_telefone=data['numero_telefone']
        agente.empresa=Empresa.objects.get(pk=data['empresa'])
        agente.endereco=data['endereco']

        agente.save()

        serializer= OperadorAgenteCRUDSerializer(agente)
        return Response(serializer.data)
        


        

# ================================= Actividade dos agentes ============================
class OperadorAgenteRotasView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):

        try:
            data_atual = timezone.now() + timedelta(days=1)
            agente = Agente.objects.get(pk=pk)  # Obtém o agente
            # Filtra as viagens do agente específico
            rotas = Rotas.objects.filter(agente=agente).annotate(
                total_aprovados=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Aprovado')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                total_pendentes=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Pendente')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                total_cancelados=Count('agente_viagem_rota__bilhetes_viagem', filter=Q(agente_viagem_rota__bilhetes_viagem__status_bilhete='Cancelado')
                                    & Q(agente_viagem_rota__data_saida__gte=data_atual)),
                
            )
        
            serializer = AgenteRotasSerializer(rotas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class OperadorEstatisticasAgenteOntemView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        data_atual = timezone.now().date() - timedelta(days=1)
        data_ontem = data_atual - timedelta(days=1)
        agente=Agente.objects.get(pk=pk)

        # Estatísticas de bilhetes hoje
        total_bilhetes = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
        ).count()

        bilhetes_aprovados = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        receita_ontem = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_ontem,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Cálculo da porcentagem de variação
        def calcular_variacao_percentual(valor_atual, valor_anterior):
            if valor_anterior == 0:
                return 100 if valor_atual > 0 else 0
            return ((valor_atual - valor_anterior) / valor_anterior) * 100

        variacao_receita = calcular_variacao_percentual(receita_diaria, receita_ontem)

        # Resumo das informações para o agente
        estatisticas = {
            "total_bilhetes": total_bilhetes,
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "variacao_receita": f'{variacao_receita:.2f}',  # Variação percentual da receita
        }
        
        # Retorna as informações em formato JSON
        return Response(estatisticas)
    

class OperadorEstatisticasAgenteView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        data_atual = timezone.localdate()
        

        agente=Agente.objects.get(pk=pk)

        # Estatísticas de bilhetes hoje
        total_bilhetes = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
        ).count()

        bilhetes_aprovados = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual,
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        

        receita_ontem = Bilhete.objects.filter(
            viagem__agente=agente, 
            data_criado__exact=data_atual - timedelta(days=1),
            status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Cálculo da porcentagem de variação
        def calcular_variacao_percentual(valor_atual, valor_anterior):
            if valor_anterior == 0:
                return 100 if valor_atual > 0 else 0
            return ((valor_atual - valor_anterior) / valor_anterior) * 100

        variacao_receita = calcular_variacao_percentual(receita_diaria, receita_ontem)

        # Resumo das informações para o agente
        estatisticas = {
            "total_bilhetes": total_bilhetes,
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "variacao_receita": f'{variacao_receita:.2f}',  # Variação percentual da receita
        }
        
        # Retorna as informações em formato JSON
        return Response(estatisticas)
    
# semanal
class OperadorEstatisticasAgenteSemanalView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        agente=Agente.objects.get(pk=pk)
        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = timezone.localdate()
        if not ultimo_pedido_data:
            return Response({"error": "Nenhum pedido encontrado."}, status=404)

        # Calcula o início e o fim da semana
        inicio_da_semana = ultimo_pedido_data - timedelta(days=7)
        fim_da_semana = ultimo_pedido_data  
        

        # Estatísticas de bilhetes hoje
        total_bilhetes = Bilhete.objects.filter(
            viagem__agente=agente, data_criado__range=(inicio_da_semana, fim_da_semana),
        ).count()

        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__range=(inicio_da_semana, fim_da_semana), viagem__agente=agente, status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__range=(inicio_da_semana, fim_da_semana), viagem__agente=agente, status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__range=(inicio_da_semana, fim_da_semana), viagem__agente=agente, status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            viagem__agente=agente, data_criado__range=(inicio_da_semana, fim_da_semana), status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        

        receita_ontem = Bilhete.objects.filter(
            viagem__agente=agente, data_criado__range=(inicio_da_semana - timedelta(days=14), fim_da_semana- timedelta(days=7)), status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Cálculo da porcentagem de variação
        def calcular_variacao_percentual(valor_atual, valor_anterior):
            if valor_anterior == 0:
                return 100 if valor_atual > 0 else 0
            return ((valor_atual - valor_anterior) / valor_anterior) * 100

        variacao_receita = calcular_variacao_percentual(receita_diaria, receita_ontem)

        # Resumo das informações para o agente
        estatisticas = {
            "total_bilhetes": total_bilhetes,
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "variacao_receita": f'{variacao_receita:.2f}',  # Variação percentual da receita
        }
        
        # Retorna as informações em formato JSON
        return Response(estatisticas)

# mensal
class OperadorEstatisticasAgenteMensalView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        agente=Agente.objects.get(pk=pk)
        # Pega a última data de criação de um bilhete para a empresa
        ultimo_pedido_data = timezone.localdate()
        if not ultimo_pedido_data:
            return Response({"error": "Nenhum pedido encontrado."}, status=404)

        # Calcula o início e o fim da semana
        inicio_da_semana = ultimo_pedido_data - timedelta(days=30)
        fim_da_semana = ultimo_pedido_data  
        

        # Estatísticas de bilhetes hoje
        total_bilhetes = Bilhete.objects.filter(
            viagem__agente=agente, data_criado__range=(inicio_da_semana, fim_da_semana),
        ).count()

        bilhetes_aprovados = Bilhete.objects.filter(
            data_criado__range=(inicio_da_semana, fim_da_semana), viagem__agente=agente, status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            data_criado__range=(inicio_da_semana, fim_da_semana), viagem__agente=agente, status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            data_criado__range=(inicio_da_semana, fim_da_semana), viagem__agente=agente, status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            viagem__agente=agente, data_criado__range=(inicio_da_semana, fim_da_semana), status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        

        receita_ontem = Bilhete.objects.filter(
            viagem__agente=agente, data_criado__range=(inicio_da_semana - timedelta(days=30), fim_da_semana- timedelta(days=7)), status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Cálculo da porcentagem de variação
        def calcular_variacao_percentual(valor_atual, valor_anterior):
            if valor_anterior == 0:
                return 100 if valor_atual > 0 else 0
            return ((valor_atual - valor_anterior) / valor_anterior) * 100

        variacao_receita = calcular_variacao_percentual(receita_diaria, receita_ontem)

        # Resumo das informações para o agente
        estatisticas = {
            "total_bilhetes": total_bilhetes,
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "variacao_receita": f'{variacao_receita:.2f}',  # Variação percentual da receita
        }
        
        # Retorna as informações em formato JSON
        return Response(estatisticas)


class OperadorEstatisticaAgenteVendasSemanaisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,pk, format=None):
        data_atual = timezone.now() +timedelta(days=1)
        agente=Agente.objects.get(pk=pk)
        # Dados de vendas diárias para os últimos 7 dias
        vendas_semanais = []
        
        for i in range(7):
            dia = (data_atual - timedelta(days=i)).date()
            
            bilhete=Bilhete.objects.filter(Q(viagem__agente=agente) & Q(viagem__data_saida__exact=dia) & (Q(status_bilhete='Aprovado') | Q( status_bilhete='realizado')) )
            
            # if bilhete:
            receita_dia = bilhete.aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

            vendas_semanais.append({
                'dia': dia.strftime('%A'),
                'receita': float(receita_dia)  # Convertendo para float para JSON
            })

        # Inverte a lista para que os dias mais antigos apareçam primeiro
        vendas_semanais.reverse()

        # Resumo da receita semanal total
        # receita_total_semanal = sum([venda['receita'] for venda in vendas_semanais])
        

        return JsonResponse(vendas_semanais, safe=False, json_dumps_params={'ensure_ascii': False})
    
# inicio de agenda de viagens
class OperdaorAgenteProximaViagemView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        proxima_viagem=timedelta(days=1)+ timezone.now()
        # Filtra as viagens do agente específico
        agente=Agente.objects.get(pk=pk)
        viagens = Viagem.objects.filter(data_saida__exact=proxima_viagem, agente=agente).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})


class OperdaorAgenteProximaViagemOntemView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        proxima_viagem=timezone.now()
        print(proxima_viagem)

        # Filtra as viagens do agente específico
        agente=Agente.objects.get(pk=pk)
        viagens = Viagem.objects.filter(data_saida__exact=proxima_viagem, agente=agente).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})


class OperdaorAgenteProximaViagemAmanhaView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        proxima_viagem=timedelta(days=2)+ timezone.now()
        # Filtra as viagens do agente específico
        agente=Agente.objects.get(pk=pk)
        viagens = Viagem.objects.filter(data_saida__exact=proxima_viagem, agente=agente).annotate(
            total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
            total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
            total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
            total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
        )

        # Serializa os dados das viagens com a contagem de pedidos por status
        serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})
# Fim proximas agendas de viagens


# reserva por agente
class OperadorReservasBilhetesAgenteOntemView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:
            agente=Agente.objects.get(pk=pk)
            dataAtual = timezone.localdate() - timedelta(days=1)
            
            reservas = Bilhete.objects.filter(
                data_criado__exact=dataAtual, 
                viagem__agente=agente,
            ).order_by('-pk')
            serializer = OperadorReservasSerializer(reservas, many=True, context={"request": request})
            return Response(serializer.data)
        
        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class OperadorReservasBilhetesAgenteDiarioView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:
            agente=Agente.objects.get(pk=pk)
            dataAtual = timezone.localdate() 

            reservas = Bilhete.objects.filter(
                data_criado__exact=dataAtual,
                viagem__agente=agente,
            ).order_by('-pk')
            serializer = OperadorReservasSerializer(reservas, many=True, context={"request": request})
            
            print(serializer.data)
            return Response(serializer.data)
        
        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class OperadorReservasBilhetesAgenteSemanalView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:
            agente=Agente.objects.get(pk=pk)
            dataAtual = timezone.localdate()

            # Obter o último pedido da empresa
            ultimo_pedido_data = dataAtual

            # Cálculo do início e fim da semana
            inicio_da_semana = ultimo_pedido_data - timedelta(days=7)
            inicio_da_semana = timezone.make_aware(datetime.combine(inicio_da_semana, datetime.min.time()))  # Início do dia (00:00)
            fim_da_semana = ultimo_pedido_data
            fim_da_semana = timezone.make_aware(datetime.combine(fim_da_semana, datetime.max.time()))  # Fim do dia (23:59:59)

            # Filtra as reservas da última semana
            reservas = Bilhete.objects.filter(
                viagem__agente=agente,
                data_criado__range=(inicio_da_semana, fim_da_semana)  # Última semana
            ).order_by('-pk')

            # Serializa os dados
            serializer = OperadorReservasSerializer(reservas, many=True, context={"request": request})
            
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class OperadorReservasBilhetesAgenteMensalView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:
            agente=Agente.objects.get(pk=pk)
            dataAtual = timezone.localdate()

            # Obter o último pedido da empresa
            ultimo_pedido_data = dataAtual

            # Cálculo do início e fim do mês
            inicio_do_mes = ultimo_pedido_data - timedelta(days=30)
            inicio_do_mes = timezone.make_aware(datetime.combine(inicio_do_mes, datetime.min.time()))  # Início do dia (00:00)
            fim_do_mes = ultimo_pedido_data
            fim_do_mes = timezone.make_aware(datetime.combine(fim_do_mes, datetime.max.time()))  # Fim do dia (23:59:59)

            # Filtra as reservas do último mês
            reservas = Bilhete.objects.filter(
                viagem__agente=agente,
                status_bilhete__in=['Aprovado', 'Cancelado', 'Pendente'],
                data_criado__range=(inicio_do_mes, fim_do_mes)  # Últimos 30 dias
            ).order_by('-pk')

            # Serializa os dados
            serializer = OperadorReservasSerializer(reservas, many=True, context={"request": request})
         
            
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)

# Fim de reservas por agente


# Reservas das proximas viagens
class AgenteViagemReservaBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, pk, format=None):
        data_proxima=timedelta(days=1)+timezone.now()

        try:

            bilhetes = Bilhete.objects.filter(viagem__agente=request.user.agente, viagem__pk=pk, viagem__data_saida__exact=data_proxima)
            serializer = ReservasBilheteSerializer(bilhetes, many=True, context={'request': request})
            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


# todas reservas de bilhetes
class AgenteRelatoriosBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request, format=None):
        try:
            proxima_viagem=timedelta(days=2)+ timezone.now()

            viagens = Bilhete.objects.filter(viagem__agente=request.user.agente, viagem_data_saida__lte=proxima_viagem).values('viagem')
            serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)
        

# Proximas reservas
class OperadorAgenteProximasReservasBilhetesView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:

            proxima_viagem=timedelta(days=2)+ timezone.now()
            agente=Agente.objects.get(pk=pk)
            bilhetes = Bilhete.objects.filter(viagem__agente=agente, viagem__data_saida__gte=proxima_viagem)
            viagens=[
                Viagem.objects.filter(pk=bilhete.viagem.pk).annotate(
                    total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
                    total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
                    total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
                    total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
                ) 
                     
                    for bilhete in bilhetes ]
            
            
            serializers = list(AgenteViagemBilheteStatusSerializer(viagem, many=True).data[0] for viagem in viagens)
            
            return JsonResponse(serializers,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            print(e)
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


# Estatisticas das proximas viagens marcadas
class OperadorEstatisticasAgenteReservasView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        data_atual = timezone.now() + timedelta(days=2)
        data_ontem = data_atual + timedelta(days=1)
        agente=Agente.objects.get(pk=pk)

        # Estatísticas de bilhetes hoje
        total_bilhetes = Bilhete.objects.filter(
            viagem__agente=agente, viagem__data_saida__gte=data_atual
        ).count()

        bilhetes_aprovados = Bilhete.objects.filter(
            viagem__data_saida__gte=data_atual, viagem__agente=agente, status_bilhete='Aprovado'
        ).count()

        bilhetes_pendentes = Bilhete.objects.filter(
            viagem__data_saida__gte=data_atual, viagem__agente=agente, status_bilhete='Pendente'
        ).count()

        bilhetes_cancelados = Bilhete.objects.filter(
            viagem__data_saida__gte=data_atual, viagem__agente=agente, status_bilhete='Cancelado'
        ).count()

        # Receita diária de hoje
        receita_diaria = Bilhete.objects.filter(
            viagem__agente=agente, viagem__data_saida__gte=data_atual, status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Comparações com o dia anterior (ontem)
        total_bilhetes_ontem = Bilhete.objects.filter(
            viagem__agente=agente, viagem__data_saida__gte=data_ontem
        ).count()

        receita_ontem = Bilhete.objects.filter(
            viagem__agente=agente, viagem__data_saida__gte=data_ontem, status_bilhete='Aprovado'
        ).aggregate(receita=Sum('preco'))['receita'] or Decimal('0.00')

        # Cálculo da porcentagem de variação
        def calcular_variacao_percentual(valor_atual, valor_anterior):
            if valor_anterior == 0:
                return 100 if valor_atual > 0 else 0
            return ((valor_atual - valor_anterior) / valor_anterior) * 100

        variacao_receita = calcular_variacao_percentual(receita_diaria, receita_ontem)

        # Resumo das informações para o agente
        estatisticas = {
            "total_bilhetes": total_bilhetes,
            "bilhetes_aprovados": bilhetes_aprovados,
            "bilhetes_pendentes": bilhetes_pendentes,
            "bilhetes_cancelados": bilhetes_cancelados,
            "receita_diaria": f'{receita_diaria:.2f}',
            "variacao_receita": f'{variacao_receita:.2f}',  # Variação percentual da receita
        }

        # Retorna as informações em formato JSON
        return Response(estatisticas)


class OperadorAgenteCheckinViagensView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:
            proxima_viagem= timezone.now()
            agente=Agente.objects.get(pk=pk)
            viagens=Viagem.objects.filter(agente=agente,data_saida__exact=proxima_viagem).order_by('-data_saida').annotate(
                total_realizados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='realizado')),
                total_aprovados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Aprovado')),
                total_pendentes=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Pendente')),
                total_cancelados=Count('bilhetes_viagem', filter=Q(bilhetes_viagem__status_bilhete='Cancelado'))
            ) 
            
            
            serializer = AgenteViagemBilheteStatusSerializer(viagens, many=True)
            
            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            print(e)
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)


class OperadorAgenteCheckinListPassageiroView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):
        try:
            data_actual= timezone.now()
            agente=Agente.objects.get(pk=pk)
            bilhetes = Bilhete.objects.filter(viagem__agente=agente,viagem__data_saida__exact=data_actual,status_bilhete='Aprovado') 
            
            serializer = BilheteSerializer(bilhetes, many=True, context={'request': request})

            return JsonResponse(serializer.data,safe=False, json_dumps_params={'ensure_ascii': False})
        
        except Exception as e:
            print(e)
            return Response({"error":f'{e}'}, status=status.HTTP_401_UNAUTHORIZED)
        



# -----------------------------------------------------------------------

# actualizar agente
class OperadorAgenteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Agente.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'  # Assume que o identificador é o campo 'pk'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"message": "Ponto intermedio atualizada com sucesso.", }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Rota excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# Obtem estatisticas de numero de rotas responsavel
class OperadorAgenteRotasView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Garante que o cliente esteja logado

    def get(self, request,pk, format=None):

        try:
            data_atual = timezone.now() + timedelta(days=1)
            agente=Agente.objects.get(pk=pk)
            rota= agente.rota_agente.all()
            # Filtra as viagens do agente específico
            rotas = rota.annotate(
                total_aprovados=Count('empresa__bilhetes_empresa', filter=Q(empresa__bilhetes_empresa__status_bilhete='Aprovado')
                                    & Q(empresa__bilhetes_empresa__viagem__data_saida__gte=data_atual)),
                total_pendentes=Count('empresa__bilhetes_empresa', filter=Q(empresa__bilhetes_empresa__status_bilhete='Pendente')
                                    & Q(empresa__bilhetes_empresa__viagem__data_saida__gte=data_atual)),
                total_cancelados=Count('empresa__bilhetes_empresa', filter=Q(empresa__bilhetes_empresa__status_bilhete='Cancelado')
                                    & Q(empresa__bilhetes_empresa__viagem__data_saida__gte=data_atual)),
                
            )
        
            serializer = AgenteRotasSerializer(rotas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Cria pontos de venda
class OperadorPontosVendaCreateView(generics.CreateAPIView):
    queryset = PontoVenda.objects.all()
    serializer_class = OperadorPontoVendaSerializer

    def create(self, request, *args, **kwargs):
        # Serializa os dados
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            print(serializer)
            # Cria o ponto de venda
            pontovenda = serializer.save()
            
            return Response({"message": "Ponto de venda adicionado com sucesso."}, status=201)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


# Update de ponto de venda
class OperadorPontosVendaUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PontoVenda.objects.all()
    serializer_class = OperadorPontoVendaSerializer
    lookup_field = 'pk'  # Utilize o campo de identificação do ponto de venda (ex.: 'id' ou 'pk')

    def update(self, request, *args, **kwargs):
        try:
            # Obtém o objeto a ser atualizado
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Atualiza o ponto de venda
            self.perform_update(serializer)
            return Response({"message": "Ponto de venda atualizado com sucesso."}, status=status.HTTP_200_OK)
        
        except NotFound:
            return Response({"message": "Ponto de venda não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response({"message": "Erro ao atualizar o ponto de venda."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            # Obtém o objeto a ser deletado
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Ponto de venda excluído com sucesso."}, status=status.HTTP_204_NO_CONTENT)
        
        except NotFound:
            return Response({"message": "Ponto de venda não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response({"message": "Erro ao excluir o ponto de venda."}, status=status.HTTP_400_BAD_REQUEST)


# busca um unico ponto de venda
class OperadorPontoVendaView(APIView):
    
    def get(self, request, pk,):
        # Serializa os dados
        try:
            pontovenda=PontoVenda.objects.get(pk=pk, empresa=request.user.operador.operador_empresa)
            serializers=OperadorPontoVendaSerializer(pontovenda, )
            return Response(serializers.data, status=200)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


# List Ponto de vendas
class OperadorPontosVendaListView(APIView):
    
    def get(self, request, *args, **kwargs):
        # Serializa os dados
        try:
            pontovenda=request.user.operador.operador_empresa.empresa_pontovenda
            serializers=OperadorPontoVendaSerializer(pontovenda, many=True)
            return Response(serializers.data, status=200)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


# Cria uma rota
class OperadorRotaCreateView(generics.CreateAPIView):
    queryset = Rotas.objects.all()
    serializer_class = OperadorRotaSerializer

    def create(self, request, *args, **kwargs):
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"message": "Rota criada com sucesso.", }, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            return Response({"message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


# lista rotas
class OperadorRotasListView(APIView):
    
    def get(self, request):
        # Serializa os dados
        try:
            rotas=request.user.operador.operador_empresa.empresa_rota.all()
            serializers=OperadorRotaSerializer(rotas, many=True)
            return Response(serializers.data, status=200)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


# Actualiza rota
class OperadorRotaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rotas.objects.all()
    serializer_class = OperadorRotaSerializer
    lookup_field = 'pk'  # Assume que o identificador é o campo 'pk'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"message": "Rota atualizada com sucesso.", }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Rota excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# busca uma unica rota
class OperadorRotaView(APIView):
    
    def get(self, request, pk,):
        # Serializa os dados
        try:
            pontovenda=Rotas.objects.get(pk=pk, empresa=request.user.operador.operador_empresa)
            serializers=OperadorRotaSerializer(pontovenda, )
            return Response(serializers.data, status=200)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


# Cria um ponto intermedio
class OperadorPontoIntermedioCreateView(generics.CreateAPIView):
    queryset = PontoIntermediario.objects.all()
    serializer_class = OperadorPontoIntermediarioSerializer

    def create(self, request, *args, **kwargs):
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"message": "Ponto intermedio criado com sucesso.", }, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            return Response({"message":f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


# lista pontos intermediarios
class OperadorPontoIntermediarioListView(APIView):
    
    def get(self, request, pk):
        # Serializa os dados
        try:
            rota=Rotas.objects.get(pk=pk)
            pontos=rota.rota_ponto_intermedio.all()
            serializers=OperadorPontoIntermediarioSerializer(pontos, many=True)
            
            return Response(serializers.data, status=200)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Actualiza ponto intermedio
class OperadorPontoIntermedioRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PontoIntermediario.objects.all()
    serializer_class = OperadorPontoIntermediarioSerializer
    lookup_field = 'pk'  # Assume que o identificador é o campo 'pk'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"message": "Ponto intermedio atualizada com sucesso.", }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Rota excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# ========================== Update Agente ============================
class UpdateUserAgenteView(APIView):
    
    def put(self, request):
        # Serializa os dados
        try:
            data = request.data
            user=request.user
            user.username=data.get('username')
            user.first_name=data.get('first_name')
            user.last_name=data.get('last_name')
            user.save()
            user.agente.numero_telefone=data.get('numero_telefone')
            user.agente.endereco=data.get('endereco')
            user.agente.save()
            
            return Response({"message":"Actualizado com sucesso"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserOperadorView(APIView):
    
    def put(self, request):
        # Serializa os dados
        try:
            data = request.data
            user=request.user
            user.username=data.get('username')
            user.first_name=data.get('first_name')
            user.last_name=data.get('last_name')
            user.save()
            user.operador.numero_telefone=data.get('numero_telefone')
            user.operador.endereco=data.get('endereco')
            user.operador.save()
            
            return Response({"message":"Actualizado com sucesso"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response ({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)