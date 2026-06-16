from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth.models import User
from core.models import Obra, Acordo, Avaliacao
from .test_helpers import criar_usuario, criar_obra, criar_acordo


class IndexViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')

    def test_acessivel_sem_login(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_exibe_apenas_obras_ativas(self):
        criar_obra(self.gerador, descricao='Ativa', status='ATIVO')
        criar_obra(self.gerador, descricao='Concluida', status='CONCLUIDO')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['obras'].count(), 1)
        self.assertEqual(response.context['obras'].first().descricao, 'Ativa')


class CadastrarUsuarioViewTest(TestCase):

    def test_get_retorna_formulario(self):
        response = self.client.get(reverse('cadastrar_usuario'))
        self.assertEqual(response.status_code, 200)

    def test_post_valido_cria_usuario_e_perfil(self):
        self.client.post(reverse('cadastrar_usuario'), {
            'username': 'novousuario',
            'email': 'novo@teste.com',
            'password1': 'SenhaForte@123',
            'password2': 'SenhaForte@123',
            'tipo_usuario': 'GERADOR',
        })
        self.assertTrue(User.objects.filter(username='novousuario').exists())
        self.assertTrue(User.objects.filter(username='novousuario').first().perfil.tipo == 'GERADOR')

    def test_post_valido_redireciona_para_painel(self):
        response = self.client.post(reverse('cadastrar_usuario'), {
            'username': 'novousuario',
            'email': 'novo@teste.com',
            'password1': 'SenhaForte@123',
            'password2': 'SenhaForte@123',
            'tipo_usuario': 'GERADOR',
        })
        self.assertRedirects(response, reverse('painel'))

    def test_usuario_ja_logado_redireciona(self):
        criar_usuario('existente', 'GERADOR')
        self.client.login(username='existente', password='senha123')
        response = self.client.get(reverse('cadastrar_usuario'))
        self.assertRedirects(response, reverse('painel'))

    def test_senha_fraca_nao_cria_usuario(self):
        self.client.post(reverse('cadastrar_usuario'), {
            'username': 'fraco',
            'password1': '123',
            'password2': '123',
            'tipo_usuario': 'GERADOR',
        })
        self.assertFalse(User.objects.filter(username='fraco').exists())


class PainelViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')

    def test_requer_login(self):
        response = self.client.get(reverse('painel'))
        self.assertRedirects(response, '/entrar/?next=/painel/')

    def test_gerador_usa_template_correto(self):
        self.client.login(username='gerador', password='senha123')
        response = self.client.get(reverse('painel'))
        self.assertTemplateUsed(response, 'core/painel.html')

    def test_centro_usa_template_correto(self):
        self.client.login(username='centro', password='senha123')
        response = self.client.get(reverse('painel'))
        self.assertTemplateUsed(response, 'core/painel_centro.html')


class CadastrarObraViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')

    def test_requer_login(self):
        response = self.client.get(reverse('cadastrar_obra'))
        self.assertEqual(response.status_code, 302)

    def test_post_valido_cria_obra(self):
        self.client.login(username='gerador', password='senha123')
        self.client.post(reverse('cadastrar_obra'), {
            'descricao': 'Entulho de demolição',
            'tipo_residuo': 'Concreto',
            'endereco': 'Rua Teste, 123',
        })
        self.assertTrue(Obra.objects.filter(descricao='Entulho de demolição', gerador=self.gerador).exists())

    def test_post_valido_redireciona_para_painel(self):
        self.client.login(username='gerador', password='senha123')
        response = self.client.post(reverse('cadastrar_obra'), {
            'descricao': 'Entulho de demolição',
            'tipo_residuo': 'Concreto',
            'endereco': 'Rua Teste, 123',
        })
        self.assertRedirects(response, reverse('painel'))


class ProporAcordoViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        self.obra = criar_obra(self.gerador)

    def test_gerador_nao_pode_propor_na_propria_obra(self):
        self.client.login(username='gerador', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '100.00'})
        self.assertFalse(Acordo.objects.filter(obra=self.obra).exists())

    def test_centro_pode_propor_acordo(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '250.00'})
        self.assertTrue(Acordo.objects.filter(obra=self.obra, centro=self.centro).exists())

    def test_proposta_muda_status_da_obra_para_em_negociacao(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '100.00'})
        self.obra.refresh_from_db()
        self.assertEqual(self.obra.status, 'EM_NEGOCIACAO')

    def test_valor_zero_nao_cria_acordo(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '0.00'})
        self.assertFalse(Acordo.objects.filter(obra=self.obra).exists())

    def test_valor_negativo_nao_cria_acordo(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '-50.00'})
        self.assertFalse(Acordo.objects.filter(obra=self.obra).exists())

    def test_valor_invalido_nao_cria_acordo(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': 'abc'})
        self.assertFalse(Acordo.objects.filter(obra=self.obra).exists())

    def test_valor_acima_do_limite_nao_cria_acordo(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '99999999.99'})
        self.assertFalse(Acordo.objects.filter(obra=self.obra).exists())

    def test_dupla_proposta_nao_permitida(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '100.00'})
        self.client.post(reverse('propor_acordo', args=[self.obra.id]), {'valor_transporte': '200.00'})
        self.assertEqual(Acordo.objects.filter(obra=self.obra, centro=self.centro).count(), 1)


class ResponderPropostaViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        self.obra = criar_obra(self.gerador, status='EM_NEGOCIACAO')
        self.acordo = criar_acordo(self.obra, self.centro)

    def test_aceitar_proposta(self):
        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('responder_proposta', args=[self.acordo.id, 'aceitar']))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'ACEITO')

    def test_recusar_proposta(self):
        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('responder_proposta', args=[self.acordo.id, 'recusar']))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'RECUSADO')

    def test_aceitar_recusa_outras_propostas_pendentes(self):
        centro2 = criar_usuario('centro2', 'CENTRO')
        acordo2 = criar_acordo(self.obra, centro2, valor='120.00')
        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('responder_proposta', args=[self.acordo.id, 'aceitar']))
        acordo2.refresh_from_db()
        self.assertEqual(acordo2.status, 'RECUSADO')

    def test_recusar_ultima_proposta_volta_obra_para_ativo(self):
        # quando não há mais propostas pendentes, a obra volta a aceitar novas propostas
        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('responder_proposta', args=[self.acordo.id, 'recusar']))
        self.obra.refresh_from_db()
        self.assertEqual(self.obra.status, 'ATIVO')

    def test_nao_gerador_nao_pode_responder(self):
        self.client.login(username='centro', password='senha123')
        self.client.get(reverse('responder_proposta', args=[self.acordo.id, 'aceitar']))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'PROPOSTA')


class PagamentoViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        obra = criar_obra(self.gerador, status='EM_NEGOCIACAO')
        self.acordo = criar_acordo(obra, self.centro, status='ACEITO')

    def test_pagamento_na_entrega_libera_transporte(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('escolher_pagamento', args=[self.acordo.id]), {'forma_pagamento': 'ENTREGA'})
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'TRANSPORTE_LIBERADO')

    def test_pagamento_online_muda_para_aguardando_validacao(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('escolher_pagamento', args=[self.acordo.id]), {'forma_pagamento': 'ONLINE'})
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'AGUARDANDO_VALIDACAO')

    def test_nao_centro_nao_pode_escolher_pagamento(self):
        self.client.login(username='gerador', password='senha123')
        self.client.post(reverse('escolher_pagamento', args=[self.acordo.id]), {'forma_pagamento': 'ENTREGA'})
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'ACEITO')

    def test_simulacao_pagamento_online_libera_transporte_e_marca_pago(self):
        self.acordo.status = 'AGUARDANDO_VALIDACAO'
        self.acordo.forma_pagamento = 'ONLINE'
        self.acordo.save()
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('simular_pagamento_online', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'TRANSPORTE_LIBERADO')
        self.assertTrue(self.acordo.pago)

    def test_nao_centro_nao_pode_simular_pagamento_online(self):
        self.acordo.status = 'AGUARDANDO_VALIDACAO'
        self.acordo.save()
        self.client.login(username='gerador', password='senha123')
        self.client.post(reverse('simular_pagamento_online', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertFalse(self.acordo.pago)


class EnvioRecolhimentoViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        self.obra = criar_obra(self.gerador, status='EM_NEGOCIACAO')
        self.acordo = criar_acordo(self.obra, self.centro, status='TRANSPORTE_LIBERADO', forma_pagamento='ENTREGA')

    def test_gerador_envia_material(self):
        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('enviar_material', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'EM_TRANSPORTE')

    def test_nao_gerador_nao_pode_enviar(self):
        self.client.login(username='centro', password='senha123')
        self.client.get(reverse('enviar_material', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'TRANSPORTE_LIBERADO')

    def test_centro_recolhe_material(self):
        self.acordo.status = 'EM_TRANSPORTE'
        self.acordo.save()
        self.client.login(username='centro', password='senha123')
        self.client.get(reverse('recolher_material', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'CONCLUIDO')

    def test_recolhimento_pagamento_entrega_marca_como_pago(self):
        self.acordo.status = 'EM_TRANSPORTE'
        self.acordo.save()
        self.client.login(username='centro', password='senha123')
        self.client.get(reverse('recolher_material', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertTrue(self.acordo.pago)

    def test_recolhimento_gera_token_comprovante(self):
        self.acordo.status = 'EM_TRANSPORTE'
        self.acordo.save()
        self.client.login(username='centro', password='senha123')
        self.client.get(reverse('recolher_material', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertIsNotNone(self.acordo.comprovante_token)

    def test_nao_centro_nao_pode_recolher(self):
        self.acordo.status = 'EM_TRANSPORTE'
        self.acordo.save()
        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('recolher_material', args=[self.acordo.id]))
        self.acordo.refresh_from_db()
        self.assertEqual(self.acordo.status, 'EM_TRANSPORTE')


class ComprovanteViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        obra = criar_obra(self.gerador, status='CONCLUIDO')
        self.acordo = criar_acordo(obra, self.centro, status='CONCLUIDO')
        self.acordo.comprovante_token = 'ABC12345'
        self.acordo.save()

    def test_acesso_com_token_valido(self):
        self.client.login(username='gerador', password='senha123')
        response = self.client.get(reverse('comprovante', args=['ABC12345']))
        self.assertEqual(response.status_code, 200)

    def test_token_invalido_retorna_404(self):
        self.client.login(username='gerador', password='senha123')
        response = self.client.get(reverse('comprovante', args=['INVALIDO']))
        self.assertEqual(response.status_code, 404)


class AvaliarAcordoViewTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        obra = criar_obra(self.gerador, status='CONCLUIDO')
        self.acordo = criar_acordo(obra, self.centro, status='CONCLUIDO')
        self.acordo.comprovante_token = 'ABC12345'
        self.acordo.save()

    def test_centro_pode_avaliar(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('avaliar_acordo', args=[self.acordo.id]), {
            'nota': 5, 'titulo': 'Ótimo', 'comentario': 'Tudo certo'
        })
        self.assertTrue(Avaliacao.objects.filter(acordo=self.acordo, avaliador=self.centro).exists())

    def test_nao_centro_nao_pode_avaliar(self):
        self.client.login(username='gerador', password='senha123')
        self.client.post(reverse('avaliar_acordo', args=[self.acordo.id]), {
            'nota': 5, 'titulo': 'Ótimo', 'comentario': 'Tudo certo'
        })
        self.assertFalse(Avaliacao.objects.filter(acordo=self.acordo).exists())

    def test_dupla_avaliacao_nao_permitida(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('avaliar_acordo', args=[self.acordo.id]), {
            'nota': 5, 'titulo': 'Ótimo', 'comentario': 'Tudo certo'
        })
        self.client.post(reverse('avaliar_acordo', args=[self.acordo.id]), {
            'nota': 1, 'titulo': 'Ruim', 'comentario': 'Mudei de ideia'
        })
        self.assertEqual(Avaliacao.objects.filter(acordo=self.acordo, avaliador=self.centro).count(), 1)

    def test_avaliacao_registra_avaliado_como_gerador_da_obra(self):
        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('avaliar_acordo', args=[self.acordo.id]), {
            'nota': 4, 'titulo': 'Bom', 'comentario': 'Ok'
        })
        avaliacao = Avaliacao.objects.get(acordo=self.acordo, avaliador=self.centro)
        self.assertEqual(avaliacao.avaliado, self.gerador)


class PerfilVendedorViewTest(TestCase):

    def setUp(self):
        self.vendedor = criar_usuario('vendedor', 'GERADOR')

    def test_acessivel_sem_login(self):
        response = self.client.get(reverse('perfil_vendedor', args=[self.vendedor.id]))
        self.assertEqual(response.status_code, 200)

    def test_inexistente_retorna_404(self):
        response = self.client.get(reverse('perfil_vendedor', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ListaObrasViewTest(TestCase):

    def setUp(self):
        self.user = criar_usuario('user', 'GERADOR')
        criar_obra(self.user, descricao='Entulho de concreto', tipo_residuo='Concreto')
        criar_obra(self.user, descricao='Resíduos de madeira', tipo_residuo='Madeira')
        criar_obra(self.user, descricao='Obra concluída', tipo_residuo='Tijolo', status='CONCLUIDO')

    def test_exibe_apenas_obras_ativas(self):
        response = self.client.get(reverse('lista_obras'))
        self.assertEqual(response.context['obras'].count(), 2)

    def test_busca_filtra_por_tipo_residuo(self):
        response = self.client.get(reverse('lista_obras'), {'q': 'Concreto'})
        self.assertEqual(response.context['obras'].count(), 1)

    def test_busca_sem_resultado_retorna_vazio(self):
        response = self.client.get(reverse('lista_obras'), {'q': 'Inexistente'})
        self.assertEqual(response.context['obras'].count(), 0)

    def test_busca_por_descricao(self):
        response = self.client.get(reverse('lista_obras'), {'q': 'madeira'})
        self.assertEqual(response.context['obras'].count(), 1)


class FluxoCompletoTest(TestCase):
    # Simula o ciclo completo de uma negociação do início ao fim

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')

    def test_fluxo_pagamento_na_entrega(self):
        self.client.login(username='gerador', password='senha123')
        self.client.post(reverse('cadastrar_obra'), {
            'descricao': 'Entulho pesado', 'tipo_residuo': 'Concreto', 'endereco': 'Rua A, 1'
        })
        obra = Obra.objects.get(descricao='Entulho pesado')

        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[obra.id]), {'valor_transporte': '300.00'})
        acordo = Acordo.objects.get(obra=obra, centro=self.centro)
        self.assertEqual(acordo.status, 'PROPOSTA')

        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('responder_proposta', args=[acordo.id, 'aceitar']))
        acordo.refresh_from_db()
        self.assertEqual(acordo.status, 'ACEITO')

        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('escolher_pagamento', args=[acordo.id]), {'forma_pagamento': 'ENTREGA'})
        acordo.refresh_from_db()
        self.assertEqual(acordo.status, 'TRANSPORTE_LIBERADO')

        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('enviar_material', args=[acordo.id]))
        acordo.refresh_from_db()
        self.assertEqual(acordo.status, 'EM_TRANSPORTE')

        self.client.login(username='centro', password='senha123')
        self.client.get(reverse('recolher_material', args=[acordo.id]))
        acordo.refresh_from_db()
        self.assertEqual(acordo.status, 'CONCLUIDO')
        self.assertTrue(acordo.pago)
        self.assertIsNotNone(acordo.comprovante_token)

    def test_fluxo_pagamento_online(self):
        self.client.login(username='gerador', password='senha123')
        self.client.post(reverse('cadastrar_obra'), {
            'descricao': 'Obra online', 'tipo_residuo': 'Madeira', 'endereco': 'Rua B, 2'
        })
        obra = Obra.objects.get(descricao='Obra online')

        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('propor_acordo', args=[obra.id]), {'valor_transporte': '150.00'})
        acordo = Acordo.objects.get(obra=obra, centro=self.centro)

        self.client.login(username='gerador', password='senha123')
        self.client.get(reverse('responder_proposta', args=[acordo.id, 'aceitar']))

        self.client.login(username='centro', password='senha123')
        self.client.post(reverse('escolher_pagamento', args=[acordo.id]), {'forma_pagamento': 'ONLINE'})
        acordo.refresh_from_db()
        self.assertEqual(acordo.status, 'AGUARDANDO_VALIDACAO')

        self.client.post(reverse('simular_pagamento_online', args=[acordo.id]))
        acordo.refresh_from_db()
        self.assertEqual(acordo.status, 'TRANSPORTE_LIBERADO')
        self.assertTrue(acordo.pago)