import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from demo_agentes import main
from defensor_agno import AgenteDefensorAgno
from fraudador_agno import AgenteFraudadorAgno


class TestDemoAgentes(unittest.TestCase):
    def setUp(self):
        self.backend_fraudador = Mock()
        self.backend_defensor = Mock()
        self.fabrica_fraudador = self.enterContext(patch(
            "demo_agentes.AgenteFraudadorAgno",
            side_effect=lambda modelo: AgenteFraudadorAgno(
                modelo=modelo, agente=self.backend_fraudador
            ),
        ))
        self.fabrica_defensor = self.enterContext(patch(
            "demo_agentes.AgenteDefensorAgno",
            side_effect=lambda modelo: AgenteDefensorAgno(
                modelo=modelo, agente=self.backend_defensor
            ),
        ))
        self.enterContext(patch("builtins.print"))
        self.saida = Path(self.enterContext(TemporaryDirectory())) / "evidencias" / "agentes.json"

    def test_dois_agentes_recebem_feedback_e_exportam_evidencias(self):
        def decidir_fraude(entrada):
            observacoes = json.loads(entrada)["observacoes"]
            bloqueado = observacoes and not observacoes[-1]["cupom_resgatado"]
            return SimpleNamespace(content={
                "estrategia": "A2" if bloqueado else "A1",
                "motivo": "Observou bloqueio." if bloqueado else "Explora A1.",
            })

        def decidir_defesa(entrada):
            observacoes = json.loads(entrada)["observacoes"]
            fraude = observacoes and observacoes[-1]["cupom_resgatado"]
            return SimpleNamespace(content={
                "estrategia": "B2" if fraude else "B1",
                "motivo": "Observou fraude." if fraude else "Mantém B1.",
            })

        self.backend_fraudador.run.side_effect = decidir_fraude
        self.backend_defensor.run.side_effect = decidir_defesa
        main([
            "--rodadas", "3", "--seed", "0", "--saida", str(self.saida),
            "--modelo-fraudador", "modelo-fraude-teste",
            "--modelo-defensor", "modelo-defesa-teste",
        ])

        evidencia = json.loads(self.saida.read_text(encoding="utf-8"))
        self.assertEqual(evidencia["status"], "concluida")
        self.assertEqual(evidencia["seed"], 0)
        self.assertEqual(evidencia["rodadas_solicitadas"], 3)
        self.assertEqual(evidencia["resumo"]["total_rodadas"], 3)
        self.assertEqual(evidencia["modelos"], {
            "fraudador": "modelo-fraude-teste", "defensor": "modelo-defesa-teste"
        })
        self.fabrica_fraudador.assert_called_once_with(modelo="modelo-fraude-teste")
        self.fabrica_defensor.assert_called_once_with(modelo="modelo-defesa-teste")
        self.assertEqual([r["ataque"] for r in evidencia["historico"]], ["A1", "A2", "A1"])
        self.assertEqual([r["defesa"] for r in evidencia["historico"]], ["B1", "B1", "B2"])

        for papel, backend in (
            ("fraudador", self.backend_fraudador),
            ("defensor", self.backend_defensor),
        ):
            decisoes = evidencia[f"decisoes_{papel}"]
            self.assertEqual([len(d["observacoes"]) for d in decisoes], [0, 1, 2])
            self.assertTrue(any(d["mudou_estrategia"] for d in decisoes))
            for chamada, decisao in zip(backend.run.call_args_list, decisoes):
                observacoes = json.loads(chamada.args[0])["observacoes"]
                self.assertEqual(observacoes, decisao["observacoes"])
                for observacao in observacoes:
                    self.assertNotIn("probabilidade_sucesso", observacao)
                    if papel == "fraudador":
                        self.assertNotIn("defesa", observacao)

    def test_falha_preserva_rodadas_e_decisoes_parciais(self):
        self.backend_fraudador.run.return_value = SimpleNamespace(content={
            "estrategia": "A1", "motivo": "Explora A1."
        })
        self.backend_defensor.run.side_effect = [
            SimpleNamespace(content={"estrategia": "B1", "motivo": "Explora B1."}),
            RuntimeError("Provedor indisponível"),
        ]
        with patch.dict("os.environ", {
            "FRAUDADOR_MODEL": "modelo-fraude-ambiente",
            "DEFENSOR_MODEL": "modelo-defesa-ambiente",
        }):
            with self.assertRaisesRegex(RuntimeError, "Provedor indisponível"):
                main(["--rodadas", "3", "--saida", str(self.saida)])

        evidencia = json.loads(self.saida.read_text(encoding="utf-8"))
        self.assertEqual(evidencia["status"], "interrompida")
        self.assertEqual(evidencia["resumo"]["total_rodadas"], 1)
        self.assertEqual(len(evidencia["historico"]), 1)
        self.assertEqual(len(evidencia["decisoes_fraudador"]), 2)
        self.assertEqual(len(evidencia["decisoes_defensor"]), 1)
        self.assertEqual(evidencia["modelos"], {
            "fraudador": "modelo-fraude-ambiente", "defensor": "modelo-defesa-ambiente"
        })

    def test_rejeita_rodadas_invalidas_antes_de_criar_agentes(self):
        with patch("sys.stderr"):
            with self.assertRaises(SystemExit) as erro:
                main(["--rodadas", "2", "--saida", str(self.saida)])
        self.assertEqual(erro.exception.code, 2)
        self.fabrica_fraudador.assert_not_called()
        self.fabrica_defensor.assert_not_called()
        self.assertFalse(self.saida.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
