
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pydantic import ValidationError

from defensor_agno import AgenteDefensorAgno
from simulation import Ambiente


class TestDefensorAgno(unittest.TestCase):

    def test_primeira_decisao(self):
        backend = Mock()
        backend.run.return_value = SimpleNamespace(
            content={
                "estrategia": "B1",
                "motivo": "Começa com defesa básica."
            }
        )

        agente = AgenteDefensorAgno(agente=backend)

        self.assertEqual(agente.escolher_acao([]), "B1")
        self.assertEqual(agente.estrategia_atual, "B1")
        self.assertEqual(len(agente.decisoes), 1)

    def test_historico_sem_vazamento(self):
        ambiente = Ambiente()
        ambiente.processar("A1", "B1")

        backend = Mock()
        backend.run.return_value = SimpleNamespace(
            content={
                "estrategia": "B2",
                "motivo": "Considera reforçar a proteção."
            }
        )

        agente = AgenteDefensorAgno(agente=backend)

        agente.escolher_acao(ambiente.historico)

        entrada = json.loads(backend.run.call_args.args[0])
        observacao = entrada["observacoes"][0]

        self.assertEqual(
            set(observacao),
            {
                "rodada",
                "ataque",
                "defesa",
                "cupom_resgatado",
                "fraude_detectada",
                "custo_operacional",
                "custo_friccao",
                "custo_sistema",
                "beneficio_defensor",
                "utilidade_defensor",
            }
        )

        self.assertNotIn("probabilidade_sucesso", observacao)

    def test_mudanca_de_estrategia(self):
        backend = Mock()
        backend.run.side_effect = [
            SimpleNamespace(content={
                "estrategia": "B1",
                "motivo": "Defesa inicial."
            }),
            SimpleNamespace(content={
                "estrategia": "B2",
                "motivo": "Considera reforçar a proteção."
            }),
        ]

        agente = AgenteDefensorAgno(agente=backend)

        self.assertEqual(agente.escolher_acao([]), "B1")

        self.assertEqual(
            agente.escolher_acao([
                {
                    "rodada": 1,
                    "ataque": "A1",
                    "defesa": "B1",
                    "resultado": SimpleNamespace(
                        cupom_resgatado=True,
                        fraude_detectada=False,
                        custo_operacional=1.0,
                        custo_friccao=0.0,
                        custo_sistema=1.0,
                        beneficio_defensor=0.0,
                        utilidade_defensor=-11.0,
                    )
                }
            ]),
            "B2"
        )

        self.assertTrue(agente.decisoes[1]["mudou_estrategia"])

    def test_resposta_invalida(self):
        backend = Mock()
        backend.run.return_value = SimpleNamespace(
            content={
                "estrategia": "B3",
                "motivo": "Estratégia inválida."
            }
        )

        agente = AgenteDefensorAgno(agente=backend)

        with self.assertRaises(ValidationError):
            agente.escolher_acao([])

        self.assertEqual(agente.decisoes, [])
        self.assertIsNone(agente.estrategia_atual)

    def test_falha_do_provedor(self):
        backend = Mock()
        backend.run.side_effect = RuntimeError("API indisponível")

        agente = AgenteDefensorAgno(agente=backend)

        with self.assertRaises(RuntimeError):
            agente.escolher_acao([])

        self.assertEqual(agente.decisoes, [])

    def test_chave_ausente(self):
        with patch.dict(
            "os.environ",
            {"ANTHROPIC_API_KEY": ""}
        ):
            with self.assertRaisesRegex(
                ValueError,
                "ANTHROPIC_API_KEY"
            ):
                AgenteDefensorAgno()


if __name__ == "__main__":
    unittest.main(verbosity=2)
