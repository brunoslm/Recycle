# 1. ESTÁGIO BASE (Comum para ambos)

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instala dependências do sistema necessárias para o Pillow e compilações C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 2. ESTÁGIO DE DESENVOLVIMENTO (dev)

FROM base AS development
# No dev, o código será linkado via volume, então só precisamos expor a porta
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# 3. ESTÁGIO DE PRODUÇÃO (prod)

FROM base AS production

# Copia o código-fonte (em produção o código FICA dentro da imagem)
COPY . /app/

# Cria as pastas necessárias e um usuário de sistema não-root por segurança
RUN mkdir -p /app/media /app/static && \
    useradd -u 8888 djangouser && \
    chown -R djangouser:djangouser /app

# Muda para o usuário seguro
USER djangouser

EXPOSE 8000

# Em produção, o ideal é usar um servidor WSGI como o Gunicorn, 
# mas mantive o collectstatic + migrate inicial para o seu fluxo.
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn setup.wsgi:application --bind 0.0.0.0:8000"]