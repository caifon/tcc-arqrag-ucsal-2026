"""
Monta o arquivo api/data/seed_corpus.json com os estudos INCLUÍDOS no mapeamento.

Regras do acervo (para manter o MVP honesto):
- Só entram estudos que passaram pela seleção da revisão (Scopus + IEEE Xplore).
- Todo nó "Trecho" (Snippet) contém um trecho COPIADO do PDF, sem paráfrase,
  e a página indicada é a página do arquivo PDF. Rode `scripts/verificar_trechos.py`
  depois de qualquer alteração para conferir isso automaticamente.
- As descrições dos demais nós são resumos em português escritos pelo grupo
  a partir da leitura dos artigos.

Para acrescentar um estudo (ex.: os da IEEE), copie um bloco de ESTUDOS abaixo,
preencha os campos e rode:  python scripts/montar_corpus.py
"""
import json
import os

VERSAO_CORPUS = "2026-10-15-v3"

ESTUDOS = [
    {
        "id": "est_rawat",
        "nome": "A Conceptual Framework for LLM-Based Multi-Agent Systems in Construction Management",
        "descricao": "Framework conceitual de sistema multiagente baseado em LLMs para gestão de obras na construção civil, com memória híbrida (grafo de conhecimento em Neo4j e banco vetorial).",
        "metadados": {
            "autores": "Rawat, Witt e Lill",
            "ano": 2025,
            "veiculo": "European Conference on Computing in Construction (EC3) / CIB W78",
            "arquivo_pdf": "A CONCEPTUAL FRAMEWORK FOR LLM-BASED MULTI-AGENT SYSTEMS IN CONSTRUCTION MANAGEMENT.pdf",
        },
        "tecnica": {
            "id": "tec_rawat",
            "nome": "Sistema multiagente com grafo de dependências da obra",
            "descricao": "Um coordenador central distribui tarefas entre agentes de LLM. O grafo (Neo4j) guarda entregas de materiais, atividades do cronograma e as dependências entre elas, e é atualizado a cada evento da obra.",
            "metadados": {"ferramentas": "Neo4j, LangGraph, Gemini"},
        },
        "cenario": {
            "id": "cen_rawat",
            "nome": "Gestão de obras – impacto de atrasos na entrega de materiais",
            "descricao": "Identificar quais atividades do cronograma de uma obra são afetadas quando a entrega de um material atrasa e avisar o gestor do projeto antes que o atraso se espalhe.",
        },
        "estrategias": ["estr_consulta_cypher"],
        "metricas": ["met_demonstracao_viabilidade"],
        "limitacoes": ["lim_dados_sinteticos", "lim_coordenador_central"],
        "trechos": [
            {
                "id": "tr_rawat_1",
                "pagina": 1,
                "texto": "We demonstrate feasibility through an experiment simulating logistics delay detection using LangGraph, Neo4j (KG), and Gemini LLMs. The system successfully ingested simulated site data, updated the KG, used graph reasoning to identify the delay's impact on activities, and generated alerts.",
            },
            {
                "id": "tr_rawat_2",
                "pagina": 6,
                "texto": "The experiment relied on synthetic data (generated via Imagen 3 and Gemini 2.0 Flash), lacking the noise and complexity of real-world construction data; validation with actual project data is essential.",
            },
        ],
    },
    {
        "id": "est_niederhaus",
        "nome": "Integrating Graph Retrieval-Augmented Generation into Prescriptive Recommender Systems",
        "descricao": "Plataforma de análise prescritiva que usa GraphRAG orientado por ontologia para recomendar ações de correção de falhas em uma fábrica inteligente (IoT-Factory), a partir da documentação técnica.",
        "metadados": {
            "autores": "Niederhaus et al.",
            "ano": 2025,
            "veiculo": "Big Data and Cognitive Computing, v. 9, n. 10",
            "arquivo_pdf": "Integrating Graph Retrieval-Augmented Generation into Prescriptive Recommender Systems.pdf",
        },
        "tecnica": {
            "id": "tec_niederhaus",
            "nome": "GraphRAG orientado por ontologia para recomendação prescritiva",
            "descricao": "Manuais e documentos técnicos são divididos em trechos, classificados por um LLM como erro, ação ou contexto e guardados como nós em Neo4j. Cada erro é ligado às ações e aos contextos mais parecidos, que viram a base da recomendação.",
            "metadados": {"ferramentas": "Neo4j, classificador zero-shot com LLM"},
        },
        "cenario": {
            "id": "cen_niederhaus",
            "nome": "Indústria – recomendar ações para corrigir falhas em máquinas",
            "descricao": "Ajudar operadores de fábrica a encontrar rapidamente, nos manuais e na documentação técnica, a ação recomendada para resolver uma falha ou parada de máquina.",
        },
        "estrategias": ["estr_ligacoes_precomputadas"],
        "metricas": ["met_tempo_busca_usuarios", "met_acuracia_classificacao"],
        "limitacoes": ["lim_erros_extracao_automatica", "lim_manutencao_ontologia"],
        "trechos": [
            {
                "id": "tr_niederhaus_1",
                "pagina": 16,
                "texto": "To evaluate the performance of our prescriptive platform, we conducted a customer clinic with n = 11 industrial company representatives.",
            },
            {
                "id": "tr_niederhaus_2",
                "pagina": 11,
                "texto": "We performed a benchmark, comparing the labels produced by the zero-shot classifier with the labels assigned by a human expert. The zero-shot classifier achieved an accuracy of 72.80%.",
            },
            {
                "id": "tr_niederhaus_3",
                "pagina": 17,
                "texto": "However, GraphRAG is more complex than traditional RAG, and it requires continuous maintenance beyond document processing and embeddings.",
            },
        ],
    },
    {
        "id": "est_dindukurthi",
        "nome": "An explainable graph retrieval augmented generation framework for personalized nutrition recommendation",
        "descricao": "Framework explicável de GraphRAG para recomendação nutricional personalizada, que relaciona doenças, nutrientes e alimentos em um grafo de conhecimento.",
        "metadados": {
            "autores": "Dindukurthi et al.",
            "ano": 2026,
            "veiculo": "Frontiers in Artificial Intelligence, v. 9",
            "arquivo_pdf": "An explainable graph retrieval augmented generation framework for personalized nutrition recommendation.pdf",
        },
        "tecnica": {
            "id": "tec_dindukurthi",
            "nome": "GraphRAG com LLM restrito à formatação",
            "descricao": "O grafo (Neo4j) liga doenças, nutrientes e alimentos, montado a partir de bases nutricionais estruturadas. A escolha e o ranqueamento dos alimentos são feitos por um cálculo determinístico (similaridade de cosseno); o LLM só escreve a resposta final.",
            "metadados": {"ferramentas": "Neo4j, Gemini"},
        },
        "cenario": {
            "id": "cen_dindukurthi",
            "nome": "Saúde – recomendação de alimentos para pessoas com uma doença",
            "descricao": "Indicar alimentos adequados às necessidades nutricionais de uma pessoa com uma condição de saúde, como anemia, hipertensão ou diabetes, explicando o motivo de cada indicação.",
        },
        "estrategias": ["estr_entrada_por_similaridade_e_travessia"],
        "metricas": ["met_ndcg_precisao", "met_risco_alucinacao"],
        "limitacoes": ["lim_sem_validacao_real"],
        "trechos": [
            {
                "id": "tr_dindukurthi_1",
                "pagina": 1,
                "texto": "At inference time, nutrient requirements are retrieved from the graph and matched with food composition profiles using a deterministic cosine similarity-based ranking algorithm that prioritizes proportional nutrient balance. A language model is restricted to formatting graph-validated outputs.",
            },
            {
                "id": "tr_dindukurthi_2",
                "pagina": 14,
                "texto": "Consequently, these results demonstrate the system's internal reasoning and ranking consistency rather than independent clinical validation.",
            },
        ],
    },
    {
        "id": "est_elssa",
        "nome": "ELSSA: Explainable large language model-based decision support for public transit incident management",
        "descricao": "Sistema explicável de apoio à decisão para supervisores do transporte público durante incidentes, que combina procedimentos formais com a experiência registrada em ocorrências anteriores.",
        "metadados": {
            "autores": "Wang e Shalaby",
            "ano": 2026,
            "veiculo": "Transportation Research Part C, v. 193",
            "arquivo_pdf": "ELSSA Explainable large language model-based decision support for public transit incident management.pdf",
        },
        "tecnica": {
            "id": "tec_elssa",
            "nome": "GraphRAG de incidentes com comunidades e regularização",
            "descricao": "Um LLM extrai, dos relatórios de ocorrência, entidades e relações seguindo um esquema operacional. O grafo é organizado em comunidades (algoritmo de Leiden) e passa por uma regularização automática para corrigir entidades sem tipo.",
            "metadados": {"ferramentas": "LLM para extração, algoritmo de Leiden"},
        },
        "cenario": {
            "id": "cen_elssa",
            "nome": "Transporte público – ações durante incidentes",
            "descricao": "Sugerir a supervisores de ônibus e metrô quais ações tomar durante um incidente operacional, com base nos procedimentos e em ocorrências parecidas do passado.",
        },
        "estrategias": ["estr_entrada_por_similaridade_e_travessia", "estr_resumos_comunidades"],
        "metricas": ["met_f1_acoes", "met_taxa_fabricacao_acoes"],
        "limitacoes": ["lim_erros_extracao_automatica", "lim_custo_chamadas_llm"],
        "trechos": [
            {
                "id": "tr_elssa_1",
                "pagina": 17,
                "texto": "Under the original tone, ELSSA achieves the highest code F1 score of 0.733, compared with 0.650–0.657 for other RAG structure.",
            },
            {
                "id": "tr_elssa_2",
                "pagina": 15,
                "texto": "The initial graph contains 106 entities labelled as UNKNOW, reflecting cases where the LLM could not confidently assign a type.",
            },
            {
                "id": "tr_elssa_3",
                "pagina": 15,
                "texto": "On average, ELSSA makes 5.607 LLM calls per query, reflecting its iterative agent-in-the-loop retrieval process, including LLM-based retrieval stopping and final recommendation generation.",
            },
        ],
    },
]

