"""
Barramento de eventos — padrão Observer thread-safe.

Permite que os agentes publiquem e assinem eventos de forma desacoplada.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos de evento do pipeline
# ---------------------------------------------------------------------------

class EventType(str, Enum):
    """Eventos emitidos durante a execução do pipeline de agentes."""

    METRICS_DOC_READY = "METRICS_DOC_READY"
    METRICS_STRUCT_READY = "METRICS_STRUCT_READY"
    PREDICTION_READY = "PREDICTION_READY"
    VALIDATION_READY = "VALIDATION_READY"
    REPORT_READY = "REPORT_READY"


# Tipo do callback: recebe (event_type, data)
Callback = Callable[[EventType, Any], None]


# ---------------------------------------------------------------------------
# EventBus
# ---------------------------------------------------------------------------

class EventBus:
    """
    Barramento de eventos com suporte a múltiplos assinantes por tipo.

    Thread-safe: utiliza ``threading.Lock`` para proteger o dicionário
    interno de assinantes.
    """

    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[Callback]] = defaultdict(list)
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def subscribe(self, event_type: EventType, callback: Callback) -> None:
        """Registra *callback* para ser chamado quando *event_type* for publicado."""
        with self._lock:
            self._subscribers[event_type].append(callback)
        logger.debug(
            "Assinante registrado para '%s': %s",
            event_type.value,
            getattr(callback, "__name__", repr(callback)),
        )

    def publish(self, event_type: EventType, data: Any = None) -> None:
        """Publica *event_type* e notifica todos os assinantes registrados."""
        with self._lock:
            callbacks = list(self._subscribers.get(event_type, []))

        logger.info(
            "Evento '%s' publicado — %d assinante(s).",
            event_type.value,
            len(callbacks),
        )

        for cb in callbacks:
            try:
                cb(event_type, data)
            except Exception:
                logger.exception(
                    "Erro ao notificar assinante '%s' do evento '%s'.",
                    getattr(cb, "__name__", repr(cb)),
                    event_type.value,
                )

    def list_subscribers(self) -> dict[str, list[str]]:
        """Retorna um dicionário legível de evento → lista de nomes de callbacks."""
        with self._lock:
            return {
                evt.value: [
                    getattr(cb, "__name__", repr(cb)) for cb in cbs
                ]
                for evt, cbs in self._subscribers.items()
            }
