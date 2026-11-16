"""Executa o fraudador Agno com o defensor de regras e exporta evidências."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from agents import AgenteDefensor
from fraudador_agno import AgenteFraudadorAgno
from runner import executar_simulacao
from simulation import Ambiente


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rodadas", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--modelo", default=None)
    parser.add_argument("--saida", type=Path, default=Path("evidencias/fraudador.json"))
    args = parser.parse_args()
    if args.rodadas < 3:
        parser.error("Use pelo menos três rodadas para a demonstração.")

    ambiente = Ambiente(seed=args.seed)
    fraudador = AgenteFraudadorAgno(modelo=args.modelo)
    resumo = executar_simulacao(ambiente, fraudador, AgenteDefensor(), args.rodadas)
    evidencia = {
        "seed": args.seed,
        "defensor": "regras",
        "resumo": resumo,
        "decisoes_fraudador": fraudador.decisoes,
        "historico": [
            {**rodada, "resultado": asdict(rodada["resultado"])}
            for rodada in ambiente.historico
        ],
    }
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nEvidências salvas em {args.saida}")


if __name__ == "__main__":
    main()
