"""Executa fraudador e defensor Agno e exporta as evidências dos dois agentes."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from defensor_agno import AgenteDefensorAgno
from fraudador_agno import AgenteFraudadorAgno
from runner import calcular_resumo, executar_simulacao
from simulation import Ambiente


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rodadas", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--modelo-fraudador", default=None)
    parser.add_argument("--modelo-defensor", default=None)
    parser.add_argument("--saida", type=Path, default=Path("evidencias/agentes.json"))
    args = parser.parse_args(argv)
    if args.rodadas < 3:
        parser.error("Use pelo menos três rodadas para a demonstração.")

    ambiente = Ambiente(seed=args.seed)
    fraudador = AgenteFraudadorAgno(modelo=args.modelo_fraudador)
    defensor = AgenteDefensorAgno(modelo=args.modelo_defensor)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    concluida = False
    try:
        executar_simulacao(ambiente, fraudador, defensor, args.rodadas)
        concluida = True
    finally:
        # Preserva as rodadas concluídas e as decisões já tomadas se uma
        # chamada à API falhar. A exceção continua sendo propagada.
        evidencia = {
            "status": "concluida" if concluida else "interrompida",
            "rodadas_solicitadas": args.rodadas,
            "seed": args.seed,
            "fraudador": "agno",
            "defensor": "agno",
            "modelos": {
                "fraudador": fraudador.modelo,
                "defensor": defensor.modelo,
            },
            "resumo": calcular_resumo(ambiente.historico),
            "decisoes_fraudador": fraudador.decisoes,
            "decisoes_defensor": defensor.decisoes,
            "historico": [
                {**rodada, "resultado": asdict(rodada["resultado"])}
                for rodada in ambiente.historico
            ],
        }
        args.saida.write_text(
            json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nEvidências salvas em {args.saida}")


if __name__ == "__main__":
    main()
