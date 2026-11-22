"""Agente fraudador para o jogo acadêmico, compatível com runner.Agente."""

from __future__ import annotations

import json
import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DecisaoFraudador(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    estrategia: Literal["A1", "A2"]
    motivo: str = Field(min_length=1, description="Justificativa curta baseada nas observações.")


INSTRUCOES = """
Você é o Fraudador de uma simulação acadêmica de cupom de primeira compra.
Seu objetivo é maximizar sua utilidade acumulada (benefício recebido).
Suas únicas ações são A1 (tentativa simples) e A2 (tentativa alternativa).
Não realiza operações reais: apenas escolhe um desses rótulos.
Cada rodada representa uma nova conta fictícia do mesmo fraudador.
Você observa suas ações, resgates e utilidades anteriores, mas não a defesa
atual, as probabilidades internas ou as regras privadas do adversário.
Sem observações, explore A1 para obter uma referência inicial.
Nas próximas decisões, compare os resultados observados das estratégias.
Considere explorar uma alternativa após bloqueios e manter ações bem-sucedidas;
uma tentativa isolada não prova que uma estratégia sempre funciona ou falha.
Decida a partir dos resultados, nunca do número da rodada ou de uma sequência
predefinida. Não invente observações. Explique brevemente a evidência que levou
a manter ou alterar a ação. O ambiente determina o sucesso, não você.
Retorne a estratégia e o motivo no esquema solicitado.
"""


class AgenteFraudadorAgno:
    def __init__(self, modelo: str | None = None, *, agente=None):
        """`agente` permite testar com um substituto de Agent.run, sem API."""
        self.estrategia_atual = None
        self.motivo = "Nenhuma decisão realizada."
        self.decisoes = []
        self.modelo = modelo or os.getenv("FRAUDADOR_MODEL", "claude-haiku-4-5-20251001")
        if agente is None:
            if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
                raise ValueError("Defina ANTHROPIC_API_KEY para executar o fraudador com IA.")
            from agno.agent import Agent
            from agno.models.anthropic import Claude

            agente = Agent(
                name="Fraudador de cupom",
                model=Claude(
                    id=self.modelo,
                    max_tokens=1024,
                ),
                instructions=INSTRUCOES,
                output_schema=DecisaoFraudador,
                markdown=False,
                telemetry=False,
            )
        self.agente = agente

    def escolher_acao(self, historico: list[dict]) -> str:
        # Projeção explícita: não fornece a verdade interna do ambiente ao LLM.
        observacoes = [
            {
                "rodada": rodada["rodada"],
                "ataque": rodada["ataque"],
                "cupom_resgatado": rodada["resultado"].cupom_resgatado,
                "utilidade_fraudador": rodada["resultado"].utilidade_fraudador,
            }
            for rodada in historico
        ]
        entrada = json.dumps({"observacoes": observacoes}, ensure_ascii=False)
        resposta = self.agente.run(entrada)
        conteudo = resposta.content
        # Valida inclusive respostas de provedores que retornem JSON em texto.
        if isinstance(conteudo, str):
            decisao = DecisaoFraudador.model_validate_json(conteudo)
        else:
            decisao = DecisaoFraudador.model_validate(conteudo)
        anterior = self.estrategia_atual
        self.estrategia_atual = decisao.estrategia
        self.motivo = decisao.motivo
        self.decisoes.append({
            "rodada": len(historico) + 1,
            **decisao.model_dump(),
            "estrategia_anterior": anterior,
            "mudou_estrategia": anterior is not None and anterior != decisao.estrategia,
            "observacoes": observacoes,
        })
        return decisao.estrategia
