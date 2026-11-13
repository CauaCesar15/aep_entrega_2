"""
Agente 3 — Agente de Acessibilidade Preditiva (Núcleo do Ergane).

Responsável por cruzar métricas de documentação (Agente 1) e métricas estruturais (Agente 2)
com as regras 60+ para prever barreiras de acessibilidade front-end nas 4 frentes:
percepção, operação, compreensão e fluxo.
"""

from ergane_agents.agent3_acessibilidade.agent import AgenteAcessibilidade

__all__ = ["AgenteAcessibilidade"]
