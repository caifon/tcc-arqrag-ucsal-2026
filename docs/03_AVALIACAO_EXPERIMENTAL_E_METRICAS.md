# 📊 Avaliação Experimental e Métricas Metodológicas

**Projeto:** GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura  
**Instituição:** Universidade Católica do Salvador (UCSAL) — Bacharelado em Engenharia de Software (2026)  
**Referência Metodológica:** Seção 3.7 do documento monográfico do TCC (harmonizado em [04_CONTEUDO_MONOGRAFIA_TCC.md](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/docs/04_CONTEUDO_MONOGRAFIA_TCC.md))

---

## 1. Fundamentação das Métricas

Conforme estabelecido formalmente na **Seção 3.7 do TCC**, a validação do MVP foi orientada a duas métricas principais de qualidade de software e recuperação da informação:

### 1.1 Hit Rate (Taxa de Acerto de Recuperação)
Mede a eficácia do sistema em identificar e recuperar, a partir de uma consulta em linguagem natural, o conjunto de estudos científicos pertinentes cadastrados no grafo:

$$\text{Hit Rate} = \frac{|\text{Estudos Recuperados} \cap \text{Estudos Esperados}|}{|\text{Estudos Esperados}|}$$

* **Interpretação:** Um valor de $1.0$ ($100\%$) indica que todos os estudos científicos pertinentes ao problema foram recuperados na vizinhança topológica de até 2 saltos.

### 1.2 Precisão Média
Mede a proporção de alternativas recuperadas pelo sistema que efetivamente eram esperadas pelo gabarito (penalizando recuperações ruidosas ou excessivas):

$$\text{Precisão} = \frac{|\text{Estudos Recuperados} \cap \text{Estudos Esperados}|}{|\text{Estudos Recuperados}|}$$

### 1.3 Abstenção Correta (Recusa de Escopo)
Mede a capacidade do sistema em reconhecer os limites do seu acervo fechado diante de perguntas que fogem ao escopo da literatura mapeada (ex.: mercado financeiro, receitas, streaming):

$$\text{Abstenção Correta} = \begin{cases} 1.0, & \text{se } |\text{Estudos Recuperados}| = 0 \\ 0.0, & \text{se } |\text{Estudos Recuperados}| > 0 \end{cases}$$

### 1.4 Taxa de Fabricação (Alucinação Factual)
Mede a proporção de declarações, conclusões ou entidades geradas pelo modelo de linguagem que não possuem correspondência direta com as evidências cadastradas nos nós e arestas do subgrafo recuperado:

$$\text{Taxa de Fabricação} = \frac{|\text{Afirmações sem Rastreabilidade no Grafo}|}{|\text{Total de Afirmações na Resposta}|}$$

* **Por Design:** Devido à arquitetura do sistema — onde o modelo de linguagem atua estritamente como formatador neutro condicionado ao subgrafo serializado —, a Taxa de Fabricação é mantida em **$0.0\%$**. Se uma relação não existe no grafo, ela não entra no contexto de formatação.

---

## 2. O Banco de 43 Cenários de Teste com Gabarito Formal

A validação foi realizada sobre o banco padronizado em [test_scenarios.json](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/graphrag-web/api/data/test_scenarios.json), formulado com 4 classes de desafios epistemológicos:

### 2.1 Distribuição das 43 Perguntas de Teste

| Grupo de Teste | Quantidade | Objetivo da Avaliação |
| :--- | :---: | :--- |
| **Perguntas Diretas** | 10 | Avalia a recuperação imediata de cada um dos 10 estudos primários ativos (E01 a E10) a partir da descrição técnica formal do seu cenário decisório. |
| **Paráfrases e Variações Léxicas** | 10 | Avalia a robustez semântica e a capacidade de generalização do embedding diante de vocabulário informal, sinônimos e termos práticos de engenharia. |
| **Perguntas Cruzadas / Multi-Estudo** | 13 | Avalia o raciocínio relacional e a travessia topológica entre paradigmas concorrentes (ex.: abordagens multiagentes, ontologias industriais, restrição de LLM, validação em campo vs dados simulados). |
| **Fora do Escopo (Testes de Recusa)** | 10 | Avalia a blindagem contra alucinações e a abstenção ética do sistema diante de perguntas externas ou domínios não cobertos pelo acervo fechado (bolsa de valores, meteorologia, aviação descontinuada). |

---

## 3. Resultados Experimentais Consolidados (Calculados em Tempo Real)

A execução automatizada do avaliador ([`metrics.py`](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/graphrag-web/api/evaluation/metrics.py)) sobre os 43 cenários gerou as seguintes métricas comparadas contra o baseline de busca vetorial simples (sem grafo):

| Métrica Avaliada | Baseline (Busca Sem Grafo) | GraphRAG Estruturado | Ganho / Comportamento |
| :--- | :---: | :---: | :---: |
| **Total de Cenários Avaliados** | 43 perguntas | **43 perguntas** | Cobertura integral das 4 categorias |
| **Hit Rate Médio (Perguntas com Resposta)** | 29,0% | **58,0% ~ 73,3%** | Superioridade na recuperação de contexto |
| **Precisão Média** | 29,0% | **63,0% ~ 76,7%** | Redução drástica de ruído e falsos positivos |
| **Abstenção Correta (Perguntas Fora de Escopo)** | Variável | **87,5% a 100,0%** | Recusa confiável sem forçar relações |
| **Taxa de Fabricação / Alucinação Factual** | Incontrolável (LLM livre) | **0,0%** (117+ fatos auditados) | Eliminação estrutural de alucinações |

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
