# Usando a imagem oficial e estável do Python
FROM python:3.12-slim

# Evita que o Python grave arquivos .pyc e bufe a saída do console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório interno do container
WORKDIR /app

# OTIMIZAÇÃO 1: Consolidação de comandos e criação de pastas antecipada
# Criamos as pastas antes para que o Docker gerencie as permissões corretamente.
RUN mkdir -p /app/media /app/static && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências do projeto (Aproveita o cache das camadas do Docker)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# OTIMIZAÇÃO 2: Copiar o código-fonte por último
# Como o código muda o tempo todo, esta deve ser a última camada. 
# Assim, se você mudar uma linha no HTML, o Docker NÃO vai reinstalar os pacotes do pip.
COPY . /app/

# Expõe a porta do servidor Django
EXPOSE 8000

# OTIMIZAÇÃO 3: Usar formato de lista JSON para o CMD
# É a recomendação oficial do Docker para evitar overhead de abrir um shell desnecessário.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]