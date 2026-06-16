from decimal import Decimal
from django.contrib.auth.models import User
from core.models import Perfil, Obra, Acordo

# Funções auxiliares reutilizadas nos testes unitários e de integração

def criar_usuario(username, tipo):
    user = User.objects.create_user(username=username, password='senha123')
    Perfil.objects.create(user=user, tipo=tipo)
    return user


def criar_obra(gerador, descricao='Obra teste', tipo_residuo='Concreto', status='ATIVO'):
    return Obra.objects.create(
        gerador=gerador, descricao=descricao,
        tipo_residuo=tipo_residuo, endereco='Rua A, 1', status=status
    )


def criar_acordo(obra, centro, valor='100.00', status='PROPOSTA', forma_pagamento=None):
    return Acordo.objects.create(
        obra=obra, centro=centro,
        valor_transporte=Decimal(valor),
        status=status,
        forma_pagamento=forma_pagamento
    )