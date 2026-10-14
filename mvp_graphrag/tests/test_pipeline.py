import unittest
import os
import json
from mvp_graphrag.ontology import NoGrafo, ArestaGrafo
from mvp_graphrag.graph.inmemory_adapter import InMemoryGraphRepository
from mvp_graphrag.engine.embeddings import LightweightEmbeddingEngine
from mvp_graphrag.engine.traversal import GraphTraversalEngine
from mvp_graphrag.evaluation.metrics import Evaluator


class TestGraphRAGPipeline(unittest.TestCase):

    def setUp(self):
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_seed = os.path.join(caminho_base, "data", "seed_corpus.json")
        with open(caminho_seed, "r", encoding="utf-8") as f:
            dados = json.load(f)

        self.nos = [NoGrafo(**item) for item in dados["nos"]]
        self.arestas = [ArestaGrafo(**item) for item in dados["arestas"]]

        self.repo = InMemoryGraphRepository()
        self.repo.carregar_dados(self.nos, self.arestas)
        self.embedding_engine = LightweightEmbeddingEngine()
        self.traversal_engine = GraphTraversalEngine(self.repo, self.embedding_engine)

    def test_carga_grafo(self):
        self.assertGreater(len(self.repo.obter_todos_nos()), 0)

    def test_recuperacao_sintese_global(self):
        query = "síntese temática global de grandes coleções"
        subgrafo, alternativas = self.traversal_engine.executar_recuperacao(query, top_k_entrada=2, max_saltos=2)
        self.assertGreater(len(subgrafo.nos_recuperados), 0)
        self.assertGreater(len(alternativas), 0)
        nomes_tecnicas = [alt.tecnica_nome for alt in alternativas]
        # Esperado que a técnica hierárquica por comunidades apareça
        self.assertTrue(any("Hierárquico" in nome or "Microsoft" in nome for nome in nomes_tecnicas))

    def test_recuperacao_multi_hop(self):
        query = "raciocínio multi-hop conectando entidades distantes"
        subgrafo, alternativas = self.traversal_engine.executar_recuperacao(query, top_k_entrada=2, max_saltos=2)
        nomes_tecnicas = [alt.tecnica_nome for alt in alternativas]
        self.assertTrue(any("HippoRAG" in nome or "GRAG" in nome for nome in nomes_tecnicas))

    def test_banco_avaliador_metricas(self):
        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_testes = os.path.join(caminho_base, "data", "test_scenarios.json")
        relatorio = Evaluator.avaliar_banco_completo(self.traversal_engine, caminho_testes)
        self.assertEqual(relatorio["total_cenarios"], 20)
        self.assertGreater(relatorio["hit_rate_medio"], 0.70)
        self.assertEqual(relatorio["taxa_fabricacao_media"], 0.0)


if __name__ == "__main__":
    unittest.main()
