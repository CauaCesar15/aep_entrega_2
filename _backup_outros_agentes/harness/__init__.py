"""
Harness de Execução, Orquestração e Validação do Ecossistema Ergane.

Fornece o pipeline de orquestração dos 5 agentes e o harness de testes
automatizados para verificação dos critérios de aceitação da Entrega 2.
"""

from ergane_agents.harness.orchestrator import ErganePipelineOrchestrator
from ergane_agents.harness.test_harness import ErganeTestHarness

__all__ = ["ErganePipelineOrchestrator", "ErganeTestHarness"]
