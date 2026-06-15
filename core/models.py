from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Q                        

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('GERADOR', 'Gerador'), ('CENTRO', 'Centro Reciclagem')])

    @property
    def total_transacoes(self):
        if self.tipo == 'CENTRO':
            return Acordo.objects.filter(centro=self.user, status='CONCLUIDO').count()
        return Acordo.objects.filter(obra__gerador=self.user, status='CONCLUIDO').count()

    @property
    def media_avaliacao(self):
        from django.db.models import Avg
        media = Avaliacao.objects.filter(avaliado=self.user).aggregate(models.Avg('nota'))['nota__avg']
        return round(media, 1) if media else 0.0

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
<<<<<<< HEAD
    
=======
    imagem = models.ImageField(upload_to='obras/', blank=True, null=True)
>>>>>>> da5e4e1f72e0220c94d4855c85c088227388352c
    endereco = models.CharField(max_length=255, default='') 
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True) 
<<<<<<< HEAD
    
=======
>>>>>>> da5e4e1f72e0220c94d4855c85c088227388352c
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
<<<<<<< HEAD
    
    valor_transporte = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True)
    pago = models.BooleanField(default=False)
    status = models.CharField(max_length=25, choices=STATUS_ACORDO, default='PROPOSTA')
    
=======
    valor_transporte = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True)
    pago = models.BooleanField(default=False)
    status = models.CharField(max_length=25, choices=STATUS_ACORDO, default='PROPOSTA')
>>>>>>> da5e4e1f72e0220c94d4855c85c088227388352c
    comprovante_token = models.CharField(max_length=100, unique=True, blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(valor_transporte__gt=0), 
                name='valor_transporte_positivo'
            )
        ]

    def __str__(self):
<<<<<<< HEAD
        return f"Acordo #{self.id} - Obra: {self.obra.descricao}"
=======
        return f"Acordo #{self.id} - Obra: {self.obra.descricao}"

class Avaliacao(models.Model):
    acordo = models.ForeignKey(Acordo, on_delete=models.CASCADE)
    avaliador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    avaliado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_recebidas')
    nota = models.IntegerField(choices=[(1, '1 Estrela'), (2, '2 Estrelas'), (3, '3 Estrelas'), (4, '4 Estrelas'), (5, '5 Estrelas')])
    titulo = models.CharField(max_length=150, blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.avaliador.username} para {self.avaliado.username} - Nota: {self.nota}"
>>>>>>> da5e4e1f72e0220c94d4855c85c088227388352c
