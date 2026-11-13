"""
Suíte de Testes Unitários e de Critérios de Aceitação — Agente 3 (Acessibilidade Preditiva 60+).

Responsável: Caua Cesar da Silva de Oliveira
Projeto: Ergane (ODS 10)
Curso: Engenharia de Software — UniCesumar
"""

import unittest
from pathlib import Path

from ergane_agents.agent3_acessibilidade.agent import AgenteAcessibilidade
from ergane_agents.agent3_acessibilidade.engine import AccessibilityEngine
from ergane_agents.agent3_acessibilidade.predictors import (
    BasePredictor,
    CompreensaoPredictor,
    FluxoPredictor,
    OperacaoPredictor,
    PercepcaoPredictor,
    PredictorFactory,
    RuleDecorator,
)
from ergane_agents.shared.event_bus import EventBus
from ergane_agents.shared.models import StatusAgente, TipoBarreira

BASE_DIR = Path(__file__).resolve().parents[1]


class TestAgente3Acessibilidade(unittest.TestCase):
    """Testes cobrindo os 5 critérios da Entrega 2 e os padrões GoF/GRASP do Agente 3."""

    def setUp(self):
        self.event_bus = EventBus()
        self.rules_path = BASE_DIR / "config" / "rules_60plus.yaml"
        self.agent = AgenteAcessibilidade(
            event_bus=self.event_bus,
            rules_path=str(self.rules_path),
        )

        self.mock_context = {
            "doc_metrics": {
                "arquivo": "checkout_senior.py",
                "indice_flesch": 30.0,
                "jargoes_detectados": ["payload", "backend"],
                "cobertura_docstrings_percentual": 45.0,
            },
            "struct_metrics": {
                "arquivo": "checkout_senior.py",
                "complexidade_media": 5.0,
                "tags_semanticas": ["button", "input"],
                "total_tags": 2,
                "total_divs": 5,
                "indice_semantico": 0.3,
                "consistencia_nomes": 0.7,
                "mensagens_erro_problematicas": ["Erro inesperado"],
                "loc": 320,
            },
        }

    def test_criterio_3_1_cruzamento_metricas_com_regras_60plus(self):
        """Critério 3.1: Deve cruzar métricas e identificar barreiras."""
        resultado = self.agent.execute(self.mock_context)
        self.assertEqual(resultado.status, StatusAgente.SUCESSO)
        barreiras = resultado.data.get("barreiras", [])
        self.assertGreater(len(barreiras), 0)

    def test_criterio_3_2_prever_quatro_categorias_de_barreiras(self):
        """Critério 3.2: Deve prever as 4 frentes (Percepção, Operação, Compreensão e Fluxo)."""
        resultado = self.agent.execute(self.mock_context)
        barreiras = resultado.data.get("barreiras", [])
        tipos_previstos = set(b.get("tipo") for b in barreiras)
        self.assertIn("percepção", tipos_previstos)
        self.assertIn("operação", tipos_previstos)
        self.assertIn("compreensão", tipos_previstos)
        self.assertIn("fluxo", tipos_previstos)
        self.assertGreaterEqual(len(tipos_previstos), 4)

    def test_criterio_3_3_gerar_relatorio_markdown_e_json(self):
        """Critério 3.3: Deve gerar relatório detalhado em Markdown e estrutura JSON."""
        resultado = self.agent.execute(self.mock_context)
        self.assertIn("relatorio_markdown", resultado.data)
        self.assertIn("# Relatório Preditivo de Acessibilidade 60+", resultado.data["relatorio_markdown"])
        self.assertIn("ODS 10", resultado.data["relatorio_markdown"])
        self.assertIn("barreiras", resultado.data)

    def test_criterio_3_4_sugestao_correcao_para_todas_barreiras(self):
        """Critério 3.4: Cada barreira prevista deve possuir recomendação acionável."""
        resultado = self.agent.execute(self.mock_context)
        barreiras = resultado.data.get("barreiras", [])
        for b in barreiras:
            self.assertTrue(bool(b.get("sugestao_correcao")), f"Barreira sem sugestão: {b}")

    def test_criterio_3_5_tempo_analise_menor_que_30_segundos(self):
        """Critério 3.5: Tempo de análise deve ser <= 30 segundos."""
        resultado = self.agent.execute(self.mock_context)
        tempo = resultado.data.get("tempo_analise_segundos", 999)
        self.assertLessEqual(tempo, 30.0)

    def test_padrao_factory_method(self):
        """Padrão Factory Method (GoF): PredictorFactory deve instanciar preditores corretos."""
        p_perc = PredictorFactory.create(TipoBarreira.PERCEPCAO)
        p_oper = PredictorFactory.create(TipoBarreira.OPERACAO)
        p_comp = PredictorFactory.create(TipoBarreira.COMPREENSAO)
        p_flux = PredictorFactory.create(TipoBarreira.FLUXO)

        self.assertIsInstance(p_perc, PercepcaoPredictor)
        self.assertIsInstance(p_oper, OperacaoPredictor)
        self.assertIsInstance(p_comp, CompreensaoPredictor)
        self.assertIsInstance(p_flux, FluxoPredictor)

    def test_padrao_decorator(self):
        """Padrão Decorator (GoF): RuleDecorator deve estender regras dinamicamente."""
        preditor_base = PercepcaoPredictor()
        regras_extras = [
            {"id": "TESTE-01", "descricao": "Regra customizada", "sugestao": "Ajustar", "severidade": "alta"}
        ]
        decorado = RuleDecorator(preditor_base, regras_extras)
        self.assertIsInstance(decorado, BasePredictor)

    def test_execucao_autonoma_arquivo_direto(self):
        """Agente 3 deve funcionar sozinho passando diretamente um arquivo de código."""
        resultado = self.agent.execute({"arquivo": str(BASE_DIR / "sample_ergane_module.py")})
        self.assertEqual(resultado.status, StatusAgente.SUCESSO)
        self.assertGreater(resultado.data["total_barreiras_previstas"], 0)


if __name__ == "__main__":
    unittest.main()
