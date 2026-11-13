"""
Agente 5 — Agente de Gestão de Projeto.

Arquitetura Pipe-and-filter:
  Backlog/Issues + Relatórios Agentes 3 e 4 → Métricas Ágeis → Priorização ODS 10 → Relatório + Alertas
"""

from __future__ import annotations

import time
from typing import Any

from ergane_agents.agent5_gestao.adapters import IssueAdapter, ProjectTask
from ergane_agents.agent5_gestao.metrics import (
    calcular_burndown,
    calcular_velocity,
    identificar_alertas_risco,
    priorizar_backlog,
)
from ergane_agents.agent5_gestao.reports import ReportFactory
from ergane_agents.shared.base_agent import BaseAgent
from ergane_agents.shared.event_bus import EventBus, EventType
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import AgentResult, RelatorioGestao, StatusAgente


class AgenteGestao(BaseAgent):
    """
    Agente 5 — Gestão de Projeto e Priorização ODS 10.
    Garante que melhorias de inclusão 60+ e erros financeiros não sejam adiados.
    """

    # Backlog padrão de tarefas caso nenhuma fonte externa seja injetada
    BACKLOG_PADRAO: list[dict[str, Any]] = [
        {"id": "ERG-101", "titulo": "Aumentar contraste de botões de ação para 4.5:1", "pontos": 3, "categoria": "acessibilidade_60+", "responsavel": "Caua/Enzo", "status": "todo"},
        {"id": "ERG-102", "titulo": "Tratamento amigável para falha de pagamento PIX", "pontos": 5, "categoria": "financeiro", "responsavel": "Francisco", "status": "in_progress"},
        {"id": "ERG-103", "titulo": "Implementar navegação completa por teclado no checkout", "pontos": 5, "categoria": "acessibilidade_60+", "responsavel": "Luigi", "status": "blocked"},
        {"id": "ERG-104", "titulo": "Nova animação 3D de transição no dashboard", "pontos": 8, "categoria": "funcional", "responsavel": "Luigi", "status": "todo"},
        {"id": "ERG-105", "titulo": "Correção de mensagem técnica de timeout na consulta de CEP", "pontos": 2, "categoria": "documentacao", "responsavel": "Caua/Enzo", "status": "todo"},
        {"id": "ERG-106", "titulo": "Validação com máscara clara para CNPJ de 14 dígitos", "pontos": 3, "categoria": "financeiro", "responsavel": "Francisco", "status": "todo"},
        {"id": "ERG-107", "titulo": "Aviso preventivo de faturamento anual MEI", "pontos": 5, "categoria": "financeiro", "responsavel": "Luigi", "status": "todo"},
    ]

    def __init__(
        self,
        event_bus: EventBus,
        llm_client: LLMClient | None = None,
    ) -> None:
        super().__init__(
            name="AgenteGestao",
            event_bus=event_bus,
            llm_client=llm_client,
        )
        self.barreiras_cache: list[dict[str, Any]] = []
        self.validacao_cache: dict[str, Any] = {}

        # Assina relatórios dos Agentes 3 e 4
        self.event_bus.subscribe(EventType.PREDICTION_READY, self._on_prediction)
        self.event_bus.subscribe(EventType.VALIDATION_READY, self._on_validation)

    def _on_prediction(self, event_type: EventType, data: Any) -> None:
        if isinstance(data, dict):
            self.barreiras_cache = data.get("barreiras", [])
            self.log_info("Agente 5 recebeu %d barreiras do Agente 3.", len(self.barreiras_cache))

    def _on_validation(self, event_type: EventType, data: Any) -> None:
        if isinstance(data, dict):
            self.validacao_cache = data
            self.log_info("Agente 5 recebeu validação dos testes do Agente 4.")

    def get_required_inputs(self) -> list[str]:
        return []

    def validate_input(self, context: dict[str, Any]) -> bool:
        return True

    def execute(self, context: dict[str, Any]) -> AgentResult:
        """
        Executa a consolidação de gestão ágil:
        1. Adaptação do backlog
        2. Cálculo de Velocity e Burndown
        3. Priorização automática (Erros Financeiros > Acessibilidade 60+ > Outros)
        4. Identificação de alertas de risco
        5. Geração de relatórios via Factory
        6. Emissão do evento REPORT_READY
        """
        tempo_inicio = time.time()
        self.log_info("Iniciando ciclo de gestão de projeto...")

        # 1. Coleta e adaptação
        raw_issues = context.get("backlog") or self.BACKLOG_PADRAO
        tarefas = IssueAdapter.adapt_collection(raw_issues)

        # 2. Métricas ágeis
        sprints_anteriores = context.get("historico_sprints", [
            {"sprint": 1, "pontos_entregues": 21},
            {"sprint": 2, "pontos_entregues": 23},
        ])
        velocity = calcular_velocity(sprints_anteriores)

        pontos_totais_sprint = sum(t.pontos for t in tarefas)
        queimados_dia = context.get("queimados_por_dia", [4, 6, 3, 5])
        burndown = calcular_burndown(pontos_totais_sprint, dias_sprint=7, pontos_queimados_por_dia=queimados_dia)

        # 3. Priorização automática
        tarefas_priorizadas = priorizar_backlog(tarefas, self.barreiras_cache)

        # 4. Alertas de risco
        alertas = identificar_alertas_risco(tarefas_priorizadas)

        # 5. Geração dos relatórios via ReportFactory (Factory Method)
        rep_velocity = ReportFactory.create("velocity").render({"velocity": velocity})
        rep_burndown = ReportFactory.create("burndown").render({"burndown": burndown})
        rep_prioridade = ReportFactory.create("prioridade").render({
            "tarefas_priorizadas": tarefas_priorizadas,
            "alertas": alertas,
        })

        relatorio_completo_md = (
            "# Relatório Consolidado de Gestão de Projeto — Ergane\n\n"
            f"{rep_prioridade}\n\n---\n\n"
            f"{rep_velocity}\n\n---\n\n"
            f"{rep_burndown}\n"
        )

        tempo_gasto_s = round(time.time() - tempo_inicio, 4)

        relatorio_gestao = RelatorioGestao(
            velocity=velocity,
            burndown=burndown,
            issues_acessibilidade_risco=alertas,
            prioridades=[f"[{t.id}] {t.titulo} (P{t.prioridade_calculada})" for t in tarefas_priorizadas],
        )

        payload = {
            "tempo_processamento_s": tempo_gasto_s,
            "conformidade_tempo": tempo_gasto_s <= 30.0,
            "velocity": relatorio_gestao.velocity,
            "burndown": relatorio_gestao.burndown,
            "alertas_risco": relatorio_gestao.issues_acessibilidade_risco,
            "prioridades": relatorio_gestao.prioridades,
            "total_tarefas": len(tarefas),
            "relatorio_markdown": relatorio_completo_md,
        }

        # Emite evento de relatório pronto no barramento
        self.emit_event(EventType.REPORT_READY, payload)

        return self.publish_result(data=payload, status=StatusAgente.SUCESSO)
