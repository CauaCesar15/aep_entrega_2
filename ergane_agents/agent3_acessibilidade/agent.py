"""
Agente 3 — Agente de Acessibilidade Preditiva (Núcleo do Ecossistema Ergane).

Cruza métricas de documentação (Agente 1) e estruturais (Agente 2)
com as regras 60+ para prever barreiras de acessibilidade antes da renderização.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ergane_agents.agent3_acessibilidade.engine import AccessibilityEngine
from ergane_agents.shared.base_agent import BaseAgent
from ergane_agents.shared.event_bus import EventBus, EventType
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import AgentResult, BarreiraPreditiva, StatusAgente


class AgenteAcessibilidade(BaseAgent):
    """
    Agente 3 — Acessibilidade Preditiva.
    Materializa a ODS 10 no Ergane.
    """

    def __init__(
        self,
        event_bus: EventBus,
        llm_client: LLMClient | None = None,
        rules_path: str | None = None,
    ) -> None:
        super().__init__(
            name="AgenteAcessibilidade",
            event_bus=event_bus,
            llm_client=llm_client,
        )
        self.engine = AccessibilityEngine(rules_path=rules_path)

        # Cache interno de métricas para suportar orquestração orientada a eventos
        self.doc_metrics_cache: dict[str, Any] = {}
        self.struct_metrics_cache: dict[str, Any] = {}

        # Assina eventos dos Agentes 1 e 2 no barramento (Observer)
        self.event_bus.subscribe(EventType.METRICS_DOC_READY, self._on_doc_metrics_ready)
        self.event_bus.subscribe(EventType.METRICS_STRUCT_READY, self._on_struct_metrics_ready)

    def _on_doc_metrics_ready(self, event_type: EventType, data: Any) -> None:
        if isinstance(data, dict):
            self.doc_metrics_cache = data.get("metricas", data)
            self.log_info("Cache atualizado com métricas de documentação.")

    def _on_struct_metrics_ready(self, event_type: EventType, data: Any) -> None:
        if isinstance(data, dict):
            self.struct_metrics_cache = data.get("metricas_estruturais", data)
            self.log_info("Cache atualizado com métricas estruturais.")

    def get_required_inputs(self) -> list[str]:
        return ["doc_metrics", "struct_metrics"]

    def validate_input(self, context: dict[str, Any]) -> bool:
        # Suporta tanto o modo multi-agente (métricas prontas) quanto o modo autônomo (arquivo/código direto)
        has_doc = "doc_metrics" in context or bool(self.doc_metrics_cache)
        has_struct = "struct_metrics" in context or bool(self.struct_metrics_cache)
        has_direct = "arquivo" in context or "codigo" in context
        return (has_doc and has_struct) or has_direct

    def _extrair_metricas_autonomas(self, context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Extrai métricas diretamente quando o Agente 3 é executado de forma autônoma.
        100% autossuficiente e desacoplado de outros agentes.
        """
        from ergane_agents.agent3_acessibilidade.extractor import StandaloneCodeExtractor

        arquivo_path = context.get("arquivo")
        codigo = context.get("codigo", "")
        nome_arquivo = "modulo.py"

        if arquivo_path:
            p = Path(arquivo_path)
            nome_arquivo = p.name
            if p.exists() and not codigo:
                codigo = p.read_text(encoding="utf-8", errors="ignore")

        return StandaloneCodeExtractor.extract_metrics(codigo, nome_arquivo)

    def execute(self, context: dict[str, Any]) -> AgentResult:
        """
        Executa o cruzamento de regras 60+ e gera o relatório preditivo.
        Garante tempo de resposta <= 30s por arquivo.
        """
        tempo_inicio = time.time()

        doc_data = context.get("doc_metrics", self.doc_metrics_cache)
        struct_data = context.get("struct_metrics", self.struct_metrics_cache)

        # Se operando de forma autônoma (arquivo/código direto), extrai métricas
        if not doc_data or not struct_data:
            doc_data, struct_data = self._extrair_metricas_autonomas(context)

        arquivo = context.get("arquivo", struct_data.get("arquivo", "modulo.py"))
        self.log_info("Iniciando predição de acessibilidade 60+ para: %s", arquivo)

        # Executa predição nas 4 frentes
        barreiras: list[BarreiraPreditiva] = self.engine.run_prediction(doc_data, struct_data)

        # Enriquecimento opcional via LLM (Ollama) para linguagem natural
        if self.llm_client and self.llm_client.is_available() and barreiras:
            prompt = (
                f"Você é um especialista em acessibilidade para idosos na plataforma Ergane. "
                f"Foram previstas as seguintes barreiras: {[b.descricao for b in barreiras[:3]]}. "
                f"Escreva uma breve recomendação empática para os desenvolvedores em 2 frases."
            )
            sugestao_llm = self.llm_client.generate(prompt)
            if sugestao_llm:
                self.log_info("Recomendação LLM gerada: %s", sugestao_llm[:60])

        tempo_gasto_s = round(time.time() - tempo_inicio, 4)
        relatorio_md = self.engine.gerar_relatorio_markdown(arquivo, barreiras, {
            "doc": doc_data,
            "struct": struct_data,
        })

        # Serializa barreiras para payload
        barreiras_dict = [
            {
                "tipo": b.tipo.value,
                "severidade": b.severidade.value,
                "arquivo": b.arquivo,
                "descricao": b.descricao,
                "sugestao_correcao": b.sugestao_correcao,
            }
            for b in barreiras
        ]

        payload = {
            "arquivo": arquivo,
            "tempo_analise_segundos": tempo_gasto_s,
            "conformidade_tempo": tempo_gasto_s <= 30.0,
            "total_barreiras_previstas": len(barreiras),
            "barreiras": barreiras_dict,
            "relatorio_markdown": relatorio_md,
        }

        # Emite evento de predição concluída para os Agentes 4 e 5 (Observer)
        self.emit_event(EventType.PREDICTION_READY, payload)

        return self.publish_result(data=payload, status=StatusAgente.SUCESSO)
