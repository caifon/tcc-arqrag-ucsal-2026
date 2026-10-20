import os
from typing import List, Tuple, Dict, Any, Optional
from api.graph.base import BaseGraphRepository
from api.engine.gemini_service import GeminiService
from api.ontology import (
    SubgrafoEvidencia, AlternativaDecisao, PassoCaminho, EstudoResumo,
    TipoNo, TipoAresta, NoGrafo, ArestaGrafo,
)

ROTULO_TIPO = {
    TipoNo.ESTUDO: "Estudo",
    TipoNo.TECNICA: "Abordagem",
    TipoNo.CENARIO_DECISAO: "Cenário de decisão",
    TipoNo.ESTRATEGIA: "Estratégia de recuperação",
    TipoNo.METRICA_AVALIACAO: "Forma de avaliação",
    TipoNo.LIMITACAO: "Limitação",
    TipoNo.SNIPPET: "Trecho do artigo",
}


def _valor(tipo) -> str:
    return tipo.value if hasattr(tipo, "value") else str(tipo)


class GraphTraversalEngine:
    """
    Recuperação em 4 etapas (Metodologia do TCC):
    1. Pergunta do usuário.
    2. Porta de entrada: similaridade de texto (embedding) escolhe até `top_k` nós de entrada,
       desde que passem do limiar mínimo. Se nenhum passar, o sistema NÃO responde (abstenção).
    3. Caminho no grafo: de cada nó de entrada, o sistema segue as relações até chegar às
       abordagens (nós Técnica) ligadas a ele e depois reúne o contexto de cada abordagem
       (estudo, cenário, estratégias, avaliação, limitações e trechos literais).
    4. Formatação: o LLM só escreve um resumo com os dados recuperados (ver gemini_service).
    """

    def __init__(self, repo: BaseGraphRepository, gemini_service: GeminiService):
        self.repo = repo
        self.gemini_service = gemini_service

    # ------------------------------------------------------------------ #
    def executar_recuperacao(self, query: str, top_k_entrada: int = 3, max_saltos: int = 2,
                             limiar: Optional[float] = None) -> Tuple[SubgrafoEvidencia, List[AlternativaDecisao]]:
        candidatos = self.repo.obter_todos_nos()
        entradas = self.gemini_service.encontrar_nos_entrada(query, candidatos, top_k=top_k_entrada, threshold=limiar)

        if not entradas:
            return SubgrafoEvidencia(nos_entrada=[], nos_recuperados=[], arestas=[], snippets=[]), []

        # Etapa 3a: da entrada até as abordagens (no máximo 2 saltos: Trecho -> Estudo -> Abordagem)
        tecnicas_motivo: Dict[str, List[NoGrafo]] = {}
        for no_entrada, _ in entradas:
            for tec_id in self._tecnicas_alcancadas(no_entrada):
                tecnicas_motivo.setdefault(tec_id, []).append(no_entrada)

        # Etapa 3b: contexto de cada abordagem (1 salto a partir dela + trechos do estudo)
        nos_recuperados: Dict[str, NoGrafo] = {n.id: n for n, _ in entradas}
        arestas_recuperadas: Dict[str, ArestaGrafo] = {}
        snippets: List[Dict[str, Any]] = []
        alternativas: List[AlternativaDecisao] = []

        for tec_id, motivos in tecnicas_motivo.items():
            alt, sub = self._montar_alternativa(tec_id, motivos)
            if alt is None:
                continue
            alternativas.append(alt)
            for n in sub.nos_recuperados:
                nos_recuperados[n.id] = n
            for a in sub.arestas:
                arestas_recuperadas[f"{a.origem_id}|{_valor(a.tipo)}|{a.destino_id}"] = a
            snippets.extend(alt.trechos_evidencia)

        # Ordem neutra (por ano e título), sem ranking de "melhor alternativa".
        alternativas.sort(key=lambda a: (str(a.estudo.ano or "") if a.estudo else "", a.tecnica_nome))

        subgrafo = SubgrafoEvidencia(
            nos_entrada=[n for n, _ in entradas],
            nos_recuperados=list(nos_recuperados.values()),
            arestas=list(arestas_recuperadas.values()),
            snippets=snippets,
        )
        return subgrafo, alternativas

    # ------------------------------------------------------------------ #
    def _vizinhanca(self, no_id: str) -> SubgrafoEvidencia:
        return self.repo.buscar_subgrafo_multi_nos([no_id], max_saltos=1)

    def _tecnicas_alcancadas(self, no_entrada: NoGrafo) -> List[str]:
        if no_entrada.tipo == TipoNo.TECNICA:
            return [no_entrada.id]

        sub = self._vizinhanca(no_entrada.id)
        ids = [a.destino_id if a.origem_id == no_entrada.id else a.origem_id
               for a in sub.arestas if no_entrada.id in (a.origem_id, a.destino_id)]
        mapa = {n.id: n for n in sub.nos_recuperados}
        tecnicas = [i for i in ids if i in mapa and mapa[i].tipo == TipoNo.TECNICA]

        if no_entrada.tipo == TipoNo.SNIPPET:
            # Trecho -> Estudo -> Abordagem (2 saltos)
            for est_id in [i for i in ids if i in mapa and mapa[i].tipo == TipoNo.ESTUDO]:
                sub_est = self._vizinhanca(est_id)
                mapa_est = {n.id: n for n in sub_est.nos_recuperados}
                tecnicas += [a.destino_id for a in sub_est.arestas
                             if a.origem_id == est_id and _valor(a.tipo) == TipoAresta.USA.value
                             and a.destino_id in mapa_est]
        return list(dict.fromkeys(tecnicas))

    def _montar_alternativa(self, tec_id: str, motivos: List[NoGrafo]) -> Tuple[Optional[AlternativaDecisao], SubgrafoEvidencia]:
        sub = self._vizinhanca(tec_id)
        mapa = {n.id: n for n in sub.nos_recuperados}
        tec = mapa.get(tec_id)
        if tec is None:
            return None, sub

        estudo_no: Optional[NoGrafo] = None
        cenarios, estrategias, metricas, limitacoes = [], [], [], []
        for a in sub.arestas:
            t = _valor(a.tipo)
            if t == TipoAresta.USA.value and a.destino_id == tec_id and a.origem_id in mapa:
                estudo_no = mapa[a.origem_id]
            elif a.origem_id == tec_id and a.destino_id in mapa:
                alvo = mapa[a.destino_id]
                texto = f"{alvo.nome}: {alvo.descricao}"
                if t == TipoAresta.APLICADO_EM.value:
                    cenarios.append(texto)
                elif t == TipoAresta.UTILIZA_ESTRATEGIA.value:
                    estrategias.append(texto)
                elif t == TipoAresta.AVALIADO_POR.value:
                    metricas.append(texto)
                elif t == TipoAresta.POSSUI_LIMITACAO.value:
                    limitacoes.append(texto)

        trechos: List[Dict[str, Any]] = []
        estudo_resumo = None
        arestas_extra: List[ArestaGrafo] = []
        nos_extra: List[NoGrafo] = []
        if estudo_no is not None:
            md = estudo_no.metadados or {}
            estudo_resumo = EstudoResumo(
                id=estudo_no.id, titulo=estudo_no.nome, autores=str(md.get("autores", "")),
                ano=md.get("ano"),
                veiculo=str(md.get("veiculo", "")),
            )
            sub_est = self._vizinhanca(estudo_no.id)
            mapa_est = {n.id: n for n in sub_est.nos_recuperados}
            for a in sub_est.arestas:
                if a.origem_id == estudo_no.id and _valor(a.tipo) == TipoAresta.EVIDENCIA_TEXTUAL.value and a.destino_id in mapa_est:
                    sn = mapa_est[a.destino_id]
                    trechos.append({
                        "id": sn.id,
                        "texto": sn.descricao,
                        "pagina": (sn.metadados or {}).get("pagina", ""),
                        "estudo_id": estudo_no.id,
                    })
                    arestas_extra.append(a)
                    nos_extra.append(sn)

        caminho = self._caminho(motivos, tec, estudo_no)
        alt = AlternativaDecisao(
            tecnica_id=tec.id, tecnica_nome=tec.nome, descricao=tec.descricao, estudo=estudo_resumo,
            cenarios=cenarios, estrategias=estrategias, metricas_avaliacao=metricas,
            limitacoes=limitacoes, trechos_evidencia=trechos, caminho=caminho,
        )
        sub.nos_recuperados.extend(nos_extra)
        sub.arestas.extend(arestas_extra)
        return alt, sub

    def _caminho(self, motivos: List[NoGrafo], tec: NoGrafo, estudo: Optional[NoGrafo]) -> List[PassoCaminho]:
        passos = [PassoCaminho(tipo="Pergunta", nome="Sua pergunta")]
        entrada = motivos[0]
        passos.append(PassoCaminho(tipo=ROTULO_TIPO.get(entrada.tipo, _valor(entrada.tipo)), nome=entrada.nome,
                                   relacao="parecido com a pergunta"))
        if entrada.tipo == TipoNo.SNIPPET and estudo is not None:
            passos.append(PassoCaminho(tipo="Estudo", nome=estudo.nome, relacao="trecho do estudo"))
        if entrada.tipo != TipoNo.TECNICA:
            passos.append(PassoCaminho(tipo="Abordagem", nome=tec.nome, relacao="ligado à abordagem"))
        return passos
