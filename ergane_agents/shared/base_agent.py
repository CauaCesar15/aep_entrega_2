"""
Classe base abstrata para todos os agentes do pipeline Ergane.

Define a interface comum e métodos utilitários compartilhados.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ergane_agents.shared.event_bus import EventBus, EventType
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import AgentResult, StatusAgente


class BaseAgent(ABC):
    """
    Classe base para agentes do sistema Ergane.

    Cada agente concreto deve implementar :meth:`execute`,
    :meth:`validate_input` e :meth:`get_required_inputs`.

    Parâmetros
    ----------
    name : str
        Nome identificador do agente.
    event_bus : EventBus
        Barramento de eventos compartilhado.
    llm_client : LLMClient | None
        Cliente LLM (pode ser ``None`` se o agente não precisar de LLM).
    """

    def __init__(
        self,
        name: str,
        event_bus: EventBus,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.name = name
        self.event_bus = event_bus
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"ergane.agent.{name}")

    # ------------------------------------------------------------------
    # Métodos abstratos — devem ser implementados por cada agente
    # ------------------------------------------------------------------

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> AgentResult:
        """Executa a lógica principal do agente e retorna o resultado."""
        ...

    @abstractmethod
    def validate_input(self, context: dict[str, Any]) -> bool:
        """Valida se o contexto contém as entradas necessárias."""
        ...

    @abstractmethod
    def get_required_inputs(self) -> list[str]:
        """Retorna a lista de chaves obrigatórias esperadas no contexto."""
        ...

    # ------------------------------------------------------------------
    # Métodos concretos — utilitários compartilhados
    # ------------------------------------------------------------------

    def log_info(self, msg: str, *args: Any) -> None:
        """Registra mensagem informativa com o logger do agente."""
        self.logger.info(msg, *args)

    def log_error(self, msg: str, *args: Any) -> None:
        """Registra mensagem de erro com o logger do agente."""
        self.logger.error(msg, *args)

    def publish_result(self, data: dict[str, Any], status: StatusAgente = StatusAgente.SUCESSO) -> AgentResult:
        """Cria e retorna um :class:`AgentResult` preenchido."""
        result = AgentResult(
            agent_name=self.name,
            timestamp=datetime.now().isoformat(),
            data=data,
            status=status,
        )
        self.log_info("Resultado publicado: status=%s", status.value)
        return result

    def emit_event(self, event_type: EventType, data: Any = None) -> None:
        """Publica um evento no barramento compartilhado."""
        self.event_bus.publish(event_type, data)
        self.log_info("Evento emitido: %s", event_type.value)
