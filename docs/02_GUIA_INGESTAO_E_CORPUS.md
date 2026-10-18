# 📥 Guia de Ingestão, Extração e Expansão do Corpus Científico

**Projeto:** GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura  
**Instituição:** Universidade Católica do Salvador (UCSAL) — Bacharelado em Engenharia de Software (2026)  
**Público-Alvo:** Integrantes do Grupo (Equipe de Triagem Teórica e Desenvolvedores)

---

## 1. Contexto e Objetivo da Ingestão

O objetivo deste guia é fornecer o procedimento padronizado para transformar os artigos científicos selecionados na Revisão Sistemática da Literatura (PRISMA 2020) em **conhecimento estruturado no Grafo (Neo4j / JSON)**.

Atualmente, o sistema opera com um *Corpus Calibrado* de **11 estudos primários rigorosamente extraídos** (84 nós, 92 arestas e 24 trechos literais auditados). À medida que novos artigos forem adicionados pela equipe, seus dados deverão ser inseridos seguindo este protocolo para manter a integridade ontológica e o cálculo automático de métricas.

### 1.1 Catálogo dos 11 Estudos Primários Ativos no Acervo

| ID | Estudo / Autores | Domínio Decisório | Abordagem GraphRAG |
| :---: | :--- | :--- | :--- |
| **E01** | Rawat, Witt e Lill (2025) | Gestão de Obras / Construção Civil | LLM-MAS com Memória Híbrida Neo4j |
| **E02** | Dindukurthi et al. (2024) | Nutrição Clínica Personalizada | Subgrafo Clínico e Filtragem Determinística |
| **E03** | Niederhaus et al. (2024) | Manufatura Inteligente / O&M | Ontologia Industrial Prescritiva |
| **E04** | Wang & Shalaby / ELSSA (2024) | Transporte Público Urbano | Grafo com Trilha de Auditoria e Proveniência |
| **E05** | Lu et al. (2024) | Oleodutos e Infraestrutura Crítica | Avaliação de Riscos Físicos, Cibernéticos e Geopolíticos |
| **E06** | Yu et al. (2024) | Aviação Civil / Relatórios AAIB | Análise Estruturada de Acidentes sem Atribuição de Culpa |
| **E07** | Zheng et al. (2024 TCM) | Medicina / Clínica Gastrointestinal | Ontologia e Grafo Clínico com Validação Médica |
| **E08** | Zheng et al. (2024 EV) | Eletropostos e Recarga de VEs | Grafo Hierárquico de Falhas e Despacho de Técnicos |
| **E09** | Liu et al. (2024 FusionOM) | O&M em Componentes Industriais | Integração de Busca Semântica e Raciocínio em Grafos |
| **E10** | Yan et al. (2024) | Robótica Submarina / UUVs | Decisão de Emergência sob Falhas de Subsistemas |
| **E11** | Mallala et al. (2024) | Robôs Autônomos Móveis (AMR) | Correlação de Telemetria e Logs para Causa-Raiz |

---

## 2. A Planilha de Extração Padronizada (10 Colunas)

A equipe que faz a leitura dos artigos em PDF deve preencher uma planilha compartilhada (Google Sheets / Excel) contendo rigorosamente as seguintes 10 colunas:

| Coluna | Nome do Campo | Descrição e Exemplo | Mapeamento no Grafo |
| :---: | :--- | :--- | :--- |
| **1** | `id` | Identificador único alfanumérico (ex.: `est_34_nomeautor`). | Nó `Estudo.id` |
| **2** | `titulo` | Título original completo da publicação científica. | Nó `Estudo.nome` |
| **3** | `autores` | Nome dos autores e ano (ex.: *Rawat, Witt e Lill, 2025*). | `Estudo.metadados.autores` |
| **4** | `doi` | DOI oficial ou identificador arXiv/link do artigo. | `Estudo.metadados.doi` |
| **5** | `tecnica_nome` | Nome da arquitetura/técnica de GraphRAG proposta no estudo. | Cria nó `Tecnica` e aresta `Estudo -[USA]-> Tecnica` |
| **6** | `cenario_decisao` | Tipo de problema prático em que a técnica apoia a decisão. | Cria nó `CenarioDecisao` e aresta `Tecnica -[APLICADO_EM]-> Cenario` |
| **7** | `estrategia` | Algoritmo de recuperação empregado (ex.: *Leiden, PPR, k-hop*). | Cria nó `EstrategiaRecuperacao` e aresta `UTILIZA_ESTRATEGIA` |
| **8** | `limitacoes` | Gargalo computacional, custo ou restrição apontada no artigo. | Cria nó `Limitacao` e aresta `Tecnica -[POSSUI_LIMITACAO]-> Limitacao` |
| **9** | `snippet_literal`| Trecho textual literal em inglês/português extraído do PDF. | Cria nó `Snippet` e aresta `Estudo -[EVIDENCIA_TEXTUAL]-> Snippet` |
| **10**| `pagina` | Número da página ou seção de onde o snippet foi extraído. | `Snippet.metadados.pagina` |

---

## 3. Estrutura do Arquivo `seed_corpus.json`

