"""
Orquestrador do Pipeline de Agentes do Ergane.

Implementa o fluxo arquitetural definido na especificação:
Código / Documentação → Agentes 1 e 2 → Agente 3 (predição 60+) → Agente 4 (validação) → Agente 5 (priorização)
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from ergane_agents.agent1_documentacao import AgenteDocumentacao
from ergane_agents.agent2_validacao import AgenteValidacao
from ergane_agents.agent3_acessibilidade import AgenteAcessibilidade
from ergane_agents.agent4_testes import AgenteTestes
from ergane_agents.agent5_gestao import AgenteGestao
from ergane_agents.shared.event_bus import EventBus
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import AgentResult, StatusAgente
from ergane_agents.shared.utils import ensure_dir, save_json

logger = logging.getLogger("ergane.harness.orchestrator")


class ErganePipelineOrchestrator:
    """
    Harness de orquestração do ecossistema de 5 agentes do Ergane.
    """

    def __init__(
        self,
        output_dir: str | Path = "./output",
        ollama_url: str = "http://localhost:11434",
    ) -> None:
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)

        # Infraestrutura compartilhada
        self.event_bus = EventBus()
        self.llm_client = LLMClient(base_url=ollama_url)

        # Instanciação dos 5 agentes
        self.agent1_doc = AgenteDocumentacao(self.event_bus, self.llm_client)
        self.agent2_val = AgenteValidacao(self.event_bus, self.llm_client)
        self.agent3_acess = AgenteAcessibilidade(self.event_bus, self.llm_client)
        self.agent4_test = AgenteTestes(self.event_bus, self.llm_client)
        self.agent5_gestao = AgenteGestao(self.event_bus, self.llm_client)

    def run_pipeline(
        self,
        codigo_ou_arquivo: str | Path,
        nome_arquivo: str | None = None,
        backlog_custom: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Executa o pipeline completo de ponta a ponta:
        1. Executa Agente 1 (Documentação) e Agente 2 (Validação)
        2. Passa métricas para o Agente 3 (Acessibilidade Preditiva)
        3. Passa barreiras para o Agente 4 (Testes Automatizados - Sr. José)
        4. Passa resultados consolidados para o Agente 5 (Gestão e Priorização)
        5. Salva todos os artefatos gerados no diretório de saída
        """
        inicio_total = time.time()
        logger.info("=== INICIANDO PIPELINE DE EXECUÇÃO ERGANE (5 AGENTES) ===")

        # Resolve código ou arquivo
        conteudo_codigo = ""
        caminho_arquivo = None

        if isinstance(codigo_ou_arquivo, Path) or (isinstance(codigo_ou_arquivo, str) and Path(codigo_ou_arquivo).is_file()):
            caminho_arquivo = Path(codigo_ou_arquivo)
            nome_arquivo = nome_arquivo or caminho_arquivo.name
            conteudo_codigo = caminho_arquivo.read_text(encoding="utf-8", errors="ignore")
        else:
            conteudo_codigo = str(codigo_ou_arquivo)
            nome_arquivo = nome_arquivo or "modulo_ergane.py"

        resultados: dict[str, AgentResult] = {}

        # -------------------------------------------------------------
        # ETAPA 1: Agente 1 (Documentação) e Agente 2 (Validação de Código)
        # -------------------------------------------------------------
        logger.info("[ETAPA 1/4] Executando Agente 1 (Documentação) e Agente 2 (Validação)...")
        ctx_agente1 = {"codigo": conteudo_codigo, "arquivo": str(caminho_arquivo) if caminho_arquivo else None}
        res_agente1 = self.agent1_doc.execute(ctx_agente1)
        resultados["agente1_documentacao"] = res_agente1

        ctx_agente2 = {"codigo": conteudo_codigo, "arquivo": str(caminho_arquivo) if caminho_arquivo else None, "nome_arquivo": nome_arquivo}
        res_agente2 = self.agent2_val.execute(ctx_agente2)
        resultados["agente2_validacao"] = res_agente2

        # -------------------------------------------------------------
        # ETAPA 2: Agente 3 (Acessibilidade Preditiva - Núcleo)
        # -------------------------------------------------------------
        logger.info("[ETAPA 2/4] Executando Agente 3 (Acessibilidade Preditiva 60+)...")
        ctx_agente3 = {
            "arquivo": nome_arquivo,
            "doc_metrics": res_agente1.data.get("metricas", {}),
            "struct_metrics": res_agente2.data.get("metricas_estruturais", {}),
        }
        res_agente3 = self.agent3_acess.execute(ctx_agente3)
        resultados["agente3_acessibilidade"] = res_agente3

        # -------------------------------------------------------------
        # ETAPA 3: Agente 4 (Testes Automatizados - Perfil Sr. José)
        # -------------------------------------------------------------
        logger.info("[ETAPA 3/4] Executando Agente 4 (Validação com Persona Sr. José)...")
        ctx_agente4 = {
            "barreiras": res_agente3.data.get("barreiras", []),
        }
        res_agente4 = self.agent4_test.execute(ctx_agente4)
        resultados["agente4_testes"] = res_agente4

        # -------------------------------------------------------------
        # ETAPA 4: Agente 5 (Gestão de Projeto e Priorização ODS 10)
        # -------------------------------------------------------------
        logger.info("[ETAPA 4/4] Executando Agente 5 (Gestão de Projeto e Priorização)...")
        ctx_agente5 = {
            "backlog": backlog_custom,
        }
        res_agente5 = self.agent5_gestao.execute(ctx_agente5)
        resultados["agente5_gestao"] = res_agente5

        tempo_total = round(time.time() - inicio_total, 4)
        logger.info("=== PIPELINE CONCLUÍDO EM %.2f SEGUNDOS ===", tempo_total)

        # -------------------------------------------------------------
        # Persistência de Artefatos no diretório de saída
        # -------------------------------------------------------------
        self._salvar_artefatos(resultados, nome_arquivo)

        return {
            "tempo_total_segundos": tempo_total,
            "arquivo_analisado": nome_arquivo,
            "todos_sucesso": all(r.status == StatusAgente.SUCESSO for r in resultados.values()),
            "resultados": {nome: r.data for nome, r in resultados.items()},
        }

    def _salvar_artefatos(self, resultados: dict[str, AgentResult], nome_base: str) -> None:
        """Grava JSONs e relatórios Markdown formatados no diretório de saída."""
        safe_name = Path(nome_base).stem

        # 1. JSON consolidado de métricas e predições
        dados_json = {
            "arquivo": nome_base,
            "metricas_documentacao": resultados["agente1_documentacao"].data.get("metricas", {}),
            "metricas_estruturais": resultados["agente2_validacao"].data.get("metricas_estruturais", {}),
            "predicoes_60plus": resultados["agente3_acessibilidade"].data.get("barreiras", []),
            "validacao_testes": resultados["agente4_testes"].data.get("estatisticas", {}),
            "gestao_prioridades": resultados["agente5_gestao"].data.get("prioridades", []),
        }
        save_json(dados_json, self.output_dir / f"ergane_metricas_{safe_name}.json")

        # 2. Guia de Erros 60+ (Markdown)
        guia_md = resultados["agente1_documentacao"].data.get("guia_erros_60plus_md", "")
        if guia_md:
            (self.output_dir / "guia_erros_60plus.md").write_text(guia_md, encoding="utf-8")

        # 3. Relatório Preditivo de Acessibilidade (Markdown)
        rel_acess_md = resultados["agente3_acessibilidade"].data.get("relatorio_markdown", "")
        if rel_acess_md:
            (self.output_dir / f"relatorio_acessibilidade_{safe_name}.md").write_text(rel_acess_md, encoding="utf-8")

        # 4. Relatório de Testes Automatizados (Markdown)
        rel_test_md = resultados["agente4_testes"].data.get("relatorio_markdown", "")
        if rel_test_md:
            (self.output_dir / f"relatorio_testes_{safe_name}.md").write_text(rel_test_md, encoding="utf-8")

        # 5. Relatório de Gestão de Projeto (Markdown)
        rel_gestao_md = resultados["agente5_gestao"].data.get("relatorio_markdown", "")
        if rel_gestao_md:
            (self.output_dir / "relatorio_gestao_projeto.md").write_text(rel_gestao_md, encoding="utf-8")
