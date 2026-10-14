import os
import json
from typing import List, Optional
from mvp_graphrag.ontology import AlternativaDecisao, SubgrafoEvidencia


SYSTEM_PROMPT_FORMATTER = """Você é um assistente de síntese científica estritamente imparcial para apoio à tomada de decisão (Seções 3.3, 3.6 e 3.8 do TCC UCSAL 2026).
Sua única responsabilidade é organizar e formatar os dados recuperados de um Grafo de Conhecimento (GraphRAG).

DIRETRIZES INEGOCIÁVEIS:
1. O LLM AGE APENAS COMO FORMATADOR: NÃO crie fatos, não invente e não altere informações (Taxa de Fabricação = 0%).
2. NÃO RECOMENDE ESCOLHA FINAL: Apresente as alternativas LADO A LADO com suas evidências, métricas e limitações, mas a escolha pertence exclusivamente ao usuário (Simon, 1960).
3. Apresente as alternativas em tabela comparativa lado a lado e transcreva os trechos literais de origem (snippets).
"""


class StrictLLMFormatter:
    """Orquestrador do LLM formatador: garantia de rastreabilidade, neutralidade decisória e zero alucinação."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "qwen2.5:14b"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name

    def formatar_resposta(self, query: str, alternativas: List[AlternativaDecisao], subgrafo: SubgrafoEvidencia) -> str:
        if not alternativas:
            return "Nenhuma abordagem correspondente foi identificada no grafo para o cenário informado. Tente reformular a consulta."

        return self._formatar_determinístico(query, alternativas, subgrafo)

    def _formatar_determinístico(self, query: str, alternativas: List[AlternativaDecisao], subgrafo: SubgrafoEvidencia) -> str:
        linhas = []
        linhas.append(f"### 🎯 Cenário Decisório em Análise (Metodologia PRISMA / TCC UCSAL 2026)")
        linhas.append(f"> **Consulta do Usuário:** *\"{query}\"*\n")
        linhas.append(f"O grafo identificou **{len(alternativas)} família(s) de abordagem(ns)** diretamente conectada(s) ao cenário.\n")

        # Tabela comparativa Resumo Lado a Lado (Seção 3.3)
        linhas.append("#### ⚖️ Matriz Comparativa Lado a Lado (Sem Imposição de Escolha)")
        linhas.append("| Dimensão | " + " | ".join([f"**{alt.tecnica_nome}**" for alt in alternativas]) + " |")
        linhas.append("| :--- | " + " | ".join([":---" for _ in alternativas]) + " |")
        linhas.append("| **Descrição do Paradigma** | " + " | ".join([alt.descricao for alt in alternativas]) + " |")
        linhas.append("| **Estudos de Suporte** | " + " | ".join([", ".join(alt.estudos_apoio) if alt.estudos_apoio else "Evidência indireta" for alt in alternativas]) + " |")
        linhas.append("| **Estratégias Chave** | " + " | ".join(["; ".join(alt.estrategias) if alt.estrategias else "Padrão" for alt in alternativas]) + " |")
        linhas.append("| **Métricas de Avaliação Reportadas** | " + " | ".join(["; ".join(alt.metricas_avaliacao) if alt.metricas_avaliacao else "Não reportada" for alt in alternativas]) + " |")
        linhas.append("| **Principais Limitações** | " + " | ".join(["; ".join(alt.limitacoes) if alt.limitacoes else "Não mapeada" for alt in alternativas]) + " |")
        linhas.append("\n---\n")

        # Detalhamento com Trechos Literais de Evidência
        linhas.append("#### 📚 Trilha de Evidências e Trechos Literais de Origem")
        for i, alt in enumerate(alternativas, 1):
            linhas.append(f"##### Alternativa {i}: {alt.tecnica_nome}")
            linhas.append(f"- **Fundamentação Teórica:**")
            if alt.estudos_apoio:
                for est in alt.estudos_apoio:
                    linhas.append(f"  * {est}")
            else:
                linhas.append("  * Relação topológica derivada de similaridade semântica no subgrafo.")

            linhas.append(f"- **Métricas de Avaliação Reportadas:**")
            if alt.metricas_avaliacao:
                for met in alt.metricas_avaliacao:
                    linhas.append(f"  * 📊 {met}")
            else:
                linhas.append("  * Não reportada explicitamente.")

            linhas.append(f"- **Limitações & Riscos Mapeados:**")
            for lim in alt.limitacoes:
                linhas.append(f"  * ⚠️ {lim}")

            linhas.append(f"- **Trechos Literais Recuperados:**")
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
