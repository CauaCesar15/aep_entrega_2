"""
Definição da Persona do Usuário Idoso (Sr. José) para o Agente 4.

Baseado nas diretrizes de usabilidade para seniores (Nielsen, W3C, WCAG 2.2).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SeniorPersona:
    """
    Persona de validação de acessibilidade 60+.
    Representa o empreendedor sênior com menor familiaridade digital.
    """

    nome: str = "Sr. José da Silva"
    idade: int = 68
    ocupacao: str = "Marceneiro e Empreendedor MEI"
    nivel_tecnologico: str = "Básico (usa WhatsApp com apoio e precisa de telas claras)"

    # Parâmetros de simulação comportamental
    zoom_tela: float = 2.0  # 200% de ampliação (WCAG 1.4.4)
    preferencia_teclado: bool = True  # Prefere Tab/Enter para evitar tremores no mouse
    fator_desaceleracao_cognitiva: float = 2.5  # Pausas 2.5x maiores para leitura e interpretação
    tolerancia_frustracao_segundos: float = 90.0  # Tempo máximo antes de desistir ou pedir socorro

    # Metas de recuperação por tipo de erro (Critérios da Entrega 2)
    meta_tempo_recuperacao_tecnico_s: float = 60.0  # <= 60s
    meta_tempo_recuperacao_financeiro_s: float = 90.0  # <= 90s


PERSONA_PADRAO = SeniorPersona()
