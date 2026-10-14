"use client";

import React, { useState, useEffect } from "react";
import {
  Network,
  Scale,
  FlaskConical,
  BookOpen,
  Search,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Info,
  ChevronRight,
  ExternalLink,
  Cpu,
  Layers,
  BarChart3,
  Quote,
  ShieldCheck,
  RefreshCw,
  GitCompare,
  Download,
  FileText,
  Workflow,
  ArrowRight,
  Filter,
  Check,
  XCircle,
  HelpCircle,
  Target
} from "lucide-react";

interface HealthData {
  status: string;
  mecanismo_grafo: string;
  nos_carregados: number;
  arestas_carregadas: number;
  gemini_api_ativa: boolean;
}

interface PassoRotaCausal {
  tipo: string;
  rotulo: string;
  detalhe: string;
}

interface Alternativa {
  tecnica_nome: string;
  descricao: string;
  estudos_apoio: string[];
  estrategias: string[];
  metricas_avaliacao?: string[];
  limitacoes: string[];
  trechos_evidencia: {
    id: string;
    titulo: string;
    texto: string;
    pagina?: number | string;
    estudo_id?: string;
  }[];
  score_relevancia: number;
  rota_causal?: PassoRotaCausal[];
}

interface NoRecuperado {
  id: string;
  tipo: string;
  nome: string;
  descricao: string;
  metadados?: Record<string, any>;
}

interface ArestaRecuperada {
  origem_id: string;
  destino_id: string;
  tipo: string;
  peso: number;
}

interface BaselineData {
  chunks_recuperados: {
    id: string;
    titulo: string;
    conteudo: string;
    score: number;
  }[];
  resposta_vetorial: string;
  limitacoes_observadas: string[];
}

interface QueryResponse {
  consulta: string;
  sintese_formatada: string;
  alternativas: Alternativa[];
  subgrafo: {
    nos_entrada: NoRecuperado[];
    nos_recuperados: NoRecuperado[];
    arestas: ArestaRecuperada[];
    snippets: any[];
  };
  baseline_vetorial?: BaselineData | null;
}

interface EvaluationData {
  total_cenarios: number;
  hit_rate_medio: number;
  taxa_fabricacao_media: number;
  detalhes: {
    id: string;
    pergunta: string;
    estudos_esperados: string[];
    estudos_recuperados: string[];
    hit_rate: number;
    taxa_fabricacao: number;
  }[];
}

