
from simulation import Ambiente


ambiente = Ambiente()

resultado = ambiente.processar("A2", "B2")

print(resultado)
print(f"Rodadas registradas: {len(ambiente.historico)}")