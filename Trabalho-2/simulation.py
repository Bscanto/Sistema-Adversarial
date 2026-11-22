import random
from dataclasses import dataclass


@dataclass
class Resultado:
    cupom_resgatado: bool
    fraude_detectada: bool

    probabilidade_sucesso: float

    custo_operacional: float
    custo_friccao: float
    custo_sistema: float

    perda_por_fraude: float
    custo_total_sistema: float

    beneficio_fraudador: float
    beneficio_defensor: float

    utilidade_fraudador: float
    utilidade_defensor: float

    cupom_ja_utilizado: bool


class Ambiente:
    """
    Ambiente responsável por executar as interações
    entre as estratégias de ataque e defesa.

    Os agentes escolhem as ações.
    O ambiente calcula os resultados.
    """

    # Probabilidade de sucesso de cada combinação
    CHANCES = {
        ("A1", "B1"): 0.70,
        ("A1", "B2"): 0.10,
        ("A2", "B1"): 0.80,
        ("A2", "B2"): 0.35,
    }

    # Custo operacional das defesas
    CUSTOS_OPERACIONAIS = {
        "B1": 1.0,
        "B2": 3.0,
    }

    # Penalidade estimada pela fricção causada
    # aos compradores legítimos.
    CUSTOS_FRICCAO = {
        "B1": 0.0,
        "B2": 8.0,
    }

    # Valor econômico atribuído ao cupom
    VALOR_CUPOM = 10.0

    def __init__(self, seed=42):
        self.historico = []
        self.cupons_utilizados = set()
        self.random = random.Random(seed)

    def processar(
        self,
        ataque: str,
        defesa: str,
        id_cliente: str = None
    ) -> Resultado:

        # Validação das estratégias
        ataques_validos = {"A1", "A2"}
        defesas_validas = {"B1", "B2"}

        if ataque not in ataques_validos:
            raise ValueError(f"Estratégia de ataque inválida: {ataque}")

        if defesa not in defesas_validas:
            raise ValueError(f"Estratégia de defesa inválida: {defesa}")

        # Se não houver identificador, considera uma nova conta
        if id_cliente is None:
            ids_existentes = {rodada["id_cliente"] for rodada in self.historico}
            numero_cliente = len(self.historico) + 1
            id_cliente = f"cliente_{numero_cliente:03d}"
            # Identificadores informados manualmente também ficam reservados,
            # mesmo quando a tentativa anterior não resgatou o cupom.
            while id_cliente in ids_existentes:
                numero_cliente += 1
                id_cliente = f"cliente_{numero_cliente:03d}"

        if not id_cliente.strip():
            raise ValueError("O identificador do cliente não pode ser vazio.")

        # Verifica se o cupom já foi utilizado pelo cliente
        cupom_ja_utilizado = id_cliente in self.cupons_utilizados

        # Probabilidade de sucesso da tentativa
        if cupom_ja_utilizado:
            sucesso = False
            probabilidade = 0.0
        else:
            probabilidade = self.CHANCES[(ataque, defesa)]
            sucesso = self.random.random() < probabilidade

        # Registra o cupom caso o resgate tenha sido bem-sucedido
        if sucesso:
            self.cupons_utilizados.add(id_cliente)

        # Custos da defesa
        custo_operacional = self.CUSTOS_OPERACIONAIS[defesa]
        custo_friccao = self.CUSTOS_FRICCAO[defesa]

        custo_sistema = custo_operacional + custo_friccao

        # Consequências econômicas
        perda_por_fraude = (
            self.VALOR_CUPOM if sucesso else 0.0
        )

        custo_total_sistema = custo_sistema + perda_por_fraude

        beneficio_fraudador = (
            self.VALOR_CUPOM if sucesso else 0.0
        )

        # Benefício do defensor: valor da fraude evitada
        beneficio_defensor = (
            self.VALOR_CUPOM if not sucesso else 0.0
        )

        # Utilidades dos agentes
        utilidade_fraudador = beneficio_fraudador

        utilidade_defensor = (
            beneficio_defensor - custo_total_sistema
        )

        resultado = Resultado(
            cupom_resgatado=sucesso,
            fraude_detectada=not sucesso,
            probabilidade_sucesso=probabilidade,
            custo_operacional=custo_operacional,
            custo_friccao=custo_friccao,
            custo_sistema=custo_sistema,
            perda_por_fraude=perda_por_fraude,
            custo_total_sistema=custo_total_sistema,
            beneficio_fraudador=beneficio_fraudador,
            beneficio_defensor=beneficio_defensor,
            utilidade_fraudador=utilidade_fraudador,
            utilidade_defensor=utilidade_defensor,
            cupom_ja_utilizado=cupom_ja_utilizado,
        )

        # Registro da rodada
        self.historico.append({
            "rodada": len(self.historico) + 1,
            "id_cliente": id_cliente,
            "ataque": ataque,
            "defesa": defesa,
            "resultado": resultado,
        })

        return resultado
