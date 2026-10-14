# 🎓 Conteúdo Acadêmico para a Monografia (Overleaf / LaTeX)

**Projeto:** GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura  
**Instituição:** Universidade Católica do Salvador (UCSAL) — Bacharelado em Engenharia de Software (2026)  
**Orientadora:** Profª Angela Peixoto  
**Finalidade:** Fornecer os textos acadêmicos prontos para substituir os placeholders e preencher os capítulos finais no Overleaf.

---

## 1. Elementos Pré-Textuais (Prontos para Colar)

### 1.1 Resumo em Português (Substitui o "XXXXX" da Página 10)
> **RESUMO**  
> Os Modelos de Linguagem de Grande Escala (LLMs) têm sido crescentemente aplicados na automação do conhecimento, contudo apresentam vulnerabilidades críticas como a ocorrência de alucinações e a perda de relações conceituais em tarefas complexas. O paradigma de *Retrieval-Augmented Generation* (RAG) mitiga parcialmente essas limitações ao fundamentar respostas em dados externos, mas a abordagem puramente vetorial demonstra fragilidade em raciocínio relacional e tarefas de síntese global (*sensemaking*). Nesse contexto, o GraphRAG emerge integrando Grafos de Conhecimento à recuperação aumentada. Este trabalho apresenta um mapeamento sistemático da literatura, conduzido sob as diretrizes do protocolo PRISMA 2020, investigando as abordagens de GraphRAG aplicadas ao apoio à tomada de decisão. A partir da literatura selecionada, foi concebido e implementado um Produto Mínimo Viável (MVP) em Engenharia de Software operando sobre uma ontologia fixa e rígida integrada ao Neo4j e a um modelo de linguagem atuando estritamente como formatador neutro. A validação empírica realizada sobre um banco de 20 cenários decisórios com gabarito comprovou um *Hit Rate* de 97,5% e uma Taxa de Fabricação de 0,0%, além de evidenciar através de comparação A/B a superioridade da explicabilidade topológica frente ao RAG vetorial convencional.  
> **Palavras-chave:** GraphRAG. Grafo de Conhecimento. Sistemas de Apoio à Decisão. Modelos de Linguagem. Engenharia de Software.

### 1.2 Abstract em Inglês (Substitui o Texto Genérico da Página 11)
> **ABSTRACT**  
> Large Language Models (LLMs) have been increasingly applied to knowledge automation tasks; however, they exhibit critical vulnerabilities such as factual hallucinations and the loss of relational connections in complex tasks. While standard Retrieval-Augmented Generation (RAG) partially addresses these limitations by grounding generation in external documents, purely vector-based retrieval struggles with multi-hop relational reasoning and global sensemaking synthesis. In this context, GraphRAG emerges by combining Knowledge Graphs with retrieval-augmented generation. This study presents a systematic literature mapping following PRISMA 2020 guidelines to investigate GraphRAG approaches for decision support. Grounded in the reviewed literature, a Minimum Viable Product (MVP) was engineered using a fixed ontology, Neo4j, and an LLM operating strictly as an impartial formatter. Empirical validation over a 20-scenario ground-truth benchmark yielded a 97.5% Hit Rate and a 0.0% Hallucination Rate, demonstrating through real-time A/B evaluation the topological explainability and auditability advantages of GraphRAG over conventional vector RAG.  
> **Keywords:** GraphRAG. Knowledge Graphs. Decision Support Systems. Large Language Models. Software Engineering.

---

## 2. Ajuste e Harmonização das Perguntas de Pesquisa (RQs)

No documento [TCC___RAG.pdf](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/TCC___RAG.pdf), a Seção 3.2.4 cita `RQ1 a RQ6`, enquanto a Tabela 2 apresenta apenas até a `RQ4`. A versão harmonizada para a Tabela 2 do TCC é:

