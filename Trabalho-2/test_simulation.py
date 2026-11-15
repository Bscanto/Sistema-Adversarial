from simulation import Ambiente
from agents import AgenteFraudador, AgenteDefensor


ambiente = Ambiente(seed=42)

fraudador = AgenteFraudador()
defensor = AgenteDefensor()

TOTAL_RODADAS = 10

print("=== SISTEMA ADVERSARIAL ===")

for rodada in range(1, TOTAL_RODADAS + 1):

    ataque = fraudador.escolher_acao(ambiente.historico)
    defesa = defensor.escolher_acao(ambiente.historico)

    resultado = ambiente.processar(
        ataque,
        defesa,
        id_cliente=f"CPF-{rodada:03d}"
    )

    print(f"\n--- Rodada {rodada} ---")

    print(f"Fraudador: {ataque}")
    print(f"Motivo: {fraudador.motivo}")

    print(f"Defensor: {defesa}")
    print(f"Motivo: {defensor.motivo}")

    print(f"Probabilidade de sucesso: {resultado.probabilidade_sucesso:.0%}")
    print(f"Cupom resgatado: {resultado.cupom_resgatado}")
    print(f"Fraude detectada: {resultado.fraude_detectada}")

    print(f"Custo operacional: {resultado.custo_operacional}")
    print(f"Custo de fricção: {resultado.custo_friccao}")
    print(f"Custo da defesa: {resultado.custo_sistema}")

    print(f"Perda por fraude: {resultado.perda_por_fraude}")
    print(f"Utilidade fraudador: {resultado.utilidade_fraudador}")
    print(f"Utilidade defensor: {resultado.utilidade_defensor}")


# Consolidação dos resultados

historico = ambiente.historico

sucessos = sum(
    r["resultado"].cupom_resgatado
    for r in historico
)

bloqueios = sum(
    r["resultado"].fraude_detectada
    for r in historico
)

custo_operacional = sum(
    r["resultado"].custo_operacional
    for r in historico
)

custo_friccao = sum(
    r["resultado"].custo_friccao
    for r in historico
)

custo_defesas = sum(
    r["resultado"].custo_sistema
    for r in historico
)

perdas_fraude = sum(
    r["resultado"].perda_por_fraude
    for r in historico
)

beneficio_fraudador = sum(
    r["resultado"].beneficio_fraudador
    for r in historico
)

beneficio_defensor = sum(
    r["resultado"].beneficio_defensor
    for r in historico
)

utilidade_fraudador = sum(
    r["resultado"].utilidade_fraudador
    for r in historico
)

utilidade_defensor = sum(
    r["resultado"].utilidade_defensor
    for r in historico
)

print("\n=== RESULTADO FINAL ===")

print(f"Total de rodadas: {len(historico)}")
print(f"Fraudes bem-sucedidas: {sucessos}")
print(f"Fraudes bloqueadas: {bloqueios}")

print("\nCustos do sistema:")
print(f"Custo operacional: {custo_operacional}")
print(f"Custo de fricção: {custo_friccao}")
print(f"Custo das defesas: {custo_defesas}")
print(f"Perdas por fraude: {perdas_fraude}")

print("\nResultados econômicos:")
print(f"Benefício fraudador: {beneficio_fraudador}")
print(f"Benefício defensor: {beneficio_defensor}")
print(f"Utilidade fraudador: {utilidade_fraudador}")
print(f"Utilidade defensor: {utilidade_defensor}")