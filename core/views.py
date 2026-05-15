from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from .models import Obra, Acordo, Perfil
from .forms import ObraForm, CadastroForm
import uuid # Para gerar um token único para o comprovante

def index(request):
    obras = Obra.objects.filter(status='ATIVO')
    return render(request, 'core/index.html', {'obras': obras})

@login_required(login_url='login')
def cadastrar_obra(request):
    if request.method == 'POST':
        form = ObraForm(request.POST)
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
    # Verifica se o usuário tem um perfil e se é um Centro
    if hasattr(request.user, 'perfil') and request.user.perfil.tipo == 'CENTRO':
        # Busca todas as propostas que este centro enviou
        acordos = Acordo.objects.filter(centro=request.user).order_by('-id')
        return render(request, 'core/painel_centro.html', {'acordos': acordos})
    
    # Caso contrário (Gerador ou Admin), mostra as obras criadas
    obras = Obra.objects.filter(gerador=request.user).order_by('-id')
    return render(request, 'core/painel.html', {'obras': obras})

@login_required(login_url='login')
def detalhe_obra(request, id):
    obra = get_object_or_404(Obra, id=id)
    # Busca todas as propostas (acordos) feitas para esta obra
    propostas = Acordo.objects.filter(obra=obra)
    
    return render(request, 'core/detalhe_obra.html', {
        'obra': obra, 
        'propostas': propostas
    })

@login_required(login_url='login')
def propor_acordo(request, id):
    obra = get_object_or_404(Obra, id=id)
    
    # Impede que o próprio dono da obra faça uma proposta para si mesmo
    if request.user == obra.gerador:
        return redirect('detalhe_obra', id=obra.id)

    if request.method == 'POST':
        valor = request.POST.get('valor_transporte')
        
        # Cria a proposta/acordo no banco de dados
        Acordo.objects.create(
            obra=obra,
            centro=request.user,
            valor_transporte=valor,
            comprovante_token=str(uuid.uuid4())[:8].upper() # Gera um token curto
        )
        return redirect('detalhe_obra', id=obra.id)
        
    return render(request, 'core/propor_acordo.html', {'obra': obra})

def cadastrar_usuario(request):
    if request.user.is_authenticated:
        return redirect('painel')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- CÓDIGO NOVO AQUI ---
            # Pega a escolha do formulário e cria o perfil no banco
            tipo_escolhido = form.cleaned_data.get('tipo_usuario')
            Perfil.objects.create(user=user, tipo=tipo_escolhido)
            # ------------------------
            
            login(request, user)
            return redirect('painel')
    else:
        form = CadastroForm()
        
    return render(request, 'core/cadastrar_usuario.html', {'form': form})

@login_required(login_url='login')
def aceitar_acordo(request, id):
    acordo = get_object_or_404(Acordo, id=id)
    obra = acordo.obra

    if request.user == obra.gerador:
        acordo.pago = True
        acordo.save()
        
        obra.status = 'EM TRANSPORTE'
        obra.save()
        
    return redirect('painel')

@login_required(login_url='login')
def confirmar_entrega(request, id):
    acordo = get_object_or_404(Acordo, id=id)
    
    if request.user == acordo.centro:
        acordo.entregue = True
        acordo.save()
        
        obra = acordo.obra
        obra.status = 'CONCLUIDO'
        obra.save()
        
    return redirect('detalhe_obra', id=acordo.obra.id)

@login_required(login_url='login')
def comprovante(request, token):
    acordo = get_object_or_404(Acordo, comprovante_token=token, entregue=True)
    return render(request, 'core/comprovante.html', {'acordo': acordo})

def lista_obras(request):
    query = request.GET.get('q', '')
    obras = Obra.objects.all()

    if query:
        # Pega a frase "Tijolo Recife PE" e transforma na lista ["Tijolo", "Recife", "PE"]
        palavras_buscadas = query.split()
        
        # Cria um filtro base vazio
        filtro_geral = Q()
        
        for palavra in palavras_buscadas:
            # Para CADA palavra digitada, ela tem que existir em pelo menos um desses campos
            filtro_palavra = (
                Q(descricao__icontains=palavra) |
                Q(tipo_residuo__icontains=palavra) |
                Q(endereco__icontains=palavra)
            )
            
            filtro_palavra |= Q(bairro__icontains=palavra)
            filtro_palavra |= Q(cidade__icontains=palavra)
            filtro_palavra |= Q(estado__icontains=palavra)

            if not filtro_geral:
                filtro_geral = filtro_palavra
            else:
                # O operador & (AND) garante que se o cara buscar "Tijolo Recife", 
                # a obra TEM que ter a palavra Tijolo E a palavra Recife.
                filtro_geral &= filtro_palavra
                
        obras = obras.filter(filtro_geral).distinct()

    return render(request, 'core/obras.html', {'obras': obras, 'query': query})