# Nós compartilhados (podem ligar mais de um estudo; é aí que o grafo ajuda a comparar).
ESTRATEGIAS = {
    "estr_consulta_cypher": ("Consultas estruturadas no grafo (Cypher)", "O sistema percorre as dependências guardadas no grafo com consultas Cypher para descobrir o que é afetado por um evento."),
    "estr_ligacoes_precomputadas": ("Ligações calculadas antes da consulta", "Na montagem do grafo, cada erro já é ligado às ações e contextos mais parecidos; na consulta, o sistema só segue essas ligações."),
    "estr_entrada_por_similaridade_e_travessia": ("Similaridade como porta de entrada e depois caminho no grafo", "A pergunta é comparada por similaridade de texto para achar os nós de entrada; a partir deles, a recuperação segue as relações do grafo."),
    "estr_resumos_comunidades": ("Resumos de comunidades do grafo", "O grafo é dividido em comunidades de entidades relacionadas, e os resumos dessas comunidades complementam o contexto entregue ao LLM."),
}

METRICAS = {
    "met_demonstracao_viabilidade": ("Demonstração de viabilidade (sem métrica numérica)", "O estudo mostra que o sistema funciona em um cenário simulado, mas não reporta métricas quantitativas."),
    "met_tempo_busca_usuarios": ("Tempo para encontrar a solução, com usuários", "Teste com 11 representantes de empresas industriais, comparando o tempo para achar a solução com a documentação e com a plataforma."),
    "met_acuracia_classificacao": ("Acurácia da classificação dos trechos", "Comparação entre os rótulos dados pelo classificador zero-shot e os rótulos de um especialista (acurácia de 72,8%)."),
    "met_ndcg_precisao": ("NDCG@5 e Precision@5", "Qualidade do ranqueamento das recomendações em 20 perfis de usuário, comparada com 5 abordagens de referência."),
    "met_risco_alucinacao": ("Risco de alucinação", "Proporção de respostas com informação não verificável: 0,3% no sistema proposto, contra 14,2% de um LLM sem grafo."),
    "met_f1_acoes": ("F1 das ações recomendadas", "Compara as ações sugeridas com as ações registradas pelos supervisores (F1 de 0,733, contra 0,650 a 0,657 de outras estruturas de RAG, no tom original)."),
    "met_taxa_fabricacao_acoes": ("Taxa de ações sem suporte", "Mede quantas ações sugeridas não têm apoio nas evidências recuperadas."),
}