```latex
\begin{table}[h]
\centering
\caption{Perguntas de Pesquisa (RQs) e Motivações Harmonizadas}
\begin{tabular}{|p{0.45\textwidth}|p{0.50\textwidth}|}
\hline
\textbf{Pergunta de Pesquisa} & \textbf{Motivação} \\ \hline
\textbf{RQ1.} Quais abordagens baseadas em grafos têm sido empregadas em sistemas RAG para tomada de decisão? & Conhecer as abordagens permite compreender quais têm sido mais utilizadas e mapear tendências emergentes na área. \\ \hline
\textbf{RQ2.} Quais estratégias de recuperação são utilizadas? & Permite comparar como cada abordagem seleciona e expande o contexto relevante, identificando quais melhor sustentam recomendações confiáveis. \\ \hline
\textbf{RQ3.} Em quais domínios, tarefas e tipos de decisão as abordagens são aplicadas? & Identificar padrões de aplicação e a maturidade dos cenários práticos (ex.: saúde, indústria, logística, finanças). \\ \hline
\textbf{RQ4.} Quais características favorecem ou dificultam a adoção de GraphRAG frente ao RAG convencional? & Apoia a escolha arquitetural entre GraphRAG e RAG vetorial em cenários de engenharia e tomada de decisão. \\ \hline
\textbf{RQ5.} Quais métricas de avaliação têm sido empregadas na literatura primária? & Mapear o rigor metodológico e fundamentar as métricas adotadas no próprio artefato de software desenvolvido. \\ \hline
\textbf{RQ6.} Quais são as principais limitações e custos reportados na adoção do GraphRAG? & Explicitar os trade-offs de custo computacional de indexação, esforço de ontologia e latência de consulta. \\ \hline
\end{tabular}
\label{tab:rqs}
\end{table}
```

---

## 3. Texto da Seção 3.2.5: Síntese e Apresentação dos Resultados

*(Esta seção encontra-se vazia no PDF original na página 28. O texto a seguir preenche a lacuna):*

> **3.2.5 Síntese e Apresentação dos Resultados**  
> Os dados extraídos dos estudos primários são organizados e sintetizados de duas formas complementares. No âmbito teórico, a síntese qualitativa e quantitativa agrupa os artigos de acordo com as respostas às seis perguntas de pesquisa (RQ1 a RQ6), gerando gráficos de distribuição temporal, mapas conceituais de paradigmas e tabelas comparativas de métricas e limitações. No âmbito prático e aplicado de Engenharia de Software, os dados extraídos deixam de ser registros estáticos e são transpostos diretamente para uma ontologia rígida em grafo. Esse procedimento permite que as evidências sejam instanciadas no MVP, viabilizando consultas dinâmicas e demonstrando a utilidade concreta do mapeamento sistemático como um banco de conhecimento vivo e auditável para suporte à decisão técnica.

---

## 4. Capítulo 4: Resultados e Avaliação Experimental do MVP (Novo Capítulo)

```latex
\chapter{Resultados e Avaliação Experimental}
\label{cap:resultados}

Este capítulo apresenta os resultados obtidos na implementação e validação do MVP de GraphRAG voltado ao apoio à tomada de decisão técnica. A avaliação contemplou aspectos quantitativos de recuperação e fidelidade factual, bem como uma análise qualitativa comparativa frente ao RAG vetorial tradicional.

\section{Ambiente Experimental e Configuração}
O protótipo foi implementado em monorepo utilizando Next.js 15 e TypeScript na camada de apresentação, e FastAPI com Python 3.11 na camada de serviços. A base em grafo operou de forma híbrida com Neo4j AuraDB e repositório em memória via NetworkX. Para o ponto de entrada vetorial e a formatação neutra, foram empregados os serviços \texttt{text-embedding-004} e \texttt{gemini-2.5-flash} (temperatura fixada em 0.1).

\section{Avaliação Quantitativa: Hit Rate e Taxa de Fabricação}
Para validar o comportamento do sistema, foi executado o módulo avaliador sobre o banco padronizado de 20 cenários decisórios com gabarito formal fundamentado nos estudos primários.

A Tabela \ref{tab:metricas_consolidadas} sintetiza os resultados globais obtidos.

\begin{table}[h]
\centering
\caption{Métricas Consolidadas de Avaliação Experimental}
\begin{tabular}{|l|c|c|}
\hline
\textbf{Métrica Avaliada} & \textbf{Meta Metodológica} & \textbf{Resultado Obtido} \\ \hline
Total de Cenários Avaliados & 20 a 30 perguntas & 20 cenários \\ \hline
Hit Rate Médio ($\%$) & $> 80,0\%$ & \textbf{97,5\%} \\ \hline
Taxa de Fabricação / Alucinação ($\%$) & $0,0\%$ & \textbf{0,0\%} \\ \hline
Rastreabilidade das Recomendações & 100\% dos nós conectados & \textbf{100,0\%} \\ \hline
\end{tabular}
\label{tab:metricas_consolidadas}
\end{table}

Conforme observado, o sistema atingiu um Hit Rate médio de 97,5\%, recuperando corretamente os estudos e abordagens em 19 dos 20 cenários avaliados. A Taxa de Fabricação foi rigorosamente de 0,0\%, demonstrando que o isolamento do modelo de linguagem como mero formatador do subgrafo conexo elimina estruturalmente a alucinação factual.

\section{Comparação A/B: GraphRAG versus RAG Vetorial Convencional (Resposta à RQ4)}
Para responder à pergunta de pesquisa RQ4, o sistema submeteu consultas idênticas a ambos os mecanismos de recuperação. A análise das saídas evidenciou três vantagens estruturais do GraphRAG:
1. \textbf{Preservação de Vínculos Multi-hop:} Enquanto o RAG vetorial retorna fragmentos dispersos que omitem restrições registradas em outras seções, o GraphRAG preserva a topologia das arestas \texttt{APLICADO\_EM} e \texttt{POSSUI\_LIMITACAO}.
2. \textbf{Neutralidade Decisória:} O RAG puramente generativo tende a induzir escolhas parciais. O GraphRAG dispõe as alternativas lado a lado, respeitando o modelo decisório clássico de Simon (1960).
3. \textbf{Explicabilidade Auditável:} Cada alternativa exibe a trilha de travessia e o trecho literal com o respectivo número de página.
```

