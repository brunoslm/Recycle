from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('GERADOR', 'Gerador'), ('CENTRO', 'Centro Reciclagem')])

    def __str__(self):
        return f"{self.user.username} - {self.tipo}"

class Obra(models.Model):
    STATUS_OBRA = [
        ('ATIVO', 'Disponível para Propostas'),
        ('EM_NEGOCIACAO', 'Em Negociação'),
        ('EM_TRANSPORTE', 'Material em Transporte'),
        ('CONCLUIDO', 'Finalizada'),
    ]

    gerador = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.TextField()
    tipo_residuo = models.CharField(max_length=100)
    
    # Endereço detalhado
    endereco = models.CharField(max_length=255, default='') 
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True) 
    
    # Coordenadas do Mapa
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_OBRA, default='ATIVO')
    
    def __str__(self):
        return self.descricao

class Acordo(models.Model):
    STATUS_ACORDO = [
        ('PROPOSTA', 'Proposta Enviada'),
        ('RECUSADO', 'Não Aceito pelo Gerador'),
        ('ACEITO', 'Aceito (Aguardando Definição de Pagamento)'),
        ('AGUARDANDO_VALIDACAO', 'Aguardando Validação do Pagamento Online'),
        ('TRANSPORTE_LIBERADO', 'Transporte Liberado (Aguardando Envio)'),
        ('EM_TRANSPORTE', 'Material em Transporte'),
        ('CONCLUIDO', 'Material Recolhido / Processo Concluído'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('ONLINE', 'Pagamento Online (PIX, Cartão, Transferência)'),
        ('ENTREGA', 'Efetuar pagamento na entrega'),
    ]

    obra = models.ForeignKey(Obra, on_delete=models.CASCADE)
    centro = models.ForeignKey(User, on_delete=models.CASCADE)
    valor_transporte = models.DecimalField(max_digits=10, decimal_places=2)
    
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True)
    pago = models.BooleanField(default=False)
    status = models.CharField(max_length=25, choices=STATUS_ACORDO, default='PROPOSTA')
    
    # Gerado apenas no final do fluxo, conforme o diagrama
    comprovante_token = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return f"Acordo #{self.id} - Obra: {self.obra.descricao}"
