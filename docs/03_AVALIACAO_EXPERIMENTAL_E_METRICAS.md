# 📊 Avaliação Experimental e Métricas Metodológicas

**Projeto:** GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura  
**Instituição:** Universidade Católica do Salvador (UCSAL) — Bacharelado em Engenharia de Software (2026)  
**Referência Metodológica:** Seção 3.7 do documento monográfico [TCC___RAG.pdf](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/TCC___RAG.pdf)

---

## 1. Fundamentação das Métricas

Conforme estabelecido formalmente na **Seção 3.7 do TCC**, a validação do MVP foi orientada a duas métricas principais de qualidade de software e recuperação da informação:

### 1.1 Hit Rate (Taxa de Acerto de Recuperação)
Mede a eficácia do sistema em identificar e recuperar, a partir de uma consulta em linguagem natural, o conjunto de estudos científicos pertinentes cadastrados no grafo:

$$\text{Hit Rate} = \frac{|\text{Estudos Recuperados} \cap \text{Estudos Esperados}|}{|\text{Estudos Esperados}|}$$

* **Interpretação:** Um valor de $1.0$ ($100\%$) indica que todos os estudos científicos pertinentes ao problema foram recuperados na vizinhança topológica de até 2 saltos.

### 1.2 Taxa de Fabricação (Alucinação Factual)
Mede a proporção de declarações, conclusões ou estudos gerados pelo modelo de linguagem que não possuem correspondência direta com as evidências cadastradas nos nós e arestas:

$$\text{Taxa de Fabricação} = \frac{|\text{Afirmações sem Rastreabilidade no Grafo}|}{|\text{Total de Afirmações na Resposta}|}$$

* **Por Design:** Devido à arquitetura do sistema — onde o modelo de linguagem atua estritamente como formatador neutro condicionado ao subgrafo serializado —, a Taxa de Fabricação é matematicamente delimitada em **$0.0\%$**. Se uma relação não existe no grafo, ela não entra no contexto de formatação.

---

## 2. O Banco de 20 Cenários de Teste com Gabarito Formal

A validação foi realizada sobre o banco padronizado em [test_scenarios.json](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/graphrag-web/api/data/test_scenarios.json), formulado com base nas situações decisórias identificadas na literatura:

| ID | Cenário / Consulta de Teste | Estudos Esperados (Gabarito) | Técnicas Mapeadas | Estratégia |
| :---: | :--- | :--- | :--- | :--- |
| **q01** | Síntese temática ampla sobre relatórios técnicos (perguntas globais). | `est_ms_graphrag` (Edge et al.) | Resumos Hierárquicos de Comunidades | Leiden + Map-Reduce |
| **q02** | Raciocínio multi-hop conectando entidades distantes em documentos separados. | `est_hipporag`, `est_grag` | Memória Associativa / Subgrafos | PPR / Expansão k-hop |
| **q03** | Apoio à decisão na gestão de incidentes operacionais de transporte crítico. | `est_elssa` (Wang & Shalaby) | Decisão com Trilha de Auditoria | Subgrafo com Proveniência |
| **q04** | Recomendação nutricional e prescrições clínicas com LLM restrito à formatação. | `est_dindukurthi_nutrition` | LLM Restrito + Validação determinística | Cosseno Determinístico |
| **q05** | Simulação de atrasos logísticos na entrega de materiais de construção com Neo4j. | `est_rawat_construction` | Multi-Agent System (MAS) + Grafo Neo4j | Híbrida (Grafo + Vetorial) |
| **q06** | Manutenção prescritiva em fábrica inteligente (smart factory) com ontologia. | `est_niederhaus_prescriptive` | Ontologia Industrial Prescritiva | Travessia Causal de Falhas |
| **q07** | Difusão por Personalized PageRank para conexões associativas de longo prazo. | `est_hipporag` | Memória Associativa HippoRAG | Difusão em Grafo (PPR) |
| **q08** | Limitações de custo computacional ao construir grafos e resumos hierárquicos. | `est_ms_graphrag` | Resumos Hierárquicos de Comunidades | Análise de Limitação |
| **q09** | Preservação da topologia de subgrafos conexos para o contexto do LLM. | `est_grag` (Hu et al.) | Subgrafos Topológicos Preservados | Expansão k-hop |
| **q10** | Grafos ontológicos pré-existentes para decisões críticas em transporte/indústria. | `est_elssa`, `est_niederhaus` | Ontologia Operacional / Industrial | Travessia Causal / k-hop |
| **q11** | Comparação para summarization orientada por consulta (QFS) em larga escala. | `est_ms_graphrag` | Resumos Hierárquicos de Comunidades | Leiden + Map-Reduce |
| **q12** | Avaliação de recomendação nutricional com métricas NDCG@5 e Precision@5. | `est_dindukurthi_nutrition` | Recomendação Explicável | Ranqueamento Cosseno |
| **q13** | Integração de dependências de obras com alertas preditivos para gestores. | `est_rawat_construction` | LLM-MAS com Grafo de Obras | Memória Híbrida Neo4j |
| **q14** | Validação com usuários reais (n=11) medindo tempo de resolução de falhas. | `est_niederhaus_prescriptive` | Prescritivo em Fábrica Inteligente | Time-to-Resolution |
| **q15** | Limitações de streaming e dados em tempo real em indexação hierárquica. | `est_ms_graphrag` | Resumos Hierárquicos de Comunidades | Análise de Limitação |
| **q16** | Conexões associativas entre sintomas, patologias e nutrientes de forma controlada. | `est_dindukurthi_nutrition` | LLM Restrito à Formatação | Subgrafo Clínico Filtrado |
| **q17** | Grafos com restrições operacionais para equipes de campo e fiscais. | `est_elssa` | Proveniência em Incidentes Críticos | Trilha de Auditoria |
| **q18** | Mitigação de perda de recall em raciocínio relacional disperso. | `est_hipporag`, `est_grag` | Difusão Associativa / Subgrafos | PPR / Expansão k-hop |
| **q19** | Sistemas multiagentes com Coordenador Central para dependências de engenharia. | `est_rawat_construction` | Multi-Agent System (MAS) | Memória Híbrida Neo4j |
| **q20** | Trade-offs comprovados de abrangência e diversidade (72% a 83%) vs RAG comum. | `est_ms_graphrag` | Resumos Hierárquicos de Comunidades | Win-Rate / Tokens |

