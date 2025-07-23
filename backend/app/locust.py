from locust import HttpUser, task, between

base_url = '/api/v1'


class ContratoUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # Autentica e salva o token para usar nas requisições
        response = self.client.post(
            f"{base_url}/login/access-token",
            data={"username": "alef@gmail.com", "password": "string"},
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            self.token = None

    @task
    def listar_contratos(self):
        if self.token:
            self.client.get(f"{base_url}/contratos", headers={"Authorization": f"Bearer {self.token}"})

    @task
    def listar_professores(self):
        if self.token:
            self.client.get(f"{base_url}/perfis/professores", headers={"Authorization": f"Bearer {self.token}"})

    @task
    def listar_alunos(self):
        if self.token:
            self.client.get(f"{base_url}/alunos", headers={"Authorization": f"Bearer {self.token}"})
    @task
    def listar_relatorio(self):
        if self.token:
            self.client.get(f"{base_url}/relatorios/aulas", headers={"Authorization": f"Bearer {self.token}"})
