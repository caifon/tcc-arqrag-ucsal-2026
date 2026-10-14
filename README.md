# 🕸️ GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura

[![Vercel Live](https://img.shields.io/badge/Deploy-Vercel%20Live-success.svg?logo=vercel)](https://graphrag-web-rho.vercel.app)
[![GitHub Repo](https://img.shields.io/badge/GitHub-caifon%2Ftcc--arqrag--ucsal--2026-blue.svg?logo=github)](https://github.com/caifon/tcc-arqrag-ucsal-2026)
[![UCSAL](https://img.shields.io/badge/Institui%C3%A7%C3%A3o-UCSAL-blue.svg)](https://ucsal.br)
[![Curso](https://img.shields.io/badge/Curso-Engenharia%20de%20Software-brightgreen.svg)]()
[![Ano](https://img.shields.io/badge/Ano-2026-orange.svg)]()
[![Hit Rate](https://img.shields.io/badge/Hit%20Rate-97.5%25-success.svg)]()
[![Taxa de Alucinação](https://img.shields.io/badge/Taxa%20de%20Fabrica%C3%A7%C3%A3o-0.0%25-informational.svg)]()

> **Trabalho de Conclusão de Curso (TCC)** apresentado à Universidade Católica do Salvador (UCSAL) como requisito parcial para a obtenção do título de Bacharel em Engenharia de Software.  
> **Orientadora:** Profª. Angela Peixoto.  
> **Base Metodológica:** Diretrizes PRISMA 2020 e Teoria da Decisão de Herbert Simon (1960).  
> **Aplicação Online (Produção):** 🌐 [https://graphrag-web-rho.vercel.app](https://graphrag-web-rho.vercel.app)  
> **Código Fonte:** 🐙 [https://github.com/caifon/tcc-arqrag-ucsal-2026](https://github.com/caifon/tcc-arqrag-ucsal-2026)

---

## 💡 Sobre o Projeto

Este projeto investiga e desenvolve uma solução inovadora em **GraphRAG (Retrieval-Augmented Generation baseado em Grafos)** aplicada ao suporte à tomada de decisão técnica em Engenharia de Software e sistemas complexos.

Enquanto sistemas de busca vetorial convencionais (*Naive RAG*) fatiam documentos em trechos soltos e perdem conexões conceituais, este sistema preserva a topologia relacional das ideias científicas por meio de uma **ontologia fixa pré-estabelecida**. O modelo de linguagem (LLM) atua estritamente como um **formatador neutro**, organizando alternativas concorrentes lado a lado com suas evidências, restrições e citações literais, **sem impor escolhas ao usuário**.

### 🎯 Decisão Arquitetural: Por que focar no Corpus PRISMA em vez de "Upload Genérico de PDFs"?
Uma das perguntas metodológicas mais relevantes do projeto é: *"Por que não focar o MVP em uma ferramenta genérica de upload e análise de PDFs anexados na hora?"*
1. **Diferença Científica entre "ChatPDF" e GraphRAG:** Fazer upload de um arquivo e buscar por palavras-chave é o que qualquer ferramenta comercial de RAG vetorial básico faz. O mérito de Engenharia de Software desta tese é transformar uma **Revisão Sistemática da Literatura (protocolo PRISMA 2020)** — tradicionalmente uma tabela estática e esquecida — em um **banco de conhecimento vivo, navegável e auditável em Grafo**.
2. **Eliminação de Alucinações por Design (Taxa 0.0%):** A literatura (Gao et al., 2023; Edge et al., 2024) comprova que extrair grafos abertos (*Open Information Extraction*) de PDFs arbitrários em tempo de execução introduz entidades falsas, sinônimos duplicados e ruído. A ontologia rígida pré-qualificada garante que o modelo **não fabrique nenhuma relação causal**.
3. **Validade Experimental e Benchmarking:** Um banco formal de 20 cenários de teste com gabarito formal (*Ground Truth*) só é matematicamente validável sobre um corpus controlado com *Hit Rate* auditável (97.5%).
4. **Viabilidade e Latência em Produção:** Extrair nós e arestas de um artigo acadêmico completo via LLM em tempo de upload exigiria minutos e causaria *timeouts* em ambientes serverless. No modelo adotado, a consulta responde em menos de 2 segundos.
*(A ingestão dinâmica assistida é mapeada como Trabalho Futuro no Capítulo 5 da monografia e estruturada no [02_GUIA_INGESTAO_E_CORPUS.md](docs/02_GUIA_INGESTAO_E_CORPUS.md)).*

---

## 📚 Índice da Documentação Oficial

Toda a documentação técnica, acadêmica e metodológica do projeto encontra-se detalhada no diretório [`docs/`](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/docs):

1. [**01. Arquitetura e Engenharia de Software**](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/docs/01_ARQUITETURA_E_ENGENHARIA.md):
   * Diagrama C4 de componentes da aplicação monorepo (Next.js 15 + FastAPI Serverless).
   * Modelo Ontológico formal (Nós: *Estudo, Técnica, Cenário, Estratégia, Métrica, Limitação, Snippet*; Arestas: *USA, APLICADO_EM, UTILIZA_ESTRATEGIA, AVALIADO_POR, POSSUI_LIMITACAO, EVIDENCIA_TEXTUAL*).
   * O pipeline de recuperação em 4 etapas detalhado.
2. [**02. Guia de Ingestão e Expansão do Corpus**](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/docs/02_GUIA_INGESTAO_E_CORPUS.md):
   * Modelo de planilha de extração de 10 colunas para o time de triagem teórica (PRISMA).
   * Scripts de carga via JSON e comandos Cypher `MERGE` para o Neo4j AuraDB.
   * Regras de integridade ontológica e validação de dados.
3. [**03. Avaliação Experimental e Métricas**](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/docs/03_AVALIACAO_EXPERIMENTAL_E_METRICAS.md):
   * Formulação matemática do *Hit Rate* (97.5%) e da *Taxa de Fabricação* (0.0%).
   * O banco padronizado de 20 cenários de teste com gabarito formal.
   * Resultados do modo comparativo A/B contra o RAG vetorial tradicional (resposta à RQ4).
4. [**04. Conteúdo Acadêmico para a Monografia (Overleaf)**](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/docs/04_CONTEUDO_MONOGRAFIA_TCC.md):
   * Resumo em Português e Abstract em Inglês prontos para substituir os placeholders do PDF.
   * Harmonização e expansão da Tabela de Perguntas de Pesquisa (RQ1 a RQ6).
   * Texto completo do **Capítulo 4 (Resultados e Discussão)** e **Capítulo 5 (Conclusão)**.
   * Entradas BibTeX corrigidas para sanar as referências `(??)` do texto.
5. [**05. Manual Estratégico de Defesa para a Banca**](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/docs/05_MANUAL_DE_DEFESA_BANCA.md):
   * Roteiro sugerido de apresentação de 15 a 20 minutos com script de demo prática.
   * Os 3 Pilares Científicos Irrefutáveis para responder sobre a necessidade do GraphRAG.
   * Banco com 12 perguntas difíceis prováveis da banca e suas respostas fundamentadas.
6. [**Próximos Passos e Roadmap**](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/PROXIMOS_PASSOS_E_ROADMAP.md):
   * Cronograma de atividades finais para o time teórico e time de desenvolvimento.

---

## 🚀 Como Executar o Sistema

### Pré-requisitos
* **Node.js** v18+ instalado.
* **Python** v3.10+ instalado.
* *(Opcional)* Chave de API gratuita do [Google AI Studio](https://aistudio.google.com/) (`GEMINI_API_KEY`) e instância gratuita no [Neo4j AuraDB](https://neo4j.com/cloud/platform/aura-graph-database/).

### Passo a Passo Local

1. **Acessar a pasta do sistema web:**
   ```powershell
   cd "graphrag-web"
   ```

2. **Instalar dependências do Frontend e Backend:**
   ```powershell
   npm install
   pip install -r api/requirements.txt
   ```

3. **Configurar variáveis de ambiente (Opcional):**
   Copie o arquivo `.env.example` para `.env` e configure suas chaves se desejar usar os modelos em nuvem:
   ```powershell
   copy .env.example .env
   ```
   *(Caso não configure o `.env`, o sistema executará automaticamente com os adaptadores de fallback in-memory via NetworkX e formatação determinística local).*

4. **Iniciar o ambiente de desenvolvimento:**
   ```powershell
   npm run dev
   ```

5. **Acessar no navegador:**
   Abra [http://localhost:3000](http://localhost:3000).

---

## 🖥️ Funcionalidades da Aplicação Web

* **⚖️ Aba 1: Apoio à Decisão & Comparador A/B:**
  * Submissão de consultas decisórias em linguagem natural.
  * Visualização de alternativas concorrentes em matriz lado a lado com restrições e citações.
  * Switch comparativo em tempo real: **RAG Tradicional vs. GraphRAG**.
  * Visualizador interativo da **Rota Causal Topológica** (*Multi-hop Explainability*).
  * Exportador de **Dossiê Decisório em Markdown** em 1 clique.
* **🧪 Aba 2: Avaliação Experimental:**
  * Painel de auditoria do banco de 20 cenários de teste com gabarito formal.
  * Execução da reavaliação em tempo real com apuração do *Hit Rate* (97.5%) e *Taxa de Fabricação* (0.0%).
* **🕸️ Aba 3: Ontologia e Corpus:**
  * Inspecionador do acervo de artigos científicos, técnicas, métricas e limitações catalogadas no grafo.

---

## 🏛️ Estrutura do Repositório

```text
├── docs/                             # Documentação técnica e acadêmica completa
│   ├── 01_ARQUITETURA_E_ENGENHARIA.md
│   ├── 02_GUIA_INGESTAO_E_CORPUS.md
│   ├── 03_AVALIACAO_EXPERIMENTAL_E_METRICAS.md
│   ├── 04_CONTEUDO_MONOGRAFIA_TCC.md
│   └── 05_MANUAL_DE_DEFESA_BANCA.md
├── graphrag-web/                     # Aplicação Web Monorepo Oficial (Next.js + FastAPI)
│   ├── api/                          # Backend Serverless Python
│   │   ├── data/                     # Seed corpus e banco de 20 cenários de teste
│   │   ├── engine/                   # TraversalEngine e GeminiService
│   │   ├── evaluation/               # Aferidor de Hit Rate e Fabricação
│   │   ├── graph/                    # Adaptadores Neo4j e NetworkX
│   │   └── ontology.py               # Modelo ontológico formal tipado
│   ├── app/                          # Frontend Next.js (App Router / Tailwind)
│   └── README.md                     # Manual técnico da aplicação web
├── mvp_graphrag/                     # Protótipo inicial em Streamlit (legado)
├── PROXIMOS_PASSOS_E_ROADMAP.md      # Roteiro de entrega e transição final
└── TCC___RAG.pdf                     # Documento Monográfico Oficial do TCC
```
