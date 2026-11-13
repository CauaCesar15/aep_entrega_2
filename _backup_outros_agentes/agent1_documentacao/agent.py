"""
Agente 1 — Agente de Documentação de Software.

Arquitetura: Pipe-and-filter:
  Código / Docs → Extração AST → Cálculo de Métricas → Guia 60+ → JSON + Evento
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ergane_agents.agent1_documentacao.extractors import ExtractorFactory, SourceAdapter
from ergane_agents.agent1_documentacao.guide_generator import GuiaErrosIdoso
from ergane_agents.agent1_documentacao.metrics import (
    avaliar_clareza_nomes,
    calcular_cobertura_docstrings,
    calcular_indice_flesch,
    calcular_tamanho_medio_frases,
    detectar_jargao,
)
from ergane_agents.shared.base_agent import BaseAgent
from ergane_agents.shared.event_bus import EventBus, EventType
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import AgentResult, DocMetrics, StatusAgente


class AgenteDocumentacao(BaseAgent):
    """
    Agente de Documentação de Software do Ergane.

    Calcula métricas de qualidade de documentação e gera o Guia de Erros
    para idosos, enviando o evento METRICS_DOC_READY ao barramento.
    """

    def __init__(
        self,
        event_bus: EventBus,
        llm_client: LLMClient | None = None,
    ) -> None:
        super().__init__(
            name="AgenteDocumentacao",
            event_bus=event_bus,
            llm_client=llm_client,
        )
        self.guia_generator = GuiaErrosIdoso()

    def get_required_inputs(self) -> list[str]:
        """Chaves necessárias no contexto de execução."""
        return ["codigo"]

    def validate_input(self, context: dict[str, Any]) -> bool:
        """Verifica se há código ou caminho de arquivo fornecido."""
        return bool(context.get("codigo") or context.get("arquivo"))

    def execute(self, context: dict[str, Any]) -> AgentResult:
        """
        Executa o pipeline Pipe-and-Filter:
        1. Adaptação e extração via AST
        2. Cálculo das métricas determinísticas (cobertura, flesch, frases, jargões, nomes)
        3. Geração do Guia de Erros 60+ (com apoio opcional do Ollama se disponível)
        4. Publicação do evento METRICS_DOC_READY e retorno de AgentResult
        """
        if not self.validate_input(context):
            return self.publish_result(
                data={"erro": "Entrada inválida. Necessário 'codigo' ou 'arquivo'."},
                status=StatusAgente.FALHA,
            )

        entrada = context.get("arquivo") or context.get("codigo")
        nome_arquivo, codigo_texto = SourceAdapter.adapt(entrada)
        self.log_info("Processando documentação de: %s", nome_arquivo)

        # 1. Extração AST
        extractor = ExtractorFactory.create("docstring")
        ast_data = extractor.extract(codigo_texto)

        # 2. Cálculo das métricas
        cobertura = calcular_cobertura_docstrings(ast_data)

        # Junta todas as docstrings para análise textual
        docstrings_texto = " ".join(ast_data.get("docstrings", []))
        if not docstrings_texto.strip():
            docstrings_texto = codigo_texto  # Avalia comentários gerais caso não haja docstrings

        indice_flesch = calcular_indice_flesch(docstrings_texto)
        tamanho_frases = calcular_tamanho_medio_frases(docstrings_texto)
        jargoes = detectar_jargao(docstrings_texto)
        clareza_nomes = avaliar_clareza_nomes(ast_data.get("nomes", []))

        # Objeto de métricas
        doc_metrics = DocMetrics(
            arquivo=nome_arquivo,
            cobertura_docstrings=cobertura,
            indice_flesch=indice_flesch,
            tamanho_medio_frases=tamanho_frases,
            jargoes_detectados=jargoes,
            clareza_nomes=clareza_nomes,
        )

        # 3. Geração do Guia de Erros
        guia_markdown = self.guia_generator.gerar_guia(context)

        # Opcional: Se Ollama estiver ativo, pode tentar enriquecer o guia
        if self.llm_client and self.llm_client.is_available():
            prompt_resumo = (
                f"Resuma em um parágrafo acolhedor para um idoso com baixa afinidade digital "
                f"a importância de ler mensagens de aviso com calma. Use linguagem simples."
            )
            msg_llm = self.llm_client.generate(prompt_resumo)
            if msg_llm:
                guia_markdown = f"{msg_llm.strip()}\n\n{guia_markdown}"

        payload = {
            "arquivo": nome_arquivo,
            "metricas": {
                "cobertura_docstrings": doc_metrics.cobertura_docstrings,
                "indice_flesch": doc_metrics.indice_flesch,
                "tamanho_medio_frases": doc_metrics.tamanho_medio_frases,
                "jargoes_detectados": doc_metrics.jargoes_detectados,
                "clareza_nomes": doc_metrics.clareza_nomes,
            },
            "guia_erros_60plus_md": guia_markdown,
            "total_erros_catalogados": len(self.guia_generator.CATALOGO_ERROS_60PLUS),
        }

        # 4. Emissão de evento no barramento (Observer)
        self.emit_event(EventType.METRICS_DOC_READY, payload)

        return self.publish_result(data=payload, status=StatusAgente.SUCESSO)
