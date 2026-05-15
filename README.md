# Recycle ♻️

## 🛠️ Tecnologias Utilizadas
* **Backend:** Python + Django
* **Frontend:** Tailwind CSS, HTML/Templates do Django
* **Mapas:** Leaflet.js (Mapas interativos e geolocalização)
* **Banco de Dados:** SQLite (padrão do Django para desenvolvimento) ->> Depois vamos mudar para PostgreSQL

---

### 1. Criando e ativando o Ambiente Virtual (venv)
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

### 2. Instalando as dependências do Django
Com o ambiente ativado, instale todas as bibliotecas necessárias listadas no projeto:
```bash
pip install -r requirements.txt
```

### 3. Configurando o Banco de Dados
Prepare o banco de dados e crie as tabelas necessárias rodando as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Rodando o Servidor
Agora é só dar o play no servidor local do Django:
```bash
python manage.py runserver
```
