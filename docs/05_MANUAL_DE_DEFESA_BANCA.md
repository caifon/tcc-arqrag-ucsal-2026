# 🛡️ Manual Estratégico de Defesa Perante a Banca Examinadora

**Projeto:** GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura  
**Instituição:** Universidade Católica do Salvador (UCSAL) — Bacharelado em Engenharia de Software (2026)  
**Orientadora:** Profª Angela Peixoto  
**Público-Alvo:** Integrantes do Grupo na Apresentação de TCC

---

## 1. Roteiro Sugerido de Apresentação (15 a 20 Minutos)

| Bloco | Tempo | Foco da Fala | Slide / Demonstração |
| :---: | :---: | :--- | :--- |
| **1. Introdução & O Problema** | 3 min | Limitações dos LLMs (alucinações) e o gargalo do RAG puramente vetorial: perda de contexto relacional e incapacidade de síntese global. | Slide do problema conceitual. |
| **2. Metodologia PRISMA & Ontologia** | 4 min | Como a RSL foi planejada e como o conhecimento científico foi formalizado em um modelo ontológico rígido (nós e arestas). | Diagrama do modelo ontológico rígido. |
| **3. Arquitetura do Software (MVP)** | 4 min | O pipeline de 4 etapas: entrada vetorial leve, travessia topológica de 1 a 2 saltos, e LLM estritamente como formatador neutro. | Diagrama de componentes e fluxo. |
| **4. Demonstração Prática ao Vivo** | 5 min | 1. Executar consulta de gestão de obras; <br>2. Mostrar matriz lado a lado e rota causal topológica; <br>3. Ativar o Switch A/B contra o RAG vetorial comum; <br>4. Exibir a aba de Avaliação com 97.5% de Hit Rate. | Navegador em `http://localhost:3000`. |
| **5. Conclusão & Contribuições** | 2 min | A transformação de uma revisão estática em um software vivo; soberania decisória humana (Simon, 1960). | Slide de encerramento e agradecimentos. |

---

## 2. A Pergunta Inevitável da Banca e a Resposta Irrefutável

> **Pergunta do Avaliador:**  
> *"Por que precisamos de uma arquitetura complexa com Grafos e GraphRAG para apoiar decisões se uma simples busca vetorial com ChatGPT ou Perplexity já busca trechos de artigos?"*

### A Resposta dos 3 Pilares Científicos:

1. **Pilar A: O Abismo entre Recuperação Factual e Raciocínio Decisório (Lewis et al., 2020 vs. Edge et al., 2024)**
   > *"Professor, a busca vetorial simples opera por fragmentos textuais isolados (chunks). Ela responde com perfeição a perguntas factuais pontuais, como 'qual o valor de X?'. Contudo, a **tomada de decisão técnica exige ponderação relacional multi-hop**: 'Se eu adotar a técnica do Estudo A, quais limitações documentadas no Estudo B eu assumo e quais requisitos do Estudo C eu quebro?'. O RAG comum fatia o texto e perde essas pontes; o GraphRAG preserva a causalidade e a topologia das ideias."*

2. **Pilar B: Eliminação da Caixa-Preta e Rastreabilidade Formal**
   > *"Em Engenharia de Software, Saúde ou Infraestrutura, nenhuma decisão técnica crítica pode ser tomada com base em uma resposta de IA que não seja 100% auditável. Nosso sistema implementa um princípio em que o modelo generativo atua exclusivamente como formatador neutro de subgrafos conexos. Se uma relação não existe no grafo, a IA não tem permissão para inventar. Por isso, nossa Taxa de Fabricação factual é comprovadamente 0,0%."*

3. **Pilar C: Respeito à Teoria da Decisão de Herbert Simon (1960)**
   > *"A literatura de Sistemas de Apoio à Decisão define que o computador apoia as fases de Inteligência e Concepção, mas a Escolha pertence estritamente ao decisor humano. O RAG convencional frequentemente sofre de viés estocástico, recomendando uma única opção sem transparência. Nosso software dispõe as alternativas e evidências lado a lado com suas limitações, capacitando o engenheiro a decidir com respaldo científico."*

