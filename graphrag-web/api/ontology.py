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


class PassoCaminho(BaseModel):
    """Um passo do caminho no grafo que explica por que a alternativa apareceu."""
    tipo: str
    nome: str
    relacao: Optional[str] = None


class EstudoResumo(BaseModel):
    id: str
    titulo: str
    autores: str = ""
    ano: Optional[int] = None
    veiculo: str = ""


class AlternativaDecisao(BaseModel):
    tecnica_id: str
    tecnica_nome: str
    descricao: str
    estudo: Optional[EstudoResumo] = None
    cenarios: List[str] = Field(default_factory=list)
    estrategias: List[str] = Field(default_factory=list)
    metricas_avaliacao: List[str] = Field(default_factory=list)
    limitacoes: List[str] = Field(default_factory=list)
    trechos_evidencia: List[Dict[str, Any]] = Field(default_factory=list)
    caminho: List[PassoCaminho] = Field(default_factory=list)
