import os
import logging
from typing import List, Optional
from api.graph.base import BaseGraphRepository
from api.ontology import NoGrafo, ArestaGrafo, SubgrafoEvidencia, TipoNo

logger = logging.getLogger(__name__)


class Neo4jGraphRepository(BaseGraphRepository):
    """Adaptador oficial para Neo4j (Local ou Neo4j AuraDB na nuvem)."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self._driver = None
        self._conectado = False

    def conectar(self) -> bool:
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._driver.verify_connectivity()
            self._conectado = True
            logger.info("Conectado com sucesso ao Neo4j!")
            return True
        except Exception as e:
            logger.warning(f"Neo4j indisponível ({self.uri}): {e}. Operando com fallback in-memory.")
            self._conectado = False
            return False

    @property
    def is_connected(self) -> bool:
        return self._conectado

    def carregar_dados(self, nos: List[NoGrafo], arestas: List[ArestaGrafo]) -> None:
        if not self._conectado:
            return

        with self._driver.session() as session:
            for no in nos:
                session.run(
                    f"""
                    MERGE (n:{no.tipo.value} {{id: $id}})
                    SET n.nome = $nome, n.descricao = $descricao, n.metadados = $metadados
                    """,
                    id=no.id,
                    nome=no.nome,
                    descricao=no.descricao,
                    metadados=str(no.metadados)
                )

            for aresta in arestas:
                session.run(
                    f"""
                    MATCH (a {{id: $origem_id}}), (b {{id: $destino_id}})
                    MERGE (a)-[r:{aresta.tipo.value}]->(b)
                    SET r.peso = $peso
                    """,
                    origem_id=aresta.origem_id,
                    destino_id=aresta.destino_id,
                    peso=aresta.peso
                )

    def obter_todos_nos(self, tipo: Optional[TipoNo] = None) -> List[NoGrafo]:
        if not self._conectado:
            return []
        nos = []
        with self._driver.session() as session:
            query = f"MATCH (n:{tipo.value}) RETURN n" if tipo else "MATCH (n) RETURN n, labels(n) as lbls"
            result = session.run(query)
            for record in result:
                n = record["n"]
                tipo_no = tipo if tipo else TipoNo(record["lbls"][0])
                nos.append(NoGrafo(
                    id=n["id"],
                    tipo=tipo_no,
                    nome=n.get("nome", ""),
                    descricao=n.get("descricao", "")
                ))
        return nos

    def obter_no_por_id(self, no_id: str) -> Optional[NoGrafo]:
        if not self._conectado:
            return None
        with self._driver.session() as session:
            result = session.run("MATCH (n {id: $id}) RETURN n, labels(n) as lbls", id=no_id)
            record = result.single()
            if record:
                n = record["n"]
                return NoGrafo(
                    id=n["id"],
                    tipo=TipoNo(record["lbls"][0]),
                    nome=n.get("nome", ""),
                    descricao=n.get("descricao", "")
                )
        return None

    def buscar_vizinhos(self, no_id: str, max_saltos: int = 2) -> SubgrafoEvidencia:
        return self.buscar_subgrafo_multi_nos([no_id], max_saltos=max_saltos)

    def buscar_subgrafo_multi_nos(self, nos_ids: List[str], max_saltos: int = 2) -> SubgrafoEvidencia:
        if not self._conectado:
            return SubgrafoEvidencia(nos_entrada=[], nos_recuperados=[], arestas=[], snippets=[])

        nos_recuperados = {}
        arestas = []
        snippets = []

        with self._driver.session() as session:
            query = f"""
            MATCH (start) WHERE start.id IN $nos_ids
            MATCH path = (start)-[r*1..{max_saltos}]-(target)
            UNWIND nodes(path) as n
            UNWIND relationships(path) as rel
            RETURN DISTINCT n, labels(n) as lbls, startNode(rel).id as o_id, endNode(rel).id as d_id, type(rel) as rel_tipo
            """
            result = session.run(query, nos_ids=nos_ids)
            for record in result:
                n = record["n"]
                nid = n["id"]
                if nid not in nos_recuperados:
                    tipo_str = record["lbls"][0] if record["lbls"] else "Tecnica"
                    try:
                        tipo_enum = TipoNo(tipo_str)
                    except ValueError:
                        tipo_enum = TipoNo.TECNICA

                    no_obj = NoGrafo(
                        id=nid,
                        tipo=tipo_enum,
                        nome=n.get("nome", ""),
                        descricao=n.get("descricao", "")
                    )
                    nos_recuperados[nid] = no_obj
                    if tipo_enum == TipoNo.SNIPPET:
                        snippets.append({
                            "id": nid,
                            "titulo": n.get("nome", ""),
                            "texto": n.get("descricao", ""),
                            "estudo_id": n.get("estudo_id", "")
                        })

        nos_entrada_objs = [nos_recuperados[nid] for nid in nos_ids if nid in nos_recuperados]

        return SubgrafoEvidencia(
            nos_entrada=nos_entrada_objs,
            nos_recuperados=list(nos_recuperados.values()),
            arestas=arestas,
            snippets=snippets
        )
