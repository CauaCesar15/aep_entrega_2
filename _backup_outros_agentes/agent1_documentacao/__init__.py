"""
Agente 1 — Agente de Documentação de Software.

Responsável por extrair métricas de documentação (cobertura de docstrings,
índice Flesch, tamanho médio de frases, detecção de jargão técnico e clareza
de nomes) e gerar o Guia de Erros em linguagem simples para usuários 60+.
"""

from ergane_agents.agent1_documentacao.agent import AgenteDocumentacao

__all__ = ["AgenteDocumentacao"]
