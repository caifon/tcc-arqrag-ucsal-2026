from abc import ABC, abstractmethod
from typing import List, Optional
from api.ontology import NoGrafo, ArestaGrafo, SubgrafoEvidencia, TipoNo


class BaseGraphRepository(ABC):

    @abstractmethod
    def carregar_dados(self, nos: List[NoGrafo], arestas: List[ArestaGrafo], versao: str = "") -> None:
        pass

    @abstractmethod
    def obter_todos_nos(self, tipo: Optional[TipoNo] = None) -> List[NoGrafo]:
        pass

    @abstractmethod
    def obter_no_por_id(self, no_id: str) -> Optional[NoGrafo]:
        pass

    @abstractmethod
    def buscar_vizinhos(self, no_id: str, max_saltos: int = 2) -> SubgrafoEvidencia:
        pass

    @abstractmethod
    def buscar_subgrafo_multi_nos(self, nos_ids: List[str], max_saltos: int = 2) -> SubgrafoEvidencia:
        pass
