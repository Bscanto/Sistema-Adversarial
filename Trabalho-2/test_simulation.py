from simulation import Ambiente

ambiente = Ambiente(seed=42)

combinacoes = [
    ("A1", "B1"),
    ("A1", "B2"),
    ("A2", "B1"),
    ("A2", "B2"),
]

for ataque, defesa in combinacoes:
    sucessos = 0
    rodadas = 100

    for _ in range(rodadas):
        resultado = ambiente.processar(ataque, defesa)

        if resultado.cupom_resgatado:
            sucessos += 1

    percentual = sucessos / rodadas * 100

    print(
        f"{ataque} vs {defesa}: "
        f"{sucessos}/{rodadas} sucessos "
        f"({percentual:.1f}%)"
    )

print(f"\nTotal de rodadas: {len(ambiente.historico)}")