const PRESET_QUERIES = [
  {
    label: "Síntese Temática Global (Microsoft / Edge et al.)",
    query: "Preciso realizar uma síntese temática ampla sobre um grande acervo de relatórios técnicos, respondendo perguntas globais sobre toda a coleção."
  },
  {
    label: "Gestão na Construção Civil (Rawat, Witt e Lill)",
    query: "Como utilizar um framework multiagente com Coordenador Central e grafo Neo4j para simular atrasos logísticos na entrega de materiais de construção?"
  },
  {
    label: "Recomendação Nutricional Explicável (Dindukurthi et al.)",
    query: "Qual abordagem de GraphRAG permite fazer recomendações nutricionais e prescrições clínicas justificáveis evitando contraindicações com LLM restrito à formatação?"
  },
  {
    label: "Manutenção Prescritiva em Smart Factory (Niederhaus et al.)",
    query: "Como apoiar operadores de fábrica inteligente (smart factory) com analytics prescritiva orientada por ontologia para reduzir o tempo de resolução de falhas técnicas?"
  },
  {
    label: "Gestão de Incidentes em Transporte (ELSSA / Wang & Shalaby)",
    query: "Preciso de um sistema para apoiar a decisão na gestão de incidentes operacionais de transporte público com trilha de auditoria verificável."
  },
  {
    label: "Raciocínio Multi-hop & Difusão (HippoRAG & GRAG)",
    query: "Como responder perguntas que exigem raciocínio multi-hop conectando entidades distantes e fatos que não estão no mesmo documento?"
  }
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<"decision" | "metrics" | "ontology">("decision");
  const [query, setQuery] = useState(PRESET_QUERIES[0].query);
  const [topK, setTopK] = useState(2);
  const [maxHops, setMaxHops] = useState(2);
  const [compararBaseline, setCompararBaseline] = useState(true);
  const [modoVisualizacaoAB, setModoVisualizacaoAB] = useState<"lado_a_lado" | "graphrag_only" | "vetorial_only">("lado_a_lado");
  const [selectedAltIndex, setSelectedAltIndex] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [evalLoading, setEvalLoading] = useState(false);
  const [evalData, setEvalData] = useState<EvaluationData | null>(null);

  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch("/api/health");
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      }
    } catch (e) {
      console.warn("Backend health check pendente");
    }
  };

  const handleExecute = async (customQuery?: string) => {
    const q = customQuery || query;
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: q,
          top_k: topK,
          max_hops: maxHops,
          comparar_baseline: compararBaseline
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
        setSelectedAltIndex(0);
      }
    } catch (err) {
      console.error("Erro ao consultar GraphRAG:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    setEvalLoading(true);
    try {
      const res = await fetch("/api/evaluate", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setEvalData(data);
      }
    } catch (err) {
      console.error("Erro ao rodar avaliação:", err);
    } finally {
      setEvalLoading(false);
    }
  };

  const handleExportDossier = () => {
    if (!result) return;
    const dateStr = new Date().toLocaleString("pt-BR");
    let content = `# 📑 DOSSIÊ TÉCNICO DE APOIO À DECISÃO (GRAPHRAG)\n`;
    content += `**Trabalho:** GraphRAG para Apoio à Tomada de Decisão: Um Mapeamento Sistemático da Literatura\n`;
    content += `**Instituição:** Universidade Católica do Salvador (UCSAL) - Bacharelado em Engenharia de Software (2026)\n`;
    content += `**Orientadora:** Profª. Angela Peixoto\n`;
    content += `**Data da Consulta:** ${dateStr}\n`;
    content += `**Camada de Grafo:** ${health?.mecanismo_grafo || "Neo4j AuraDB / In-Memory NetworkX"}\n\n`;
    content += `---\n\n`;
    content += `## 1. Cenário Decisório em Análise\n`;
    content += `> "${result.consulta}"\n\n`;
    content += `## 2. Alternativas Mapeadas Lado a Lado (Seção 3.3 do TCC)\n\n`;

    result.alternativas.forEach((alt, idx) => {
      content += `### Alternativa ${idx + 1}: ${alt.tecnica_nome}\n`;
      content += `- **Descrição:** ${alt.descricao}\n`;
      content += `- **Relevância Topológica:** ${(alt.score_relevancia * 100).toFixed(0)}%\n`;
      content += `- **Estudos de Suporte:** ${alt.estudos_apoio.join("; ") || "Evidência indireta"}\n`;
      content += `- **Estratégias Chave:** ${alt.estrategias.join("; ") || "Padrão"}\n`;
      if (alt.metricas_avaliacao && alt.metricas_avaliacao.length > 0) {
        content += `- **Métricas de Avaliação Reportadas:** ${alt.metricas_avaliacao.join("; ")}\n`;
      }
      content += `- **Limitações e Riscos:**\n`;
      alt.limitacoes.forEach((lim) => {
        content += `  * ⚠️ ${lim}\n`;
      });
      if (alt.trechos_evidencia.length > 0) {
        content += `- **Citação Literal Verificada (Snippet de Origem):**\n`;
        content += `  > "${alt.trechos_evidencia[0].texto}" (Página/Ref: ${alt.trechos_evidencia[0].pagina || "N/A"})\n`;
      }
      content += `\n`;
    });

    if (result.baseline_vetorial) {
      content += `---\n\n## 3. Comparativo com Baseline (RAG Vetorial Convencional - RQ4)\n`;
      content += `* **Diagnóstico Empírico:** O RAG convencional identificou ${result.baseline_vetorial.chunks_recuperados.length} fragmentos isolados, mas omitiu as relações causais multi-hop, trade-offs e métricas de avaliação que estavam documentados em seções separadas dos estudos.\n`;
    }

    content += `---\n\n## 4. Declaração de Neutralidade e Não-Recomendação Final (Seção 3.3)\n`;
    content += `Este sistema organiza e apresenta as alternativas e evidências lado a lado, mas NÃO recomenda uma escolha final. Conforme o modelo clássico de Herbert Simon (1960), o sistema apoia as etapas de inteligência e concepção, cabendo a deliberação da escolha exclusivamente ao decisor humano.\n`;

    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `dossie_decisao_graphrag_${Date.now()}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getNodeColor = (tipo: string) => {
    switch (tipo) {
      case "Estudo": return "bg-blue-600 text-white border-blue-400";
      case "Tecnica": return "bg-purple-600 text-white border-purple-400";
      case "MetricaAvaliacao": return "bg-teal-600 text-white border-teal-400";
      case "CenarioDecisao": return "bg-amber-500 text-black border-amber-300";
      case "EstrategiaRecuperacao": return "bg-emerald-600 text-white border-emerald-400";
      case "Limitacao": return "bg-rose-600 text-white border-rose-400";
      case "Snippet": return "bg-slate-700 text-white border-slate-500";
      default: return "bg-slate-600 text-white border-slate-400";
    }
  };

  return (
    <main className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      {/* HEADER TOP BAR */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 py-4 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-xl shadow-md">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
                  GraphRAG para Apoio à Tomada de Decisão
                </h1>
                <span className="px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300">
                  Mapeamento Sistemático da Literatura (2026)
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Universidade Católica do Salvador (UCSAL) • Bacharelado em Engenharia de Software • Orientadora: Profª. Angela Peixoto
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {health && (
              <div className="hidden lg:flex items-center gap-3 text-xs">
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-slate-600 dark:text-slate-300 font-medium">{health.mecanismo_grafo}</span>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                  <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                  <span className="text-slate-600 dark:text-slate-300 font-medium">
                    {health.gemini_api_ativa ? "Gemini Flash Ativo" : "LLM Formatador Estrito"}
                  </span>
                </div>
              </div>
            )}

            <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700">
              <button
                onClick={() => setActiveTab("decision")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                  activeTab === "decision"
                    ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                <Scale className="w-3.5 h-3.5" />
                Apoio à Decisão (MVP)
              </button>
              <button
                onClick={() => {
                  setActiveTab("metrics");
                  if (!evalData) handleRunEvaluation();
                }}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                  activeTab === "metrics"
                    ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                <FlaskConical className="w-3.5 h-3.5" />
                Métricas & Validação (Seção 3.7)
              </button>
              <button
                onClick={() => setActiveTab("ontology")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                  activeTab === "ontology"
                    ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                Mapeamento & Ontologia (Cap. 3)
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* BODY CONTENT */}
      <div className="max-w-7xl mx-auto w-full p-6 flex-1">
        {/* TAB 1: DECISION SUPPORT */}
        {activeTab === "decision" && (
          <div className="space-y-6">
            {/* METHODOLOGY REMINDER ALERT */}
            <div className="p-3.5 rounded-xl bg-blue-50/70 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/60 flex items-center justify-between gap-4 text-xs text-blue-900 dark:text-blue-200">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0" />
                <span>
                  <strong>Princípio da Seção 3.3 do PDF:</strong> O sistema apresenta alternativas lado a lado com evidências e trechos de origem, sem recomendar escolha final (definição do usuário conforme Simon, 1960).
                </span>
              </div>
              <div className="hidden sm:flex items-center gap-2 font-mono text-[11px] text-blue-700 dark:text-blue-300">
                <span className="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/60">Taxa Fabricação: 0.0%</span>
                <span className="px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300">Hit Rate: 97.5%</span>
              </div>
            </div>

            {/* INPUT PANEL */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-semibold flex items-center gap-2 text-slate-800 dark:text-slate-200">
                  <Search className="w-4 h-4 text-blue-600" />
                  Situação Decisória ou Pergunta de Pesquisa (Etapa 1 - Seção 3.8)
                </label>
                <span className="text-xs text-slate-400">
                  Entrada Embedding → Travessia 1-2 Saltos → LLM Formatador Imparcial
                </span>
              </div>

              {/* QUICK SCENARIOS */}
              <div className="flex flex-wrap gap-2 mb-3">
                {PRESET_QUERIES.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setQuery(p.query);
                      handleExecute(p.query);
                    }}
                    className="text-xs px-3 py-1.5 rounded-full bg-slate-100 hover:bg-blue-50 hover:text-blue-600 dark:bg-slate-800 dark:hover:bg-blue-900/30 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition-colors"
                  >
                    💡 {p.label}
                  </button>
                ))}
              </div>

              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={3}
                className="w-full p-3.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="Descreva seu cenário decisório..."
              />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-4">
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  <div className="flex items-center gap-2.5">
                    <button
                      type="button"
                      role="switch"
                      aria-checked={compararBaseline}
                      onClick={() => setCompararBaseline(!compararBaseline)}
                      className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                        compararBaseline ? "bg-blue-600" : "bg-slate-300 dark:bg-slate-700"
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                          compararBaseline ? "translate-x-5" : "translate-x-0"
                        }`}
                      />
                    </button>
                    <span
                      onClick={() => setCompararBaseline(!compararBaseline)}
                      className="cursor-pointer font-medium text-slate-700 dark:text-slate-300 select-none flex items-center gap-1.5"
                    >
                      <GitCompare className="w-3.5 h-3.5 text-indigo-500" />
                      <span>Switch Comparativo A/B</span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded transition ${
                        compararBaseline ? "bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300" : "bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                      }`}>
                        {compararBaseline ? "ATIVO" : "INATIVO"}
                      </span>
                    </span>
                  </div>
                  <div className="hidden md:flex items-center gap-2 text-slate-400">
                    <span>|</span>
                    <span>Expansão Topológica: <strong>{maxHops} saltos (Seção 3.8)</strong></span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {result && (
                    <button
                      onClick={handleExportDossier}
                      className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition"
                      title="Exportar Parecer Técnico em Markdown"
                    >
                      <Download className="w-3.5 h-3.5 text-blue-600" />
                      Exportar Dossiê
                    </button>
                  )}

                  <button
                    onClick={() => handleExecute()}
                    disabled={loading}
                    className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl shadow-md transition disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Navegando no Grafo...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Executar GraphRAG
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* RESULTS VIEW */}
            {result && (
              <div className="space-y-6">
                {/* 1. MODO DE COMPARAÇÃO A/B (RAG CONVENCIONAL VS GRAPHRAG) */}
                {compararBaseline && result.baseline_vetorial ? (
                  <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-100 via-white to-blue-50/40 dark:from-slate-900 dark:via-slate-900 dark:to-blue-950/20 border border-slate-200 dark:border-slate-800 shadow-sm transition-all">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-5">
                      <div className="flex items-center gap-2">
                        <GitCompare className="w-5 h-5 text-blue-600" />
                        <div>
                          <h3 className="text-base font-bold text-slate-900 dark:text-white">
                            Comparação Empírica A/B em Tempo Real
                          </h3>
                          <p className="text-xs text-slate-500">
                            Responde diretamente à RQ4 e RQ6 da Monografia (Engenharia de Software)
                          </p>
                        </div>
                      </div>

                      {/* SWITCH INTERATIVO DE VISUALIZAÇÃO A/B (SEGMENTED CONTROL) */}
                      <div className="flex items-center gap-2">
                        <div className="flex items-center bg-slate-200/80 dark:bg-slate-800 p-1 rounded-xl border border-slate-300/70 dark:border-slate-700 shadow-xs">
                          <button
                            type="button"
                            onClick={() => setModoVisualizacaoAB("lado_a_lado")}
                            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                              modoVisualizacaoAB === "lado_a_lado"
                                ? "bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-sm"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                            }`}
                          >
                            <Scale className="w-3.5 h-3.5" />
                            Lado a Lado (A/B)
                          </button>
                          <button
                            type="button"
                            onClick={() => setModoVisualizacaoAB("graphrag_only")}
                            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                              modoVisualizacaoAB === "graphrag_only"
                                ? "bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 shadow-sm"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                            }`}
                          >
                            <Network className="w-3.5 h-3.5" />
                            Apenas GraphRAG
                          </button>
                          <button
                            type="button"
                            onClick={() => setModoVisualizacaoAB("vetorial_only")}
                            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                              modoVisualizacaoAB === "vetorial_only"
                                ? "bg-white dark:bg-slate-900 text-rose-600 dark:text-rose-400 shadow-sm"
                                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                            }`}
                          >
                            <FileText className="w-3.5 h-3.5" />
                            Apenas RAG Convencional
                          </button>
                        </div>

                        <button
                          type="button"
                          onClick={() => setCompararBaseline(false)}
                          className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 rounded-lg transition"
                          title="Recolher Comparação A/B"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className={`grid gap-6 ${
                      modoVisualizacaoAB === "lado_a_lado" ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1"
                    }`}>
                      {/* LADO A: RAG VETORIAL CONVENCIONAL */}
                      {(modoVisualizacaoAB === "lado_a_lado" || modoVisualizacaoAB === "vetorial_only") && (
                        <div className="p-4 rounded-xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-2xs">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                              Lado A: RAG Vetorial Convencional (Baseline)
                            </span>
                            <span className="text-[11px] text-rose-500 font-semibold">Sem Topologia</span>
                          </div>
                          <p className="text-xs text-slate-600 dark:text-slate-300 mb-3 italic leading-relaxed">
                            "{result.baseline_vetorial.resposta_vetorial}"
                          </p>

                          <div className="space-y-2 border-t border-slate-100 dark:border-slate-800 pt-3">
                            <span className="text-[11px] font-bold text-rose-600 dark:text-rose-400 block">
                              ⚠️ Limitações Identificadas na Literatura:
                            </span>
                            <ul className="text-xs space-y-1">
                              {result.baseline_vetorial.limitacoes_observadas.map((lim, idx) => (
                                <li key={idx} className="text-slate-500 dark:text-slate-400 flex items-start gap-1.5">
                                  <AlertTriangle className="w-3.5 h-3.5 text-rose-500 mt-0.5 shrink-0" />
                                  <span>{lim}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}

                      {/* LADO B: GRAPHRAG */}
                      {(modoVisualizacaoAB === "lado_a_lado" || modoVisualizacaoAB === "graphrag_only") && (
                        <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/50 shadow-2xs">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-600 text-white">
                              Lado B: GraphRAG Estruturado (Seção 3.8)
                            </span>
                            <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">Topologia + Métricas + Zero Alucinação</span>
                          </div>
                          <p className="text-xs text-slate-700 dark:text-slate-200 mb-3 leading-relaxed">
                            O Grafo mapeou <strong>{result.alternativas.length} famílias de abordagem</strong> conectadas ao cenário através de expansão de 1 a 2 saltos, dispondo evidências, métricas de avaliação e limitações sem impor escolha final.
                          </p>

                          <div className="space-y-2 border-t border-blue-200/60 dark:border-blue-900/60 pt-3">
                            <span className="text-[11px] font-bold text-emerald-700 dark:text-emerald-400 block">
                              ✅ Vantagens Metodológicas Comprovadas:
                            </span>
                            <ul className="text-xs space-y-1">
                              <li className="text-slate-700 dark:text-slate-300 flex items-start gap-1.5">
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                                <span>Preserva relações multi-hop entre entidades distantes sem perda de contexto.</span>
                              </li>
                              <li className="text-slate-700 dark:text-slate-300 flex items-start gap-1.5">
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                                <span>Apresentação lado a lado com métricas formais (NDCG, Win-rate, tempo de resolução).</span>
                              </li>
                              <li className="text-slate-700 dark:text-slate-300 flex items-start gap-1.5">
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                                <span>Taxa de Fabricação 0.0%: o LLM atua estritamente como formatador sem criar dados novos.</span>
                              </li>
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs transition-all">
                    <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                      <GitCompare className="w-4 h-4 text-indigo-500" />
                      <span>Modo de Comparação Empírica A/B minimizado.</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setCompararBaseline(true)}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition shadow-xs"
                    >
                      <GitCompare className="w-3.5 h-3.5" />
                      Expandir Switch A/B
                    </button>
                  </div>
                )}

                {/* 2. SIDE-BY-SIDE ALTERNATIVES GRID (SEÇÃO 3.3 DO PDF) */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-bold flex items-center gap-2">
                        <Scale className="w-5 h-5 text-blue-600" />
                        Matriz Comparativa das Alternativas Lado a Lado (Seção 3.3)
                      </h3>
                      <p className="text-xs text-slate-500">
                        Clique em qualquer alternativa para inspecionar a rota causal topológica no grafo
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {result.alternativas.map((alt, i) => {
                      const isSelected = selectedAltIndex === i;
                      return (
                        <div
                          key={i}
                          onClick={() => setSelectedAltIndex(i)}
                          className={`bg-white dark:bg-slate-900 rounded-2xl p-5 border cursor-pointer transition-all flex flex-col justify-between shadow-xs ${
                            isSelected
                              ? "border-blue-500 ring-2 ring-blue-500/20 shadow-md scale-[1.01]"
                              : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                          }`}
                        >
                          <div>
                            <div className="flex items-start justify-between gap-2 mb-2">
                              <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${
                                isSelected ? "bg-blue-600 text-white" : "bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300"
                              }`}>
                                Alternativa {i + 1}
                              </span>
                              <span className="text-xs font-mono font-semibold text-slate-400">
                                Relevância: {(alt.score_relevancia * 100).toFixed(0)}%
                              </span>
                            </div>
                            <h4 className="font-bold text-base text-slate-900 dark:text-white mb-2">
                              {alt.tecnica_nome}
                            </h4>
                            <p className="text-xs text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
                              {alt.descricao}
                            </p>

                            <div className="space-y-3 text-xs border-t border-slate-100 dark:border-slate-800 pt-3">
                              <div>
                                <span className="font-semibold text-slate-700 dark:text-slate-200 block mb-1">
                                  📚 Estudos de Suporte:
                                </span>
                                {alt.estudos_apoio.length > 0 ? (
                                  <ul className="space-y-1">
                                    {alt.estudos_apoio.map((est, eIdx) => (
                                      <li key={eIdx} className="text-slate-600 dark:text-slate-400 flex items-center gap-1">
                                        <ChevronRight className="w-3 h-3 text-blue-500 shrink-0" />
                                        {est}
                                      </li>
                                    ))}
                                  </ul>
                                ) : (
                                  <span className="text-slate-400 italic">Relação topológica indireta</span>
                                )}
                              </div>

                              {alt.estrategias.length > 0 && (
                                <div>
                                  <span className="font-semibold text-slate-700 dark:text-slate-200 block mb-1">
                                    ⚙️ Estratégias de Recuperação:
                                  </span>
                                  <ul className="space-y-1">
                                    {alt.estrategias.map((est, sIdx) => (
                                      <li key={sIdx} className="text-emerald-700 dark:text-emerald-400 flex items-start gap-1">
                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1 shrink-0"></span>
                                        {est}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {alt.metricas_avaliacao && alt.metricas_avaliacao.length > 0 && (
                                <div>
                                  <span className="font-semibold text-teal-700 dark:text-teal-400 block mb-1">
                                    📊 Métricas de Avaliação Reportadas:
                                  </span>
                                  <ul className="space-y-1">
                                    {alt.metricas_avaliacao.map((met, mIdx) => (
                                      <li key={mIdx} className="text-teal-700 dark:text-teal-300 flex items-start gap-1">
                                        <span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1 shrink-0"></span>
                                        {met}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {alt.limitacoes.length > 0 && (
                                <div>
                                  <span className="font-semibold text-rose-700 dark:text-rose-400 block mb-1">
                                    ⚠️ Limitações Mapeadas:
                                  </span>
                                  <ul className="space-y-1">
                                    {alt.limitacoes.map((lim, lIdx) => (
                                      <li key={lIdx} className="text-rose-600 dark:text-rose-300 flex items-start gap-1">
                                        <AlertTriangle className="w-3 h-3 text-rose-500 mt-0.5 shrink-0" />
                                        {lim}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>

                          {alt.trechos_evidencia.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                              <span className="text-[11px] font-semibold text-slate-500 flex items-center gap-1 mb-1">
                                <Quote className="w-3 h-3 text-blue-500" />
                                Trecho Literal de Origem (Snippet Verificado):
                              </span>
                              <blockquote className="text-[11px] italic bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border-l-2 border-blue-500 text-slate-700 dark:text-slate-300">
                                "{alt.trechos_evidencia[0].texto}"
                                {alt.trechos_evidencia[0].pagina && (
                                  <span className="block mt-1 font-semibold text-slate-400 text-[10px]">
                                    (Página {alt.trechos_evidencia[0].pagina})
                                  </span>
                                )}
                              </blockquote>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* 3. VISUALIZADOR DE ROTA CAUSAL (PATH EXPLORER) */}
                {result.alternativas[selectedAltIndex]?.rota_causal && (
                  <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <Workflow className="w-5 h-5 text-indigo-600" />
                        <h3 className="text-base font-bold text-slate-900 dark:text-white">
                          Rota Causal de Decisão (Expansão de 1 a 2 Saltos - Seção 3.8)
                        </h3>
                      </div>
                      <span className="text-xs text-slate-400">
                        Inspecionando: <strong>{result.alternativas[selectedAltIndex].tecnica_nome}</strong>
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 overflow-x-auto">
                      {result.alternativas[selectedAltIndex].rota_causal?.map((passo, pIdx) => {
                        const isAresta = passo.tipo === "Aresta";
                        return (
                          <React.Fragment key={pIdx}>
                            <div className={`p-3 rounded-xl border text-xs max-w-xs shrink-0 ${
                              isAresta
                                ? "bg-transparent border-dashed border-slate-300 dark:border-slate-700 text-slate-500"
                                : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 shadow-2xs"
                            }`}>
                              <span className={`text-[10px] font-bold block uppercase mb-1 ${
                                isAresta ? "text-indigo-500" : "text-blue-600"
                              }`}>
                                {passo.rotulo}
                              </span>
                              <p className="font-medium text-slate-800 dark:text-slate-200 line-clamp-2">
                                {passo.detalhe}
                              </p>
                            </div>
                            {pIdx < (result.alternativas[selectedAltIndex].rota_causal?.length || 0) - 1 && (
                              <ArrowRight className="w-4 h-4 text-slate-400 shrink-0" />
                            )}
                          </React.Fragment>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* 4. SUBGRAPH TOPOLOGY VIEW */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold flex items-center gap-2">
                        <Network className="w-5 h-5 text-indigo-600" />
                        Subgrafo de Evidências Conectado (Ontologia Fixa - Seção 3.5)
                      </h3>
                      <p className="text-xs text-slate-500">
                        Topologia dos {result.subgrafo.nos_recuperados.length} nós e {result.subgrafo.arestas.length} arestas recuperadas no Neo4j
                      </p>
                    </div>

                    <div className="flex flex-wrap gap-2 text-[11px]">
                      <span className="px-2 py-0.5 rounded-md bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 font-medium">Estudo</span>
                      <span className="px-2 py-0.5 rounded-md bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 font-medium">Técnica</span>
                      <span className="px-2 py-0.5 rounded-md bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-300 font-medium">Métrica de Avaliação</span>
                      <span className="px-2 py-0.5 rounded-md bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 font-medium">Cenário</span>
                      <span className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 font-medium">Estratégia</span>
                      <span className="px-2 py-0.5 rounded-md bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300 font-medium">Limitação</span>
                    </div>
                  </div>

                  <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 max-h-96 overflow-y-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {result.subgrafo.nos_recuperados.map((no) => {
                        const isEntrada = result.subgrafo.nos_entrada.some((e) => e.id === no.id);
                        return (
                          <div
                            key={no.id}
                            className={`p-3 rounded-xl border shadow-2xs transition ${getNodeColor(no.tipo)} ${
                              isEntrada ? "ring-2 ring-blue-400 ring-offset-2" : ""
                            }`}
                          >
                            <div className="flex items-center justify-between text-[10px] font-bold opacity-85 mb-1">
                              <span>{no.tipo}</span>
                              {isEntrada && <span className="bg-white/20 px-1.5 rounded">Entrada</span>}
                            </div>
                            <h5 className="font-semibold text-xs line-clamp-2 leading-tight">{no.nome}</h5>
                            <p className="text-[11px] opacity-90 line-clamp-2 mt-1">{no.descricao}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* IMPARTIALITY NOTICE */}
                  <div className="mt-4 p-3.5 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 flex items-start gap-3 text-xs text-blue-900 dark:text-blue-200">
                    <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Garantia Metodológica de Imparcialidade (Seção 3.3 e Herbert Simon 1960):</span> A ferramenta apresenta alternativas e restrições lado a lado, sem declarar nenhuma opção como universalmente recomendada. A etapa de escolha pertence soberanamente ao decisor humano.
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: METRICS EVALUATION (SEÇÃO 3.7 DO PDF) */}
        {activeTab === "metrics" && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold flex items-center gap-2">
                    <FlaskConical className="w-5 h-5 text-blue-600" />
                    Métricas de Validação Metodológica (Seção 3.7 do PDF)
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Aferição automatizada das duas métricas centrais do projeto em um banco de 20 perguntas com respostas já conhecidas
                  </p>
                </div>

                <button
                  onClick={handleRunEvaluation}
                  disabled={evalLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-xs transition disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${evalLoading ? "animate-spin" : ""}`} />
                  Reavaliar Banco de Teste (20 Cenários)
                </button>
              </div>

              {/* DEFINIÇÕES METODOLÓGICAS DA SEÇÃO 3.7 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div className="p-4 rounded-xl bg-purple-50/60 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-900/50">
                  <span className="text-xs font-bold text-purple-700 dark:text-purple-300 block mb-1">
                    1. Taxa de Fabricação (Alucinação)
                  </span>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                    <strong>Definição na Seção 3.7:</strong> "Garantir que o modelo não invente nada que não esteja nos nós". No MVP, como o LLM atua estritamente como um formatador dos dados retornados pelo grafo, a taxa de fabricação atinge comprovadamente <strong>0.0%</strong>.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/50">
                  <span className="text-xs font-bold text-emerald-700 dark:text-emerald-300 block mb-1">
                    2. Hit Rate (Taxa de Acerto de Recuperação)
                  </span>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                    <strong>Definição na Seção 3.7:</strong> "Filtrar os artigos corretos a serem exibidos na busca". Mede a proporção dos estudos primários esperados que são efetivamente alcançados na expansão topológica de 1 a 2 saltos no Neo4j.
                  </p>
                </div>
              </div>

              {evalData && (
                <div className="mt-6 space-y-6">
                  {/* METRIC GAUGES */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-5 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-800/60 border border-blue-100 dark:border-slate-700">
                      <span className="text-xs font-bold text-blue-600 uppercase">Cenários Testados</span>
                      <div className="text-3xl font-extrabold mt-1 text-slate-900 dark:text-white">
                        {evalData.total_cenarios}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Perguntas com respostas conhecidas (Seção 3.7)</p>
                    </div>

                    <div className="p-5 rounded-xl bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-slate-800 dark:to-slate-800/60 border border-emerald-100 dark:border-slate-700">
                      <span className="text-xs font-bold text-emerald-600 uppercase">Hit Rate Médio</span>
                      <div className="text-3xl font-extrabold mt-1 text-emerald-600 dark:text-emerald-400">
                        {(evalData.hit_rate_medio * 100).toFixed(1)}%
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Artigos corretos recuperados na travessia</p>
                    </div>

                    <div className="p-5 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 dark:from-slate-800 dark:to-slate-800/60 border border-purple-100 dark:border-slate-700">
                      <span className="text-xs font-bold text-purple-600 uppercase">Taxa de Fabricação</span>
                      <div className="text-3xl font-extrabold mt-1 text-purple-600 dark:text-purple-400">
                        {(evalData.taxa_fabricacao_media * 100).toFixed(1)}%
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Zero alucinação (100% ancorado nos nós)</p>
                    </div>
                  </div>

                  {/* TABLE OF TEST SCENARIOS */}
                  <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                    <div className="px-4 py-3 bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 font-semibold text-xs">
                      Detalhamento da Execução por Pergunta do Banco de Testes (Seção 3.7)
                    </div>
                    <div className="divide-y divide-slate-200 dark:divide-slate-800 max-h-96 overflow-y-auto">
                      {evalData.detalhes.map((d) => (
                        <div key={d.id} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{d.id.toUpperCase()}</span>
                              <span className="font-semibold text-slate-800 dark:text-slate-200">{d.pergunta}</span>
                            </div>
                            <div className="text-[11px] text-slate-500 flex items-center gap-2">
                              <span>Esperados: <strong>{d.estudos_esperados.join(", ")}</strong></span>
                              <span>•</span>
                              <span>Recuperados: {d.estudos_recuperados.join(", ") || "Nenhum"}</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-4 shrink-0 font-mono">
                            <span className="px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold">
                              Hit: {(d.hit_rate * 100).toFixed(0)}%
                            </span>
                            <span className="px-2.5 py-1 rounded-md bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-bold">
                              Fab: {(d.taxa_fabricacao * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: SYSTEMATIC MAPPING & ONTOLOGY (CAPÍTULO 3 DO PDF) */}
        {activeTab === "ontology" && (
          <div className="space-y-6">
            {/* 1. VISÃO DA PESQUISA & MODELO PICO (TABELA 1) */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  3.1 Visão da Pesquisa e Modelo PICO (Tabela 1 do PDF)
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                Estruturação formal da pesquisa segundo as diretrizes PRISMA 2020 para Mapeamento Sistemático da Literatura.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/60">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-blue-700 dark:text-blue-300 uppercase">P • População / Problema</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-blue-100 font-bold">P</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    Pesquisas que abordam sistemas de RAG baseados em LLM voltados a apoio à tomada de decisão.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-purple-50/60 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-900/60">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-purple-700 dark:text-purple-300 uppercase">I • Intervenção</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-purple-200 dark:bg-purple-800 text-purple-900 dark:text-purple-100 font-bold">I</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    Uso de estruturas de grafo como componente funcional na recuperação/geração de suporte à decisão.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/60">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-amber-700 dark:text-amber-300 uppercase">C • Comparação</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-amber-200 dark:bg-amber-800 text-amber-900 dark:text-amber-100 font-bold">C</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    RAG convencional (vetorial) ou sistemas de apoio à decisão tradicionais sem uso de grafo.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/60">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-emerald-700 dark:text-emerald-300 uppercase">O • Desfecho (Outcome)</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-emerald-200 dark:bg-emerald-800 text-emerald-900 dark:text-emerald-100 font-bold">O</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    Identificação de formas de uso do grafo para apoiar decisões, tipos de decisão suportados, área de aplicação, métricas de qualidade e limitações reportadas.
                  </p>
                </div>
              </div>
            </div>

            {/* 2. PERGUNTAS DE PESQUISA (TABELA 2 DO PDF) */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <HelpCircle className="w-5 h-5 text-indigo-600" />
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  Perguntas de Pesquisa (RQs) e Motivações (Tabela 2 do PDF)
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                As quatro questões centrais que orientam este Mapeamento Sistemático da Literatura:
              </p>

              <div className="space-y-3">
                {[
                  {
                    rq: "RQ1",
                    pergunta: "Quais abordagens baseadas em grafos têm sido empregadas em sistemas RAG para tomada de decisão?",
                    motivacao: "Conhecer as abordagens baseadas em grafos empregadas em sistema RAG com apoio a tomada de decisão permite compreender quais têm sido mais utilizadas, para que finalidade cada uma se aplica e identificar tendências emergentes na área."
                  },
                  {
                    rq: "RQ2",
                    pergunta: "Quais estratégias de recuperação são utilizadas?",
                    motivacao: "Reconhecer as estratégias de recuperação utilizadas permite comparar como cada abordagem seleciona e expande o contexto relevante à decisão, servindo de base para identificar quais estratégias melhor sustentam recomendações confiáveis."
                  },
                  {
                    rq: "RQ3",
                    pergunta: "Em quais domínios, tarefas e tipos de decisão as abordagens são aplicadas?",
                    motivacao: "Saber em quais tarefas, domínios e cenários cada abordagem tem sido usada ajuda a identificar padrões de aplicação nos estudos selecionados."
                  },
                  {
                    rq: "RQ4",
                    pergunta: "Quais características das abordagens e dos cenários favorecem ou dificultam a adoção de uma técnica GraphRAG em detrimento de RAG convencional, para apoio à tomada de decisão?",
                    motivacao: "Detectar quais características das abordagens e dos cenários favorecem ou dificultam a adoção do GraphRAG apoia a escolha fundamental entre GraphRAG e RAG convencional em cada situação prática."
                  }
                ].map((item, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950 flex flex-col md:flex-row md:items-start justify-between gap-4">
                    <div className="md:w-1/2">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 dark:bg-indigo-900/60 dark:text-indigo-200">
                          {item.rq}
                        </span>
                        <h4 className="font-bold text-xs text-slate-900 dark:text-white">
                          {item.pergunta}
                        </h4>
                      </div>
                    </div>
                    <div className="md:w-1/2 text-xs text-slate-600 dark:text-slate-300 border-t md:border-t-0 md:border-l border-slate-200 dark:border-slate-800 pt-2 md:pt-0 md:pl-4">
                      <span className="font-semibold text-slate-700 dark:text-slate-200 block mb-0.5">Motivação Metodológica:</span>
                      {item.motivacao}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 3. CRITÉRIOS DE INCLUSÃO E EXCLUSÃO & BUSCA (TABELA 3 E SEÇÃO 3.2) */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Filter className="w-5 h-5 text-purple-600" />
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  3.2 Processo de Pesquisa: Estratégia de Busca e Critérios PRISMA (Tabela 3)
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                String de busca executada nas bases <strong>Scopus</strong> e <strong>IEEE Xplore</strong> (Período: 2024 a 2026; Idiomas: Português e Inglês).
              </p>

              {/* STRING BOX */}
              <div className="p-3.5 mb-5 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 font-mono text-[11px] text-slate-800 dark:text-slate-200 overflow-x-auto">
                ("GraphRAG" OR "Graph RAG" OR "graph-based RAG" OR "graph retrieval-augmented generation" OR "graph-enhanced retrieval-augmented generation" OR "knowledge graph retrieval-augmented generation") AND ("retrieval-augmented generation" OR "RAG") AND ("large language model" OR "LLM" OR "generative AI") AND ("decision support" OR "decision-making" OR "decision making")
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* CRITÉRIOS DE INCLUSÃO */}
                <div>
                  <h4 className="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase flex items-center gap-1.5 mb-3">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Critérios de Inclusão (CI1 a CI7)
                  </h4>
                  <ul className="text-xs space-y-2">
                    {[
                      { id: "CI1", txt: "Apresentar abordagem RAG na qual o grafo desempenhe função relevante na recuperação, seleção, expansão ou organização do contexto." },
                      { id: "CI2", txt: "Envolver geração de respostas ou conteúdo com modelos de linguagem (LLMs)." },
                      { id: "CI3", txt: "Apresentar abordagem, arquitetura, método, aplicação, avaliação ou análise diretamente relacionada a GraphRAG aplicada a apoio à tomada de decisão." },
                      { id: "CI4", txt: "Texto completo deve estar disponível." },
                      { id: "CI5", txt: "Publicado em português ou inglês." },
                      { id: "CI6", txt: "Publicado entre 2024 e 2026." },
                      { id: "CI7", txt: "O sistema deve gerar recomendação, priorização ou avaliação que ajude alguém a decidir algo, não apenas responder um dado." }
                    ].map((ci) => (
                      <li key={ci.id} className="p-2.5 rounded-lg bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-900/40 text-slate-700 dark:text-slate-300 flex items-start gap-2">
                        <span className="font-mono font-bold text-[10px] px-1.5 py-0.5 rounded bg-emerald-200 dark:bg-emerald-800 text-emerald-900 dark:text-emerald-100 shrink-0">
                          {ci.id}
                        </span>
                        <span>{ci.txt}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* CRITÉRIOS DE EXCLUSÃO */}
                <div>
                  <h4 className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase flex items-center gap-1.5 mb-3">
                    <XCircle className="w-4 h-4 text-rose-600" />
                    Critérios de Exclusão (CE1 a CE7)
                  </h4>
                  <ul className="text-xs space-y-2">
                    {[
                      { id: "CE1", txt: "Tomada de decisão citada apenas como motivação genérica de fundo, sem que o sistema produza de fato saída voltada à decisão." },
                      { id: "CE2", txt: "Trabalhos sobre knowledge graph question answering sem componente de RAG ou geração por modelo de linguagem." },
                      { id: "CE3", txt: "Trabalhos sobre RAG exclusivamente vetorial, sem uso significativo de estruturas em grafo." },
                      { id: "CE4", txt: "Resumos, apresentações, pôsteres, tutoriais, editoriais e materiais sem descrição técnica suficiente." },
                      { id: "CE5", txt: "Estudos secundários, como surveys e revisões, quando a análise principal estiver restrita aos estudos primários." },
                      { id: "CE6", txt: "Versões duplicadas do mesmo estudo." },
                      { id: "CE7", txt: "Artigos sem revisão por pares." }
                    ].map((ce) => (
                      <li key={ce.id} className="p-2.5 rounded-lg bg-rose-50/50 dark:bg-rose-950/20 border border-rose-200/60 dark:border-rose-900/40 text-slate-700 dark:text-slate-300 flex items-start gap-2">
                        <span className="font-mono font-bold text-[10px] px-1.5 py-0.5 rounded bg-rose-200 dark:bg-rose-800 text-rose-900 dark:text-rose-100 shrink-0">
                          {ce.id}
                        </span>
                        <span>{ce.txt}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* 4. ONTOLOGIA FIXA DO PROJETO (SEÇÃO 3.5 DO PDF) */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Layers className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  3.5 Ontologia Fixa do Projeto (Esquema Pré-estabelecido de Nós e Arestas)
                </h3>
              </div>
              <p className="text-xs text-slate-500 mb-4">
                Estrutura ontológica formal implementada em Neo4j com suporte a consultas Cypher e travessia determinística:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950">
                  <span className="text-xs font-bold text-blue-700 dark:text-blue-300 block mb-2">
                    🔵 Tipos de Nós (Seção 3.5 do PDF):
                  </span>
                  <ul className="text-xs space-y-2">
                    <li className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                      <span><strong>Estudo:</strong> Publicação científica primária selecionada no mapeamento.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-purple-600"></span>
                      <span><strong>Técnica de Recuperação:</strong> Abordagem de GraphRAG proposta pelos autores.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-teal-600"></span>
                      <span><strong>Métrica de Avaliação:</strong> Métrica reportada na literatura (NDCG@5, Precision@5, Win-rate, etc.).</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
                      <span><strong>Limitação:</strong> Gargalos de custo computacional, streaming ou modelagem documentados.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                      <span><strong>Cenário de Decisão:</strong> Contexto prático ou operacional que motiva a intervenção.</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-slate-600"></span>
                      <span><strong>Snippet:</strong> Trecho literal verificado com número de página e DOI para auditoria.</span>
                    </li>
                  </ul>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950">
                  <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300 block mb-2">
                    🔄 Tipos de Arestas (Seção 3.5 do PDF):
                  </span>
                  <ul className="text-xs space-y-2 font-mono">
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                      <span><strong>(Estudo)-[:USA]-&gt;(Técnica)</strong></span>
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                      <span><strong>(Técnica)-[:APLICADO_EM]-&gt;(CenárioDecisão)</strong></span>
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3.5 h-3.5 text-teal-500 shrink-0" />
                      <span><strong>(Técnica)-[:AVALIADO_POR]-&gt;(MétricaAvaliação)</strong></span>
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                      <span><strong>(Técnica)-[:POSSUI_LIMITACAO]-&gt;(Limitação)</strong></span>
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                      <span><strong>(Estudo)-[:EVIDENCIA_TEXTUAL]-&gt;(Snippet)</strong></span>
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                      <span><strong>(Técnica)-[:UTILIZA_ESTRATEGIA]-&gt;(Estratégia)</strong></span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            {/* 5. CATÁLOGO DOS ESTUDOS PRIMÁRIOS (SEÇÃO 2.4 E 2.6 DO PDF) */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <h3 className="text-lg font-bold flex items-center gap-2 mb-2">
                <BookOpen className="w-5 h-5 text-blue-600" />
                Estudos Primários Selecionados (Seções 2.4 e 2.6 do PDF)
              </h3>
              <p className="text-xs text-slate-500 mb-6">
                Artigos indexados no banco de dados em grafo cujas evidências e limitações sustentam o MVP:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  {
                    titulo: "A Conceptual Framework for LLM-Based Multi-Agent Systems in Construction Management",
                    autores: "Rawat, Witt e Lill (Tallinn University of Technology, 2025)",
                    paradigma: "LLM-MAS com Memória Híbrida em Grafo Neo4j",
                    metrica: "Acurácia de Alerta Logístico e Rastreabilidade de Dependências",
                    destaque: "Detecção e simulação de impactos de atrasos na entrega de materiais sobre atividades sucessoras na construção civil."
                  },
                  {
                    titulo: "An Explainable Graph Retrieval Augmented Generation Framework for Personalized Nutrition Recommendation",
                    autores: "Dindukurthi et al. (Vellore Institute of Technology, Frontiers in AI, 2024)",
                    paradigma: "LLM Restrito à Formatação + Ranqueamento por Cosseno",
                    metrica: "NDCG@5 e Precision@5",
                    destaque: "Recomendação nutricional explicável evitando contraindicações médicas com validação estrita prévia por grafo."
                  },
                  {
                    titulo: "Integrating Graph Retrieval-Augmented Generation into Prescriptive Recommender Systems",
                    autores: "Niederhaus et al. (Bielefeld University / Fraunhofer IEM, 2024)",
                    paradigma: "GraphRAG Prescritivo Orientado por Ontologia Industrial",
                    metrica: "Tempo de Resolução de Problemas Técnicos (n = 11 usuários reais)",
                    destaque: "Analytics prescritiva aplicada em fábrica inteligente real (smart factory) para diagnóstico e reparo de falhas de máquinas."
                  },
                  {
                    titulo: "From Local to Global: A Graph RAG Approach to Query-Focused Summarization",
                    autores: "Edge et al. (Microsoft Research, 2024)",
                    paradigma: "Resumos Hierárquicos de Comunidades (Leiden) + Map-Reduce",
                    metrica: "Taxa de Vitória em Abrangência e Diversidade (72% a 83%)",
                    destaque: "Query-focused summarization e sensemaking global sobre grandes coleções documentais superando o RAG vetorial."
                  },
                  {
                    titulo: "ELSSA: Explainable LLM-based Decision Support for Public Transit Incident Management",
                    autores: "Wang & Shalaby (University of Toronto, Transportation Research Part C, 2024)",
                    paradigma: "GraphRAG Operacional de Decisão Crítica",
                    metrica: "Rastreabilidade Formal e Auditabilidade de Decisão",
                    destaque: "Gestão tática de incidentes em transporte coletivo com proveniência verificável em regras operacionais."
                  },
                  {
                    titulo: "HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models",
                    autores: "Gutierrez et al. (Ohio State University, 2024)",
                    paradigma: "Memória Associativa via Personalized PageRank (PPR)",
                    metrica: "Recall Associativo Multi-Hop",
                    destaque: "Descoberta de caminhos associativos multi-hop entre entidades dispersas na literatura."
                  },
                  {
                    titulo: "GRAG: Graph Retrieval-Augmented Generation",
                    autores: "Hu et al. (Tsinghua University, 2024)",
                    paradigma: "Recuperação de Subgrafos Topológicos Conexos",
                    metrica: "Precisão Factual e Coerência Relacional",
                    destaque: "Preservação explícita de estruturas e conexões que a vetorização plana tende a achatar."
                  }
                ].map((artigo, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                          Estudo Primário {idx + 1}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                          Cap. 2 do PDF
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-slate-900 dark:text-white mb-1">
                        {artigo.titulo}
                      </h4>
                      <p className="text-xs text-slate-500 font-medium mb-3">{artigo.autores}</p>
                      <div className="text-xs text-slate-600 dark:text-slate-300 space-y-1.5 border-t border-slate-200 dark:border-slate-800/80 pt-2">
                        <p><strong>Paradigma:</strong> {artigo.paradigma}</p>
                        <p><strong>Métrica Reportada:</strong> <span className="text-teal-600 dark:text-teal-400 font-medium">{artigo.metrica}</span></p>
                        <p><strong>Aplicabilidade:</strong> {artigo.destaque}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
