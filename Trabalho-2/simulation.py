from dataclasses import dataclass


@dataclass
class Resultado:
    cupom_resgatado: bool
    fraude_detectada: bool
    custo_sistema: float
    beneficio_fraudador: float


class Ambiente:
    def __init__(self):
        self.historico = []
        self.cupom_ja_utilizado = False

    def processar(self, ataque: str, defesa: str) -> Resultado:
        # Probabilidade de sucesso da tentativa
        chances = {
            ("A1", "B1"): 0.70,
            ("A1", "B2"): 0.10,
            ("A2", "B1"): 0.80,
            ("A2", "B2"): 0.35,
        }

        # Custos da defesa
        custos = {
            "B1": 1.0,
            "B2": 3.0,
        }

        sucesso = chances[(ataque, defesa)]

        # Simulação determinística inicial
        # Posteriormente utilizaremos aleatoriedade controlada
        resgatado = sucesso >= 0.50

        fraude = resgatado
        custo = custos[defesa]

        resultado = Resultado(
            cupom_resgatado=resgatado,
            fraude_detectada=not fraude,
            custo_sistema=custo,
            beneficio_fraudador=10.0 if fraude else 0.0,
        )

        self.historico.append({
            "ataque": ataque,
            "defesa": defesa,
            "resultado": resultado,
        })

        return resultado