class AgenteFraudador:
    def __init__(self):
        self.estrategia_atual = "A1"
        self.motivo = "Inicia com ataque simples."

    def escolher_acao(self, historico):
        if historico:
            ultima_rodada = historico[-1]
            resultado = ultima_rodada["resultado"]

            if not resultado.cupom_resgatado:
                self.estrategia_atual = "A2"
                self.motivo = (
                    "A tentativa anterior foi bloqueada. "
                    "Adota uma estratégia adaptativa."
                )
            else:
                self.motivo = (
                    "A tentativa anterior teve sucesso. "
                    "Mantém a estratégia atual."
                )

        return self.estrategia_atual


class AgenteDefensor:
    def __init__(self):
        self.estrategia_atual = "B1"
        self.motivo = "Inicia com defesa básica."

    def escolher_acao(self, historico):
        if not historico:
            return self.estrategia_atual

        ultima_rodada = historico[-1]
        resultado = ultima_rodada["resultado"]

        # Se uma fraude passou, reforça a defesa.
        if resultado.cupom_resgatado:
            self.estrategia_atual = "B2"
            self.motivo = (
                "Uma fraude passou pela defesa. "
                "Ativa a validação reforçada."
            )

        # Se duas tentativas consecutivas foram bloqueadas
        # com B2, reduz a defesa para economizar recursos.
        elif self.estrategia_atual == "B2":
            ultimas_rodadas = historico[-2:]

            duas_bloqueadas = (
                len(ultimas_rodadas) == 2
                and all(
                    not rodada["resultado"].cupom_resgatado
                    and rodada["defesa"] == "B2"
                    for rodada in ultimas_rodadas
                )
            )

            if duas_bloqueadas:
                self.estrategia_atual = "B1"
                self.motivo = (
                    "Duas tentativas foram bloqueadas. "
                    "Reduz a defesa para diminuir custos."
                )
            else:
                self.motivo = (
                    "Mantém a defesa reforçada."
                )

        else:
            self.motivo = (
                "Mantém a defesa básica."
            )

        return self.estrategia_atual