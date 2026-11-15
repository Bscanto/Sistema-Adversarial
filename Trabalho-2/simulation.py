import random
from dataclasses import dataclass


@dataclass
class Resultado:
    cupom_resgatado: bool
    fraude_detectada: bool
    custo_sistema: float
    beneficio_fraudador: float


class Ambiente:
    def __init__(self, seed=42):
        self.historico = []
        self.cupom_ja_utilizado = False
        self.random = random.Random(seed)

    def processar(self, ataque: str, defesa: str) -> Resultado:
        chances = {
            ("A1", "B1"): 0.70,
            ("A1", "B2"): 0.10,
            ("A2", "B1"): 0.80,
            ("A2", "B2"): 0.35,
        }

        custos = {
            "B1": 1.0,
            "B2": 3.0,
        }

        sucesso = chances[(ataque, defesa)]

        # Sorteio probabilístico
        resgatado = self.random.random() < sucesso

        resultado = Resultado(
            cupom_resgatado=resgatado,
            fraude_detectada=not resgatado,
            custo_sistema=custos[defesa],
            beneficio_fraudador=10.0 if resgatado else 0.0,
        )

        self.historico.append({
            "ataque": ataque,
            "defesa": defesa,
            "resultado": resultado,
        })

        return resultado