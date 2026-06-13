from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nova-obra/', views.cadastrar_obra, name='cadastrar_obra'),
    path('painel/', views.painel, name='painel'),
    
    # Rotas de Negociação e Detalhes
    path('obras/', views.lista_obras, name='lista_obras'),
    path('obra/<int:id>/', views.detalhe_obra, name='detalhe_obra'),
    path('obra/<int:id>/propor-acordo/', views.propor_acordo, name='propor_acordo'),
    
    # Rotas do fluxo (BPMN do Figma)
    path('acordo/<int:id>/responder/<str:acao>/', views.responder_proposta, name='responder_proposta'),
    path('acordo/<int:id>/pagamento/', views.escolher_pagamento, name='escolher_pagamento'),
    path('acordo/<int:id>/validar-pagamento/', views.simular_pagamento_online, name='simular_pagamento_online'),
    path('acordo/<int:id>/enviar/', views.enviar_material, name='enviar_material'),
    path('acordo/<int:id>/recolher/', views.recolher_material, name='recolher_material'),
    
    # Comprovante
    path('comprovante/<str:token>/', views.comprovante, name='comprovante'),
    
    # Rotas de Autenticação
    path('entrar/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
]
