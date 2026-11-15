import unittest

from simulation import Ambiente
from runner import executar_simulacao


class AgenteTeste:
    """Agente simples utilizado para testar o orquestrador."""

    def __init__(self, estrategia):
        self.estrategia = estrategia

    def escolher_acao(self, historico):
        return self.estrategia


class TestAmbiente(unittest.TestCase):

    def test_reutilizacao_cupom(self):
        ambiente = Ambiente(seed=42)

        primeiro = ambiente.processar(
            "A1", "B1", "cliente_teste"
        )

        segundo = ambiente.processar(
            "A1", "B1", "cliente_teste"
        )

        self.assertTrue(primeiro.cupom_resgatado)
        self.assertTrue(segundo.cupom_ja_utilizado)
        self.assertFalse(segundo.cupom_resgatado)

    def test_estrategia_invalida(self):
        ambiente = Ambiente()

        with self.assertRaises(ValueError):
            ambiente.processar("A3", "B1")

    def test_reprodutibilidade(self):
        ambiente1 = Ambiente(seed=42)
        ambiente2 = Ambiente(seed=42)

        resultado1 = ambiente1.processar("A1", "B1")
        resultado2 = ambiente2.processar("A1", "B1")

        self.assertEqual(resultado1, resultado2)


class TestOrquestrador(unittest.TestCase):

    def test_execucao_multiplas_rodadas(self):
        ambiente = Ambiente(seed=42)

        fraudador = AgenteTeste("A1")
        defensor = AgenteTeste("B1")

        resumo = executar_simulacao(
            ambiente=ambiente,
            fraudador=fraudador,
            defensor=defensor,
            total_rodadas=5,
            exibir=False,
        )

        self.assertEqual(len(ambiente.historico), 5)
        self.assertEqual(resumo["total_rodadas"], 5)

    def test_quantidade_invalida_rodadas(self):
        ambiente = Ambiente(seed=42)

        fraudador = AgenteTeste("A1")
        defensor = AgenteTeste("B1")

        with self.assertRaises(ValueError):
            executar_simulacao(
                ambiente,
                fraudador,
                defensor,
                total_rodadas=0,
                exibir=False,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)