O arquivo oficial de dados em disco localiza-se em:
[`graphrag-web/api/data/seed_corpus.json`](file:///c:/Users/caior/OneDrive/Área%20de%20Trabalho/Faculdade/TCC/graphrag-web/api/data/seed_corpus.json)

Ele possui a seguinte estrutura JSON:

```json
{
  "nos": [
    {
      "id": "est_exemplo",
      "tipo": "Estudo",
      "nome": "Título do Estudo",
      "descricao": "Síntese dos objetivos do trabalho...",
      "metadados": {
        "autores": "Silva et al.",
        "ano": 2025,
        "instituicao": "UCSAL",
        "doi": "10.1016/j.exemplo.2025.01"
      }
    },
    {
      "id": "tec_exemplo",
      "tipo": "Tecnica",
      "nome": "Nome da Técnica GraphRAG",
      "descricao": "Descrição do pipeline e funcionamento...",
      "metadados": {
        "paradigma": "Construção com LLM + Grafo Conexo"
      }
    }
  ],
  "arestas": [
    {
      "origem_id": "est_exemplo",
      "destino_id": "tec_exemplo",
      "tipo": "USA",
      "peso": 1.0
    }
  ]
}
```

---

## 4. Ingestão Direta no Neo4j AuraDB (Script Cypher)

Para carregar dados diretamente no banco Neo4j na nuvem (ou no navegador Neo4j Browser), utilize o comando Cypher `MERGE` (que cria ou atualiza sem duplicar):

```cypher
// 1. Cadastrar o Estudo
MERGE (e:Estudo {id: "est_rawat_construction"})
SET e.nome = "A Conceptual Framework for LLM-Based Multi-Agent Systems in Construction Management",
    e.descricao = "Framework de sistema multiagente baseado em LLM (LLM-MAS) com Neo4j para gestão de atrasos em obras.",
    e.autores = "Rawat, Witt e Lill",
    e.ano = 2025,
    e.doi = "CIB-W78-2025";

// 2. Cadastrar a Técnica de GraphRAG
MERGE (t:Tecnica {id: "tec_multiagent_construction"})
SET t.nome = "LLM-MAS com Memória Híbrida em Grafo",
    t.descricao = "Arquitetura multiagente com Coordenador Central e grafo de dependências Neo4j.",
    t.paradigma = "Multi-Agent System (MAS) + Grafo Neo4j";

// 3. Cadastrar o Cenário Decisório Apoiado
MERGE (c:CenarioDecisao {id: "cen_gestao_projetos_logistica"})
SET c.nome = "Gestão de Projetos e Detecção de Impactos de Atrasos Logísticos",
    c.descricao = "Apoio a decisões táticas de reagendamento e prevenção de gargalos em obras.",
    c.foco = "Construção Civil";

// 4. Cadastrar a Estratégia de Recuperação
MERGE (r:EstrategiaRecuperacao {id: "est_hybrid_graph_vector"})
SET r.nome = "Memória Híbrida (Grafo de Dependências Neo4j + Banco Vetorial)",
    r.descricao = "Integração de busca semântica vetorial com travessia de dependências de atividades.";

// 5. Cadastrar a Limitação Mapeada
MERGE (l:Limitacao {id: "lim_complexidade_multiagente"})
SET l.nome = "Complexidade de Coordenação de Agentes e Sincronização Híbrida",
    l.descricao = "Necessidade de coordenar múltiplos agentes autônomos e manter consistência.",
    l.tipo = "Complexidade Arquitetural";

// 6. Cadastrar o Snippet Literal (Evidência Factual com Página)
MERGE (s:Snippet {id: "snip_rawat_1"})
SET s.nome = "Snippet: Rawat, Witt e Lill (2025) - Pág. 4",
    s.descricao = "In construction management, a central coordinator agent combines Neo4j dependency knowledge graphs with vector storage to simulate logistics delays and evaluate cascading effects on successor tasks...",
    s.pagina = 4;

// 7. Criar as Conexões Semânticas (Arestas)
MATCH (e:Estudo {id: "est_rawat_construction"}), (t:Tecnica {id: "tec_multiagent_construction"})
MERGE (e)-[:USA]->(t);

MATCH (t:Tecnica {id: "tec_multiagent_construction"}), (c:CenarioDecisao {id: "cen_gestao_projetos_logistica"})
MERGE (t)-[:APLICADO_EM]->(c);

MATCH (t:Tecnica {id: "tec_multiagent_construction"}), (r:EstrategiaRecuperacao {id: "est_hybrid_graph_vector"})
MERGE (t)-[:UTILIZA_ESTRATEGIA]->(r);

MATCH (t:Tecnica {id: "tec_multiagent_construction"}), (l:Limitacao {id: "lim_complexidade_multiagente"})
MERGE (t)-[:POSSUI_LIMITACAO]->(l);

MATCH (e:Estudo {id: "est_rawat_construction"}), (s:Snippet {id: "snip_rawat_1"})
MERGE (e)-[:EVIDENCIA_TEXTUAL]->(s);
```

---

## 5. Regras de Validação de Consistência

Antes de submeter novas adições ao repositório ou ao banco de dados:

1. **Nenhum nó pode ficar órfão:** Todo nó de `Tecnica` deve possuir ao menos uma aresta `USA` conectada a um `Estudo` e ao menos uma aresta `APLICADO_EM` conectada a um `CenarioDecisao`.
2. **Auditabilidade estrita:** Todo `Estudo` deve obrigatoriamente possuir ao menos um `Snippet` literal apontando para o número exato da página do artigo.
3. **Imparcialidade:** As descrições das técnicas devem relatar apenas o que os autores comprovaram no texto, registrando com fidelidade as limitações no nó de `Limitacao`.
