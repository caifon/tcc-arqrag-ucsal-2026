import os
import re
import math
import json
import requests
from typing import List, Tuple, Optional, Dict, Any
from collections import Counter
from api.ontology import NoGrafo, AlternativaDecisao, SubgrafoEvidencia


class GeminiService:
    """
    Serviço unificado para Embeddings Leves e Formatação Estrita com LLM (Seções 3.4, 3.6 e 3.8 do PDF):
    - Embedding leve: usado estritamente como porta de entrada para encontrar o nó inicial.
    - LLM Formatador (gemini-2.5-flash / fallback estruturado): organiza e apresenta o que o grafo recuperou,
      sem inventar informações (taxa de fabricação = 0%) e sem recomendar escolha final (conforme Simon, 1960 e Seção 3.3).
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_key = key.strip() if key else None
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._cache_embeddings: Dict[str, List[float]] = {}
        self._api_desabilitada: bool = False
        self.ultimo_modo = "embedding" if self.api_key else "local"

    # ----------------- 1. EMBEDDINGS LEVES (PORTA DE ENTRADA) ----------------- #

    def _tokenizar_fallback(self, texto: str) -> List[str]:
        palavras = re.findall(r"\w+", texto.lower())
        ngrams = []
        for p in palavras:
            ngrams.append(p)
            if len(p) >= 4:
                for i in range(len(p) - 2):
                    ngrams.append(p[i:i + 3])
        return ngrams

    def _cosseno_fallback(self, tokens1: List[str], tokens2: List[str]) -> float:
        c1 = Counter(tokens1)
        c2 = Counter(tokens2)
        inter = set(c1.keys()).intersection(set(c2.keys()))
        dot = sum(c1[t] * c2[t] for t in inter)
        norm1 = math.sqrt(sum(v ** 2 for v in c1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in c2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def obter_embedding_gemini(self, texto: str) -> Optional[List[float]]:
        if not self.api_key or self._api_desabilitada:
            return None
        if texto in self._cache_embeddings:
            return self._cache_embeddings[texto]
        try:
            url = f"{self.base_url}/models/gemini-embedding-001:embedContent?key={self.api_key}"
            payload = {
                "model": "models/gemini-embedding-001",
                "content": {"parts": [{"text": texto[:2000]}]}
            }
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                vals = data.get("embedding", {}).get("values")
                if vals:
                    self._cache_embeddings[texto] = vals
                    return vals
            elif resp.status_code in (400, 403):
                self._api_desabilitada = True
                self.ultimo_modo = "local"
        except Exception:
            pass
        return None

    def obter_embeddings_lote(self, textos: List[str]) -> Dict[str, List[float]]:
        faltantes = [t for t in textos if t and t not in self._cache_embeddings]
        if not faltantes or not self.api_key or self._api_desabilitada:
            return {t: self._cache_embeddings[t] for t in textos if t in self._cache_embeddings}

        try:
            for i in range(0, len(faltantes), 50):
                chunk = faltantes[i:i + 50]
                url = f"{self.base_url}/models/gemini-embedding-001:batchEmbedContents?key={self.api_key}"
                payload = {
                    "requests": [
                        {
                            "model": "models/gemini-embedding-001",
                            "content": {"parts": [{"text": t[:2000]}]}
                        }
                        for t in chunk
                    ]
                }
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    embs = data.get("embeddings", [])
                    for t, e in zip(chunk, embs):
                        vals = e.get("values")
                        if vals:
                            self._cache_embeddings[t] = vals
                elif resp.status_code in (400, 403):
                    self._api_desabilitada = True
                    self.ultimo_modo = "local"
                    break
        except Exception:
            pass

        return {t: self._cache_embeddings[t] for t in textos if t in self._cache_embeddings}

    def calcular_similaridade(self, texto_query: str, texto_no: str) -> float:
        v1 = self.obter_embedding_gemini(texto_query)
        v2 = self.obter_embedding_gemini(texto_no)
        if v1 and v2:
            self.ultimo_modo = "embedding"
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a ** 2 for a in v1))
            norm2 = math.sqrt(sum(b ** 2 for b in v2))
            if norm1 > 0 and norm2 > 0:
                return float(dot / (norm1 * norm2))

        self.ultimo_modo = "local"
        t_q = self._tokenizar_fallback(texto_query)
        t_n = self._tokenizar_fallback(texto_no)
        return self._cosseno_fallback(t_q, t_n)

    # Metadados que ajudam a achar o nó (os demais, como nome do arquivo PDF, só atrapalham)
    CAMPOS_METADADOS_BUSCA = ("autores", "ano", "veiculo", "ferramentas")

    def texto_do_no(self, no: NoGrafo) -> str:
        extras = " ".join(str(no.metadados[c]) for c in self.CAMPOS_METADADOS_BUSCA if c in (no.metadados or {}))
        return f"{no.nome}. {no.descricao} {extras}".strip()

    def limiar_padrao(self) -> float:
        """
        Similaridade mínima para um nó virar porta de entrada. Abaixo disso o sistema responde
        que não encontrou nada (em vez de "forçar" uma resposta). Os valores mudam conforme o
        modelo de similaridade, por isso há dois limiares. Calibre com scripts/calibrar_limiar.py.
        """
        if self.api_key and not self._api_desabilitada:
            return float(os.getenv("LIMIAR_SIMILARIDADE", "0.66"))
        return float(os.getenv("LIMIAR_SIMILARIDADE_LOCAL", "0.45"))

    def encontrar_nos_entrada(self, query: str, nos: List[NoGrafo], top_k: int = 3,
                              threshold: Optional[float] = None) -> List[Tuple[NoGrafo, float]]:
        """Pontua todos os nós e devolve até top_k nós acima do limiar (pode devolver lista vazia)."""
        pontuados = self.pontuar_nos(query, nos)
        if threshold is None:
            threshold = self.limiar_padrao() if self.ultimo_modo == "embedding" else float(
                os.getenv("LIMIAR_SIMILARIDADE_LOCAL", "0.45"))
        if not pontuados or pontuados[0][1] < threshold:
            return []
        # Só entram nós quase tão parecidos com a pergunta quanto o melhor (evita "puxar" estudos por ligações fracas)
        margem = float(os.getenv("MARGEM_SIMILARIDADE", "0.03"))
        corte = max(threshold, pontuados[0][1] - margem)
        return [(n, s) for n, s in pontuados if s >= corte][:top_k]

    def pontuar_nos(self, query: str, nos: List[NoGrafo]) -> List[Tuple[NoGrafo, float]]:
        """Similaridade entre a pergunta e cada nó, em ordem decrescente. Registra o modo usado."""
        textos_alvo = [self.texto_do_no(no) for no in nos]
        if self.api_key:
            self.obter_embeddings_lote([query] + textos_alvo)

        v_query = self._cache_embeddings.get(query)
        self.ultimo_modo = "embedding" if v_query else "local"
        t_query = self._tokenizar_fallback(query)
        scores = []
        for no, texto_alvo in zip(nos, textos_alvo):
            v_no = self._cache_embeddings.get(texto_alvo)
            if v_query and v_no:
                dot = sum(a * b for a, b in zip(v_query, v_no))
                norm1 = math.sqrt(sum(a ** 2 for a in v_query))
                norm2 = math.sqrt(sum(b ** 2 for b in v_no))
                score = float(dot / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
            else:
                score = self._cosseno_fallback(t_query, self._tokenizar_fallback(texto_alvo))
            scores.append((no, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    # ----------------- 2. LLM APENAS FORMATADOR ----------------- #

    def formatar_sintese(self, query: str, alternativas: List[AlternativaDecisao],
                         subgrafo: Optional[SubgrafoEvidencia] = None,
                         usar_llm: bool = True) -> Dict[str, str]:
        """Devolve {"texto": ..., "origem": "llm" | "modelo_fixo"}."""
        if not alternativas:
            return {
                "texto": "Nenhuma abordagem dos estudos selecionados corresponde a essa situação. "
                         "O acervo contém apenas os estudos incluídos no mapeamento; tente descrever a situação de outra forma.",
                "origem": "modelo_fixo",
            }

        if self.api_key and not self._api_desabilitada and usar_llm:
            try:
                sintese_llm = self._chamar_gemini_formatador(query, alternativas)
                if sintese_llm:
                    return {"texto": sintese_llm.strip(), "origem": "llm"}
            except Exception:
                pass

        return {"texto": self._formatar_deterministico(alternativas), "origem": "modelo_fixo"}

    @staticmethod
    def _dados_para_llm(alternativas: List[AlternativaDecisao]) -> List[Dict[str, Any]]:
        return [{
            "abordagem": a.tecnica_nome,
            "como_funciona": a.descricao,
            "estudo": f"{a.estudo.autores} ({a.estudo.ano})" if a.estudo else "",
            "onde_foi_aplicada": a.cenarios,
            "como_foi_avaliada": a.metricas_avaliacao,
            "limitacoes": a.limitacoes,
        } for a in alternativas]

    def _chamar_gemini_formatador(self, query: str, alternativas: List[AlternativaDecisao]) -> Optional[str]:
        url = f"{self.base_url}/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        dados = json.dumps(self._dados_para_llm(alternativas), ensure_ascii=False, indent=2)
        prompt = f"""Você resume, em português, dados recuperados de um grafo de estudos científicos.

