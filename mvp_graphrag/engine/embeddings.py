import math
import re
from typing import List, Tuple
from collections import Counter
from mvp_graphrag.ontology import NoGrafo


class LightweightEmbeddingEngine:
    """Motor leve de embeddings e similaridade semântica para identificação de nós de entrada."""

    def __init__(self):
        self._has_sentence_transformers = False
        self._model = None
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._has_sentence_transformers = True
        except ImportError:
            self._has_sentence_transformers = False

    def _tokenizar(self, texto: str) -> List[str]:
        palavras = re.findall(r"\w+", texto.lower())
        # Cria unigramas e bigramas de caracteres para robustez com termos técnicos e digitações variantes
        ngrams = []
        for p in palavras:
            ngrams.append(p)
            if len(p) >= 4:
                for i in range(len(p) - 2):
                    ngrams.append(p[i:i + 3])
        return ngrams

    def _vetor_cosseno(self, tokens1: List[str], tokens2: List[str]) -> float:
        c1 = Counter(tokens1)
        c2 = Counter(tokens2)
        inter = set(c1.keys()).intersection(set(c2.keys()))
        dot = sum(c1[t] * c2[t] for t in inter)
        norm1 = math.sqrt(sum(v ** 2 for v in c1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in c2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def calcular_similaridade(self, texto_query: str, texto_no: str) -> float:
        if self._has_sentence_transformers and self._model is not None:
            v1 = self._model.encode(texto_query)
            v2 = self._model.encode(texto_no)
            import numpy as np
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

        t_q = self._tokenizar(texto_query)
        t_n = self._tokenizar(texto_no)
        return self._vetor_cosseno(t_q, t_n)

    def encontrar_nos_entrada(self, query: str, nos: List[NoGrafo], top_k: int = 3, threshold: float = 0.10) -> List[Tuple[NoGrafo, float]]:
        """Identifica os Top-K nós de entrada mais compatíveis com a pergunta do usuário."""
        scores = []
        for no in nos:
            # Compara a query com o nome + descrição + palavras do nó
            texto_alvo = f"{no.nome} {no.descricao} {' '.join(str(v) for v in no.metadados.values())}"
            score = self.calcular_similaridade(query, texto_alvo)
            if score >= threshold:
                scores.append((no, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
