import json
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pydantic import ValidationError

from agents import AgenteDefensor
from fraudador_agno import AgenteFraudadorAgno, DecisaoFraudador
from runner import executar_simulacao
from simulation import Ambiente


class TestFraudadorAgno(unittest.TestCase):
    def test_contrato_e_observacoes_sem_vazamento(self):
        ambiente = Ambiente()
        ambiente.processar("A1", "B2")
        antes = deepcopy(ambiente.historico)
        backend = Mock()
        backend.run.return_value = SimpleNamespace(content=DecisaoFraudador(
            estrategia="A2", motivo="A tentativa anterior foi bloqueada."
        ))
        agente = AgenteFraudadorAgno(agente=backend)
        self.assertEqual(agente.escolher_acao(ambiente.historico), "A2")
        observacao = json.loads(backend.run.call_args.args[0])["observacoes"][0]
        self.assertEqual(set(observacao), {
            "rodada", "ataque", "cupom_resgatado", "utilidade_fraudador"
        })
        self.assertEqual(ambiente.historico, antes)
        self.assertEqual(agente.motivo, agente.decisoes[0]["motivo"])

    def test_rodadas_conectadas_com_backend_controlado(self):
        # Este substituto verifica o fluxo de feedback, não a inteligência do LLM.
        def decidir(entrada):
            observacoes = json.loads(entrada)["observacoes"]
            bloqueado = observacoes and not observacoes[-1]["cupom_resgatado"]
            return SimpleNamespace(content={
                "estrategia": "A2" if bloqueado else "A1",
                "motivo": "Observou bloqueio." if bloqueado else "Explora tentativa simples.",
            })

        backend = Mock()
        backend.run.side_effect = decidir
        agente = AgenteFraudadorAgno(agente=backend)
        ambiente = Ambiente(seed=0)  # Primeiro sorteio bloqueia A1/B1.
        resumo = executar_simulacao(ambiente, agente, AgenteDefensor(), 3, exibir=False)
        self.assertEqual(resumo["total_rodadas"], 3)
        self.assertEqual([len(d["observacoes"]) for d in agente.decisoes], [0, 1, 2])
        self.assertEqual(agente.decisoes[0]["estrategia"], "A1")
        self.assertEqual(agente.decisoes[1]["estrategia"], "A2")
        self.assertTrue(agente.decisoes[1]["mudou_estrategia"])

    def test_respostas_invalidas_nao_alteram_estado(self):
        for conteudo in [None, {"estrategia": "A3", "motivo": "Inválida"},
                         {"estrategia": "A1", "motivo": "  "}, "não é JSON"]:
            with self.subTest(conteudo=conteudo):
                backend = Mock()
                backend.run.return_value = SimpleNamespace(content=conteudo)
                agente = AgenteFraudadorAgno(agente=backend)
                with self.assertRaises(ValidationError):
                    agente.escolher_acao([])
                self.assertEqual(agente.decisoes, [])
                self.assertIsNone(agente.estrategia_atual)

    def test_json_e_falha_do_provedor(self):
        backend = Mock()
        backend.run.return_value = SimpleNamespace(content='{"estrategia":"A1","motivo":"Exploração."}')
        agente = AgenteFraudadorAgno(agente=backend)
        self.assertEqual(agente.escolher_acao([]), "A1")
        backend.run.side_effect = RuntimeError("Provedor indisponível")
        with self.assertRaises(RuntimeError):
            agente.escolher_acao([])
        self.assertEqual(len(agente.decisoes), 1)

    def test_chave_ausente(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "ANTHROPIC_API_KEY"):
                AgenteFraudadorAgno()


if __name__ == "__main__":
    unittest.main(verbosity=2)
