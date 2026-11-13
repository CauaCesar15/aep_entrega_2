#!/usr/bin/env python3
"""
CLI Oficial do Agente 3 — Agente de Acessibilidade Preditiva (Núcleo do Ergane).

Entrega Individual — AEP Engenharia de Software (UniCesumar)
Aluno: Caua Cesar da Silva de Oliveira
ODS 10: Redução das Desigualdades (Inclusão Digital da Economia Prateada 60+)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ergane_agents.agent3_acessibilidade.agent import AgenteAcessibilidade
from ergane_agents.agent3_acessibilidade.engine import AccessibilityEngine
from ergane_agents.agent3_acessibilidade.predictors import PredictorFactory, RuleDecorator
from ergane_agents.shared.event_bus import EventBus
from ergane_agents.shared.llm_client import LLMClient
from ergane_agents.shared.models import BarreiraPreditiva, Severidade, StatusAgente, TipoBarreira
from ergane_agents.shared.utils import load_yaml, save_json


def print_banner() -> None:
    print(r"""
  ========================================================================
    AGENTE 3 — ACESSIBILIDADE PREDITIVA 60+ (NÚCLEO DO ERGANE)
    ODS 10: Redução das Desigualdades | Inclusão de Empreendedores 60+
    Responsável: Caua Cesar da Silva de Oliveira | UniCesumar
  ========================================================================
    Padrões Aplicados:
      • Factory Method (GoF) — Instanciação dinâmica de preditores
      • Decorator (GoF)      — Injeção de regras WCAG 60+
      • Observer (GoF)       — Notificação de barreiras críticas
      • MVC Adaptado         — Model (Regras), View (Markdown), Controller (Engine)
      • GRASP                — Especialista na Informação + Controlador
  ========================================================================
    """)


def cmd_analyze(args: argparse.Namespace) -> None:
    """Analisa um arquivo de código ou tela e prevê barreiras 60+."""
    arquivo_alvo = Path(args.arquivo)
    if not arquivo_alvo.exists():
        print(f"❌ Erro: Arquivo '{arquivo_alvo}' não encontrado.")
        sys.exit(1)

    print(f"\n🔍 Executando Agente 3 de forma autônoma sobre: {arquivo_alvo.name}")
    print(f"📄 Caminho completo: {arquivo_alvo.resolve()}\n")

    event_bus = EventBus()
    llm_client = LLMClient()
    agent3 = AgenteAcessibilidade(
        event_bus=event_bus,
        llm_client=llm_client,
        rules_path=str(BASE_DIR / "config" / "rules_60plus.yaml"),
    )

    t0 = time.time()
    resultado = agent3.execute({"arquivo": str(arquivo_alvo)})
    tempo_exec = round(time.time() - t0, 4)

    if resultado.status != StatusAgente.SUCESSO:
        print(f"❌ Falha na análise: {resultado.data.get('erro', 'Erro desconhecido')}")
        sys.exit(1)

    data = resultado.data
    barreiras = data.get("barreiras", [])
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Salva relatório em Markdown
    slug = arquivo_alvo.stem
    relatorio_md_path = output_dir / f"relatorio_acessibilidade_{slug}.md"
    relatorio_json_path = output_dir / f"predicoes_acessibilidade_{slug}.json"

    relatorio_md_path.write_text(data["relatorio_markdown"], encoding="utf-8")
    save_json(data, relatorio_json_path)

    # Exibe resumo formatado no terminal
    print("=" * 72)
    print(f"  RESULTADO DA PREDIÇÃO DE ACESSIBILIDADE 60+ (Tempo: {tempo_exec}s)")
    print("=" * 72)
    print(f"Total de Barreiras Previstas: {len(barreiras)}")

    contagem_severidade = {"alta": 0, "media": 0, "baixa": 0}
    contagem_tipo = {t.value: 0 for t in TipoBarreira}

    for b in barreiras:
        sev = b.get("severidade", "media").lower()
        contagem_severidade[sev] = contagem_severidade.get(sev, 0) + 1
        t = b.get("tipo", "percepção")
        contagem_tipo[t] = contagem_tipo.get(t, 0) + 1

    print(f"  🔴 Alta: {contagem_severidade['alta']} | 🟡 Média: {contagem_severidade['media']} | 🟢 Baixa: {contagem_severidade['baixa']}\n")

    print("Distribuição por Frente de Acessibilidade:")
    for tipo, count in contagem_tipo.items():
        icone = "👁️" if tipo == "percepção" else ("⌨️" if tipo == "operação" else ("🧠" if tipo == "compreensão" else "🧭"))
        print(f"  {icone} {tipo.capitalize()}: {count} barreira(s)")

    print("\nDetalhamento das Barreiras:")
    for idx, b in enumerate(barreiras, 1):
        sev_icon = "🔴" if b.get("severidade") == "alta" else ("🟡" if b.get("severidade") == "media" else "🟢")
        print(f"\n  [{idx}] {sev_icon} [{b.get('tipo', '').upper()}] {b.get('descricao')}")
        print(f"      💡 Correção recomendada: {b.get('sugestao_correcao')}")

    print("\n" + "=" * 72)
    print(f"✅ Relatório Markdown salvo em: {relatorio_md_path.resolve()}")
    print(f"✅ Predições estruturadas em JSON: {relatorio_json_path.resolve()}")
    print("=" * 72 + "\n")


def cmd_cruzamento(args: argparse.Namespace) -> None:
    """Executa o cruzamento formal a partir de arquivos JSON de métricas."""
    doc_path = Path(args.doc_metrics)
    struct_path = Path(args.struct_metrics)

    if not doc_path.exists() or not struct_path.exists():
        print("❌ Erro: Arquivos JSON de métricas não encontrados.")
        sys.exit(1)

    print(f"\n🔄 Cruzando métricas dos Agentes 1 e 2 com regras 60+...")
    with open(doc_path, "r", encoding="utf-8") as f:
        doc_data = json.load(f)
    with open(struct_path, "r", encoding="utf-8") as f:
        struct_data = json.load(f)

    event_bus = EventBus()
    agent3 = AgenteAcessibilidade(
        event_bus=event_bus,
        rules_path=str(BASE_DIR / "config" / "rules_60plus.yaml"),
    )

    resultado = agent3.execute({
        "doc_metrics": doc_data.get("metricas", doc_data),
        "struct_metrics": struct_data.get("metricas_estruturais", struct_data),
        "arquivo": doc_data.get("arquivo", "modulo.py"),
    })

    if resultado.status != StatusAgente.SUCESSO:
        print(f"❌ Falha: {resultado.data.get('erro', 'Erro')}")
        sys.exit(1)

    print(f"✅ Cruzamento concluído! {resultado.data['total_barreiras_previstas']} barreiras previstas.")


def cmd_test(args: argparse.Namespace) -> None:
    """Executa a verificação dos 5 critérios de aceitação formais da Entrega 2."""
    print("\n🧪 Executando Test Harness dos Critérios de Aceitação da Entrega 2 (Agente 3)...\n")

    event_bus = EventBus()
    rules_path = BASE_DIR / "config" / "rules_60plus.yaml"
    agent3 = AgenteAcessibilidade(event_bus=event_bus, rules_path=str(rules_path))

    # Contexto de teste abrangente
    contexto_teste = {
        "doc_metrics": {
            "arquivo": "checkout_senior.py",
            "indice_flesch": 35.0,  # Abaixo de 50 -> gera barreira
            "jargoes_detectados": ["payload", "backend", "token"],
            "cobertura_docstrings_percentual": 40.0,
        },
        "struct_metrics": {
            "arquivo": "checkout_senior.py",
            "complexidade_media": 5.5,  # Acima de 4.0 -> gera barreira
            "tags_semanticas": ["button", "input"],
            "total_tags": 2,
            "total_divs": 6,
            "indice_semantico": 0.25,
            "consistencia_nomes": 0.60,
            "mensagens_erro_problematicas": ["Erro inesperado", "Internal server error"],
            "loc": 350,
        },
    }

    t0 = time.time()
    resultado = agent3.execute(contexto_teste)
    t_total = time.time() - t0

    barreiras = resultado.data.get("barreiras", [])
    tipos_previstos = set(b.get("tipo") for b in barreiras)

    criterios = [
        {
            "num": "3.1",
            "nome": "Cruzar métricas de documentação e estruturais com regras 60+",
            "passou": len(barreiras) > 0,
            "detalhe": f"{len(barreiras)} barreiras previstas com sucesso",
        },
        {
            "num": "3.2",
            "nome": "Prever pelo menos 4 categorias/tipos de barreira",
            "passou": len(tipos_previstos) >= 4,
            "detalhe": f"Frentes avaliadas: {sorted(list(tipos_previstos))}",
        },
        {
            "num": "3.3",
            "nome": "Gerar relatório por arquivo e por tela (Markdown/JSON)",
            "passou": "relatorio_markdown" in resultado.data and len(resultado.data["relatorio_markdown"]) > 200,
            "detalhe": f"Relatório gerado com {len(resultado.data.get('relatorio_markdown', ''))} caracteres",
        },
        {
            "num": "3.4",
            "nome": "Emitir sugestão de correção para cada barreira",
            "passou": all(bool(b.get("sugestao_correcao")) for b in barreiras),
            "detalhe": f"100% das {len(barreiras)} barreiras com sugestão acionável",
        },
        {
            "num": "3.5",
            "nome": "Tempo de análise ≤ 30 s por arquivo",
            "passou": resultado.data.get("tempo_analise_segundos", 99) <= 30.0,
            "detalhe": f"Tempo medido: {resultado.data.get('tempo_analise_segundos')}s (limite: 30.0s)",
        },
    ]

    print("=" * 76)
    print("  SCORECARD DE AVALIAÇÃO — AGENTE 3 (ENTREGA 2)")
    print("=" * 76)

    total_passou = 0
    for c in criterios:
        status_ico = "✅ [APROVADO]" if c["passou"] else "❌ [FALHOU]"
        if c["passou"]:
            total_passou += 1
        print(f"{status_ico} Critério {c['num']}: {c['nome']}")
        print(f"             Detalhe: {c['detalhe']}")

    print("=" * 76)
    taxa = (total_passou / len(criterios)) * 100
    print(f"  Resultado Final: {total_passou}/{len(criterios)} critérios aprovados ({taxa:.1f}%)")
    print(f"  Tempo total de execução dos testes: {t_total:.4f}s")
    print("=" * 76 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI do Agente 3 — Acessibilidade Preditiva 60+ (Ergane / ODS 10)",
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando analyze
    p_analyze = subparsers.add_parser("analyze", help="Analisa um arquivo e prevê barreiras 60+")
    p_analyze.add_argument("arquivo", nargs="?", default="sample_ergane_module.py", help="Arquivo a ser analisado")
    p_analyze.add_argument("-o", "--output", default="./output", help="Diretório de saída")

    # Comando cruzamento
    p_cruzamento = subparsers.add_parser("cruzamento", help="Cruza JSONs de métricas de documentação e código")
    p_cruzamento.add_argument("--doc-metrics", required=True, help="JSON de métricas de documentação (Agente 1)")
    p_cruzamento.add_argument("--struct-metrics", required=True, help="JSON de métricas estruturais (Agente 2)")
    p_cruzamento.add_argument("-o", "--output", default="./output", help="Diretório de saída")

    # Comando test
    subparsers.add_parser("test", help="Executa o Scorecard de critérios de aceitação da Entrega 2")

    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        sys.exit(0)

    print_banner()
    args = parser.parse_args()

    if args.comando == "analyze":
        cmd_analyze(args)
    elif args.comando == "cruzamento":
        cmd_cruzamento(args)
    elif args.comando == "test":
        cmd_test(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
