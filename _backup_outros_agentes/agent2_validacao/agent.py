"""
Agente 2 — Agente de Validação de Código.

Arquitetura Pipe-and-filter:
  Código → Sintaxe → Qualidade → Segurança → Mensagens de Erro → Métricas Estruturais JSON
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ergane_agents.agent2_validacao.structural_metrics import (
    avaliar_consistencia_nomes,
    contar_loc,
    detectar_mensagens_erro_problematicas,
    extrair_complexidade_ciclomatica,
    verificar_tags_semanticas,
)
from ergane_agents.agent2_validacao.validators import ValidatorFactory
from ergane_agents.shared.base_agent import BaseAgent
from ergane_agents.shared.event_bus import EventBus, EventType
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import AgentResult, StatusAgente, StructuralMetrics


class AgenteValidacao(BaseAgent):
    """
    Agente de Validação de Código do Ergane.

    Executa análise estática (sintaxe, qualidade, segurança) e extrai métricas
    estruturais relevantes para a predição de barreiras 60+.
    """

    def __init__(
        self,
        event_bus: EventBus,
        llm_client: LLMClient | None = None,
    ) -> None:
        super().__init__(
            name="AgenteValidacao",
            event_bus=event_bus,
            llm_client=llm_client,
        )
        self.validator_suite = ValidatorFactory.create_default_suite()

    def get_required_inputs(self) -> list[str]:
        return ["codigo"]

    def validate_input(self, context: dict[str, Any]) -> bool:
        return bool(context.get("codigo") or context.get("arquivo"))

    def execute(self, context: dict[str, Any]) -> AgentResult:
        """
        Executa o pipeline Pipe-and-Filter:
        1. Carrega código
        2. Executa suíte de validadores (Composite + Strategy)
        3. Extrai métricas estruturais (complexidade, tags semânticas, consistência, erros, loc)
        4. Emite METRICS_STRUCT_READY e retorna AgentResult
        """
        tempo_inicio = time.time()

        if not self.validate_input(context):
            return self.publish_result(
                data={"erro": "Entrada inválida. Necessário 'codigo' ou 'arquivo'."},
                status=StatusAgente.FALHA,
            )

        nome_arquivo = "inline_code.py"
        codigo_texto = ""

        if context.get("arquivo"):
            path = Path(context["arquivo"])
            nome_arquivo = path.name
            if path.exists() and path.is_file():
                codigo_texto = path.read_text(encoding="utf-8", errors="ignore")
            else:
                codigo_texto = str(context.get("codigo", ""))
        else:
            codigo_texto = str(context.get("codigo", ""))
            nome_arquivo = context.get("nome_arquivo", "modulo.py")

        self.log_info("Iniciando validação de código para: %s", nome_arquivo)

        # 1. Execução dos validadores via Composite
        relatorio_validacao = self.validator_suite.validate(codigo_texto)

        # 2. Extração das métricas estruturais
        cc_info = extrair_complexidade_ciclomatica(codigo_texto)
        tags_info = verificar_tags_semanticas(codigo_texto)
        consistencia = avaliar_consistencia_nomes(codigo_texto)
        erros_problematicos = detectar_mensagens_erro_problematicas(codigo_texto)
        loc = contar_loc(codigo_texto)

        tempo_gasto_s = round(time.time() - tempo_inicio, 4)

        structural_metrics = StructuralMetrics(
            arquivo=nome_arquivo,
            complexidade_ciclomatica=cc_info.get("media", 1.0),
            tags_semanticas=tags_info.get("tags_semanticas_encontradas", []),
            consistencia_nomes=consistencia,
            mensagens_erro_problematicas=erros_problematicos,
            loc=loc,
        )

        payload = {
            "arquivo": nome_arquivo,
            "tempo_analise_segundos": tempo_gasto_s,
            "conformidade_tempo": tempo_gasto_s <= 30.0,
            "metricas_estruturais": {
                "complexidade_media": structural_metrics.complexidade_ciclomatica,
                "complexidade_maxima": cc_info.get("maxima", 1.0),
                "detalhe_funcoes_cc": cc_info.get("funcoes", []),
                "tags_semanticas": structural_metrics.tags_semanticas,
                "indice_semantico": tags_info.get("indice_semantico", 0.0),
                "consistencia_nomes": structural_metrics.consistencia_nomes,
                "mensagens_erro_problematicas": structural_metrics.mensagens_erro_problematicas,
                "loc": structural_metrics.loc,
            },
            "validacao_estatica": relatorio_validacao,
        }

        # 3. Emite evento no barramento (Observer)
        self.emit_event(EventType.METRICS_STRUCT_READY, payload)

        return self.publish_result(data=payload, status=StatusAgente.SUCESSO)