---

## 3. Banco de Perguntas Prováveis da Banca e Como Responder

### Q1. *"Como vocês garantem que o sistema não alucina informações novas?"*
* **Resposta:** O sistema não solicita ao LLM que 'pense' ou gere dados livres. O `GraphTraversalEngine` recupera primeiro o subgrafo do Neo4j. O LLM recebe apenas esse JSON com temperatura 0.1 e instruções de formatação determinística. Se uma aresta ou citação não estiver no subgrafo, o modelo não a inclui.

### Q2. *"O sistema não consome muitos tokens ou fica lento com grafos extensos?"*
* **Resposta:** Essa é uma das principais justificativas da nossa arquitetura em 4 etapas (Seção 3.8 do TCC). O embedding leve é usado apenas para localizar o nó de entrada semente. A partir dele, limitamos a travessia a um raio estrito de 1 a 2 saltos (`k-hop`). Isso garante complexidade computacional contida e custo de inferência previsível e baixo.

### Q3. *"Por que adotar uma ontologia rígida em vez de deixar o LLM extrair o grafo livremente?"*
* **Resposta:** A literatura (Gao et al., 2023) aponta que grafos de extração aberta não controlada sofrem com ruídos, nós sinônimos duplicados e relações inconsistentes. Para apoio à tomada de decisão técnica, um esquema formal rígido (Estudo, Técnica, Métrica, Limitação) garante integridade semântica e rastreabilidade ontológica.

### Q4. *"O que acontece se o banco Neo4j ficar indisponível no momento da apresentação?"*
* **Resposta:** Implementamos o padrão de projeto *Repository Pattern* com fallback resiliente. Caso a conexão externa com o Neo4j falhe, o sistema migra automaticamente e de forma transparente para o motor em memória com NetworkX, mantendo 100% das funcionalidades operacionais sem qualquer interrupção de serviço.

### Q5. *"Qual a diferença prática entre a aba de Apoio à Decisão e a aba de Avaliação Experimental?"*
* **Resposta:** A primeira aba é o ambiente operacional de uso do decisor final (onde ele pesquisa suas dúvidas de engenharia, inspeciona rotas causais e exporta dossiês técnicos). A segunda aba é o painel de validação científica para a comunidade acadêmica e auditores, que executa o banco de 20 testes com gabarito formal e exibe o Hit Rate de 97,5% em tempo real.

### Q6. *"Por que vocês focaram o MVP nos artigos selecionados pelo PRISMA em vez de permitir upload e análise de qualquer PDF anexado na hora?"*
* **Resposta:** Se o sistema recebesse qualquer PDF avulso e respondesse sobre ele, ele seria um **RAG Vetorial Comum (Naive RAG)** — ferramenta genérica já trivializada no mercado (ex.: ChatPDF). O mérito de Engenharia de Software da nossa pesquisa foi transformar uma Revisão Sistemática da Literatura (protocolo PRISMA 2020) em um **software vivo com Grafo de Conhecimento formalmente modelado**. Para o GraphRAG funcionar com integridade semântica e sem alucinações (Taxa de Fabricação 0.0%), a literatura (Gao et al., 2023) exige ontologia rígida e curada; a extração dinâmica aberta (*OpenIE*) geraria entidades inconsistentes e nós duplicados. A ingestão assistida de novos PDFs está formalizada como Trabalho Futuro no Capítulo 5 da monografia e estruturada no Guia de Ingestão do repositório.

### Q7. *"Como funciona o Switch Interativo A/B e o que ele comprova na prática?"*
* **Resposta:** O Switch A/B é o instrumento empírico do software para responder diretamente às perguntas de pesquisa **RQ4** (*fatores que favorecem o GraphRAG frente ao RAG comum*) e **RQ6** (*trade-offs de arquitetura*). Ao alternar entre a visão vetorial tradicional e a visão em grafo, o decisor constata ao vivo que a busca vetorial simples por chunks soltos omite restrições operacionais registradas em seções separadas dos artigos e quebra relações multi-hop, enquanto o GraphRAG conecta a cadeia causal e preserva os trade-offs comprovados pela literatura.

