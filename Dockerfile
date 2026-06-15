# Usando a imagem oficial e estável do Python
FROM python:3.12-slim

# Evita que o Python grave arquivos .pyc e bufe a saída do console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório interno do container
WORKDIR /app

# Instala dependências do sistema para o Pillow rodar no Linux compilando imagens
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências do projeto
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código-fonte do projeto
COPY . /app/

# Garante a criação das pastas de uploads e arquivos estáticos
RUN mkdir -p /app/media /app/static

# Expõe a porta do servidor Django
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]