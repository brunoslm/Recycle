from django.test import TestCase
from decimal import Decimal
from core.models import Perfil, Obra, Acordo, Avaliacao
from .test_helpers import criar_usuario, criar_obra, criar_acordo


class PerfilModelTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')

    def test_str(self):
        self.assertEqual(str(self.gerador.perfil), 'gerador - GERADOR')

    def test_media_avaliacao_sem_avaliacoes(self):
        self.assertEqual(self.gerador.perfil.media_avaliacao, 0.0)

    def test_media_avaliacao_com_avaliacoes(self):
        obra = criar_obra(self.gerador, status='CONCLUIDO')
        acordo = criar_acordo(obra, self.centro, status='CONCLUIDO')
        Avaliacao.objects.create(acordo=acordo, avaliador=self.centro, avaliado=self.gerador, nota=4)
        Avaliacao.objects.create(acordo=acordo, avaliador=self.centro, avaliado=self.gerador, nota=2)
        # média esperada: (4 + 2) / 2 = 3.0
        self.assertEqual(self.gerador.perfil.media_avaliacao, 3.0)

    def test_total_transacoes_gerador(self):
        obra = criar_obra(self.gerador, status='CONCLUIDO')
        criar_acordo(obra, self.centro, status='CONCLUIDO')
        self.assertEqual(self.gerador.perfil.total_transacoes, 1)

    def test_total_transacoes_centro(self):
        obra = criar_obra(self.gerador, status='CONCLUIDO')
        criar_acordo(obra, self.centro, status='CONCLUIDO')
        self.assertEqual(self.centro.perfil.total_transacoes, 1)


class ObraModelTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')

    def test_str(self):
        obra = criar_obra(self.gerador, descricao='Entulho de demolição')
        self.assertEqual(str(obra), 'Entulho de demolição')

    def test_status_padrao_ativo(self):
        obra = criar_obra(self.gerador)
        self.assertEqual(obra.status, 'ATIVO')


class AcordoModelTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        self.obra = criar_obra(self.gerador)

    def test_str(self):
        acordo = criar_acordo(self.obra, self.centro)
        self.assertIn('Acordo #', str(acordo))
        self.assertIn('Obra teste', str(acordo))

    def test_status_padrao_proposta(self):
        acordo = criar_acordo(self.obra, self.centro)
        self.assertEqual(acordo.status, 'PROPOSTA')

    def test_pago_padrao_false(self):
        acordo = criar_acordo(self.obra, self.centro)
        self.assertFalse(acordo.pago)


class AvaliacaoModelTest(TestCase):

    def setUp(self):
        self.gerador = criar_usuario('gerador', 'GERADOR')
        self.centro = criar_usuario('centro', 'CENTRO')
        obra = criar_obra(self.gerador, status='CONCLUIDO')
        self.acordo = criar_acordo(obra, self.centro, status='CONCLUIDO')

    def test_str(self):
        avaliacao = Avaliacao.objects.create(
            acordo=self.acordo, avaliador=self.centro, avaliado=self.gerador, nota=5
        )
        self.assertIn('centro', str(avaliacao))
        self.assertIn('gerador', str(avaliacao))
        self.assertIn('5', str(avaliacao))