"use client";

import { useEffect, useState, useMemo } from "react";
import {
  BookOpen,
  ChevronRight,
  CircleCheck,
  CircleX,
  FlaskConical,
  LoaderCircle,
  Quote,
  Search,
  SearchX,
  TriangleAlert,
  Sparkles,
  ShieldCheck,
  Layers,
  ArrowRight,
  ExternalLink,
  Filter,
  CheckCircle2,
  FileText,
  Workflow,
  HelpCircle,
  Scale
} from "lucide-react";

interface Estudo {
  id: string;
  titulo: string;
  autores: string;
  ano: number | null;
  veiculo: string;
}

interface Trecho {
  id: string;
  texto: string;
  pagina: number | string;
}

interface Passo {
  tipo: string;
  nome: string;
  relacao?: string | null;
}

interface Alternativa {
  tecnica_id: string;
  tecnica_nome: string;
  descricao: string;
  estudo: Estudo | null;
  cenarios: string[];
  estrategias: string[];
  metricas_avaliacao: string[];
  limitacoes: string[];
  trechos_evidencia: Trecho[];
  caminho: Passo[];
}

interface Conferencia {
  itens_verificados: number;
  itens_sem_suporte: number;
  detalhes_sem_suporte: { tipo: string; valor: string }[];
}

interface Resposta {
  consulta: string;
  resumo: string;
  resumo_origem: "llm" | "modelo_fixo";
  conferencia_resumo: Conferencia;
  alternativas: Alternativa[];
}

interface Pontuacao {
  hit_rate: number | null;
  precisao: number | null;
  abstencao_correta: boolean | null;
}

interface DetalheAvaliacao extends Pontuacao {
  id: string;
  tipo: string;
  pergunta: string;
  estudos_esperados: string[];
  estudos_recuperados: string[];
  referencia_sem_grafo: Pontuacao & { estudos_recuperados: string[] };
}

interface Avaliacao {
  total_cenarios: number;
  perguntas_com_resposta: number;
  perguntas_fora_do_escopo: number;
  modo_similaridade: "embedding" | "local" | "misto";
  perguntas_por_modo?: Record<string, number>;
  graphrag: {
    hit_rate_medio: number;
    precisao_media: number;
    abstencao_correta: number;
    taxa_fabricacao: number;
    afirmacoes_verificadas: number;
  };
  referencia_sem_grafo: {
    hit_rate_medio: number;
    precisao_media: number;
    abstencao_correta: number;
  };
  detalhes: DetalheAvaliacao[];
}

interface NoGrafo {
  id: string;
  tipo: string;
  nome: string;
  descricao: string;
  metadados: Record<string, string | number>;
}

const EXEMPLOS = [
  {
    rotulo: "Falha em máquina na fábrica",
    texto: "Quero um sistema que recomende ações para corrigir falhas em máquinas usando os manuais técnicos da fábrica.",
  },
  {
    rotulo: "Atraso de material em obra",
    texto: "Preciso avisar o gestor de uma obra quando um atraso na entrega de material afetar outras atividades do cronograma.",
  },
  {
    rotulo: "Incidente no transporte público",
    texto: "Preciso apoiar supervisores na escolha de ações durante um incidente no transporte público.",
  },
  {
    rotulo: "Alimentação para paciente",
    texto: "Como recomendar alimentos para uma pessoa com uma doença específica, explicando o motivo de cada indicação?",
  },
  {
    rotulo: "Fora do escopo: fraude em cartão",
    texto: "Como detectar fraudes em transações de cartão de crédito?",
  },
];

const pct = (v: number | null | undefined) => (v === null || v === undefined ? "—" : `${Math.round(v * 100)}%`);

const separar = (item: string) => {
  const i = item.indexOf(": ");
  return i > 0 ? { titulo: item.slice(0, i), texto: item.slice(i + 2) } : { titulo: item, texto: "" };
};

