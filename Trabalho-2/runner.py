from typing import Protocol

from simulation import Ambiente


class Agente(Protocol):
    """
    Interface esperada dos agentes.

    Qualquer agente, seja baseado em regras ou Agno,
    deverá implementar escolher_acao().
    """

    def escolher_acao(self, historico: list[dict]) -> str:
        ...


def calcular_resumo(historico: list[dict]) -> dict:
    """
    Consolida os indicadores financeiros e operacionais
    de todas as rodadas.
    """

    resultados = [
        rodada["resultado"]
        for rodada in historico
    ]

    return {
        "total_rodadas": len(resultados),

        "fraudes_bem_sucedidas": sum(
            r.cupom_resgatado for r in resultados
        ),

        "fraudes_bloqueadas": sum(
            r.fraude_detectada for r in resultados
        ),

        "custo_operacional": sum(
            r.custo_operacional for r in resultados
        ),

        "custo_friccao": sum(
            r.custo_friccao for r in resultados
        ),

        "custo_defesas": sum(
            r.custo_sistema for r in resultados
        ),

        "perdas_fraude": sum(
            r.perda_por_fraude for r in resultados
        ),

        "beneficio_fraudador": sum(
            r.beneficio_fraudador for r in resultados
        ),

        "beneficio_defensor": sum(
            r.beneficio_defensor for r in resultados
        ),

        "utilidade_fraudador": sum(
            r.utilidade_fraudador for r in resultados
        ),

        "utilidade_defensor": sum(
            r.utilidade_defensor for r in resultados
        ),
    }


def imprimir_rodada(
    rodada: int,
    ataque: str,
    defesa: str,
    fraudador: Agente,
    defensor: Agente,
    resultado,
):
    """Apresenta os detalhes de uma rodada."""

    print(f"\n--- Rodada {rodada} ---")

    print(f"Fraudador: {ataque}")
    print(f"Motivo: {getattr(fraudador, 'motivo', 'Decisão do agente')}")

    print(f"Defensor: {defesa}")
    print(f"Motivo: {getattr(defensor, 'motivo', 'Decisão do agente')}")

    print(
        f"Probabilidade de sucesso: "
        f"{resultado.probabilidade_sucesso:.0%}"
    )

    print(f"Cupom resgatado: {resultado.cupom_resgatado}")
    print(f"Fraude detectada: {resultado.fraude_detectada}")

    print(f"Custo operacional: {resultado.custo_operacional}")
    print(f"Custo de fricção: {resultado.custo_friccao}")
    print(f"Custo da defesa: {resultado.custo_sistema}")

    print(f"Perda por fraude: {resultado.perda_por_fraude}")

    print(f"Utilidade fraudador: {resultado.utilidade_fraudador}")
    print(f"Utilidade defensor: {resultado.utilidade_defensor}")


def imprimir_resumo(resumo: dict):
    """Apresenta os indicadores consolidados."""

    print("\n=== RESULTADO FINAL ===")

    print(f"Total de rodadas: {resumo['total_rodadas']}")
    print(f"Fraudes bem-sucedidas: {resumo['fraudes_bem_sucedidas']}")
    print(f"Fraudes bloqueadas: {resumo['fraudes_bloqueadas']}")

    print("\nCustos do sistema:")
    print(f"Custo operacional: {resumo['custo_operacional']}")
    print(f"Custo de fricção: {resumo['custo_friccao']}")
    print(f"Custo das defesas: {resumo['custo_defesas']}")
    print(f"Perdas por fraude: {resumo['perdas_fraude']}")

    print("\nResultados econômicos:")
    print(f"Benefício fraudador: {resumo['beneficio_fraudador']}")
    print(f"Benefício defensor: {resumo['beneficio_defensor']}")
    print(f"Utilidade fraudador: {resumo['utilidade_fraudador']}")
    print(f"Utilidade defensor: {resumo['utilidade_defensor']}")


def executar_simulacao(
    ambiente: Ambiente,
    fraudador: Agente,
    defensor: Agente,
    total_rodadas: int = 10,
    exibir: bool = True,
) -> dict:
    """
    Coordena a interação entre os agentes e o ambiente.

    Fluxo:
    1. Agentes observam o histórico.
    2. Agentes escolhem suas ações.
    3. Ambiente executa a interação.
    4. Resultado é registrado.
    5. Próxima rodada utiliza o histórico atualizado.

    Reutilizar o ambiente acrescenta rodadas com novas contas.
    O resumo inclui todo o histórico acumulado do ambiente.
    """

    if total_rodadas < 1:
        raise ValueError("O número de rodadas deve ser maior que zero.")

    if exibir:
        print("=== SISTEMA ADVERSARIAL ===")

    for _ in range(total_rodadas):

        rodada = len(ambiente.historico) + 1

        # Os dois agentes recebem o histórico anterior à rodada.
        historico = ambiente.historico

        # Cada agente escolhe sua estratégia.
        ataque = fraudador.escolher_acao(historico)
        defesa = defensor.escolher_acao(historico)

        # O ambiente executa as estratégias escolhidas.
        resultado = ambiente.processar(
            ataque=ataque,
            defesa=defesa,
        )

        if exibir:
            imprimir_rodada(
                rodada,
                ataque,
                defesa,
                fraudador,
                defensor,
                resultado,
            )

    # Consolida todos os resultados.
    resumo = calcular_resumo(ambiente.historico)

    if exibir:
        imprimir_resumo(resumo)

    return resumo


def main():
    """Executa uma demonstração com os agentes baseados em regras."""

    from agents import AgenteFraudador, AgenteDefensor

    ambiente = Ambiente(seed=42)

    fraudador = AgenteFraudador()
    defensor = AgenteDefensor()

    executar_simulacao(
        ambiente=ambiente,
        fraudador=fraudador,
        defensor=defensor,
        total_rodadas=10,
    )


if __name__ == "__main__":
    main()
