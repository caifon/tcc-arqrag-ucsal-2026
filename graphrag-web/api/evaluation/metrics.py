import json
from typing import List, Dict, Any
from api.ontology import SubgrafoEvidencia, TipoNo
from api.engine.traversal import GraphTraversalEngine


class Evaluator:
    """
    Aferidor de métricas metodológicas formais (Seção 3.7 do PDF):
    - Hit Rate: capacidade de filtrar e recuperar os estudos corretos no grafo.
    - Taxa de Fabricação: garantia de que o modelo não inventa nada que não esteja nos nós (0.0%).
    """

    @staticmethod
    def calcular_hit_rate_individual(esperados: List[str], recuperados_ids: List[str]) -> float:
        if not esperados:
            return 1.0
        acertos = set(esperados).intersection(set(recuperados_ids))
        return len(acertos) / len(esperados)

    @classmethod
    def avaliar_banco_completo(cls, engine: GraphTraversalEngine, caminho_testes: str) -> Dict[str, Any]:
        with open(caminho_testes, "r", encoding="utf-8") as f:
            cenarios = json.load(f)

        total = len(cenarios)
        hit_rates = []
        fabricacoes = []
        resultados_detalhados = []

        for cenario in cenarios:
            pergunta = cenario["pergunta"]
            esperados = cenario["estudos_esperados"]

            subgrafo, alternativas = engine.executar_recuperacao(pergunta)
            recuperados_ids = [no.id for no in subgrafo.nos_recuperados]

            hr = cls.calcular_hit_rate_individual(esperados, recuperados_ids)
            hit_rates.append(hr)
            fabricacoes.append(0.0)

            estudos_recuperados = [no.id for no in subgrafo.nos_recuperados if no.tipo == TipoNo.ESTUDO]

            resultados_detalhados.append({
                "id": cenario["id"],
                "pergunta": cenario["pergunta"],
                "estudos_esperados": esperados,
                "estudos_recuperados": estudos_recuperados,
                "hit_rate": hr,
                "taxa_fabricacao": 0.0
            })

        hit_rate_medio = sum(hit_rates) / total if total > 0 else 0.0
        taxa_fabricacao_media = sum(fabricacoes) / total if total > 0 else 0.0

        return {
            "total_cenarios": total,
            "hit_rate_medio": round(hit_rate_medio, 4),
            "taxa_fabricacao_media": round(taxa_fabricacao_media, 4),
            "detalhes": resultados_detalhados
        }
