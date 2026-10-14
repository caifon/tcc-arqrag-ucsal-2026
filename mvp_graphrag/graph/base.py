from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from mvp_graphrag.ontology import NoGrafo, ArestaGrafo, SubgrafoEvidencia, TipoNo


class BaseGraphRepository(ABC):
    """Interface abstrata para persistência e travessia do Grafo de Conhecimento."""

    @abstractmethod
    def carregar_dados(self, nos: List[NoGrafo], arestas: List[ArestaGrafo]) -> None:
        """Popula o grafo com os nós e arestas da ontologia."""
        pass

    @abstractmethod
    def obter_todos_nos(self, tipo: Optional[TipoNo] = None) -> List[NoGrafo]:
        """Retorna todos os nós ou nós filtrados por tipo."""
        pass

    @abstractmethod
    def obter_no_por_id(self, no_id: str) -> Optional[NoGrafo]:
        """Retorna um nó específico pelo identificador."""
        pass

    @abstractmethod
    def buscar_vizinhos(self, no_id: str, max_saltos: int = 2) -> SubgrafoEvidencia:
        """Realiza a expansão tipada de 1 a 2 saltos a partir de um nó-raiz."""
        pass

    @abstractmethod
    def buscar_subgrafo_multi_nos(self, nos_ids: List[str], max_saltos: int = 2) -> SubgrafoEvidencia:
        """Expande as conexões a partir de uma lista de nós de entrada (Top-K)."""
        pass
