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
from api.evaluation.metrics import Evaluator, verificar_fabricacao, sobrenomes_do_acervo

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
versao_corpus = dados_seed.get("versao", "")
repo_inmemory.carregar_dados(nos_iniciais, arestas_iniciais, versao_corpus)

repo_neo4j = Neo4jGraphRepository()
neo4j_conectado = repo_neo4j.conectar()
if neo4j_conectado:
    repo_neo4j.carregar_dados(nos_iniciais, arestas_iniciais, versao_corpus)

repo_ativo = repo_neo4j if neo4j_conectado else repo_inmemory

gemini_service = GeminiService()
traversal_engine = GraphTraversalEngine(repo_ativo, gemini_service)
traversal_engine_inmemory = GraphTraversalEngine(repo_inmemory, gemini_service)
sobrenomes = sobrenomes_do_acervo(nos_iniciais)


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    use_neo4j: Optional[bool] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "mecanismo_grafo": "Neo4j" if repo_ativo.is_connected else "Grafo em memória (NetworkX)",
        "versao_acervo": versao_corpus,
        "nos_carregados": len(nos_iniciais),
        "arestas_carregadas": len(arestas_iniciais),
        "estudos": sum(1 for n in nos_iniciais if n.tipo == TipoNo.ESTUDO),
        "gemini_api_ativa": bool(gemini_service.api_key),
    }


@app.get("/api/ontology")
def get_ontology():
    return {
        "nos": [n.model_dump() for n in nos_iniciais],
        "arestas": [a.model_dump() for a in arestas_iniciais],
    }


@app.post("/api/query")
def execute_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="A consulta não pode ser vazia.")

    engine = traversal_engine
    if req.use_neo4j is not None:
        escolhido = repo_neo4j if (req.use_neo4j and repo_neo4j.is_connected) else repo_inmemory
        engine = GraphTraversalEngine(escolhido, gemini_service)

    subgrafo, alternativas = engine.executar_recuperacao(req.query, top_k_entrada=req.top_k)
    sintese = gemini_service.formatar_sintese(req.query, alternativas, subgrafo)
    conferencia = verificar_fabricacao(sintese["texto"], alternativas, sobrenomes)

    return {
        "consulta": req.query,
        "resumo": sintese["texto"],
        "resumo_origem": sintese["origem"],
        "conferencia_resumo": conferencia,
        "alternativas": [alt.model_dump() for alt in alternativas],
        "subgrafo": {
            "nos_entrada": [n.model_dump() for n in subgrafo.nos_entrada],
            "total_nos": len(subgrafo.nos_recuperados),
            "total_arestas": len(subgrafo.arestas),
        },
    }


@app.post("/api/evaluate")
def run_evaluation():
    # Avaliação usa modo local (n-gram) para caber no timeout serverless de 60 s.
    # O ranking do grafo é avaliado sem chamadas externas ao Gemini.
    svc_local = GeminiService()
    svc_local._api_desabilitada = True  # bloqueia qualquer chamada HTTP ao Gemini
    svc_local.api_key = None            # garante que limiar_padrao use LIMIAR_SIMILARIDADE_LOCAL
    engine_local = GraphTraversalEngine(repo_inmemory, svc_local)
    return Evaluator.avaliar_banco_completo(engine_local, caminho_testes)
