"""
Agente 2 — Agente de Validação de Código.

Responsável pela análise estática de código e extração de métricas estruturais
voltadas à acessibilidade e qualidade (complexidade ciclomática, tags semânticas,
consistência de nomenclatura, mensagens de erro e LOC).
"""

from ergane_agents.agent2_validacao.agent import AgenteValidacao

__all__ = ["AgenteValidacao"]
