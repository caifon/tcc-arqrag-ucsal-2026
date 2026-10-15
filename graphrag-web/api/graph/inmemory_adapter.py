import networkx as nx
from typing import List, Optional, Set
from api.graph.base import BaseGraphRepository
from api.ontology import NoGrafo, ArestaGrafo, SubgrafoEvidencia, TipoNo, TipoAresta


class InMemoryGraphRepository(BaseGraphRepository):
    """Implementação em memória utilizando NetworkX."""

    def __init__(self):
        self.grafo = nx.MultiDiGraph()
        self.nos_dict: dict[str, NoGrafo] = {}
        self.arestas_lista: List[ArestaGrafo] = []

    @property
    def is_connected(self) -> bool:
        return False

    def carregar_dados(self, nos: List[NoGrafo], arestas: List[ArestaGrafo], versao: str = "") -> None:
        self.grafo.clear()
        self.nos_dict.clear()
        self.arestas_lista.clear()

        for no in nos:
            self.nos_dict[no.id] = no
            self.grafo.add_node(
                no.id,
                tipo=no.tipo.value,
                nome=no.nome,
                descricao=no.descricao,
                metadados=no.metadados
            )

        for aresta in arestas:
            self.arestas_lista.append(aresta)
            self.grafo.add_edge(
                aresta.origem_id,
                aresta.destino_id,
                tipo=aresta.tipo.value,
                peso=aresta.peso,
                descricao=aresta.descricao
            )

    def obter_todos_nos(self, tipo: Optional[TipoNo] = None) -> List[NoGrafo]:
        if tipo is None:
            return list(self.nos_dict.values())
        return [no for no in self.nos_dict.values() if no.tipo == tipo]

    def obter_no_por_id(self, no_id: str) -> Optional[NoGrafo]:
        return self.nos_dict.get(no_id)

    def buscar_vizinhos(self, no_id: str, max_saltos: int = 2) -> SubgrafoEvidencia:
        return self.buscar_subgrafo_multi_nos([no_id], max_saltos=max_saltos)

    def buscar_subgrafo_multi_nos(self, nos_ids: List[str], max_saltos: int = 2) -> SubgrafoEvidencia:
        if not nos_ids:
            return SubgrafoEvidencia(nos_entrada=[], nos_recuperados=[], arestas=[], snippets=[])

        grafo_undirected = self.grafo.to_undirected(as_view=True)
        nos_atingidos: Set[str] = set()

        for start_id in nos_ids:
            if start_id in self.grafo:
                nos_atingidos.add(start_id)
                distancias = nx.single_source_shortest_path_length(
                    grafo_undirected, source=start_id, cutoff=max_saltos
                )
                nos_atingidos.update(distancias.keys())

        nos_entrada_objs = [self.nos_dict[nid] for nid in nos_ids if nid in self.nos_dict]
        nos_recuperados_objs = [self.nos_dict[nid] for nid in nos_atingidos if nid in self.nos_dict]

        arestas_subgrafo: List[ArestaGrafo] = []
        for aresta in self.arestas_lista:
            if aresta.origem_id in nos_atingidos and aresta.destino_id in nos_atingidos:
                arestas_subgrafo.append(aresta)

        snippets = []
        for no in nos_recuperados_objs:
            if no.tipo == TipoNo.SNIPPET:
                snippets.append({
                    "id": no.id,
                    "titulo": no.nome,
                    "texto": no.descricao,
                    "estudo_id": no.metadados.get("estudo_id", ""),
                    "pagina": no.metadados.get("pagina", "")
                })

        return SubgrafoEvidencia(
            nos_entrada=nos_entrada_objs,
            nos_recuperados=nos_recuperados_objs,
            arestas=arestas_subgrafo,
            snippets=snippets
        )
