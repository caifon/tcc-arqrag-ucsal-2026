# 🕸️ GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura

[![Vercel Live](https://img.shields.io/badge/Deploy-Vercel%20Live-success.svg?logo=vercel)](https://graphrag-web-rho.vercel.app)
[![GitHub Repo](https://img.shields.io/badge/GitHub-caifon%2Ftcc--arqrag--ucsal--2026-blue.svg?logo=github)](https://github.com/caifon/tcc-arqrag-ucsal-2026)
[![UCSAL](https://img.shields.io/badge/Institui%C3%A7%C3%A3o-UCSAL-blue.svg)](https://ucsal.br)
[![Curso](https://img.shields.io/badge/Curso-Engenharia%20de%20Software-brightgreen.svg)]()
[![Ano](https://img.shields.io/badge/Ano-2026-orange.svg)]()

> **Trabalho de Conclusão de Curso (TCC)** apresentado à Universidade Católica do Salvador (UCSAL) como requisito parcial para a obtenção do título de Bacharel em Engenharia de Software.  
> **Autores:** Adriano Abreu de Almeida, Alison Andrade Rocha, Caio Roldão de Almeida Fonseca, Lívia Alves de Souza e Wendel Campos Bezerra.  
> **Orientadora:** Profª. Angela Peixoto.  
> **Base Metodológica:** Diretrizes PRISMA 2020 e Teoria da Decisão de Herbert Simon (1960).  
> **Aplicação Online (Produção):** 🌐 [https://graphrag-web-rho.vercel.app](https://graphrag-web-rho.vercel.app)  
> **Código Fonte:** 🐙 [https://github.com/caifon/tcc-arqrag-ucsal-2026](https://github.com/caifon/tcc-arqrag-ucsal-2026)

---

> **Atualização (out/2026 – Acervo Consolidado em 10 Artigos):** 
> - O acervo de estudos incluídos no mapeamento sistemático é composto por **10 estudos revisados por pares** (IEEE, Elsevier, Springer, ACM), localizados na pasta `Artigos Selecionados`.
> - **Evidências Literais Auditadas**: 22 trechos literais extraídos diretamente dos PDFs com conferência automática via `scripts/verificar_trechos.py` (**100% de precisão e 0 falhas**).
> - **Banco Experimental Ampliado**: 43 cenários de teste padronizados cobrindo perguntas diretas, paráfrases, análises comparativas cruzadas e questões fora do escopo com abstenção automática.
> - **Zero Alucinação**: Taxa de fabricação rigorosamente mantida em **0%**, ancorada estritamente na topologia ontológica do grafo.
> - **Controle de Geração do LLM**: `gemini-2.5-flash` configurado com `thinkingBudget: 0` e 1024 tokens para garantir síntese completa sem cortes.
>
> ### 📑 Acervo de Estudos Selecionados (10 Artigos)
> | ID | Estudo | Autores | Ano | Veículo | Domínio de Decisão |
> |---|---|---|:---:|---|---|
> | `est_rawat` | Conceptual Framework for LLM-Based MAS | Rawat, Witt & Lill | 2025 | EC3 / CIB W78 | Gestão de Obras & Cronogramas |
> | `est_niederhaus` | GraphRAG for Prescriptive Recommender Systems | Niederhaus et al. | 2025 | BDCC / MDPI | Manutenção Ciberfísica Industrial |
> | `est_dindukurthi` | Explainable GraphRAG for Nutrition Recommendation | Dindukurthi et al. | 2026 | Frontiers in AI | Nutrição Clínica & Dietoterapia |
> | `est_elssa` | ELSSA: Decision Support for Transit Incidents | Wang & Shalaby | 2026 | Transp. Res. Part C | Gestão de Incidentes em Transporte |
> | `est_lu_pipeline` | KG Reasoning and Security Assurance Decision-Making | Lu et al. | 2024 | IEEE AIIM | Segurança de Redes de Oleodutos |
> | `est_zheng_tcm` | ChatGLM-FGIDs-TCM: Clinical Decision Support | Zheng et al. | 2025b | IEEE BIBM | Medicina Clínica & Fitoterapia |
> | `est_zheng_ev` | KG Augmented Agents for EV Charging Support | Zheng et al. | 2025a | IEEE IAECST | O&M em Mobilidade Elétrica |
> | `est_liu_fusionom` | FusionOM: Dual-Channel Framework for O&M | Liu et al. | 2025 | IEEE NTCI | Estratégia de O&M em Aviação Civil |
> | `est_yan_uuv` | Autonomous Decision-Making for UUV Emergencies | Yan et al. | 2025 | IEEE | Emergências em Veículos Subaquáticos |
> | `est_mallala_robot` | Escalation Engine for Root-Cause Analysis | Mallala & Sharma | 2025 | IEEE / ArXiv | Análise de Causa-Raiz em Robótica |

## 💡 Sobre o Projeto

Este projeto investiga e desenvolve uma solução inovadora em **GraphRAG (Retrieval-Augmented Generation baseado em Grafos)** aplicada ao suporte à tomada de decisão técnica em Engenharia de Software e sistemas complexos.

Enquanto sistemas de busca vetorial convencionais (*Naive RAG*) fatiam documentos em trechos soltos e perdem conexões conceituais, este sistema preserva a topologia relacional das ideias científicas por meio de uma **ontologia fixa pré-estabelecida**. O modelo de linguagem (LLM) atua estritamente como um **formatador neutro**, organizando alternativas concorrentes lado a lado com suas evidências, restrições e citações literais, **sem impor escolhas ao usuário**.

### 🎯 Decisão Arquitetural: Por que focar no Corpus PRISMA em vez de "Upload Genérico de PDFs"?
Uma das perguntas metodológicas mais relevantes do projeto é: *"Por que não focar o MVP em uma ferramenta genérica de upload e análise de PDFs anexados na hora?"*
1. **Diferença Científica entre "ChatPDF" e GraphRAG:** Fazer upload de um arquivo e buscar por palavras-chave é o que qualquer ferramenta comercial de RAG vetorial básico faz. O mérito de Engenharia de Software desta tese é transformar uma **Revisão Sistemática da Literatura (protocolo PRISMA 2020)** — tradicionalmente uma tabela estática e esquecida — em um **banco de conhecimento vivo, navegável e auditável em Grafo**.
2. **Menos risco de informação inventada:** A literatura (Gao et al., 2023; Edge et al., 2024) comprova que extrair grafos abertos (*Open Information Extraction*) de PDFs arbitrários em tempo de execução introduz entidades falsas, sinônimos duplicados e ruído. Com uma ontologia fixa preenchida pelo grupo, cada informação exibida tem origem conferível; a taxa de fabricação é medida a cada avaliação (ver aba "Como avaliamos").
3. **Avaliação possível:** um banco de perguntas com resposta conhecida (incluindo perguntas fora do escopo) só pode ser conferido sobre um acervo controlado.
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

## 🎛️ Calibração de Limiares e Margens

Para recalibrar empiricamente os limiares de similaridade e a margem de entrada:
```powershell
cd graphrag-web
python scripts/calibrar_limiar.py
```
O script avalia combinações de limiares e margens de corte sobre o banco experimental e sugere os valores com melhor equilíbrio entre acerto, precisão e recusa:
* `LIMIAR_SIMILARIDADE`: Similaridade mínima para um nó ser considerado porta de entrada (`0.66` no modo Gemini Embedding).
* `MARGEM_SIMILARIDADE`: Margem máxima em relação ao melhor nó (`0.03`), evitando puxar estudos irrelevantes por ligações fracas.
* `LIMIAR_SIMILARIDADE_LOCAL`: Limiar para o modo fallback local sem API (`0.60`).

---

## 🖥️ Funcionalidades da Aplicação Web

* **⚖️ Aba 1: Apoio à Decisão & Comparador A/B:**
  * Submissão de consultas decisórias em linguagem natural.
  * Visualização de alternativas concorrentes em matriz lado a lado com restrições e citações.
  * Switch comparativo em tempo real: **RAG Tradicional vs. GraphRAG**.
  * Visualizador interativo da **Rota Causal Topológica** (*Multi-hop Explainability*).
  * Exportador de **Dossiê Decisório em Markdown** em 1 clique.
* **🧪 Aba 2: Avaliação Experimental:**
  * Painel de auditoria do banco de 21 cenários de teste com gabarito formal (perguntas diretas, paráfrases, cruzadas e fora do escopo).
  * Filtros dinâmicos por tipo e status.
  * Execução em tempo real com apuração dinâmica de *Hit Rate* (94%), *Precisão* (96%), *Recusa Correta* (80% com Gemini / 100% local) e *Taxa de Fabricação* (0.0%).
* **🕸️ Aba 3: Ontologia e Corpus:**
  * Inspecionador do acervo de artigos científicos, técnicas, métricas e limitações catalogadas no grafo.

---

## 🏛️ Estrutura do Repositório

```text
├── Artigos Selecionados/             # 10 estudos primários incluídos no mapeamento (PDFs oficiais)
├── docs/                             # Documentação técnica e acadêmica completa
│   ├── 01_ARQUITETURA_E_ENGENHARIA.md
│   ├── 02_GUIA_INGESTAO_E_CORPUS.md
│   ├── 03_AVALIACAO_EXPERIMENTAL_E_METRICAS.md
│   ├── 04_CONTEUDO_MONOGRAFIA_TCC.md
│   └── 05_MANUAL_DE_DEFESA_BANCA.md
└── graphrag-web/                     # Aplicação Web Monorepo Oficial (Next.js + FastAPI)
    ├── api/                          # Backend Serverless Python
    │   ├── data/                     # Seed corpus e banco de 43 cenários de teste
    │   ├── engine/                   # TraversalEngine e GeminiService
    │   ├── evaluation/               # Aferidor de Hit Rate e Fabricação
    │   ├── graph/                    # Adaptadores Neo4j e NetworkX
    │   └── ontology.py               # Modelo ontológico formal tipado
    ├── app/                          # Frontend Next.js (App Router / Tailwind)
    ├── scripts/                      # Scripts de manutenção e auditoria de evidências
    ├── tests/                        # Bateria de testes automatizados (pytest)
    └── README.md                     # Manual técnico da aplicação web
```
