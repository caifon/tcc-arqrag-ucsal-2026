from typing import List, Tuple, Dict, Any
from mvp_graphrag.graph.base import BaseGraphRepository
from mvp_graphrag.engine.embeddings import LightweightEmbeddingEngine
from mvp_graphrag.ontology import SubgrafoEvidencia, AlternativaDecisao, PassoRotaCausal, TipoNo, TipoAresta, NoGrafo


class GraphTraversalEngine:
    """
    Orquestrador da recuperação de acordo com a Seção 3.8 do documento metodológico:
    1. Pergunta na interface
    2. Ponto de Entrada (Embedding leve para encontrar o nó inicial)
    3. Busca no Grafo (expansão topológica de 1 a 2 saltos no Neo4j/grafo)
    4. Formatação Final (LLM apenas organiza e apresenta, sem inventar informações)
    """

    def __init__(self, repo: BaseGraphRepository, embedding_engine: LightweightEmbeddingEngine):
        self.repo = repo
        self.embedding_engine = embedding_engine

    def executar_recuperacao(self, query: str, top_k_entrada: int = 3, max_saltos: int = 2) -> Tuple[SubgrafoEvidencia, List[AlternativaDecisao]]:
        todos_nos = self.repo.obter_todos_nos()
        candidatos = [
            no for no in todos_nos 
            if no.tipo in {TipoNo.CENARIO_DECISAO, TipoNo.TECNICA, TipoNo.ESTRATEGIA, TipoNo.ESTUDO, TipoNo.METRICA_AVALIACAO}
        ]
        
        # Etapa 2: Ponto de Entrada via modelo leve de embedding
        nos_ranqueados = self.embedding_engine.encontrar_nos_entrada(query, candidatos, top_k=top_k_entrada)
        if not nos_ranqueados:
            nos_ranqueados = [(candidatos[0], 0.1)] if candidatos else []

        nos_ids_entrada = [no.id for no, _ in nos_ranqueados]
        scores_entrada = {no.id: score for no, score in nos_ranqueados}

        # Etapa 3: Busca no Grafo (expansão de 1 a 2 saltos)
        subgrafo = self.repo.buscar_subgrafo_multi_nos(nos_ids_entrada, max_saltos=max_saltos)
        alternativas = self._construir_alternativas(subgrafo, scores_entrada, nos_ids_entrada)

        return subgrafo, alternativas

    def _construir_alternativas(self, subgrafo: SubgrafoEvidencia, scores_entrada: Dict[str, float], nos_ids_entrada: List[str]) -> List[AlternativaDecisao]:
        mapa_nos: Dict[str, NoGrafo] = {no.id: no for no in subgrafo.nos_recuperados}
        tecnicas: List[NoGrafo] = [no for no in subgrafo.nos_recuperados if no.tipo == TipoNo.TECNICA]

        estudos_por_tecnica: Dict[str, List[str]] = {t.id: [] for t in tecnicas}
        estrategias_por_tecnica: Dict[str, List[str]] = {t.id: [] for t in tecnicas}
        metricas_por_tecnica: Dict[str, List[str]] = {t.id: [] for t in tecnicas}
        limitacoes_por_tecnica: Dict[str, List[str]] = {t.id: [] for t in tecnicas}
        snippets_por_estudo: Dict[str, List[dict]] = {}

        # 1. Mapear snippets (evidências textuais literais)
        for aresta in subgrafo.arestas:
            if aresta.tipo == TipoAresta.EVIDENCIA_TEXTUAL:
                if aresta.origem_id not in snippets_por_estudo:
                    snippets_por_estudo[aresta.origem_id] = []
                snippet_no = mapa_nos.get(aresta.destino_id)
                if snippet_no:
                    snippets_por_estudo[aresta.origem_id].append({
                        "id": snippet_no.id,
                        "titulo": snippet_no.nome,
                        "texto": snippet_no.descricao,
                        "pagina": snippet_no.metadados.get("pagina", "")
                    })

        # 2. Mapear arestas das técnicas (USA, AVALIADO_POR, POSSUI_LIMITACAO, UTILIZA_ESTRATEGIA)
        for aresta in subgrafo.arestas:
            tipo_val = aresta.tipo.value if hasattr(aresta.tipo, "value") else str(aresta.tipo)

            # Estudo -> USA -> Tecnica
            if tipo_val in {"USA", "USA_TECNICA"}:
                if aresta.destino_id in estudos_por_tecnica:
                    estudo_no = mapa_nos.get(aresta.origem_id)
                    if estudo_no:
                        autor_ano = f"{estudo_no.nome} ({estudo_no.metadados.get('autores', '')}, {estudo_no.metadados.get('ano', '')})"
                        if autor_ano not in estudos_por_tecnica[aresta.destino_id]:
                            estudos_por_tecnica[aresta.destino_id].append(autor_ano)

            # Tecnica -> UTILIZA_ESTRATEGIA -> Estrategia
            elif tipo_val == "UTILIZA_ESTRATEGIA":
                if aresta.origem_id in estrategias_por_tecnica:
                    est_no = mapa_nos.get(aresta.destino_id)
                    if est_no:
                        item = f"{est_no.nome}: {est_no.descricao}"
                        if item not in estrategias_por_tecnica[aresta.origem_id]:
                            estrategias_por_tecnica[aresta.origem_id].append(item)

            # Tecnica -> AVALIADO_POR -> MetricaAvaliacao (Seção 3.5 do PDF)
            elif tipo_val == "AVALIADO_POR":
                if aresta.origem_id in metricas_por_tecnica:
                    met_no = mapa_nos.get(aresta.destino_id)
                    if met_no:
                        item = f"{met_no.nome} ({met_no.descricao})"
                        if item not in metricas_por_tecnica[aresta.origem_id]:
                            metricas_por_tecnica[aresta.origem_id].append(item)

            # Tecnica -> POSSUI_LIMITACAO -> Limitacao
            elif tipo_val == "POSSUI_LIMITACAO":
                if aresta.origem_id in limitacoes_por_tecnica:
                    lim_no = mapa_nos.get(aresta.destino_id)
                    if lim_no:
                        item = f"{lim_no.nome}: {lim_no.descricao}"
                        if item not in limitacoes_por_tecnica[aresta.origem_id]:
                            limitacoes_por_tecnica[aresta.origem_id].append(item)

        # 3. Montar alternativas comparativas
        alternativas = []
        for t in tecnicas:
            trechos = []
            for aresta in subgrafo.arestas:
                tipo_val = aresta.tipo.value if hasattr(aresta.tipo, "value") else str(aresta.tipo)
                if tipo_val in {"USA", "USA_TECNICA"} and aresta.destino_id == t.id:
                    estudo_id = aresta.origem_id
                    if estudo_id in snippets_por_estudo:
                        trechos.extend(snippets_por_estudo[estudo_id])

            score = scores_entrada.get(t.id, 0.5)
            for aresta in subgrafo.arestas:
                if aresta.origem_id == t.id and aresta.destino_id in scores_entrada:
                    score = max(score, scores_entrada[aresta.destino_id])
                elif aresta.destino_id == t.id and aresta.origem_id in scores_entrada:
                    score = max(score, scores_entrada[aresta.origem_id])

            # Rota Causal / Caminho de Decisão Explicável no Grafo
            rota = []
            no_entrada_ref = next((mapa_nos[nid] for nid in nos_ids_entrada if nid in mapa_nos and mapa_nos[nid].tipo == TipoNo.CENARIO_DECISAO), None)
            if not no_entrada_ref and nos_ids_entrada:
                no_entrada_ref = mapa_nos.get(nos_ids_entrada[0])

            if no_entrada_ref:
                rota.append(PassoRotaCausal(
                    tipo="Entrada",
                    rotulo=f"Nó de Entrada ({no_entrada_ref.tipo.value})",
                    detalhe=no_entrada_ref.nome
                ))

            rota.append(PassoRotaCausal(
                tipo="Aresta",
                rotulo="[APLICADO_EM / VINCULADO_A]",
                detalhe="Expansão topológica (1 salto)"
            ))

            rota.append(PassoRotaCausal(
                tipo="Tecnica",
                rotulo=f"Técnica de Recuperação ({t.nome})",
                detalhe=t.descricao
            ))

            if metricas_por_tecnica.get(t.id):
                rota.append(PassoRotaCausal(
                    tipo="Aresta",
                    rotulo="[AVALIADO_POR]",
                    detalhe=metricas_por_tecnica[t.id][0]
                ))

            if limitacoes_por_tecnica.get(t.id):
                rota.append(PassoRotaCausal(
                    tipo="Limitacao",
                    rotulo="[POSSUI_LIMITACAO]",
                    detalhe=limitacoes_por_tecnica[t.id][0]
                ))

            if trechos:
                rota.append(PassoRotaCausal(
                    tipo="Snippet",
                    rotulo="[EVIDENCIA_TEXTUAL]",
                    detalhe=trechos[0]["texto"][:140] + "..."
                ))

            alternativas.append(AlternativaDecisao(
                tecnica_nome=t.nome,
                descricao=t.descricao,
                estudos_apoio=estudos_por_tecnica.get(t.id, []),
                estrategias=estrategias_por_tecnica.get(t.id, []),
                metricas_avaliacao=metricas_por_tecnica.get(t.id, []),
                limitacoes=limitacoes_por_tecnica.get(t.id, []),
                trechos_evidencia=trechos,
                score_relevancia=round(score, 3),
                rota_causal=rota
            ))

        alternativas.sort(key=lambda x: x.score_relevancia, reverse=True)
        return alternativas
