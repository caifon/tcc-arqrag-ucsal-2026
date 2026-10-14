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
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

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
        if not self.api_key:
            return None
        try:
            url = f"{self.base_url}/models/text-embedding-004:embedContent?key={self.api_key}"
            payload = {
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": texto[:2000]}]}
            }
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("embedding", {}).get("values")
        except Exception:
            pass
        return None

    def calcular_similaridade(self, texto_query: str, texto_no: str) -> float:
        v1 = self.obter_embedding_gemini(texto_query)
        v2 = self.obter_embedding_gemini(texto_no)
        if v1 and v2:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a ** 2 for a in v1))
            norm2 = math.sqrt(sum(b ** 2 for b in v2))
            if norm1 > 0 and norm2 > 0:
                return float(dot / (norm1 * norm2))

        t_q = self._tokenizar_fallback(texto_query)
        t_n = self._tokenizar_fallback(texto_no)
        return self._cosseno_fallback(t_q, t_n)

    def encontrar_nos_entrada(self, query: str, nos: List[NoGrafo], top_k: int = 3, threshold: float = 0.10) -> List[Tuple[NoGrafo, float]]:
        scores = []
        for no in nos:
            texto_alvo = f"{no.nome} {no.descricao} {' '.join(str(v) for v in no.metadados.values())}"
            score = self.calcular_similaridade(query, texto_alvo)
            if score >= threshold:
                scores.append((no, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    # ----------------- 2. LLM APENAS FORMATADOR (SEÇÃO 3.3, 3.6 E 3.8) ----------------- #

    def formatar_sintese(self, query: str, alternativas: List[AlternativaDecisao], subgrafo: SubgrafoEvidencia) -> str:
        if not alternativas:
            return "Nenhuma abordagem correspondente foi identificada no grafo para o cenário informado. Tente reformular a consulta."

        if self.api_key:
            try:
                sintese_llm = self._chamar_gemini_formatador(query, alternativas, subgrafo)
                if sintese_llm:
                    return sintese_llm
            except Exception:
                pass

        return self._formatar_determinístico(query, alternativas, subgrafo)

    def _chamar_gemini_formatador(self, query: str, alternativas: List[AlternativaDecisao], subgrafo: SubgrafoEvidencia) -> Optional[str]:
        url = f"{self.base_url}/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        contexto_estruturado = {
            "consulta": query,
            "alternativas_recuperadas": [alt.model_dump() for alt in alternativas],
            "snippets_originais": subgrafo.snippets
        }

        prompt = f"""Você é um formatador estritamente neutro e imparcial de síntese acadêmica para apoio à tomada de decisão (conforme Seções 3.3 e 3.8 do TCC de Engenharia de Software da UCSAL).
O usuário fez a seguinte pergunta:
"{query}"

Você recebeu os seguintes dados recuperados estritamente pelo Grafo de Conhecimento:
{json.dumps(contexto_estruturado, ensure_ascii=False, indent=2)}

DIRETRIZES METODOLÓGICAS OBRIGATÓRIAS (SEÇÕES 3.3, 3.6 e 3.8 DO PDF):
1. O LLM AGE APENAS COMO UM FORMATADOR: NÃO crie informações novas, não infira e não altere os dados do grafo (garantia de Taxa de Fabricação = 0%).
2. SEM ESCOLHA FINAL: Apresente as alternativas LADO A LADO com suas evidências e limitações, mas NÃO declare nenhuma alternativa como 'melhor', 'superior' ou 'recomendada'. A escolha final deve ser definida exclusivamente pelo usuário (Fase de Escolha de Simon, 1960).
3. ESTRUTURAÇÃO OBRIGATÓRIA:
   - Matriz Comparativa Lado a Lado (detalhando: Paradigma/Técnica, Estudos de Suporte, Estratégias, Métricas de Avaliação Reportadas na Literatura e Limitações).
   - Trilha de Evidências com os trechos literais dos artigos (snippets) citando autores e páginas.
   - Declaração explícita de neutralidade decisória.
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048}
        }
        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            cands = data.get("candidates", [])
            if cands and "content" in cands[0]:
                parts = cands[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text")
        return None

    def _formatar_determinístico(self, query: str, alternativas: List[AlternativaDecisao], subgrafo: SubgrafoEvidencia) -> str:
        linhas = []
        linhas.append(f"### 🎯 Cenário Decisório em Análise (Metodologia PRISMA / TCC UCSAL 2026)")
        linhas.append(f"> **Consulta:** *\"{query}\"*\n")
        linhas.append(f"O Grafo recuperou **{len(alternativas)} família(s) de abordagem(ns)** conectadas topologicamente ao cenário.\n")

        # Tabela comparativa Resumo Lado a Lado (Seção 3.3 do PDF)
        linhas.append("#### ⚖️ Matriz Comparativa Lado a Lado (Sem Imposição de Escolha)")
        linhas.append("| Dimensão | " + " | ".join([f"**{alt.tecnica_nome}**" for alt in alternativas]) + " |")
        linhas.append("| :--- | " + " | ".join([":---" for _ in alternativas]) + " |")
        linhas.append("| **Descrição do Paradigma** | " + " | ".join([alt.descricao for alt in alternativas]) + " |")
        linhas.append("| **Estudos de Suporte** | " + " | ".join([", ".join(alt.estudos_apoio) if alt.estudos_apoio else "Relação indireta" for alt in alternativas]) + " |")
        linhas.append("| **Estratégias de Recuperação** | " + " | ".join(["; ".join(alt.estrategias) if alt.estrategias else "Padrão" for alt in alternativas]) + " |")
        linhas.append("| **Métricas de Avaliação Reportadas** | " + " | ".join(["; ".join(alt.metricas_avaliacao) if alt.metricas_avaliacao else "Não reportada" for alt in alternativas]) + " |")
        linhas.append("| **Limitações Mapeadas** | " + " | ".join(["; ".join(alt.limitacoes) if alt.limitacoes else "Não reportada" for alt in alternativas]) + " |")
        linhas.append("\n---\n")

        # Trilha de Evidências e Trechos Literais de Origem (Seção 3.3 do PDF)
        linhas.append("#### 📚 Trilha de Evidências e Trechos Literais de Origem")
        for i, alt in enumerate(alternativas, 1):
            linhas.append(f"##### Alternativa {i}: {alt.tecnica_nome}")
            if alt.trechos_evidencia:
                for t in alt.trechos_evidencia:
                    linhas.append(f"  > *\"{t['texto']}\"*")
                    if t.get("pagina"):
                        linhas.append(f"  > *(Página/Seção: {t['pagina']})*\n")
            else:
                linhas.append("  > *(Sem citação textual direta vinculada ao nó)*\n")

        linhas.append("---")
        linhas.append("ℹ️ **Nota de Neutralidade Decisória (Seção 3.3):** A ferramenta organiza as alternativas e evidências lado a lado, sem recomendar uma escolha final. Conforme o modelo clássico de Herbert Simon (1960), a inteligência e concepção são apoiadas pelo sistema, mas a etapa de escolha pertence ao usuário.")
        return "\n".join(linhas)