Situação descrita pelo usuário: "{query}"

Dados recuperados (única fonte permitida):
{dados}

Regras:
1. Escreva de 2 a 4 frases curtas, em linguagem simples.
2. Use SOMENTE informações dos dados acima. Não acrescente números, estudos, autores ou fatos que não estejam neles.
3. Cite cada abordagem com o estudo entre parênteses, no formato (Autores, ano), exatamente como aparece em "estudo".
4. Não diga qual abordagem é melhor nem recomende uma escolha. Não use as palavras "melhor", "recomendo" ou "ideal".
5. Não use títulos, listas nem markdown."""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 1024,
                # sem "raciocínio" interno: senão ele consome o limite e o resumo sai cortado
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code == 200:
            cands = resp.json().get("candidates", [])
            if cands and "content" in cands[0]:
                parts = cands[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text")
        return None

    @staticmethod
    def _formatar_deterministico(alternativas: List[AlternativaDecisao]) -> str:
        if len(alternativas) == 1:
            inicio = "Os estudos selecionados trazem 1 abordagem relacionada a essa situação: "
        else:
            inicio = f"Os estudos selecionados trazem {len(alternativas)} abordagens relacionadas a essa situação: "
        partes = []
        for a in alternativas:
            ref = f" ({a.estudo.autores}, {a.estudo.ano})" if a.estudo else ""
            partes.append(f"{a.tecnica_nome}{ref}")
        return inicio + "; ".join(partes) + ". Compare as evidências e limitações de cada uma; a escolha é sua."
