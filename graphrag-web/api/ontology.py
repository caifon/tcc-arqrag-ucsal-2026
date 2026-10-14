from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TipoNo(str, Enum):
    ESTUDO = "Estudo"
    TECNICA = "Tecnica"
    METRICA_AVALIACAO = "MetricaAvaliacao"
    LIMITACAO = "Limitacao"
    CENARIO_DECISAO = "CenarioDecisao"
    ESTRATEGIA = "EstrategiaRecuperacao"
    SNIPPET = "Snippet"


class TipoAresta(str, Enum):
    USA = "USA"
    APLICADO_EM = "APLICADO_EM"
    AVALIADO_POR = "AVALIADO_POR"
    POSSUI_LIMITACAO = "POSSUI_LIMITACAO"
    EVIDENCIA_TEXTUAL = "EVIDENCIA_TEXTUAL"
    UTILIZA_ESTRATEGIA = "UTILIZA_ESTRATEGIA"


class NoGrafo(BaseModel):
    id: str
    tipo: TipoNo
    nome: str
    descricao: str
    metadados: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class ArestaGrafo(BaseModel):
    origem_id: str
    destino_id: str
    tipo: TipoAresta
    peso: float = 1.0
    descricao: Optional[str] = None


class SubgrafoEvidencia(BaseModel):
    nos_entrada: List[NoGrafo]
    nos_recuperados: List[NoGrafo]
    arestas: List[ArestaGrafo]
    snippets: List[Dict[str, Any]] = Field(default_factory=list)


class PassoRotaCausal(BaseModel):
    tipo: str
    rotulo: str
    detalhe: str


class AlternativaDecisao(BaseModel):
    tecnica_nome: str
    descricao: str
    estudos_apoio: List[str]
    estrategias: List[str]
    metricas_avaliacao: List[str] = Field(default_factory=list)
    limitacoes: List[str]
    trechos_evidencia: List[Dict[str, Any]]
    score_relevancia: float
    rota_causal: List[PassoRotaCausal] = Field(default_factory=list)
