"""
Adaptadores de fontes de dados do projeto para o Agente 5.

Padrão aplicado:
- Adapter (GoF): Converte issues de APIs externas (ex: GitHub, Jira) ou arquivos locais
  para o modelo unificado de tarefas (ProjectTask).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any


@dataclass
class ProjectTask:
    """Modelo interno padronizado de tarefa do backlog."""

    id: str
    titulo: str
    status: str  # "todo", "in_progress", "done", "blocked"
    pontos: int
    categoria: str  # "acessibilidade_60+", "financeiro", "funcional", "documentacao", "infra"
    responsavel: str  # "Luigi", "Francisco", "Caua/Enzo"
    data_limite: str | None = None
    prioridade_calculada: int = 0  # 1 = Máxima prioridade


class IssueAdapter:
    """
    Padrão Adapter (GoF).
    Adapta fontes variadas (dicionários, respostas de API GitHub, listas)
    para instâncias de ProjectTask.
    """

    @staticmethod
    def from_dict(raw: dict[str, Any]) -> ProjectTask:
        """Adapta dicionário genérico."""
        task_id = str(raw.get("id", raw.get("number", "TASK-00")))
        titulo = str(raw.get("titulo", raw.get("title", "Sem título")))
        status = str(raw.get("status", raw.get("state", "todo"))).lower()
        if status in ("open", "aberto"):
            status = "todo"
        elif status in ("closed", "concluido", "fechado"):
            status = "done"

        pontos = int(raw.get("pontos", raw.get("story_points", raw.get("points", 3))))
        categoria = str(raw.get("categoria", raw.get("labels", ["funcional"])))

        # Heurística de categoria a partir de labels ou título
        if isinstance(categoria, list):
            labels_str = " ".join(categoria).lower()
        else:
            labels_str = str(categoria).lower() + " " + titulo.lower()

        if "acessib" in labels_str or "60+" in labels_str or "idoso" in labels_str:
            cat_final = "acessibilidade_60+"
        elif "financ" in labels_str or "pix" in labels_str or "pagamento" in labels_str or "recibo" in labels_str or "mei" in labels_str:
            cat_final = "financeiro"
        elif "doc" in labels_str:
            cat_final = "documentacao"
        else:
            cat_final = "funcional"

        responsavel = str(raw.get("responsavel", raw.get("assignee", "Equipe")))

        return ProjectTask(
            id=task_id,
            titulo=titulo,
            status=status,
            pontos=pontos,
            categoria=cat_final,
            responsavel=responsavel,
            data_limite=raw.get("data_limite", raw.get("due_date")),
        )

    @classmethod
    def adapt_collection(cls, items: list[dict[str, Any]]) -> list[ProjectTask]:
        """Converte lista de itens brutos."""
        return [cls.from_dict(item) for item in items]
