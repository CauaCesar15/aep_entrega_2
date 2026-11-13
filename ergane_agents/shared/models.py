"""
Modelos de dados do sistema Ergane.

Utiliza dataclasses do Python 3.10+ para representar métricas,
barreiras preditivas, resultados de testes e relatórios de gestão.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums auxiliares
# ---------------------------------------------------------------------------

class TipoBarreira(str, Enum):
    """Tipos de barreira de acessibilidade para idosos."""

    PERCEPCAO = "percepção"
    OPERACAO = "operação"
    COMPREENSAO = "compreensão"
    FLUXO = "fluxo"


class Severidade(str, Enum):
    """Níveis de severidade de uma barreira."""

    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class StatusAgente(str, Enum):
    """Status de execução de um agente."""

    SUCESSO = "sucesso"
    FALHA = "falha"
    PARCIAL = "parcial"


# ---------------------------------------------------------------------------
# Métricas de documentação (por arquivo)
# ---------------------------------------------------------------------------

@dataclass
class DocMetrics:
    """Métricas de qualidade da documentação de um arquivo-fonte."""

    arquivo: str
    cobertura_docstrings: float
    indice_flesch: float
    tamanho_medio_frases: float
    jargoes_detectados: list[str] = field(default_factory=list)
    clareza_nomes: float = 0.0


# ---------------------------------------------------------------------------
# Métricas estruturais (por arquivo)
# ---------------------------------------------------------------------------

@dataclass
class StructuralMetrics:
    """Métricas estruturais de código de um arquivo-fonte."""

    arquivo: str
    complexidade_ciclomatica: float
    tags_semanticas: list[str] = field(default_factory=list)
    consistencia_nomes: float = 0.0
    mensagens_erro_problematicas: list[str] = field(default_factory=list)
    loc: int = 0


# ---------------------------------------------------------------------------
# Barreira preditiva
# ---------------------------------------------------------------------------

@dataclass
class BarreiraPreditiva:
    """Barreira de acessibilidade prevista para usuários 60+."""

    tipo: TipoBarreira
    severidade: Severidade
    arquivo: str
    descricao: str
    sugestao_correcao: str


# ---------------------------------------------------------------------------
# Resultado de teste
# ---------------------------------------------------------------------------

@dataclass
class ResultadoTeste:
    """Resultado de um caso de teste de validação."""

    caso: str
    tempo_recuperacao_s: float
    sucesso: bool
    barreira_validada: BarreiraPreditiva | None = None


# ---------------------------------------------------------------------------
# Relatório de gestão
# ---------------------------------------------------------------------------

@dataclass
class RelatorioGestao:
    """Relatório consolidado para a gestão do projeto."""

    velocity: float
    burndown: list[dict[str, Any]] = field(default_factory=list)
    issues_acessibilidade_risco: list[str] = field(default_factory=list)
    prioridades: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Resultado genérico de agente
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    """Resultado padronizado devolvido por qualquer agente do pipeline."""

    agent_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data: dict[str, Any] = field(default_factory=dict)
    status: StatusAgente = StatusAgente.SUCESSO
