"""
Suíte de Testes Automatizados (unittest) do Ecossistema Ergane.

Permite execução via standard test runner:
`python3 -m unittest discover tests`
"""

import unittest
from pathlib import Path

from ergane_agents.harness.orchestrator import ErganePipelineOrchestrator
from ergane_agents.harness.test_harness import CODIGO_EXEMPLO_TESTE, ErganeTestHarness


class TestErganeEcosystem(unittest.TestCase):
    """Testes automatizados cobrindo os 5 agentes e critérios da Entrega 2."""

    @classmethod
    def setUpClass(cls):
        cls.orchestrator = ErganePipelineOrchestrator(output_dir="./output")
        cls.harness = ErganeTestHarness(cls.orchestrator)
        cls.test_results = cls.harness.run_all_tests()

    def test_taxa_sucesso_geral(self):
        """Todos os 24 critérios de aceitação devem ser cumpridos (100%)."""
        self.assertEqual(
            self.test_results["taxa_sucesso_percentual"],
            100.0,
            f"Critérios com falha: {[t for t in self.test_results['scorecard'] if not t['passou']]}",
        )

    def test_agente1_documentacao(self):
        """Agente 1 deve calcular métricas e gerar guia com >= 8 erros."""
        res = self.orchestrator.agent1_doc.execute({"codigo": CODIGO_EXEMPLO_TESTE})
        self.assertIn("metricas", res.data)
        self.assertGreaterEqual(res.data.get("total_erros_catalogados", 0), 8)

    def test_agente2_validacao(self):
        """Agente 2 deve analisar sintaxe, CC, e erros problemáticos."""
        res = self.orchestrator.agent2_val.execute({"codigo": CODIGO_EXEMPLO_TESTE})
        self.assertIn("metricas_estruturais", res.data)
        self.assertLessEqual(res.data["tempo_analise_segundos"], 30.0)

    def test_agente3_acessibilidade(self):
        """Agente 3 deve prever barreiras nas 4 frentes 60+."""
        ctx = {
            "doc_metrics": {"indice_flesch": 25.0, "jargoes_detectados": ["api", "payload"]},
            "struct_metrics": {"tags_semanticas": ["div"], "indice_semantico": 0.1, "complexidade_media": 5.0, "total_divs": 10},
        }
        res = self.orchestrator.agent3_acess.execute(ctx)
        tipos = set(b["tipo"] for b in res.data["barreiras"])
        self.assertGreaterEqual(len(tipos), 2)

    def test_agente4_testes_persona_senior(self):
        """Agente 4 deve simular Sr. José e cumprir metas de recuperação."""
        res = self.orchestrator.agent4_test.execute({})
        stats = res.data["estatisticas"]
        self.assertTrue(stats["casos_tecnicos"]["conformidade_meta"])
        self.assertTrue(stats["casos_financeiros"]["conformidade_meta"])

    def test_agente5_gestao_priorizacao_financeira(self):
        """Agente 5 deve priorizar tarefas financeiras no topo (P1)."""
        res = self.orchestrator.agent5_gestao.execute({})
        top1 = res.data["prioridades"][0]
        self.assertIn("P1", top1)


if __name__ == "__main__":
    unittest.main()
