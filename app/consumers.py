from channels.generic.websocket import WebsocketConsumer
import json

class YourConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({'message': 'Você está conectado!'}))

    def receive(self, text_data):
        data = json.loads(text_data)
        # lógica para tratar a mensagem recebida
        self.send(text_data=json.dumps({'response': f'Atualização recebida!{text_data}'}))

    def disconnect(self, close_code):
        pass
