"""
Avaliação do MVP (Seção de Métricas da Metodologia).

Tudo aqui é CALCULADO a cada execução; nenhum valor é fixo no código.

- Hit rate: em perguntas que têm resposta conhecida, proporção dos estudos esperados que
  apareceram nas alternativas exibidas.
- Precisão: das alternativas exibidas, quantas eram esperadas (mede "trazer coisa a mais").
- Abstenção correta: em perguntas FORA do escopo dos estudos, proporção em que o sistema
  respondeu que não encontrou nada (em vez de inventar uma relação).
- Taxa de fabricação: proporção de afirmações verificáveis do resumo (números, autores citados
  e trechos entre aspas) que NÃO estão nos dados recuperados do grafo.
- Comparação: as mesmas perguntas são respondidas por uma busca só por similaridade de texto,
  sem caminhar no grafo (estilo RAG vetorial simples), para servir de referência.
"""
import json
import re
import unicodedata
from typing import List, Dict, Any, Iterable

from api.ontology import TipoNo, AlternativaDecisao, NoGrafo
from api.engine.traversal import GraphTraversalEngine


# ---------------------------------------------------------------------------
# Verificação de fabricação
# ---------------------------------------------------------------------------
def _norm(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", texto)


def _numeros(texto: str) -> List[str]:
    return re.findall(r"(?<![\w.,])\d+(?:[.,]\d+)?(?![\w])", texto)


def _para_float(n: str) -> float:
    return float(n.replace(",", "."))


def _textos_permitidos(alternativas: Iterable[AlternativaDecisao]) -> str:
    partes: List[str] = []
    for a in alternativas:
        partes += [a.tecnica_nome, a.descricao] + a.cenarios + a.estrategias + a.metricas_avaliacao + a.limitacoes
        partes += [t.get("texto", "") for t in a.trechos_evidencia]
        if a.estudo:
            partes += [a.estudo.titulo, a.estudo.autores, str(a.estudo.ano or ""), a.estudo.veiculo]
    return " ".join(partes)


def sobrenomes_do_acervo(nos: Iterable[NoGrafo]) -> Dict[str, set]:
    """Mapa sobrenome -> conjunto de ids de estudos com esse autor."""
    mapa: Dict[str, set] = {}
    for n in nos:
        if n.tipo == TipoNo.ESTUDO:
            for nome in re.split(r",| e | and |;", str((n.metadados or {}).get("autores", ""))):
                nome = nome.replace("et al.", "").strip()
                if len(nome) >= 3:
                    mapa.setdefault(nome, set()).add(n.id)
    return mapa


def verificar_fabricacao(texto: str, alternativas: List[AlternativaDecisao], sobrenomes: Dict[str, Any]) -> Dict[str, Any]:
    permitido = _textos_permitidos(alternativas)
    permitido_norm = _norm(permitido)
    numeros_permitidos = {_para_float(n) for n in _numeros(permitido)}
    numeros_permitidos.add(float(len(alternativas)))  # o resumo pode dizer quantas abordagens foram encontradas
    estudos_exibidos = {a.estudo.id for a in alternativas if a.estudo}

    itens = []
    for n in _numeros(texto):
        itens.append({"tipo": "número", "valor": n, "suportado": _para_float(n) in numeros_permitidos})
    for sobrenome, estudo_ids in sobrenomes.items():
        if re.search(rf"\b{re.escape(sobrenome)}\b", texto):
            if isinstance(estudo_ids, (set, list, tuple)):
                suportado = bool(set(estudo_ids) & estudos_exibidos)
            else:
                suportado = estudo_ids in estudos_exibidos
            itens.append({"tipo": "autor", "valor": sobrenome, "suportado": suportado})
    for citacao in re.findall(r"[\"“]([^\"”]{20,})[\"”]", texto):
        itens.append({"tipo": "citação", "valor": citacao[:60], "suportado": _norm(citacao) in permitido_norm})

    sem_suporte = [i for i in itens if not i["suportado"]]
    return {
        "itens_verificados": len(itens),
        "itens_sem_suporte": len(sem_suporte),
        "taxa": (len(sem_suporte) / len(itens)) if itens else 0.0,
        "detalhes_sem_suporte": sem_suporte,
    }


# ---------------------------------------------------------------------------
# Avaliação do banco de perguntas
# ---------------------------------------------------------------------------
class Evaluator:

    @staticmethod
    def _pontuar(esperados: List[str], recuperados: List[str]) -> Dict[str, Any]:
        esp, rec = set(esperados), set(recuperados)
        if not esp:  # pergunta fora do escopo: o certo é não trazer nada
            return {"hit_rate": None, "precisao": None, "abstencao_correta": len(rec) == 0}
        acertos = len(esp & rec)
        return {
            "hit_rate": acertos / len(esp),
            "precisao": (acertos / len(rec)) if rec else 0.0,
            "abstencao_correta": None,
        }

    @staticmethod
    def busca_so_similaridade(engine: GraphTraversalEngine, pergunta: str, top_k: int = 3) -> List[str]:
        """Referência sem grafo: compara a pergunta direto com estudos e trechos e devolve os estudos dos mais parecidos."""
        candidatos = [n for n in engine.repo.obter_todos_nos() if n.tipo in {TipoNo.ESTUDO, TipoNo.SNIPPET}]
        achados = engine.gemini_service.encontrar_nos_entrada(pergunta, candidatos, top_k=top_k)
        estudos = []
        for no, _ in achados:
            est = no.id if no.tipo == TipoNo.ESTUDO else (no.metadados or {}).get("estudo_id")
            if est and est not in estudos:
                estudos.append(est)
        return estudos

    @staticmethod
    def _media(valores: List[float]) -> float:
        valores = [v for v in valores if v is not None]
        return round(sum(valores) / len(valores), 4) if valores else 0.0

    @classmethod
    def avaliar_banco_completo(cls, engine: GraphTraversalEngine, caminho_testes: str) -> Dict[str, Any]:
        with open(caminho_testes, "r", encoding="utf-8") as f:
            cenarios = json.load(f)

        todos_nos = engine.repo.obter_todos_nos()
        sobrenomes = sobrenomes_do_acervo(todos_nos)

        # Pré-carrega embeddings em lote se a chave Gemini estiver ativa
        if engine.gemini_service.api_key and not getattr(engine.gemini_service, "_api_desabilitada", False):
            textos_nos = [engine.gemini_service.texto_do_no(n) for n in todos_nos]
            perguntas = [c["pergunta"] for c in cenarios]
            engine.gemini_service.obter_embeddings_lote(textos_nos + perguntas)

        detalhes = []
        total_itens = total_sem_suporte = 0
        for c in cenarios:
            _, alternativas = engine.executar_recuperacao(c["pergunta"])
            recuperados = [a.estudo.id for a in alternativas if a.estudo]
            pont = cls._pontuar(c["estudos_esperados"], recuperados)

            # Usa formatação determinística garantida para evitar 35+ chamadas síncronas de LLM e timeouts em serverless
            sintese = engine.gemini_service.formatar_sintese(c["pergunta"], alternativas, None, usar_llm=False)
            fab = verificar_fabricacao(sintese["texto"], alternativas, sobrenomes)
            total_itens += fab["itens_verificados"]
            total_sem_suporte += fab["itens_sem_suporte"]

            base_rec = cls.busca_so_similaridade(engine, c["pergunta"])
            pont_base = cls._pontuar(c["estudos_esperados"], base_rec)

            detalhes.append({
                "id": c["id"],
                "tipo": c.get("tipo", ""),
                "pergunta": c["pergunta"],
                "estudos_esperados": c["estudos_esperados"],
                "estudos_recuperados": recuperados,
                **pont,
                "fabricacao": {k: fab[k] for k in ("itens_verificados", "itens_sem_suporte", "detalhes_sem_suporte")},
                "referencia_sem_grafo": {"estudos_recuperados": base_rec, **pont_base},
            })

        com_resposta = [d for d in detalhes if d["estudos_esperados"]]
        fora_escopo = [d for d in detalhes if not d["estudos_esperados"]]

        def resumo(chave_fonte):
            fonte = (lambda d: d) if chave_fonte is None else (lambda d: d[chave_fonte])
            return {
                "hit_rate_medio": cls._media([fonte(d)["hit_rate"] for d in com_resposta]),
                "precisao_media": cls._media([fonte(d)["precisao"] for d in com_resposta]),
                "abstencao_correta": cls._media([1.0 if fonte(d)["abstencao_correta"] else 0.0 for d in fora_escopo]),
            }

        return {
            "total_cenarios": len(detalhes),
            "perguntas_com_resposta": len(com_resposta),
            "perguntas_fora_do_escopo": len(fora_escopo),
            "modo_similaridade": engine.gemini_service.ultimo_modo,
            "graphrag": {
                **resumo(None),
                "taxa_fabricacao": round(total_sem_suporte / total_itens, 4) if total_itens else 0.0,
                "afirmacoes_verificadas": total_itens,
            },
            "referencia_sem_grafo": resumo("referencia_sem_grafo"),
            "detalhes": detalhes,
        }