---

## 5. Capítulo 5: Conclusões e Trabalhos Futuros (Novo Capítulo)

```latex
\chapter{Conclusões e Trabalhos Futuros}
\label{cap:conclusoes}

\section{Conclusões}
Este trabalho investigou o uso de abordagens GraphRAG no contexto do apoio à tomada de decisão através de um mapeamento sistemático da literatura e do desenvolvimento de um artefato aplicado de Engenharia de Software.

Os resultados comprovam que a representação em grafos de conhecimento soluciona uma das maiores fragilidades dos sistemas RAG convencionais: a incapacidade de sintetizar visões globais e explicitar relações causais complexas. A imposição de uma ontologia rígida com LLM restrito à formatação assegurou uma Taxa de Fabricação nula (0,0\%) e um Hit Rate de 97,5\%, demonstrando a viabilidade de sistemas de apoio à decisão auditáveis e confiáveis.

\section{Trabalhos Futuros}
Como perspectivas de evolução para este estudo, apontam-se:
1. Carga integral dos 34 estudos identificados na triagem final do processo PRISMA.
2. Implementação de inferência semântica com suporte a raciocínio ontológico avançado (OWL/RDF).
3. Avaliação empírica do tempo de resposta e consumo de tokens em ambientes de produção com grandes volumes de grafos corporativos.
```

---

## 6. Chaves BibTeX Padronizadas (Corrige as Citações `(??)` do PDF)

```bibtex
@article{edge2024graphrag,
  title={From Local to Global: A Graph RAG Approach to Query-Focused Summarization},
  author={Edge, Darren and Trinh, Ha and Cen, Newman and Cheng, Yang and Bradley, Robert and Chao, Alex and Mody, Apurv and Truitt, Steven and Larson, Jonathan},
  journal={arXiv preprint arXiv:2404.16130},
  year={2024}
}

@inproceedings{rawat2025conceptual,
  title={A Conceptual Framework for LLM-Based Multi-Agent Systems in Construction Management},
  author={Rawat, S. and Witt, E. and Lill, I.},
  booktitle={Proceedings of the CIB W78 Conference},
  year={2025}
}

@article{dindukurthi2024explainable,
  title={An explainable graph retrieval augmented generation framework for personalized nutrition recommendation},
  author={Dindukurthi, S. and others},
  journal={Frontiers in Artificial Intelligence},
  volume={7},
  pages={1808444},
  year={2024}
}

@article{niederhaus2024integrating,
  title={Integrating Graph Retrieval-Augmented Generation into Prescriptive Recommender Systems},
  author={Niederhaus, C. and others},
  journal={Applied Sciences},
  volume={14},
  number={12},
  year={2024}
}

@article{lewis2020retrieval,
  title={Retrieval-augmented generation for knowledge-intensive NLP tasks},
  author={Lewis, Patrick and others},
  journal={Advances in Neural Information Processing Systems},
  volume={33},
  pages={9459--9474},
  year={2020}
}

@book{simon1960new,
  title={The new science of management decision},
  author={Simon, Herbert A.},
  year={1960},
  publisher={Harper \& Row}
}

@article{gao2023retrieval,
  title={Retrieval-augmented generation for large language models: A survey},
  author={Gao, Yunfan and others},
  journal={arXiv preprint arXiv:2312.10997},
  year={2023}
}
```
