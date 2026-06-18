# Recycle ♻️
O Recycle trata-se de uma plataforma de logística reversa de RCC (Resíduos de Construção Civil) desenvolvida em framework Django, que é escrito em Python sob arquitetura MTV (Model-Template-View).
As instruções abaixo irão dar uma cópia do projeto em execução na máquina local para fins de teste e desenvolvimento.

## 🛠️ Tecnologias Utilizadas
* **Backend:** Python + Django
* **Frontend:** Tailwind CSS, HTML/Templates do Django
* **Mapas e Geolocalização:**
  * **Leaflet.js:** Biblioteca interativa usada para renderizar o mapa na tela e manipular os pinos.
  * **ViaCEP:** API utilizada para autocompletar os campos de endereço (Rua, Bairro, Cidade, Estado) a partir do CEP digitado.
  * **Nominatim (OpenStreetMap):** A inteligência que transforma o texto do endereço em coordenadas geográficas (Latitude e Longitude).
* **Banco de Dados:** SQLite (padrão do Django para desenvolvimento) ->> Depois vamos mudar para PostgreSQL

---

## 💻 Como Rodar com Máquina Local

### 1. Clone o Repositório
Para clonar o repositório, utilize o comando:
```bash
git clone https://github.com/brunoslm/Recycle.git
```

### 2. Crie e Ative o Ambiente Virtual (venv)
O ambiente virtual (`venv`) serve para isolar as bibliotecas do projeto e não bagunçar o seu computador.

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**No Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```
*(Se der certo, você verá um `(venv)` no início da linha do seu terminal).*

### 3. Acesse o Diretório
Entre na pasta do projeto com o comando:
```bash
cd Recycle
```

### 4. Instale as Dependências do Django
Com o ambiente ativado, instale todas as bibliotecas necessárias listadas no projeto:
```bash
pip install -r requirements.txt
```

### 5. Configure o Banco de Dados
Prepare o banco de dados e crie as tabelas necessárias rodando as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Rode o Servidor
Agora basta dar o play no servidor local do Django:
```bash
python manage.py runserver
```

---

## 🐳 Como Rodar com Docker (Ambiente de Desenvolvimento)

### 1. Pré-Requisitos
Antes de começar, certifique-se de ter instalado em sua máquina:
- Docker
- Docker Compose

### 2. Inicie o Conteiner
Após entrar na pasta do projeto, execute um dos comandos abaixo para realizar o build e iniciar a aplicação:

**No Windows:**
```bash
docker compose up --build
```

**No Linux/Mac:**
```bash
sudo docker compose up --build
```

### 3. Acesse a Aplicação
Abra o seu navegador e acesse: [http://localhost:3000](http://localhost:8000) (substitua pela porta da sua aplicação).

### 4. Como Parar a Aplicação
Para interromper a execução dos containers sem perder seus dados, utilize:

**No Windows:**
```bash
docker compose stop
```

**No Linux/Mac:**
```bash
sudo docker compose stop
```

Para remover completamente os containers e volumes criados, utilize:

**No Windows:**
```bash
docker compose down
```

**No Linux/Mac:**
```bash
sudo docker compose down
```

---

## 🐳 Como Rodar com Docker (Ambiente de Produção)
Para implantar a aplicação em ambiente de produção com otimizações ativadas, persistência dos dados e contêineres rodando em segundo plano, execute o comando abaixo na raiz do projeto:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📝 Testes Automatizados

O projeto conta com testes automatizados para garantir a estabilidade das rotas e regras de negócio.
A cobertura de código feita pelos testes pode ser verificada seguindo os passos abaixo:

### 1. Prepare o Banco de Testes
Antes de rodar os testes pela primeira vez (ou após criar novos modelos), certifique-se de que o banco de dados está atualizado:
```bash
python manage.py migrate
```

### 2. Execute os Testes (por Python)
Para rodar a suíte de testes padrão do Django no app principal:
```bash
python manage.py test core
```

### 3. Como Verificar a Cobertura de Código (por Coverage)
Para medir a porcentagem do código que está sendo testada, foi utilizada a biblioteca **coverage**.
Se ainda não tiver instalado, instale via terminal:
```bash
pip install coverage
```

Execute os testes através do coverage para coletar os dados de análise:
```bash
coverage run manage.py test core
```

Para exibir o relatório de cobertura detalhado direto no terminal, rode:
```bash
coverage report
```
