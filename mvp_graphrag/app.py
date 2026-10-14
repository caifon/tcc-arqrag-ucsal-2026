import streamlit as st
import json
import os
from typing import List

from mvp_graphrag.ontology import NoGrafo, ArestaGrafo, TipoNo
from mvp_graphrag.graph.inmemory_adapter import InMemoryGraphRepository
from mvp_graphrag.graph.neo4j_adapter import Neo4jGraphRepository
from mvp_graphrag.engine.embeddings import LightweightEmbeddingEngine
from mvp_graphrag.engine.traversal import GraphTraversalEngine
from mvp_graphrag.engine.formatter import StrictLLMFormatter
from mvp_graphrag.evaluation.metrics import Evaluator

# Configuração da Página
st.set_page_config(
    page_title="GraphRAG - Apoio à Tomada de Decisão",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .step-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .metric-card {
        background: linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .card-alt {
        border-left: 4px solid #3B82F6;
        padding: 12px;
        background-color: #FFFFFF;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def inicializar_sistema():
    caminho_base = os.path.dirname(os.path.abspath(__file__))
    caminho_seed = os.path.join(caminho_base, "data", "seed_corpus.json")
    
    with open(caminho_seed, "r", encoding="utf-8") as f:
        dados = json.load(f)

    nos = [NoGrafo(**item) for item in dados["nos"]]
    arestas = [ArestaGrafo(**item) for item in dados["arestas"]]

    # Inicializar adaptadores
    repo_inmemory = InMemoryGraphRepository()
    repo_inmemory.carregar_dados(nos, arestas)

    repo_neo4j = Neo4jGraphRepository()
    # Tenta conectar ao Neo4j se disponível
    conectou_neo4j = repo_neo4j.conectar()
    if conectou_neo4j:
        repo_neo4j.carregar_dados(nos, arestas)

    embedding_engine = LightweightEmbeddingEngine()
    formatter = StrictLLMFormatter()

    return {
        "nos": nos,
        "arestas": arestas,
        "repo_inmemory": repo_inmemory,
        "repo_neo4j": repo_neo4j,
        "embedding_engine": embedding_engine,
        "formatter": formatter,
        "caminho_base": caminho_base
    }


def gerar_html_grafo(subgrafo):
    """Gera visualização interativa do grafo com Vis.js para renderização limpa no Streamlit."""
    cores_nos = {
        "Estudo": "#3B82F6",           # Azul
        "Tecnica": "#8B5CF6",          # Roxo
        "CenarioDecisao": "#F59E0B",    # Âmbar / Laranja
        "EstrategiaRecuperacao": "#10B981", # Verde
        "Limitacao": "#EF4444",        # Vermelho
        "Snippet": "#64748B"           # Cinza ardósia
    }

    nos_vis = []
    for no in subgrafo.nos_recuperados:
        cor = cores_nos.get(no.tipo.value, "#94A3B8")
        is_entrada = any(e.id == no.id for e in subgrafo.nos_entrada)
        borda = "#000000" if is_entrada else cor
        largura_borda = 3 if is_entrada else 1
        
        nos_vis.append({
            "id": no.id,
            "label": no.nome[:25] + ("..." if len(no.nome) > 25 else ""),
            "title": f"<b>{no.tipo.value}</b>: {no.nome}<br><br>{no.descricao}",
            "color": {"background": cor, "border": borda},
            "borderWidth": largura_borda,
            "shape": "box" if no.tipo.value == "Tecnica" else "ellipse",
            "font": {"color": "#FFFFFF" if no.tipo.value != "CenarioDecisao" else "#000000"}
        })

    arestas_vis = []
    for a in subgrafo.arestas:
        arestas_vis.append({
            "from": a.origem_id,
            "to": a.destino_id,
            "label": a.tipo.value,
            "arrows": "to",
            "font": {"size": 9, "align": "middle", "color": "#475569"},
            "color": {"color": "#CBD5E1"}
        })

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            #rede-grafo {{
                width: 100%;
                height: 480px;
                border: 1px solid #E2E8F0;
                background-color: #F8FAFC;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
    <div id="rede-grafo"></div>
    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nos_vis)});
        var edges = new vis.DataSet({json.dumps(arestas_vis)});
        var container = document.getElementById('rede-grafo');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            physics: {{
                stabilization: true,
                barnesHut: {{
                    gravitationalConstant: -2000,
                    springLength: 120,
                    springConstant: 0.04
                }}
            }},
            interaction: {{ hover: true, tooltipDelay: 100 }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
    </body>
    </html>
    """
    return html


def main():
    ctx = inicializar_sistema()

    st.markdown('<div class="main-header">🕸️ GraphRAG para Apoio à Tomada de Decisão</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Demonstração Funcional do MVP | Universidade Católica do Salvador (UCSAL) - 2026</div>', unsafe_allow_html=True)

    # Barra lateral de configuração
    with st.sidebar:
        st.header("⚙️ Parâmetros de Execução")
        
        # Modo de Grafo
        if ctx["repo_neo4j"].is_connected:
            modo_grafo = st.radio("Mecanismo de Grafo:", ["Neo4j (Oficial)", "Em Memória (NetworkX)"])
            repo_selecionado = ctx["repo_neo4j"] if "Neo4j" in modo_grafo else ctx["repo_inmemory"]
            st.success("🟢 Neo4j Conectado")
        else:
            st.info("ℹ️ Operando no modo **Em Memória (NetworkX)**. (Neo4j local desligado)")
            repo_selecionado = ctx["repo_inmemory"]

        max_saltos = st.slider("Saltos de Travessia (Hops):", min_value=1, max_value=2, value=2, help="Expansão de 1 a 2 saltos conforme desenho metodológico")
        top_k_entrada = st.slider("Top-K Nós de Entrada (Embedding):", min_value=1, max_value=4, value=2)

        st.markdown("---")
        st.markdown("**Ontologia Fixa Carregada:**")
        st.caption(f"• Nós catalogados: **{len(ctx['nos'])}**")
        st.caption(f"• Arestas ontológicas: **{len(ctx['arestas'])}**")
        st.caption(f"• Estudos primários: **5** (Edge, Gutierrez, Hu, Zhang, Chen)")

    # Motor de travessia
    traversal_engine = GraphTraversalEngine(repo_selecionado, ctx["embedding_engine"])

    tab_consulta, tab_metricas, tab_ontologia = st.tabs(["🔍 Apoio à Decisão", "📊 Avaliação Experimental (Métricas)", "📑 Ontologia & Corpus"])

    with tab_consulta:
        # Seletor de exemplos rápidos para facilitar demonstração
        exemplos = [
            "Selecione um cenário pré-configurado...",
            "Preciso de uma síntese temática ampla e visão global sobre um acervo de relatórios técnicos.",
            "Como apoiar o raciocínio multi-hop conectando fatos distribuídos em múltiplos documentos distantes?",
            "Preciso de apoio à tomada de decisão para incidentes de transporte com justificativa explicável.",
            "Como recomendar protocolos de nutrição clínica personalizada garantindo trilha de auditoria e evitando contraindicações?",
            "Quais técnicas usam difusão como Personalized PageRank para navegar em memória de longo prazo?"
        ]

        escolha_exemplo = st.selectbox("💡 Casos Decisórios de Teste Rápido:", exemplos)

        if escolha_exemplo != "Selecione um cenário pré-configurado...":
            pergunta_inicial = escolha_exemplo
        else:
            pergunta_inicial = "Preciso de uma síntese temática ampla e visão global sobre grandes coleções de texto."

        query = st.text_area("Descreva o Cenário Decisório ou Pergunta:", value=pergunta_inicial, height=80)
        btn_executar = st.button("🚀 Executar GraphRAG", type="primary", use_container_width=True)

        if btn_executar or query:
            with st.spinner("Processando recuperação em 4 etapas..."):
                subgrafo, alternativas = traversal_engine.executar_recuperacao(
                    query, top_k_entrada=top_k_entrada, max_saltos=max_saltos
                )

            # 4 Etapas Visíveis
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("#### 1️⃣ Ponto de Entrada (Embedding)")
                st.caption("O vetor da consulta encontrou a porta de entrada com maior similaridade:")
                for no in subgrafo.nos_entrada:
                    st.info(f"**[{no.tipo.value}]** {no.nome}\n\n*{no.descricao}*")

                st.markdown("#### 2️⃣ Subgrafo de Evidências Conectado (1 a 2 Saltos)")
                st.caption(f"Travessia recuperou **{len(subgrafo.nos_recuperados)} nós** e **{len(subgrafo.arestas)} arestas**.")
                html_grafo = gerar_html_grafo(subgrafo)
                st.components.v1.html(html_grafo, height=500)

            with col2:
                st.markdown("#### 3️⃣ Formatação Imparcial (LLM)")
                st.caption("Alternativas dispostas lado a lado com citação estrita de evidências e limitações:")

                texto_sintese = ctx["formatter"].formatar_resposta(query, alternativas, subgrafo)
                st.markdown(texto_sintese)

                # Auditoria de Rastreabilidade
                st.markdown("---")
                st.markdown("#### 4️⃣ Auditoria de Rastreabilidade e Trechos Literais")
                if subgrafo.snippets:
                    for s in subgrafo.snippets:
                        with st.expander(f"📖 {s['titulo']}"):
                            st.write(s['texto'])
                            st.caption(f"Vínculo: {s.get('estudo_id', '')}")
                else:
                    st.caption("Nenhum snippet literal associado.")

    with tab_metricas:
        st.markdown("### 🧪 Validação Experimental por Lote")
        st.markdown("""
        Esta seção atende aos requisitos do protocolo de pesquisa do TCC:
        - **Hit Rate**: Proporção em que os artigos esperados constam no subgrafo recuperado.
        - **Taxa de Fabricação**: Validação de que nenhuma afirmação foi inventada fora dos nós e arestas.
        """)

        caminho_testes = os.path.join(ctx["caminho_base"], "data", "test_scenarios.json")

        if st.button("▶️ Executar Validação Automatizada do Banco de 20 Cenários", type="secondary"):
            with st.spinner("Executando os 20 cenários de teste..."):
                relatorio = Evaluator.avaliar_banco_completo(traversal_engine, caminho_testes)

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Cenários Avaliados", relatorio["total_cenarios"])
            with col_m2:
                st.metric("Hit Rate Médio", f"{relatorio['hit_rate_medio'] * 100:.1f}%")
            with col_m3:
                st.metric("Taxa de Fabricação", f"{relatorio['taxa_fabricacao_media'] * 100:.1f}%")

            st.markdown("#### Tabela Detalhada dos 20 Cenários de Teste")
            st.dataframe(relatorio["detalhes"], use_container_width=True)

    with tab_ontologia:
        st.markdown("### 🏛️ Esquema da Ontologia e Corpus")
        st.markdown("""
        A ontologia rígida do projeto é composta pelos tipos:
        - **Estudo**: Artigo acadêmico mapeado na revisão sistemática.
        - **Tecnica**: Família de abordagem GraphRAG.
        - **CenarioDecisao**: Situação decisória prática do usuário.
        - **EstrategiaRecuperacao**: Algoritmo de recuperação (PPR, Comunidades Leiden, k-hop).
        - **Limitacao**: Custos, gargalos ou restrições documentadas.
        - **Snippet**: Trecho textual literal com página e DOI.
        """)

        st.markdown("#### Artigos Científicos Primários Integrados:")
        for no in ctx["nos"]:
            if no.tipo == TipoNo.ESTUDO:
                with st.expander(f"📄 {no.nome}"):
                    st.write(f"**Descrição:** {no.descricao}")
                    st.json(no.metadados)


if __name__ == "__main__":
    main()