const nomeEstudo = (id: string) =>
  ({
    est_rawat: "Rawat et al.",
    est_niederhaus: "Niederhaus et al.",
    est_dindukurthi: "Dindukurthi et al.",
    est_elssa: "Wang & Shalaby (ELSSA)",
    est_lu_pipeline: "Lu et al.",
    est_zheng_ev: "Zheng et al. (2025a)",
    est_zheng_tcm: "Zheng et al. (2025b)",
    est_liu_fusionom: "Liu et al.",
    est_yan_uuv: "Yan et al.",
    est_mallala_robot: "Mallala & Sharma",
  }[id] ?? id);

export default function Home() {
  const [aba, setAba] = useState<"consultar" | "avaliacao" | "acervo">("consultar");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 antialiased">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-teal-600 to-emerald-700 text-white shadow-sm shadow-teal-700/20">
              <Workflow className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight text-slate-900">
                  GraphRAG para Apoio à Decisão
                </h1>
                <span className="hidden rounded-full bg-teal-50 px-2 py-0.5 text-[11px] font-semibold text-teal-700 border border-teal-200/60 sm:inline-block">
                  MVP · TCC 2026
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Mapeamento Sistemático da Literatura · Engenharia de Software UCSal
              </p>
            </div>
          </div>

          <nav
            className="flex rounded-xl bg-slate-100 p-1 text-xs font-medium text-slate-600 shadow-inner"
            aria-label="Navegação do MVP"
          >
            {(
              [
                ["consultar", "Consultar", Search],
                ["avaliacao", "Avaliação", FlaskConical],
                ["acervo", "Sobre o acervo", BookOpen],
              ] as const
            ).map(([id, rotulo, Icone]) => {
              const ativo = aba === id;
              return (
                <button
                  key={id}
                  onClick={() => setAba(id)}
                  className={`flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 transition-all duration-150 ${
                    ativo
                      ? "bg-white font-semibold text-slate-900 shadow-sm"
                      : "hover:text-slate-900"
                  }`}
                >
                  <Icone className={`h-3.5 w-3.5 ${ativo ? "text-teal-600" : "text-slate-400"}`} />
                  {rotulo}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">
        {aba === "consultar" && <Consultar />}
        {aba === "avaliacao" && <AbaAvaliacao />}
        {aba === "acervo" && <SobreAcervo />}
      </main>

      <footer className="mt-16 border-t border-slate-200/60 bg-white py-6 text-center text-xs text-slate-500">
        <p>
          Trabalho de Conclusão de Curso (TCC) · Universidade Católica do Salvador (UCSal)
        </p>
        <p className="mt-1 text-slate-400">
          Orientadora: Profa. Angela Peixoto · Autores: Adriano Abreu de Almeida, Alison Andrade Rocha, Caio Roldão de Almeida Fonseca, Lívia Alves de Souza e Wendel Campos Bezerra
        </p>
      </footer>
    </div>
  );
}

function Consultar() {
  const [pergunta, setPergunta] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");
  const [resposta, setResposta] = useState<Resposta | null>(null);

  const buscar = async (texto?: string) => {
    const q = (texto ?? pergunta).trim();
    if (!q) return;
    setPergunta(q);
    setCarregando(true);
    setErro("");
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q }),
      });
      if (!res.ok) throw new Error();
      setResposta(await res.json());
    } catch {
      setErro("Não foi possível consultar o sistema agora. Tente novamente em instantes.");
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
        <div className="mb-3">
          <label htmlFor="pergunta" className="block text-sm font-semibold text-slate-800">
            Descreva o cenário ou dúvida para apoio à decisão
          </label>
          <p className="text-xs text-slate-500">
            O sistema localiza abordagens aplicáveis no grafo, com citações originais e limitações relatadas.
          </p>
        </div>

        <div className="relative">
          <textarea
            id="pergunta"
            value={pergunta}
            onChange={(e) => setPergunta(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) buscar();
            }}
            rows={3}
            placeholder="Ex.: Preciso recomendar ações para corrigir falhas em máquinas a partir dos manuais técnicos da fábrica..."
            className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50/60 p-3.5 text-sm text-slate-900 outline-none transition focus:border-teal-600 focus:bg-white focus:ring-3 focus:ring-teal-600/10 placeholder:text-slate-400"
          />
        </div>

        <div className="mt-3.5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-medium text-slate-400">Exemplos:</span>
            {EXEMPLOS.map((ex) => (
              <button
                key={ex.rotulo}
                type="button"
                onClick={() => buscar(ex.texto)}
                className="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[11px] text-slate-600 transition hover:border-teal-500 hover:bg-teal-50/50 hover:text-teal-800"
              >
                {ex.rotulo}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={() => buscar()}
            disabled={carregando || !pergunta.trim()}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
          >
            {carregando ? (
              <LoaderCircle className="h-4 w-4 animate-spin text-teal-400" />
            ) : (
              <Search className="h-4 w-4 text-teal-400" />
            )}
            {carregando ? "Consultando grafo…" : "Buscar nos estudos"}
          </button>
        </div>

        {erro && (
          <p className="mt-3 flex items-center gap-1 text-xs text-red-600">
            <CircleX className="h-3.5 w-3.5" /> {erro}
          </p>
        )}
      </section>

      {resposta && <Resultado resposta={resposta} />}
    </div>
  );
}

function Resultado({ resposta }: { resposta: Resposta }) {
  if (resposta.alternativas.length === 0) {
    return (
      <section className="flex items-start gap-3.5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="rounded-xl bg-slate-100 p-2 text-slate-500">
          <SearchX className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-slate-900">
            Nenhum dos estudos selecionados trata dessa situação.
          </h2>
          <p className="mt-1 text-xs leading-relaxed text-slate-600">
            O sistema respeita rigorosamente o limiar de similaridade para não alucinar nem forçar relações inexistentes.
            Caso a situação pertença ao domínio de GraphRAG para apoio à decisão, experimente descrevê-la com outras palavras.
          </p>
        </div>
      </section>
    );
  }

  const c = resposta.conferencia_resumo;

  return (
    <section className="space-y-5">
      <div className="rounded-2xl border border-teal-200/70 bg-gradient-to-br from-teal-50/70 to-emerald-50/40 p-5 shadow-xs">
        <div className="flex items-start justify-between gap-3">
          <p className="text-sm leading-relaxed text-slate-800">
            {resposta.resumo}
          </p>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 border-t border-teal-100/80 pt-3 text-[11px] text-slate-500">
          <span className="flex items-center gap-1 text-slate-600 font-medium">
            <Sparkles className="h-3 w-3 text-teal-600" />
            {resposta.resumo_origem === "llm" ? "Síntese assistida por IA (Gemini)" : "Síntese automática determinística"}
          </span>

          {c.itens_verificados > 0 &&
            (c.itens_sem_suporte === 0 ? (
              <span className="flex items-center gap-1 font-semibold text-emerald-800">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                {c.itens_verificados} {c.itens_verificados === 1 ? "informação conferida" : "informações conferidas"} no grafo
              </span>
            ) : (
              <span className="flex items-center gap-1 font-semibold text-amber-800">
                <TriangleAlert className="h-3.5 w-3.5 text-amber-600" />
                {c.itens_sem_suporte} informação(ões) sem apoio direto:{" "}
                {c.detalhes_sem_suporte.map((d) => d.valor).join(", ")}
              </span>
            ))}
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {resposta.alternativas.map((alt) => (
          <CartaoAbordagem key={alt.tecnica_id} alt={alt} />
        ))}
      </div>

      <div className="flex items-center justify-between border-t border-slate-200/60 pt-3 text-[11px] text-slate-400">
        <span>Estudos organizados por ano de publicação (ordem cronológica).</span>
        <span>A decisão final cabe exclusivamente ao decisor humano (Herbert Simon, 1960).</span>
      </div>
    </section>
  );
}

function CartaoAbordagem({ alt }: { alt: Alternativa }) {
  const e = alt.estudo;

  return (
    <article className="flex flex-col justify-between rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs transition hover:border-slate-300">
      <div>
        {e && (
          <div className="flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
            <span className="rounded-md bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
              {e.ano}
            </span>
            <span className="font-semibold text-slate-800">{e.autores}</span>
            <span className="text-slate-300">·</span>
            <span className="italic text-slate-500">{e.veiculo}</span>
          </div>
        )}

        <h3 className="mt-2 text-base font-bold text-slate-900 leading-snug">
          {alt.tecnica_nome}
        </h3>
        <p className="mt-1.5 text-xs leading-relaxed text-slate-600">
          {alt.descricao}
        </p>

        <div className="mt-4 space-y-3 border-t border-slate-100 pt-3 text-xs">
          <SecaoDestaque titulo="Onde foi aplicada" itens={alt.cenarios} />
          <SecaoDestaque titulo="Como foi avaliada" itens={alt.metricas_avaliacao} />
          <SecaoDestaque titulo="Limitações relatadas" itens={alt.limitacoes} alerta />
        </div>

        {alt.trechos_evidencia.length > 0 && (
          <div className="mt-4 space-y-2 border-t border-slate-100 pt-3">
            <p className="flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <Quote className="h-3 w-3 text-teal-600" /> Trechos do artigo original
            </p>
            <div className="space-y-2">
              {alt.trechos_evidencia.map((t) => (
                <div
                  key={t.id}
                  className="rounded-lg border-l-2 border-teal-600 bg-slate-50/70 p-2.5 text-xs italic leading-relaxed text-slate-700"
                >
                  “{t.texto}”
                  <span className="mt-1 block not-italic font-medium text-[10px] text-teal-700">
                    PDF pág. {t.pagina}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <details className="group mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500">
        <summary className="flex cursor-pointer list-none items-center gap-1 font-medium text-slate-600 hover:text-slate-900">
          <ChevronRight className="h-3.5 w-3.5 transition group-open:rotate-90 text-slate-400" />
          <span>Por que esta abordagem apareceu?</span>
        </summary>

        <div className="mt-2.5 rounded-lg bg-slate-50 p-3">
          <div className="flex flex-wrap items-center gap-1.5">
            {alt.caminho.map((p, i) => (
              <div key={i} className="flex items-center gap-1 text-[11px]">
                {i > 0 && <span className="text-slate-300">→</span>}
                <span className="rounded bg-white px-2 py-0.5 font-medium text-slate-700 border border-slate-200">
                  <span className="text-slate-400 font-normal">{p.tipo}: </span>
                  {p.nome}
                </span>
              </div>
            ))}
          </div>

          {alt.estrategias.length > 0 && (
            <p className="mt-2 text-[11px] text-slate-600 leading-relaxed">
              <strong className="text-slate-700">Recuperação: </strong>
              {alt.estrategias.map((s) => separar(s).titulo).join("; ")}.
            </p>
          )}
        </div>
      </details>
    </article>
  );
}

function SecaoDestaque({
  titulo,
  itens,
  alerta = false,
}: {
  titulo: string;
  itens: string[];
  alerta?: boolean;
}) {
  if (itens.length === 0) return null;

  return (
    <div>
      <h4
        className={`text-[10px] font-bold uppercase tracking-wider ${
          alerta ? "text-amber-700" : "text-slate-400"
        }`}
      >
        {titulo}
      </h4>
      <div className="mt-1 space-y-1">
        {itens.map((item) => {
          const { titulo: t, texto } = separar(item);
          return (
            <p key={item} className="text-xs leading-relaxed text-slate-700">
              <strong className={alerta ? "text-amber-950 font-semibold" : "text-slate-900 font-semibold"}>
                {t}
                {texto ? ":" : ""}
              </strong>{" "}
              {texto}
            </p>
          );
        })}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Aba 2: Avaliação                                                   */
/* ------------------------------------------------------------------ */
const TIPO_PERGUNTA: Record<string, string> = {
  direta: "Direta",
  parafrase: "Outras palavras",
  cruzada: "Cruza estudos",
  fora_do_escopo: "Fora do escopo",
};

function AbaAvaliacao() {
  const [dados, setDados] = useState<Avaliacao | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");
  const [filtroTipo, setFiltroTipo] = useState<string>("todos");
  const [filtroStatus, setFiltroStatus] = useState<string>("todos");
  const contar = (tipo?: string) =>
    (dados?.detalhes ?? []).filter((d) => !tipo || d.tipo === tipo).length;

  const rodar = async () => {
    setCarregando(true);
    setErro("");
    try {
      const res = await fetch("/api/evaluate", { method: "POST" });
      if (!res.ok) throw new Error();
      setDados(await res.json());
    } catch {
      setErro("Não foi possível executar a avaliação experimental agora.");
    } finally {
      setCarregando(false);
    }
  };

  const listaFiltrada = useMemo(() => {
    if (!dados) return [];
    return dados.detalhes.filter((d) => {
      const passaTipo = filtroTipo === "todos" || d.tipo === filtroTipo;
      const ok = d.estudos_esperados.length === 0 ? d.abstencao_correta : d.hit_rate === 1 && d.precisao === 1;
      const parcial = !ok && (d.hit_rate ?? 0) > 0;
      const passaStatus =
        filtroStatus === "todos" ||
        (filtroStatus === "certos" && ok) ||
        (filtroStatus === "parciais" && parcial) ||
        (filtroStatus === "errados" && !ok && !parcial);
      return passaTipo && passaStatus;
    });
  }, [dados, filtroTipo, filtroStatus]);

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="max-w-2xl">
            <h2 className="text-base font-bold text-slate-900">
              Protocolo de Avaliação Experimental
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-slate-600">
              Banco de perguntas avaliadas em tempo real com gabarito conhecido: perguntas diretas, paráfrases,
              cruzadas e fora do escopo. Os números são computados a cada execução, sem valores fixos.
            </p>
          </div>

          <button
            onClick={rodar}
            disabled={carregando}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-teal-700 px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-teal-800 disabled:opacity-40"
          >
            {carregando ? (
              <LoaderCircle className="h-4 w-4 animate-spin text-white" />
            ) : (
              <FlaskConical className="h-4 w-4 text-teal-200" />
            )}
            {carregando ? "Computando métricas…" : dados ? "Rodar novamente" : "Rodar avaliação empírica"}
          </button>
        </div>

        {erro && <p className="mt-3 text-xs text-red-600">{erro}</p>}
      </section>

      {/* Métricas em Cartões KPI Clean */}
      {dados && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <CardMetrica
              titulo="Acerto (Hit Rate)"
              valor={pct(dados.graphrag.hit_rate_medio)}
              comparativo={`Referência: ${pct(dados.referencia_sem_grafo.hit_rate_medio)}`}
              descricao={`${dados.perguntas_com_resposta} perguntas com resposta`}
              destaque
            />
            <CardMetrica
              titulo="Precisão Média"
              valor={pct(dados.graphrag.precisao_media)}
              comparativo={`Referência: ${pct(dados.referencia_sem_grafo.precisao_media)}`}
              descricao="Abordagens esperadas vs trazidas"
            />
            <CardMetrica
              titulo="Recusa Correta"
              valor={pct(dados.graphrag.abstencao_correta)}
              comparativo={`Referência: ${pct(dados.referencia_sem_grafo.abstencao_correta)}`}
              descricao={`${dados.perguntas_fora_do_escopo} perguntas fora de escopo`}
            />
            <CardMetrica
              titulo="Taxa de Fabricação"
              valor={pct(dados.graphrag.taxa_fabricacao)}
              comparativo="Medida a cada execução"
              descricao={`${dados.graphrag.afirmacoes_verificadas} informações auditadas`}
              valido={dados.graphrag.taxa_fabricacao === 0}
            />
          </div>

          <p className="text-[11px] text-slate-500">
            Similaridade usada nesta execução:{" "}
            <strong>
              {dados.modo_similaridade === "embedding"
                ? "Embeddings do Gemini (API)"
                : dados.modo_similaridade === "misto"
                ? `Misto: ${dados.perguntas_por_modo?.embedding ?? 0} perguntas com embeddings e ${dados.perguntas_por_modo?.local ?? 0} com comparação local (limite da API). Rode novamente.`
                : "Comparação local de termos (sem chave da API)"}
            </strong>
            .
          </p>

          {/* Tabela de Perguntas e Respostas com Filtros Clean */}
          <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm">
            {/* Barra de Filtros */}
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50/80 px-4 py-3 text-xs">
              <div className="flex flex-wrap items-center gap-1">
                <span className="mr-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Tipo:
                </span>
                {[
                  ["todos", `Todas (${contar()})`],
                  ["direta", `Diretas (${contar("direta")})`],
                  ["parafrase", `Paráfrases (${contar("parafrase")})`],
                  ["cruzada", `Cruzam (${contar("cruzada")})`],
                  ["fora_do_escopo", `Fora escopo (${contar("fora_do_escopo")})`],
                ].map(([id, label]) => (
                  <button
                    key={id}
                    onClick={() => setFiltroTipo(id)}
                    className={`rounded-full px-2.5 py-1 text-[11px] transition ${
                      filtroTipo === id
                        ? "bg-slate-900 font-semibold text-white"
                        : "bg-white text-slate-600 hover:bg-slate-200/60"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-1">
                <span className="mr-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Status:
                </span>
                {[
                  ["todos", "Todos"],
                  ["certos", "Certos"],
                  ["parciais", "Parciais"],
                  ["errados", "Errados"],
                ].map(([st, label]) => (
                  <button
                    key={st}
                    onClick={() => setFiltroStatus(st)}
                    className={`rounded-full px-2.5 py-0.5 text-[11px] transition ${
                      filtroStatus === st
                        ? "bg-teal-700 font-semibold text-white"
                        : "bg-white text-slate-600 hover:bg-slate-200/60"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

              <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-xs">
                <thead className="bg-slate-50 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  <tr>
                    <th className="px-4 py-2.5">Pergunta</th>
                    <th className="px-4 py-2.5">Esperado</th>
                    <th className="px-4 py-2.5">Encontrado (GraphRAG)</th>
                    <th className="px-4 py-2.5">Resultado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 align-top">
                  {listaFiltrada.map((d) => {
                    const ok =
                      d.estudos_esperados.length === 0
                        ? d.abstencao_correta
                        : d.hit_rate === 1 && d.precisao === 1;
                    const parcial = !ok && (d.hit_rate ?? 0) > 0;

                    return (
                      <tr key={d.id} className="transition hover:bg-slate-50/60">
                        <td className="px-4 py-3 max-w-sm">
                          <span className="mb-1 inline-block rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-600">
                            {TIPO_PERGUNTA[d.tipo] ?? d.tipo}
                          </span>
                          <p className="text-slate-800 leading-relaxed">{d.pergunta}</p>
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {d.estudos_esperados.map(nomeEstudo).join(", ") || (
                            <span className="italic text-slate-400">Nenhum (abstenção)</span>
                          )}
                        </td>
                        <td className="px-4 py-3 font-medium text-slate-800">
                          {d.estudos_recuperados.map(nomeEstudo).join(", ") || (
                            <span className="italic text-slate-400">Nenhum</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          {ok ? (
                            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 font-semibold text-emerald-800 border border-emerald-200">
                              <CircleCheck className="h-3.5 w-3.5 text-emerald-600" /> Certo
                            </span>
                          ) : parcial ? (
                            <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 font-semibold text-amber-800 border border-amber-200">
                              <TriangleAlert className="h-3.5 w-3.5 text-amber-600" /> Parcial
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2 py-0.5 font-semibold text-rose-800 border border-rose-200">
                              <CircleX className="h-3.5 w-3.5 text-rose-600" /> Errado
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function CardMetrica({
  titulo,
  valor,
  comparativo,
  descricao,
  destaque = false,
  valido = true,
}: {
  titulo: string;
  valor: string;
  comparativo: string;
  descricao: string;
  destaque?: boolean;
  valido?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border p-4 shadow-xs ${
        destaque
          ? "border-teal-200 bg-gradient-to-br from-teal-50/50 to-white"
          : "border-slate-200/80 bg-white"
      }`}
    >
      <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">{titulo}</p>
      <div className="mt-1.5 flex items-baseline gap-2">
        <span className="text-2xl font-extrabold tracking-tight text-slate-900">{valor}</span>
        {valido && (
          <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700">
            {comparativo}
          </span>
        )}
      </div>
      <p className="mt-1 text-[11px] text-slate-500">{descricao}</p>
    </div>
  );
}

function SobreAcervo() {
  const [nos, setNos] = useState<NoGrafo[]>([]);

  useEffect(() => {
    fetch("/api/ontology")
      .then((r) => (r.ok ? r.json() : { nos: [] }))
      .then((d) => setNos(d.nos ?? []))
      .catch(() => setNos([]));
  }, []);

  const estudos = nos.filter((n) => n.tipo === "Estudo");
  const contar = (tipo: string) => nos.filter((n) => n.tipo === tipo).length;

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
        <h2 className="text-base font-bold text-slate-900">
          Acervo Fechado do Mapeamento Sistemático
        </h2>
        <p className="mt-1 text-xs leading-relaxed text-slate-600 max-w-3xl">
          O grafo contém <strong>exclusivamente os 10 estudos primários incluídos</strong> após a seleção por critérios
          de elegibilidade (Scopus/IEEE). Todos os trechos foram copiados dos artigos em PDF e verificados
          computacionalmente (22 de 22 trechos validados).
        </p>
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        {estudos.map((e) => (
          <div
            key={e.id}
            className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-xs transition hover:border-slate-300"
          >
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="rounded bg-teal-50 px-2 py-0.5 font-semibold text-teal-800 border border-teal-200/60">
                {e.metadados.ano}
              </span>
              <span className="font-semibold text-slate-700">{e.metadados.autores}</span>
            </div>
            <h3 className="mt-2 text-sm font-bold text-slate-900 leading-snug">
              {e.nome}
            </h3>
            <p className="mt-1.5 text-xs leading-relaxed text-slate-600">
              {e.descricao}
            </p>
            <p className="mt-3 text-[11px] text-slate-400 italic border-t border-slate-100 pt-2">
              {e.metadados.veiculo}
            </p>
          </div>
        ))}
      </div>

      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Estrutura e Topologia do Grafo
        </h3>
        <p className="mt-1 text-xs text-slate-600">
          Cada nó e aresta representa uma entidade ou relação causal extraída da leitura sistemática.
        </p>

        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-5 text-center">
          <StatCounter rotulo="Total de Nós" valor={nos.length} />
          <StatCounter rotulo="Abordagens" valor={contar("Tecnica")} />
          <StatCounter rotulo="Cenários" valor={contar("CenarioDecisao")} />
          <StatCounter rotulo="Limitações" valor={contar("Limitacao")} />
          <StatCounter rotulo="Trechos Reais" valor={contar("Snippet")} />
        </div>
      </section>
    </div>
  );
}

function StatCounter({ rotulo, valor }: { rotulo: string; valor: number }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3 border border-slate-100">
      <div className="text-lg font-black text-slate-900">{valor}</div>
      <div className="text-[10px] font-medium text-slate-500 uppercase tracking-wide">{rotulo}</div>
    </div>
  );
}