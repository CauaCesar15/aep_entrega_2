#!/usr/bin/env python3
"""
CLI Principal e Ponto de Entrada do Ecossistema Ergane.

Permite executar o pipeline completo dos 5 agentes, testar o harness,
ou disparar análises individuais de documentação, código, acessibilidade,
testes automatizados e gestão de projeto.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ergane_agents.harness.orchestrator import ErganePipelineOrchestrator
from ergane_agents.harness.test_harness import ErganeTestHarness


def print_banner() -> None:
    print(r"""
  ==============================================================
    ███████╗██████╗  ██████╗  █████╗ ███╗   ██╗███████╗
    ██╔════╝██╔══██╗██╔════╝ ██╔══██╗████╗  ██║██╔════╝
    █████╗  ██████╔╝██║  ███╗███████║██╔██╗ ██║█████╗  
    ██╔══╝  ██╔══██╗██║   ██║██╔══██║██║╚██╗██║██╔══╝  
    ███████╗██║  ██║╚██████╔╝██║  ██║██║ ╚████║███████╗
  ==============================================================
    Ecossistema de 5 Agentes de Software | ODS 10 (Inclusão 60+)
    Plataforma Ergane para Pequenos Empreendedores (CNPJ/MEI)
  ==============================================================
    """)


def cmd_run_all(args: argparse.Namespace) -> None:
    """Executa o pipeline completo de ponta a ponta."""
    print("\n🚀 Executando Pipeline Completo dos 5 Agentes...")
    arquivo_alvo = Path(args.arquivo) if args.arquivo else BASE_DIR / "sample_ergane_module.py"

    if not arquivo_alvo.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_alvo}")
        sys.exit(1)

    orchestrator = ErganePipelineOrchestrator(output_dir=args.output)
    resultado = orchestrator.run_pipeline(arquivo_alvo)

    print("\n" + "=" * 60)
    print(f"✅ Pipeline concluído com sucesso em {resultado['tempo_total_segundos']}s!")
    print(f"📁 Artefatos salvos em: {Path(args.output).resolve()}")
    print("=" * 60)

    # Exibe resumo das predições do Agente 3
    res_ag3 = resultado["resultados"]["agente3_acessibilidade"]
    total_barreiras = res_ag3.get("total_barreiras_previstas", 0)
    print(f"\n🔍 [Agente 3 - Acessibilidade Preditiva]: {total_barreiras} barreiras identificadas.")

    # Exibe resumo dos testes do Agente 4
    res_ag4 = resultado["resultados"]["agente4_testes"]
    est4 = res_ag4.get("estatisticas", {})
    taxa = est4.get("taxa_acerto_predicoes_percentual", 0)
    print(f"🧪 [Agente 4 - Testes Persona Sr. José]: 10 casos executados. Taxa de acerto: {taxa}%")

    # Exibe resumo do Agente 5
    res_ag5 = resultado["resultados"]["agente5_gestao"]
    top_prioridades = res_ag5.get("prioridades", [])[:3]
    print(f"📊 [Agente 5 - Gestão de Projeto]: Top prioridades da Sprint:")
    for p in top_prioridades:
        print(f"   • {p}")
    print()


def cmd_test_harness(args: argparse.Namespace) -> None:
    """Executa o Test Harness contra todos os critérios de aceitação."""
    print("\n🧪 Executando Test Harness — Verificação dos Critérios de Aceitação (Entrega 2)...")
    harness = ErganeTestHarness()
    resultado = harness.run_all_tests()

    print("\n" + "=" * 75)
    print("  SCORECARD DE AVALIAÇÃO DOS CRITÉRIOS DE ACEITAÇÃO")
    print("=" * 75)

    for item in resultado["scorecard"]:
        icone = "✅ [PASSOU]" if item["passou"] else "❌ [FALHOU]"
        print(f"{icone} {item['agente']}: {item['criterio']}")
        print(f"           Detalhe: {item['detalhe']}")

    print("=" * 75)
    print(f"  Resultado Final: {resultado['passou']}/{resultado['total_testes']} testes aprovados "
          f"({resultado['taxa_sucesso_percentual']}%) em {resultado['tempo_execucao_s']}s")
    print("=" * 75 + "\n")


def cmd_guia_erros(args: argparse.Namespace) -> None:
    """Imprime ou exporta o Guia de Erros em Linguagem Simples para Idosos."""
    orchestrator = ErganePipelineOrchestrator()
    res = orchestrator.agent1_doc.execute({"codigo": "dummy = 1"})
    guia_md = res.data.get("guia_erros_60plus_md", "")

    if args.export:
        destino = Path(args.export)
        destino.write_text(guia_md, encoding="utf-8")
        print(f"✅ Guia de erros exportado para: {destino.resolve()}")
    else:
        print("\n" + guia_md + "\n")


def main() -> None:
    print_banner()
    parser = argparse.ArgumentParser(
        description="CLI do Ecossistema Ergane (5 Agentes de Software — ODS 10)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Comando run-all
    parser_run = subparsers.add_parser("run-all", help="Executa o pipeline completo dos 5 agentes")
    parser_run.add_argument("--arquivo", "-f", help="Caminho do arquivo de código a analisar", default=None)
    parser_run.add_argument("--output", "-o", help="Diretório de saída dos artefatos", default="./output")

    # Comando test-harness
    parser_test = subparsers.add_parser("test-harness", help="Executa o Test Harness de validação dos critérios")

    # Comando guia-erros
    parser_guia = subparsers.add_parser("guia-erros", help="Gera o Guia de Erros 60+ em linguagem simples")
    parser_guia.add_argument("--export", "-e", help="Salva o guia no caminho informado", default=None)

    args = parser.parse_args()

    if args.command == "run-all" or args.command is None:
        if args.command is None:
            # Sem argumentos: executa o run-all por padrão
            args.arquivo = None
            args.output = "./output"
        cmd_run_all(args)
    elif args.command == "test-harness":
        cmd_test_harness(args)
    elif args.command == "guia-erros":
        cmd_guia_erros(args)


if __name__ == "__main__":
    main()