---

## 3. Resultados Experimentais Consolidados

A execução automatizada do avaliador ([`metrics.py`](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/graphrag-web/api/evaluation/metrics.py)) sobre a totalidade do banco de teste gerou os seguintes resultados:

* **Total de Cenários Avaliados:** $20$
* **Hit Rate Médio:** **`97.5%`** (19 cenários obtiveram 100% de recuperação do gabarito e apenas 1 cenário multi-estudo recuperou 50% dos estudos pretendidos no raio imediato).
* **Taxa de Fabricação Média:** **`0.0%`** (Nenhuma alucinação; 100% das afirmações amparadas em arestas e trechos literais).

---

## 4. Comparação A/B Experimental: GraphRAG vs. RAG Vetorial Convencional (Resposta à RQ4)

Para responder experimentalmente à **Pergunta de Pesquisa RQ4** (*Quais características favorecem a adoção do GraphRAG em detrimento do RAG convencional para apoio à tomada de decisão?*), o sistema executa ambos os métodos sob as mesmas consultas. As evidências obtidas revelam três disparidades críticas:

```mermaid
graph LR
    subgraph RAG Convencional (Naive RAG)
        Doc[Documentos PDF] --> Chunks[Chunks de Texto Isolados]
        Chunks --> VecSearch[Busca Vetorial Cosseno]
        VecSearch --> PromptNaive[Contexto com Chunks Fragmentados]
        PromptNaive --> Hallucination["❌ Perda de Relações Multi-hop<br>❌ Omissão de Restrições Distantes<br>❌ Risco de Fabricação/Alucinação"]
    end

    subgraph GraphRAG Estruturado (Nosso Sistema)
        KG[(Grafo de Conhecimento Ontológico)] --> Entry[Porta de Entrada Semântica]
        Entry --> Traversal[Expansão Topológica 1-2 Saltos]
        Traversal --> Subgraph[Subgrafo Conexo com Arestas Formais]
        Subgraph --> GroundedLLM[Formatador Neutro Estrito]
        GroundedLLM --> DecisionMatrix["✅ Matriz Lado a Lado Imparcial<br>✅ Rota Causal Topológica Auditável<br>✅ Taxa de Fabricação = 0.0%"]
    end
```

### Análise Qualitativa dos Trade-Offs

1. **Raciocínio Multi-Hop (Conexões Indiretas):**
   * *RAG Vetorial:* Falha sistematicamente quando a premissa de um estudo e a restrição de outro estudo estão em documentos separados.
   * *GraphRAG:* Recupera o subgrafo conexo preservando as arestas `APLICADO_EM` e `POSSUI_LIMITACAO`.
2. **Neutralidade Decisória (Fase de Escolha de Simon):**
   * *RAG Vetorial:* O modelo generativo tenta "adivinhar" uma resposta unificada e frequentemente toma uma decisão precipitada pelo usuário.
   * *GraphRAG:* O LLM é instruído a dispor as alternativas lado a lado, sem eleger vencedores, devolvendo a soberania do julgamento ao decisor humano.
3. **Auditabilidade e Governança:**
   * *RAG Vetorial:* "Caixa-preta". O decisor não sabe por que certo trecho influenciou a recomendação.
   * *GraphRAG:* Cada alternativa exibe sua **rota causal topológica** e seus **snippets literais com indicação de página**.
