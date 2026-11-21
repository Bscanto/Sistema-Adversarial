
"""Agente defensor com Agno para o jogo acadêmico."""

from __future__ import annotations

import json
import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DecisaoDefensor(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    estrategia: Literal["B1", "B2"]

    motivo: str = Field(
        min_length=1,
        description="Justificativa curta baseada nas observações."
    )


INSTRUCOES = """
Você é o Defensor de uma simulação acadêmica de cupom de primeira compra.

Seu objetivo é maximizar a utilidade acumulada do defensor,
impedindo fraudes e controlando os custos da proteção.

Suas únicas ações são:
- B1: defesa básica, com menor custo operacional e menor fricção.
- B2: defesa reforçada, com maior capacidade de proteção,
  mas com custos operacionais e de fricção maiores.

Você recebe o histórico das rodadas anteriores, incluindo:
as estratégias de ataque e defesa, os resultados observados,
os custos e a utilidade obtida pelo defensor.

Você NÃO recebe as probabilidades internas do ambiente
nem suas regras privadas.

REGRAS DE DECISÃO:

1. Sem observações anteriores, comece com B1 para estabelecer
   uma referência inicial.

2. Analise os resultados das defesas anteriores.

3. Se fraudes estiverem passando, considere utilizar B2
   para aumentar a proteção.

4. Considere os custos operacionais e de fricção de B2.
   Uma defesa mais forte não é necessariamente mais eficiente.

5. Se B2 não estiver proporcionando resultados que justifiquem
   seus custos, considere retornar para B1.

6. Compare os resultados observados das estratégias,
   considerando também o tipo de ataque enfrentado.

7. Não reaja exageradamente a uma única tentativa.
   Resultados isolados não comprovam que uma estratégia
   sempre funciona ou falha.

8. Não siga uma sequência fixa de rodadas.
   Suas decisões devem depender das observações disponíveis.

9. Não invente informações ou resultados.

10. Explique brevemente a evidência que fundamentou sua decisão.

O ambiente determina o resultado da interação, não você.

Retorne a estratégia e o motivo no esquema solicitado.
"""


class AgenteDefensorAgno:

    def __init__(self, modelo: str | None = None, *, agente=None):

        """agente permite testar com um substituto de Agent.run."""

        self.estrategia_atual = None
        self.motivo = "Nenhuma decisão realizada."
        self.decisoes = []

        if agente is None:

            if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
                raise ValueError(
                    "Defina ANTHROPIC_API_KEY para executar "
                    "o defensor com IA."
                )

            from agno.agent import Agent
            from agno.models.anthropic import Claude

            agente = Agent(
                name="Defensor de cupom",
                model=Claude(
                    id=modelo or os.getenv(
                        "DEFENSOR_MODEL",
                        "claude-haiku-4-5-20251001"
                    ),
                    max_tokens=1024,
                ),
                instructions=INSTRUCOES,
                output_schema=DecisaoDefensor,
                markdown=False,
                telemetry=False,
            )

        self.agente = agente

    def escolher_acao(self, historico: list[dict]) -> str:

        # Projeta somente as informações observáveis pelo defensor.
        observacoes = []

        for rodada in historico:

            resultado = rodada["resultado"]

            observacoes.append({
                "rodada": rodada["rodada"],
                "ataque": rodada["ataque"],
                "defesa": rodada["defesa"],
                "cupom_resgatado": resultado.cupom_resgatado,
                "fraude_detectada": resultado.fraude_detectada,
                "custo_operacional": resultado.custo_operacional,
                "custo_friccao": resultado.custo_friccao,
                "custo_sistema": resultado.custo_sistema,
                "beneficio_defensor": resultado.beneficio_defensor,
                "utilidade_defensor": resultado.utilidade_defensor,
            })

        entrada = json.dumps(
            {"observacoes": observacoes},
            ensure_ascii=False
        )

        resposta = self.agente.run(entrada)
        conteudo = resposta.content

        # Valida a resposta do modelo.
        if isinstance(conteudo, str):
            decisao = DecisaoDefensor.model_validate_json(conteudo)
        else:
            decisao = DecisaoDefensor.model_validate(conteudo)

        anterior = self.estrategia_atual

        self.estrategia_atual = decisao.estrategia
        self.motivo = decisao.motivo

        self.decisoes.append({
            "rodada": len(historico) + 1,
            **decisao.model_dump(),
            "estrategia_anterior": anterior,
            "mudou_estrategia": (
                anterior is not None
                and anterior != decisao.estrategia
            ),
            "observacoes": observacoes,
        })

        return decisao.estrategia
