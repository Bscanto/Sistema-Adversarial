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

    resultado = ambiente.processar(ataque, defesa)

    print(f"\n--- Rodada {rodada} ---")

    print(f"Fraudador: {ataque}")
    print(f"Motivo: {fraudador.motivo}")

    print(f"Defensor: {defesa}")
    print(f"Motivo: {defensor.motivo}")

    print(f"Cupom resgatado: {resultado.cupom_resgatado}")
    print(f"Fraude detectada: {resultado.fraude_detectada}")
    print(f"Custo do sistema: {resultado.custo_sistema}")
    print(f"Benefício do fraudador: {resultado.beneficio_fraudador}")


# Resumo da simulação
sucessos = sum(
    rodada["resultado"].cupom_resgatado
    for rodada in ambiente.historico
)

deteccoes = sum(
    rodada["resultado"].fraude_detectada
    for rodada in ambiente.historico
)

custo_total = sum(
    rodada["resultado"].custo_sistema
    for rodada in ambiente.historico
)

beneficio_total = sum(
    rodada["resultado"].beneficio_fraudador
    for rodada in ambiente.historico
)

print("\n=== RESULTADO FINAL ===")
print(f"Total de rodadas: {TOTAL_RODADAS}")
print(f"Fraudes bem-sucedidas: {sucessos}")
print(f"Fraudes bloqueadas: {deteccoes}")
print(f"Custo total do sistema: {custo_total}")
print(f"Benefício total do fraudador: {beneficio_total}")