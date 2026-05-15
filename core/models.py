from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('GERADOR', 'Gerador'), ('CENTRO', 'Centro Reciclagem')])

class Obra(models.Model):
    gerador = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.TextField()
    tipo_residuo = models.CharField(max_length=100)
    
    # Endereço detalhado
    endereco = models.CharField(max_length=255, default='') # Vai guardar apenas a Rua e o Número
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True) # Apenas a sigla (Ex: PE, SP, RJ)
    
    # Coordenadas do Mapa
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    status = models.CharField(max_length=20, default='ATIVO')
    
    def __str__(self):
        return self.descricao

class Acordo(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE)
    centro = models.ForeignKey(User, on_delete=models.CASCADE)
    valor_transporte = models.DecimalField(max_digits=10, decimal_places=2)
    pago = models.BooleanField(default=False)
    entregue = models.BooleanField(default=False)
    comprovante_token = models.CharField(max_length=100, unique=True)