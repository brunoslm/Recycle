from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages  
from django.db import IntegrityError 
from decimal import Decimal, InvalidOperation
import uuid

from .models import Obra, Acordo, Perfil, Avaliacao
from .forms import ObraForm, CadastroForm, FormaPagamentoForm, AvaliacaoForm

def index(request):
    obras = Obra.objects.filter(status='ATIVO')
    return render(request, 'core/index.html', {'obras': obras})

@login_required(login_url='login')
def cadastrar_obra(request):
    if request.method == 'POST':
        form = ObraForm(request.POST, request.FILES)
        if form.is_valid():
            obra = form.save(commit=False)
            obra.gerador = request.user
            obra.save()
            return redirect('painel')
    else:
        form = ObraForm()
    return render(request, 'core/cadastrar_obra.html', {'form': form})

@login_required(login_url='login')
def painel(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.tipo == 'CENTRO':
        acordos = Acordo.objects.filter(centro=request.user).order_by('-id')
        return render(request, 'core/painel_centro.html', {'acordos': acordos})
    
    obras = Obra.objects.filter(gerador=request.user).order_by('-id')
    return render(request, 'core/painel.html', {'obras': obras})

@login_required(login_url='login')
def detalhe_obra(request, id):
    obra = get_object_or_404(Obra, id=id)
    propostas = Acordo.objects.filter(obra=obra)
    return render(request, 'core/detalhe_obra.html', {'obra': obra, 'propostas': propostas})

@login_required(login_url='login')
def propor_acordo(request, id):
    obra = get_object_or_404(Obra, id=id)
    if request.user == obra.gerador:
        return redirect('detalhe_obra', id=obra.id)

    if request.method == 'POST':
        valor_raw = request.POST.get('valor_transporte')
        
        try:
            valor_limpo = valor_raw.replace(',', '.')
            valor_decimal = Decimal(valor_limpo)
            
            # Bloqueia propostas menores ou iguais a zero
            if valor_decimal <= Decimal('0.00'):
                messages.error(request, "Ei! O valor da proposta deve ser maior que zero.")
                return render(request, 'core/propor_acordo.html', {'obra': obra})
            
            if valor_decimal > Decimal('9999999.99'):
                messages.error(request, "Valor muito alto! Por favor, insira um valor realista de até R$ 9.999.999,99.")
                return render(request, 'core/propor_acordo.html', {'obra': obra})
                
        except (InvalidOperation, ValueError, TypeError):
            messages.error(request, "Por favor, insira um valor numérico válido.")
            return render(request, 'core/propor_acordo.html', {'obra': obra})

        try:
            Acordo.objects.create(
                obra=obra,
                centro=request.user,
                valor_transporte=valor_decimal,
                status='PROPOSTA'
            )
            obra.status = 'EM_NEGOCIACAO'
            obra.save()
            messages.success(request, "Proposta enviada com sucesso!")
            return redirect('detalhe_obra', id=obra.id)
            
        except IntegrityError:
            messages.error(request, "Erro de integridade: O banco recusou esse valor.")
            return render(request, 'core/propor_acordo.html', {'obra': obra})
        
    return render(request, 'core/propor_acordo.html', {'obra': obra})

@login_required(login_url='login')
def responder_proposta(request, id, acao):
    acordo = get_object_or_404(Acordo, id=id)
    if request.user != acordo.obra.gerador:
        return redirect('painel')

    if acao == 'aceitar':
        acordo.status = 'ACEITO'
        acordo.save()
        return redirect('painel')
    elif acao == 'recusar':
        acordo.status = 'RECUSADO'
        acordo.save()
        
        if not Acordo.objects.filter(obra=acordo.obra, status='PROPOSTA').exists():
            acordo.obra.status = 'ATIVO'
            acordo.obra.save()
            
    return redirect('detalhe_obra', id=acordo.obra.id)

@login_required(login_url='login')
def escolher_pagamento(request, id):
    acordo = get_object_or_404(Acordo, id=id)
    
    if request.user != acordo.centro:
        return redirect('painel')

    if request.method == 'POST':
        form = FormaPagamentoForm(request.POST, instance=acordo)
        if form.is_valid():
            acordo = form.save(commit=False)
            if acordo.forma_pagamento == 'ONLINE':
                acordo.status = 'AGUARDANDO_VALIDACAO'
                acordo.save()
                return redirect('simular_pagamento_online', id=acordo.id)
            else:
                acordo.status = 'TRANSPORTE_LIBERADO'
                acordo.save()
                return redirect('painel')
    else:
        form = FormaPagamentoForm(instance=acordo)
        
    return render(request, 'core/escolher_pagamento.html', {'form': form, 'acordo': acordo})

@login_required(login_url='login')
def simular_pagamento_online(request, id):
    acordo = get_object_or_404(Acordo, id=id, status='AGUARDANDO_VALIDACAO')
    
    if request.user != acordo.centro:
        return redirect('painel')

    if request.method == 'POST':
        acordo.pago = True
        acordo.status = 'TRANSPORTE_LIBERADO'
        acordo.save()
        return redirect('painel')
        
    return render(request, 'core/validar_pagamento.html', {'acordo': acordo})

@login_required(login_url='login')
def enviar_material(request, id):
    acordo = get_object_or_404(Acordo, id=id, status='TRANSPORTE_LIBERADO')
    if request.user == acordo.obra.gerador:
        acordo.status = 'EM_TRANSPORTE'
        acordo.save()
        
        acordo.obra.status = 'EM_TRANSPORTE'
        acordo.obra.save()
        
    return redirect('painel')

@login_required(login_url='login')
def recolher_material(request, id):
    acordo = get_object_or_404(Acordo, id=id, status='EM_TRANSPORTE')
    if request.user == acordo.centro:
        acordo.status = 'CONCLUIDO'
        if acordo.forma_pagamento == 'ENTREGA':
            acordo.pago = True
            
        acordo.comprovante_token = str(uuid.uuid4())[:8].upper()
        acordo.save()
        
        acordo.obra.status = 'CONCLUIDO'
        acordo.obra.save()
        
    return redirect('painel')

@login_required(login_url='login')
def comprovante(request, token):
    acordo = get_object_or_404(Acordo, comprovante_token=token, status='CONCLUIDO')
    return render(request, 'core/comprovante.html', {'acordo': acordo})

@login_required(login_url='login')
def avaliar_acordo(request, id):
    acordo = get_object_or_404(Acordo, id=id, status='CONCLUIDO')
    
    if request.user != acordo.centro:
        return redirect('painel')
        
    avaliado = acordo.obra.gerador
    
    if Avaliacao.objects.filter(acordo=acordo, avaliador=request.user).exists():
        return redirect('comprovante', token=acordo.comprovante_token)
        
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.acordo = acordo
            avaliacao.avaliador = request.user
            avaliacao.avaliado = avaliado
            avaliacao.save()
            return redirect('comprovante', token=acordo.comprovante_token)
    else:
        form = AvaliacaoForm()
        
    return render(request, 'core/avaliar.html', {'form': form, 'acordo': acordo, 'avaliado': avaliado})

def cadastrar_usuario(request):
    if request.user.is_authenticated:
        return redirect('painel')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            tipo_escolhido = form.cleaned_data.get('tipo_usuario')
            Perfil.objects.create(user=user, tipo=tipo_escolhido)
            login(request, user)
            return redirect('painel')
    else:
        form = CadastroForm()
        
    return render(request, 'core/cadastrar_usuario.html', {'form': form})

def lista_obras(request):
    query = request.GET.get('q', '')
    obras = Obra.objects.filter(status='ATIVO')

    if query:
        palavras_buscadas = query.split()
        filtro_geral = Q()
        
        for palavra in palavras_buscadas:
            filtro_palavra = (
                Q(descricao__icontains=palavra) |
                Q(tipo_residuo__icontains=palavra) |
                Q(endereco__icontains=palavra) |
                Q(bairro__icontains=palavra) |
                Q(cidade__icontains=palavra) |
                Q(estado__icontains=palavra)
            )
            if not filtro_geral:
                filtro_geral = filtro_palavra
            else:
                filtro_geral &= filtro_palavra
                
        obras = obras.filter(filtro_geral).distinct()

    return render(request, 'core/obras.html', {'obras': obras, 'query': query})

def perfil_vendedor(request, id):
    vendedor = get_object_or_404(User, id=id)
    avaliacoes = Avaliacao.objects.filter(avaliado=vendedor).order_by('-data_criacao')
    return render(request, 'core/perfil_vendedor.html', {'vendedor': vendedor, 'avaliacoes': avaliacoes})