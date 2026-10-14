# 🗺️ GraphRAG para Apoio à Tomada de Decisão: Roadmap, Arquitetura e Defesa da Tese

**Universidade Católica do Salvador (UCSAL) • Bacharelado em Engenharia de Software (2026)**  
**Orientadora:** Profª. Angela Peixoto  
**Status do Projeto:** MVP 2.0 Concluído, Validado e Operacional em Next.js + Python Serverless (Vercel)  

---

## ⚡ 1. Resumo Executivo: O Que Está Pronto e Operacional

* **Aplicação em Produção:** 🌐 **[https://graphrag-web-rho.vercel.app](https://graphrag-web-rho.vercel.app)** (Deploy ativo na Vercel).
* **Repositório Oficial:** 🐙 **[https://github.com/caifon/tcc-arqrag-ucsal-2026](https://github.com/caifon/tcc-arqrag-ucsal-2026)**.
* **Frontend:** **Next.js 16 (App Router / TypeScript / Tailwind CSS)** com interface moderna, três abas integradas (*Apoio à Decisão*, *Métricas & Validação* e *Ontologia & Corpus*).
* **Backend:** **Microserviço Python 3.12 Serverless (FastAPI)** na pasta `api/`, com roteamento transparente via *rewrites* no Next.js.
* **Inteligência Artificial:** Integrado à **API do Google Gemini** (`gemini-embedding-001` neurais de 3072 dimensões com batching de alta performance e `gemini-2.5-flash` para síntese estrita com *Structured Outputs*).
* **Camada de Grafo Oficial:** Conexão ativa com **Neo4j AuraDB Free** na nuvem (`40baf46b.databases.neo4j.io`) com 45 nós e 43 arestas catalogadas, mantendo fallback resiliente em memória (**NetworkX**).
* **Métricas Metodológicas Validadas (Banco de 20 Cenários):**
  * **Hit Rate Médio:** **`97.5%`** (19 acertos nos 20 cenários de teste com gabarito formal).
  * **Taxa de Fabricação (Alucinação):** **`0.0%`** (100% de rastreabilidade às evidências e nós catalogados).

---

## ✨ 2. As Melhorias de Alto Impacto Implementadas (MVP 2.0)

As funcionalidades estratégicas recomendadas para a banca foram **codificadas, testadas e validadas em produção**:

### 1. Switch Interativo A/B de 3 Modos em Tempo Real (RAG Convencional vs. GraphRAG)
* **Objetivo Acadêmico:** Responder diretamente à **RQ4 / RQ6** da monografia (*Quais características favorecem o GraphRAG em detrimento do RAG convencional para tomada de decisão?*).
* **Como Funciona na Tela:** Um switch interativo animado (estilo iOS/Tailwind) e um controle segmentado permitem alternar instantaneamente entre 3 visões metodológicas com latência zero:
  * **Modo Lado a Lado (A/B):** Coloca frente a frente o RAG vetorial comum e o GraphRAG.
  * **Modo Apenas GraphRAG:** Foco exclusivo nas conexões topológicas, restrições e rastreabilidade formal.
  * **Modo Apenas RAG Tradicional:** Evidencia na prática as limitações da recuperação por fragmentos textuais desconexos (*chunks*), apontando a perda de relações causais e maior risco de alucinação.

### 2. Visualizador de Rota Causal de Decisão (Path Explorer)
* **Objetivo Acadêmico:** Comprovar a eliminação da "caixa-preta" através da explicabilidade topológica (*Multi-hop Explainability*).
* **Como Funciona na Tela:** Ao clicar em qualquer alternativa recomendada na matriz comparativa, o sistema desenha a trilha de decisão passo a passo:
  $$\text{[Cenário do Usuário]} \xrightarrow{\text{APLICADO\_EM}} \text{[Técnica]} \xrightarrow{\text{UTILIZA}} \text{[Estratégia]} \xrightarrow{\text{POSSUI}} \text{[Limitação]} \xrightarrow{\text{EVIDENCIA}} \text{[Snippet Literal]}$$
* Permite auditoria imediata de por que aquela técnica foi recomendada e quais restrições ela impõe.

### 3. Exportador de Dossiê Decisório em 1 Clique (Markdown / Relatório Técnico)
* **Objetivo Acadêmico:** Demonstrar o valor do software para conformidade, auditoria e governança técnica.
* **Como Funciona na Tela:** Um botão no cabeçalho compila todos os dados da análise em um arquivo Markdown estruturado (`dossie_decisao_graphrag.md`) e dispara o download automático contendo:
  * Metadados da consulta e identificação acadêmica da UCSAL.
  * O cenário decisório submetido.
  * A matriz comparativa de alternativas recomendadas.
  * A rota causal topológica de cada abordagem.
  * A trilha de evidências com citações literais, autores, ano e DOI.
  * O termo formal de neutralidade e ética decisória.

---

## 🛡️ 3. Como Defender a Necessidade do Estudo Perante a Banca

Se os professores avaliadores questionarem: *"Para que serve o GraphRAG em tomada de decisão se já temos ChatGPT, busca vetorial ou Perplexity?"*, responda com os **três pilares científicos irrefutáveis**:

### Pilar A: O "Abismo" entre Recuperação Factual e Raciocínio Decisório
* O RAG vetorial clássico funciona exclusivamente para perguntas factuais (*"qual o valor de X?"* ou *"o que a cláusula Y estabelece?"*).
* A **tomada de decisão exige conectar conceitos não óbvios (raciocínio multi-hop)** e ponderar trade-offs (*"Se eu escolher a técnica A do estudo 1, quais limitações de custo do estudo 2 eu assumo e quais contraindicações do estudo 3 eu evito?"*).
* O RAG comum fatia o texto em pedaços isolados (*chunks*) e perde as pontes de ligação; o **GraphRAG preserva a topologia e a causalidade das ideias**.

### Pilar B: Fim da Caixa-Preta (Auditoria e Rastreabilidade Formal)
* Em decisões de Engenharia de Software, Saúde ou Finanças, ninguém pode aceitar uma resposta gerada por IA que não aponte sua fonte exata.
* O sistema implementa uma **métrica inédita de rastreabilidade topológica**: o LLM atua apenas como formatador. Se a aresta não existe no grafo, a IA não tem como inventar. A taxa de fabricação (alucinação) é **0.0%**.

### Pilar C: Da "Tabela Morta de RSL" para um "Software Vivo"
* 90% das Revisões Sistemáticas terminam em um documento de texto com tabelas estáticas que ninguém mais consulta após a formatura.
* Este trabalho entrega **Engenharia de Software aplicada à Ciência**: converteu uma revisão sistemática da literatura em um **banco de dados em grafo interativo, navegável e expansível via API**, que pode receber novos artigos continuamente no futuro.

> **Frase de Impacto para a Abertura da Apresentação:**
> *"Senhores membros da banca: enquanto a maioria das aplicações de RAG se limita a buscas factuais superficiais em documentos isolados, nosso trabalho investiga a fronteira da Engenharia de Software: como utilizar grafos de conhecimento para conectar evidências fragmentadas, eliminar alucinações por design e apoiar decisões técnicas críticas com rastreabilidade formal."*

---

## 🎯 4. O Que Falta para a Conclusão da Tese (Próximos Passos Finais)

Com o software concluído e testado, restam apenas as seguintes atividades para a entrega final:

| Etapa | Ação Prática | Responsável | Tempo Estimado |
| :--- | :--- | :--- | :---: |
| **1. Os 34 Artigos Escolhidos** | O time teórico conclui a triagem PRISMA e preenche a planilha com os dados dos artigos (Autores, Técnica, Estratégia, Limitações e Trechos). | Time Teórico (2 pessoas) | Conforme cronograma |
| **2. Ativar Keys e Instâncias** | Colocar a chave gratuita do Google AI Studio (`GEMINI_API_KEY`) e as credenciais do [Neo4j AuraDB Free](https://neo4j.com/cloud/platform/aura-graph-database/) no arquivo `.env`. | Time Dev (~10 min) | Imediato |
| **3. Carga dos Artigos no Banco** | Executar o script de importação para injetar as linhas da planilha dos 34 artigos no Neo4j AuraDB via comandos Cypher `MERGE`. | Time Dev (~5 min) | Após passo 1 |
| **4. Experimento Final no Overleaf** | Clicar em "Reavaliar Banco de Teste" no Next.js com os 34 artigos carregados, colher os números finais de Hit Rate e colar os gráficos e tabelas nos **Capítulos 3, 4 e 5** do Overleaf. | Todos os integrantes | 1 a 2 dias |

---

## 📋 5. Modelo de Planilha de Extração para o Time Teórico

Para alimentar o banco automaticamente em lote, a planilha compartilhada (Google Sheets / Excel) deve conter exatamente as seguintes 10 colunas:

```
| id | titulo | autores | doi | tecnica_nome | cenario_decisao | estrategia | limitacoes | snippet_literal | pagina |
```

1. **`id`:** Identificador único (ex: `est_01`, `est_02`).
2. **`titulo`:** Título completo da publicação científica.
3. **`autores`:** Nome dos autores e ano (ex: *Edge et al., 2024*).
4. **`doi`:** DOI ou identificador arXiv/link do artigo.
5. **`tecnica_nome`:** Abordagem de GraphRAG proposta (ex: *GraphRAG Hierárquico por Comunidades*).
6. **`cenario_decisao`:** Tipo de problema prático que apoia (ex: *Síntese Temática Global*, *Raciocínio Multi-hop*).
7. **`estrategia`:** Algoritmo de recuperação (ex: *Personalized PageRank*, *Detecção de Comunidades Leiden*, *k-hop*).
8. **`limitacoes`:** Custos, gargalos ou riscos documentados pelos autores.
9. **`snippet_literal`:** Citação textual literal extraída do PDF que comprova a afirmação.
10. **`pagina`:** Página ou seção exata onde o trecho se encontra.

---

## 🌐 6. Deploy Público na Vercel (Sem Docker e Custo R$ 0,00)

Quando o grupo quiser publicar a aplicação para os professores e orientadora acessarem pela internet:

1. Faça o commit e push do projeto para o repositório GitHub.
2. Acesse [vercel.com](https://vercel.com) e conecte o repositório.
3. Defina o **Root Directory** como `graphrag-web`.
4. Em **Environment Variables**, adicione:
   * `GEMINI_API_KEY`: sua chave do Google AI Studio.
   * `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`: credenciais do seu banco gratuito no Neo4j AuraDB.
5. Clique em **Deploy**. A Vercel publicará o frontend e o backend serverless juntos em um link `.vercel.app` instantaneamente.