LIMITACOES = {
    "lim_dados_sinteticos": ("Testado só com dados simulados", "O experimento usou dados sintéticos e um único cenário; falta validação com dados reais de obra."),
    "lim_coordenador_central": ("Coordenador central pode virar gargalo", "Concentrar a coordenação em um único agente facilita o controle, mas pode limitar a escala e criar um ponto único de falha."),
    "lim_erros_extracao_automatica": ("Erros na montagem automática do grafo", "Quando o grafo é montado por LLM a partir de textos, parte das classificações sai errada ou incompleta, e esses erros chegam às recomendações."),
    "lim_manutencao_ontologia": ("Manutenção contínua da ontologia", "O GraphRAG é mais complexo que o RAG tradicional e exige atualizar a ontologia e corrigir relações continuamente."),
    "lim_sem_validacao_real": ("Sem validação clínica", "Os perfis de usuário foram construídos pelos autores; os resultados mostram consistência interna, não validação clínica independente."),
    "lim_custo_chamadas_llm": ("Mais chamadas ao LLM por consulta", "A recuperação em várias etapas faz em média 5,6 chamadas ao LLM por consulta, contra 2 de uma alternativa mais simples."),
}


def montar():
    nos, arestas = [], []

    def no(id_, tipo, nome, descricao, metadados=None):
        nos.append({"id": id_, "tipo": tipo, "nome": nome, "descricao": descricao, "metadados": metadados or {}})

    def aresta(o, d, tipo):
        arestas.append({"origem_id": o, "destino_id": d, "tipo": tipo, "peso": 1.0})

    for k, (n, d) in ESTRATEGIAS.items():
        no(k, "EstrategiaRecuperacao", n, d)
    for k, (n, d) in METRICAS.items():
        no(k, "MetricaAvaliacao", n, d)
    for k, (n, d) in LIMITACOES.items():
        no(k, "Limitacao", n, d)

    for e in ESTUDOS:
        no(e["id"], "Estudo", e["nome"], e["descricao"], e["metadados"])
        t = e["tecnica"]
        no(t["id"], "Tecnica", t["nome"], t["descricao"], dict(t.get("metadados", {}), estudo_id=e["id"]))
        c = e["cenario"]
        no(c["id"], "CenarioDecisao", c["nome"], c["descricao"])
        aresta(e["id"], t["id"], "USA")
        aresta(t["id"], c["id"], "APLICADO_EM")
        for s in e["estrategias"]:
            aresta(t["id"], s, "UTILIZA_ESTRATEGIA")
        for m in e["metricas"]:
            aresta(t["id"], m, "AVALIADO_POR")
        for l in e["limitacoes"]:
            aresta(t["id"], l, "POSSUI_LIMITACAO")
        for tr in e["trechos"]:
            no(tr["id"], "Snippet", f"Trecho de {e['metadados']['autores']} ({e['metadados']['ano']})", tr["texto"],
               {"estudo_id": e["id"], "pagina": tr["pagina"], "arquivo_pdf": e["metadados"]["arquivo_pdf"]})
            aresta(e["id"], tr["id"], "EVIDENCIA_TEXTUAL")

    return {"versao": VERSAO_CORPUS, "nos": nos, "arestas": arestas}


if __name__ == "__main__":
    destino = os.path.join(os.path.dirname(__file__), "..", "api", "data", "seed_corpus.json")
    dados = montar()
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Corpus gravado: {len(dados['nos'])} nós, {len(dados['arestas'])} arestas -> {os.path.abspath(destino)}")
