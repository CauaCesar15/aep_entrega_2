"""
Geradores de relatórios ágeis para o Agente 5.

Padrões aplicados:
- Factory Method (GoF): ReportFactory cria relatórios especializados.
- MVC Adaptado: Model = tarefas/backlog; View = relatório Markdown.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ergane_agents.agent5_gestao.adapters import ProjectTask


class BaseReport(ABC):
    """Classe base para geradores de relatório (Padrão Factory Method / Strategy)."""

    @abstractmethod
    def render(self, dados: dict[str, Any]) -> str:
        """Renderiza o relatório em formato Markdown."""
        ...


class BurndownReport(BaseReport):
    """Relatório e gráfico textual de Burndown da Sprint."""

    def render(self, dados: dict[str, Any]) -> str:
        burndown = dados.get("burndown", [])
        linhas = [
            "### 📉 Gráfico de Burndown da Sprint",
            "| Dia | Esforço Ideal Restante (pts) | Esforço Real Restante (pts) | Status |",
            "| :---: | :---: | :---: | :---: |",
        ]
        for b in burndown:
            ideal = b["ideal_restante"]
            real = b["real_restante"]
            status = "🟢 No prazo" if real <= ideal else "🔴 Em atraso"
            linhas.append(f"| Dia {b['dia']} | {ideal} pts | {real} pts | {status} |")
        return "\n".join(linhas)


class VelocityReport(BaseReport):
    """Relatório de Velocity da Equipe."""

    def render(self, dados: dict[str, Any]) -> str:
        velocity = dados.get("velocity", 0.0)
        linhas = [
            "### ⚡ Velocity da Equipe (Scrum Adaptado)",
            f"- **Velocidade média:** **{velocity} story points / sprint**",
            "- **Capacidade da Equipe (3 integrantes):** ~24 pts por sprint de 1 semana",
            f"- **Taxa de entrega prevista:** {'Equilibrada' if velocity >= 18 else 'Abaixo da meta nominal'}",
        ]
        return "\n".join(linhas)


class AccessibilityPriorityReport(BaseReport):
    """Relatório de Priorização e Alertas 60+."""

    def render(self, dados: dict[str, Any]) -> str:
        tarefas: list[ProjectTask] = dados.get("tarefas_priorizadas", [])
        alertas: list[str] = dados.get("alertas", [])

        linhas = [
            "### 🎯 Backlog Priorizado (ODS 10 — Foco em Inclusão e Finanças)",
            "| Prioridade | ID | Categoria | Título | Pontos | Responsável | Status |",
            "| :---: | :---: | :---: | :--- | :---: | :---: | :---: |",
        ]

        for t in tarefas:
            cat_badge = "💳 Financeiro" if t.categoria == "financeiro" else ("🧓 60+" if t.categoria == "acessibilidade_60+" else t.categoria)
            linhas.append(f"| P{t.prioridade_calculada} | {t.id} | {cat_badge} | {t.titulo} | {t.pontos} | {t.responsavel} | {t.status} |")

        linhas.append("")
        if alertas:
            linhas.append("### 🚨 Alertas Ativos de Risco")
            for a in alertas:
                linhas.append(f"- {a}")

        return "\n".join(linhas)


class ReportFactory:
    """
    Padrão Factory Method (GoF).
    Cria geradores de relatórios específicos.
    """

    _REPORTS = {
        "burndown": BurndownReport,
        "velocity": VelocityReport,
        "acessibilidade": AccessibilityPriorityReport,
        "prioridade": AccessibilityPriorityReport,
    }

    @classmethod
    def create(cls, tipo: str) -> BaseReport:
        report_cls = cls._REPORTS.get(tipo.lower())
        if not report_cls:
            raise ValueError(f"Tipo de relatório desconhecido: {tipo}")
        return report_cls()
