from locust import HttpUser, task, between

class AuthenticatedUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        response = self.client.post("api/login/", json={
            "phone_number": "873686545",
            "password": "Gildo8503@"
        })
        self.token = response.json().get("access")

    @task
    def listar_pedidos(self):
        
        self.client.get(
            "api/viagem/obter_bilhetes/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
