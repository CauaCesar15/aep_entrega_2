"""
Motor de Acessibilidade Preditiva — Padrão GRASP Controlador / MVC Adaptado.

Coordenador das predições de acessibilidade para o ecossistema Ergane.
Cruza os modelos de dados (Model: Métricas JSON + Regras 60+) e produz a View (Relatório).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ergane_agents.agent3_acessibilidade.predictors import PredictorFactory, RuleDecorator
from ergane_agents.shared.models import BarreiraPreditiva, Severidade, TipoBarreira
from ergane_agents.shared.utils import load_yaml


class AccessibilityEngine:
    """
    Controlador central da análise preditiva de acessibilidade 60+.
    """

    def __init__(self, rules_path: str | Path | None = None) -> None:
        self.rules_path = Path(rules_path or Path(__file__).parents[2] / "config" / "rules_60plus.yaml")
        self.rules: dict[str, Any] = {}
        self._carregar_regras()

    def _carregar_regras(self) -> None:
        if self.rules_path.exists():
            try:
                self.rules = load_yaml(self.rules_path)
            except Exception:
                self.rules = {}

    def run_prediction(
        self,
        doc_metrics: dict[str, Any],
        struct_metrics: dict[str, Any],
    ) -> list[BarreiraPreditiva]:
        """
        Executa as quatro frentes preditivas em paralelo/sequência:
        - Percepção
        - Operação
        - Compreensão
        - Fluxo
        """
        preditores_base = PredictorFactory.create_all()
        todas_barreiras: list[BarreiraPreditiva] = []

        for preditor in preditores_base:
            # Padrão Decorator: decora com regras específicas do YAML caso existam
            chave_regras = preditor.tipo.value
            regras_categoria = self.rules.get(chave_regras, [])
            if regras_categoria:
                preditor = RuleDecorator(preditor, regras_categoria)

            barreiras = preditor.predict(doc_metrics, struct_metrics, regras_categoria)
            todas_barreiras.extend(barreiras)

        return todas_barreiras

    def gerar_relatorio_markdown(
        self,
        arquivo: str,
        barreiras: list[BarreiraPreditiva],
        metricas_resumo: dict[str, Any],
    ) -> str:
        """
        View (MVC Adaptado): Gera visualização em Markdown do relatório preditivo.
        """
        linhas = [
            f"# Relatório Preditivo de Acessibilidade 60+ — Ergane",
            f"**Arquivo / Módulo analisado:** `{arquivo}`",
            f"**ODS 10:** Redução das Desigualdades — Inclusão do Empreendedor Sênior",
            "",
            "## 1. Resumo Executivo das Predições",
            f"- **Total de barreiras previstas:** {len(barreiras)}",
        ]

        # Contagem por severidade e tipo
        altas = sum(1 for b in barreiras if b.severidade == Severidade.ALTA)
        medias = sum(1 for b in barreiras if b.severidade == Severidade.MEDIA)
        baixas = sum(1 for b in barreiras if b.severidade == Severidade.BAIXA)

        linhas.append(f"- 🔴 **Alta severidade:** {altas}")
        linhas.append(f"- 🟡 **Média severidade:** {medias}")
        linhas.append(f"- 🟢 **Baixa severidade:** {baixas}")
        linhas.append("")
        linhas.append("---")
        linhas.append("")
        linhas.append("## 2. Detalhamento por Frente de Acessibilidade")

        por_tipo: dict[TipoBarreira, list[BarreiraPreditiva]] = {
            TipoBarreira.PERCEPCAO: [],
            TipoBarreira.OPERACAO: [],
            TipoBarreira.COMPREENSAO: [],
            TipoBarreira.FLUXO: [],
        }

        for b in barreiras:
            por_tipo[b.tipo].append(b)

        titulos_frentes = {
            TipoBarreira.PERCEPCAO: "👁️ Frente 1: Percepção (Contraste, Fontes, Tamanho de Alvos)",
            TipoBarreira.OPERACAO: "⌨️ Frente 2: Operação (Navegação por Teclado, Ritmo e Interação)",
            TipoBarreira.COMPREENSAO: "🧠 Frente 3: Compreensão (Linguagem Clara, Jargões e Mensagens de Erro)",
            TipoBarreira.FLUXO: "🧭 Frente 4: Fluxo (Profundidade, Clareza e Previsibilidade)",
        }

        for tipo, lista in por_tipo.items():
            linhas.append(f"### {titulos_frentes[tipo]}")
            if not lista:
                linhas.append("✅ Nenhuma barreira crítica prevista nesta frente.")
            else:
                for idx, barreira in enumerate(lista, 1):
                    badge = "🔴 ALTA" if barreira.severidade == Severidade.ALTA else ("🟡 MÉDIA" if barreira.severidade == Severidade.MEDIA else "🟢 BAIXA")
                    linhas.append(f"#### Barreira {idx} — Severidade: {badge}")
                    linhas.append(f"- **Diagnóstico:** {barreira.descricao}")
                    linhas.append(f"- **Sugestão de Correção Imediata:** {barreira.sugestao_correcao}")
            linhas.append("")

        linhas.append("---")
        linhas.append("## 3. Próximos Passos no Ciclo Ergane")
        linhas.append("1. **Agente 4 (Testes Automatizados):** Submeter as barreiras ao teste de perfil sênior (Sr. José) para validar o tempo de recuperação.")
        linhas.append("2. **Agente 5 (Gestão de Projeto):** Priorizar a resolução das barreiras de alta severidade no backlog da sprint.")

        return "\n".join(linhas)
