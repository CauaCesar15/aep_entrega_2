"""
Agente 4 — Agente de Testes Automatizados.

Arquitetura: Pipe-and-filter com ciclo de retorno.
Executa simulação do perfil sênior (Sr. José) e valida as predições do Agente 3.
"""

from __future__ import annotations

import time
from typing import Any

from ergane_agents.agent4_testes.persona import PERSONA_PADRAO, SeniorPersona
from ergane_agents.agent4_testes.simulation import TestRunnerFacade
from ergane_agents.shared.base_agent import BaseAgent
from ergane_agents.shared.event_bus import EventBus, EventType
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import AgentResult, ResultadoTeste, StatusAgente


class AgenteTestes(BaseAgent):
    """
    Agente 4 — Testes Automatizados e Validação Empírica.
    Mede tempos reais de recuperação de erros com a persona 60+.
    """

    def __init__(
        self,
        event_bus: EventBus,
        llm_client: LLMClient | None = None,
        persona: SeniorPersona | None = None,
    ) -> None:
        super().__init__(
            name="AgenteTestes",
            event_bus=event_bus,
            llm_client=llm_client,
        )
        self.persona = persona or PERSONA_PADRAO
        self.facade = TestRunnerFacade(self.persona)
        self.predicoes_cache: list[dict[str, Any]] = []

        # Assina predições do Agente 3
        self.event_bus.subscribe(EventType.PREDICTION_READY, self._on_prediction_ready)

    def _on_prediction_ready(self, event_type: EventType, data: Any) -> None:
        if isinstance(data, dict):
            self.predicoes_cache = data.get("barreiras", [])
            self.log_info("Cache atualizado com %d barreiras previstas pelo Agente 3.", len(self.predicoes_cache))

    def get_required_inputs(self) -> list[str]:
        return []

    def validate_input(self, context: dict[str, Any]) -> bool:
        return True

    def execute(self, context: dict[str, Any]) -> AgentResult:
        """
        Executa os testes simulados com o perfil do Sr. José:
        - 5 casos técnicos (meta <= 60s)
        - 5 casos financeiros (meta <= 90s)
        - Medição de tempo e validação empírica das predições do Agente 3
        """
        tempo_inicio = time.time()
        barreiras = context.get("barreiras", self.predicoes_cache)
        self.log_info("Iniciando execução da suíte de testes sênior (Sr. José)...")

        resultados, estatisticas = self.facade.executar_todos(barreiras_previstas=barreiras)

        # Relatório Markdown
        linhas_relatorio = [
            "# Relatório de Testes Automatizados — Validação Empírica 60+",
            f"**Persona Simulada:** {self.persona.nome} ({self.persona.idade} anos) — {self.persona.ocupacao}",
            f"**Parâmetros:** Zoom {int(self.persona.zoom_tela * 100)}% | Foco Teclado: {self.persona.preferencia_teclado} | Fator Cognitivo: {self.persona.fator_desaceleracao_cognitiva}x",
            "",
            "## 1. Indicadores de Desempenho e Metas (ODS 10)",
            f"- **Tempo Médio Recuperação (Técnico):** {estatisticas['casos_tecnicos']['tempo_medio_s']}s (Meta: ≤ {self.persona.meta_tempo_recuperacao_tecnico_s}s) "
            f"-> {'✅ DENTRO DA META' if estatisticas['casos_tecnicos']['conformidade_meta'] else '⚠️ FORA DA META'}",
            f"- **Tempo Médio Recuperação (Financeiro):** {estatisticas['casos_financeiros']['tempo_medio_s']}s (Meta: ≤ {self.persona.meta_tempo_recuperacao_financeiro_s}s) "
            f"-> {'✅ DENTRO DA META' if estatisticas['casos_financeiros']['conformidade_meta'] else '⚠️ FORA DA META'}",
            f"- **Taxa de Acerto das Predições do Agente 3:** {estatisticas['taxa_acerto_predicoes_percentual']}%",
            "",
            "## 2. Detalhe dos Casos de Teste Executados",
            "| Caso de Teste | Tempo Recuperação | Meta | Status |",
            "| :--- | :---: | :---: | :---: |",
        ]

        for r in resultados:
            meta_caso = self.persona.meta_tempo_recuperacao_tecnico_s if "TEC" in r.caso else self.persona.meta_tempo_recuperacao_financeiro_s
            icone_status = "✅ Sucesso" if r.sucesso else "❌ Estourou Meta"
            linhas_relatorio.append(f"| {r.caso} | {r.tempo_recuperacao_s}s | ≤ {meta_caso}s | {icone_status} |")

        linhas_relatorio.append("")
        relatorio_md = "\n".join(linhas_relatorio)

        payload = {
            "persona": {
                "nome": self.persona.nome,
                "idade": self.persona.idade,
                "zoom": self.persona.zoom_tela,
            },
            "estatisticas": estatisticas,
            "total_testes": len(resultados),
            "resultados": [
                {
                    "caso": r.caso,
                    "tempo_recuperacao_s": r.tempo_recuperacao_s,
                    "sucesso": r.sucesso,
                }
                for r in resultados
            ],
            "relatorio_markdown": relatorio_md,
            "tempo_execucao_s": round(time.time() - tempo_inicio, 4),
        }

        # Emite evento de validação para os Agentes 1 e 5
        self.emit_event(EventType.VALIDATION_READY, payload)

        return self.publish_result(data=payload, status=StatusAgente.SUCESSO)
