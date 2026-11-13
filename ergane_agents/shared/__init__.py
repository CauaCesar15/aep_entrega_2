"""
Módulo compartilhado — modelos de dados, barramento de eventos,
cliente LLM, classe base de agente e utilitários.
"""

from ergane_agents.shared.models import (
    AgentResult,
    BarreiraPreditiva,
    DocMetrics,
    RelatorioGestao,
    ResultadoTeste,
    StructuralMetrics,
)
from ergane_agents.shared.event_bus import EventBus
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.base_agent import BaseAgent

__all__ = [
    "AgentResult",
    "BarreiraPreditiva",
    "DocMetrics",
    "RelatorioGestao",
    "ResultadoTeste",
    "StructuralMetrics",
    "EventBus",
    "LLMClient",
    "BaseAgent",
]
