import os
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.ontology import NoGrafo, ArestaGrafo, TipoNo
from api.graph.inmemory_adapter import InMemoryGraphRepository
from api.graph.neo4j_adapter import Neo4jGraphRepository
from api.engine.gemini_service import GeminiService
from api.engine.traversal import GraphTraversalEngine
from api.evaluation.metrics import Evaluator

app = FastAPI(
    title="GraphRAG Decision Support API",
    description="Microserviço Python Serverless para apoio à tomada de decisão via GraphRAG (UCSAL / TCC 2026)",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

caminho_base = os.path.dirname(os.path.abspath(__file__))
caminho_seed = os.path.join(caminho_base, "data", "seed_corpus.json")
caminho_testes = os.path.join(caminho_base, "data", "test_scenarios.json")

with open(caminho_seed, "r", encoding="utf-8") as f:
    dados_seed = json.load(f)

nos_iniciais = [NoGrafo(**item) for item in dados_seed["nos"]]
arestas_iniciais = [ArestaGrafo(**item) for item in dados_seed["arestas"]]

repo_inmemory = InMemoryGraphRepository()
repo_inmemory.carregar_dados(nos_iniciais, arestas_iniciais)

repo_neo4j = Neo4jGraphRepository()
neo4j_conectado = repo_neo4j.conectar()
if neo4j_conectado:
    repo_neo4j.carregar_dados(nos_iniciais, arestas_iniciais)

repo_ativo = repo_neo4j if neo4j_conectado else repo_inmemory

gemini_service = GeminiService()
traversal_engine = GraphTraversalEngine(repo_ativo, gemini_service)


class QueryRequest(BaseModel):
    query: str
    top_k: int = 2
    max_hops: int = 2
    use_neo4j: Optional[bool] = None
    comparar_baseline: bool = False


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "mecanismo_grafo": "Neo4j (AuraDB/Local)" if repo_ativo.is_connected else "Em Memória (NetworkX)",
        "nos_carregados": len(nos_iniciais),
        "arestas_carregadas": len(arestas_iniciais),
        "gemini_api_ativa": bool(gemini_service.api_key)
    }


@app.get("/api/ontology")
def get_ontology():
    return {
        "nos": [n.model_dump() for n in nos_iniciais],
        "arestas": [a.model_dump() for a in arestas_iniciais]
    }


@app.post("/api/query")
def execute_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="A consulta não pode ser vazia.")

    engine = traversal_engine
    if req.use_neo4j is not None:
        escolhido = repo_neo4j if (req.use_neo4j and repo_neo4j.is_connected) else repo_inmemory
        engine = GraphTraversalEngine(escolhido, gemini_service)

    # 1. Execução do GraphRAG
    subgrafo, alternativas = engine.executar_recuperacao(
        req.query, top_k_entrada=req.top_k, max_saltos=req.max_hops
    )
    sintese_formatada = gemini_service.formatar_sintese(req.query, alternativas, subgrafo)

    # 2. Execução do Baseline Vetorial Tradicional (sempre disponível para o Switch A/B instantâneo)
    baseline_data = engine.executar_baseline_vetorial(req.query, top_k=req.top_k)

    return {
        "consulta": req.query,
        "sintese_formatada": sintese_formatada,
        "alternativas": [alt.model_dump() for alt in alternativas],
        "subgrafo": {
            "nos_entrada": [n.model_dump() for n in subgrafo.nos_entrada],
            "nos_recuperados": [n.model_dump() for n in subgrafo.nos_recuperados],
            "arestas": [a.model_dump() for a in subgrafo.arestas],
            "snippets": subgrafo.snippets
        },
        "baseline_vetorial": baseline_data
    }


@app.post("/api/evaluate")
def run_evaluation():
    relatorio = Evaluator.avaliar_banco_completo(traversal_engine, caminho_testes)
    return relatorio
