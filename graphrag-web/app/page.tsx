"use client";

import { useEffect, useState } from "react";
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
} from "lucide-react";

/* ------------------------------------------------------------------ */
/* Tipos (espelham a resposta da API em api/index.py)                  */
/* ------------------------------------------------------------------ */
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
  modo_similaridade: "embedding" | "local";
  graphrag: {
    hit_rate_medio: number;
    precisao_media: number;
    abstencao_correta: number;
    taxa_fabricacao: number;
    afirmacoes_verificadas: number;
  };
  referencia_sem_grafo: { hit_rate_medio: number; precisao_media: number; abstencao_correta: number };
  detalhes: DetalheAvaliacao[];
}
interface NoGrafo {
  id: string;
  tipo: string;
  nome: string;
  descricao: string;
  metadados: Record<string, string | number>;
}

/* ------------------------------------------------------------------ */
const EXEMPLOS = [
  { rotulo: "Atraso de material em obra", texto: "Preciso avisar o gestor de uma obra quando um atraso na entrega de material afetar outras atividades do cronograma." },
  { rotulo: "Falha em máquina na fábrica", texto: "Quero um sistema que recomende ações para corrigir falhas em máquinas usando os manuais técnicos da fábrica." },
  { rotulo: "Alimentação para quem tem uma doença", texto: "Como recomendar alimentos para uma pessoa com uma doença específica, explicando o motivo de cada indicação?" },
  { rotulo: "Incidente no transporte público", texto: "Preciso apoiar supervisores na escolha de ações durante um incidente no transporte público." },
  { rotulo: "Fora do escopo: bolsa de valores", texto: "Como usar GraphRAG para prever o preço de ações na bolsa de valores?" },
];

const pct = (v: number) => `${Math.round(v * 100)}%`;
const separar = (item: string) => {
  const i = item.indexOf(": ");
  return i > 0 ? { titulo: item.slice(0, i), texto: item.slice(i + 2) } : { titulo: item, texto: "" };
};

/* ------------------------------------------------------------------ */
export default function Home() {
  const [aba, setAba] = useState<"consultar" | "avaliacao" | "acervo">("consultar");

  return (
    <main className="min-h-screen bg-stone-50 text-stone-900">
      <header className="border-b border-stone-200 bg-white">
        <div className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">GraphRAG para apoio à decisão</h1>
            <p className="mt-1 text-sm text-stone-500">
              Consulta aos estudos selecionados no mapeamento sistemático · TCC Engenharia de Software · UCSal 2026
            </p>
          </div>
          <nav className="flex shrink-0 gap-1 overflow-x-auto rounded-lg bg-stone-100 p-1 text-[13px] sm:text-sm" aria-label="Seções">
            {([
              ["consultar", "Consultar", Search],
              ["avaliacao", "Como avaliamos", FlaskConical],
              ["acervo", "Sobre o acervo", BookOpen],
            ] as const).map(([id, rotulo, Icone]) => (
              <button
                key={id}
                onClick={() => setAba(id)}
                className={`flex items-center gap-1.5 whitespace-nowrap rounded-md px-2.5 py-1.5 transition sm:px-3 ${
                  aba === id ? "bg-white font-medium text-teal-800 shadow-sm" : "text-stone-600 hover:text-stone-900"
                }`}
              >
                <Icone className="h-4 w-4" />
                {rotulo}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-8">
        {aba === "consultar" && <Consultar />}
        {aba === "avaliacao" && <ComoAvaliamos />}
        {aba === "acervo" && <SobreAcervo />}
      </div>
    </main>
  );
}

/* ------------------------------------------------------------------ */
/* Aba 1: Consultar                                                    */
/* ------------------------------------------------------------------ */
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
    <div className="space-y-8">
      <section className="space-y-4">
        <p className="max-w-3xl text-[15px] leading-relaxed text-stone-700">
          Descreva uma situação em que você precisa tomar uma decisão. O sistema procura, nos estudos selecionados na
          revisão, as abordagens que se aplicam e mostra cada uma com a fonte da informação.{" "}
          <strong className="font-medium text-stone-900">Ele não escolhe por você.</strong>
        </p>

        <div className="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
          <label htmlFor="pergunta" className="sr-only">Situação de decisão</label>
          <textarea
            id="pergunta"
            value={pergunta}
            onChange={(e) => setPergunta(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) buscar();
            }}
            rows={3}
            placeholder="Ex.: Preciso recomendar ações para corrigir falhas em máquinas a partir dos manuais técnicos."
            className="w-full resize-none rounded-lg border border-stone-200 bg-stone-50 p-3 text-[15px] outline-none transition focus:border-teal-600 focus:bg-white focus:ring-2 focus:ring-teal-600/15"
          />
          <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-stone-500">Exemplos:</span>
              {EXEMPLOS.map((ex) => (
                <button
                  key={ex.rotulo}
                  onClick={() => buscar(ex.texto)}
                  className="rounded-full border border-stone-200 px-3 py-1 text-xs text-stone-600 transition hover:border-teal-600 hover:text-teal-800"
                >
                  {ex.rotulo}
                </button>
              ))}
            </div>
            <button
              onClick={() => buscar()}
              disabled={carregando || !pergunta.trim()}
              className="flex shrink-0 items-center justify-center gap-2 rounded-lg bg-teal-700 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {carregando ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              {carregando ? "Buscando…" : "Buscar nos estudos"}
            </button>
          </div>
        </div>
        {erro && <p className="text-sm text-red-700">{erro}</p>}
      </section>

      {resposta && <Resultado resposta={resposta} />}
    </div>
  );
}

function Resultado({ resposta }: { resposta: Resposta }) {
  if (resposta.alternativas.length === 0) {
    return (
      <section className="flex gap-4 rounded-xl border border-stone-200 bg-white p-6">
        <SearchX className="h-6 w-6 shrink-0 text-stone-400" />
        <div>
          <h2 className="font-medium">Nenhum dos estudos selecionados trata dessa situação.</h2>
          <p className="mt-1 text-sm leading-relaxed text-stone-600">
            O sistema só responde com base nos estudos incluídos na revisão. Quando nada no acervo é parecido o
            suficiente com a pergunta, ele prefere dizer que não encontrou a sugerir uma relação que não existe. Se a
            situação estiver dentro do tema, tente descrevê-la com outras palavras.
          </p>
        </div>
      </section>
    );
  }

  const c = resposta.conferencia_resumo;
  return (
    <section className="space-y-5">
      <div className="rounded-xl border border-teal-100 bg-teal-50/60 p-5">
        <p className="text-[15px] leading-relaxed text-stone-800">{resposta.resumo}</p>
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-500">
          <span>{resposta.resumo_origem === "llm" ? "Resumo escrito por IA a partir dos dados abaixo" : "Resumo automático"}</span>
          {c.itens_verificados > 0 &&
            (c.itens_sem_suporte === 0 ? (
              <span className="flex items-center gap-1 text-teal-800">
                <CircleCheck className="h-3.5 w-3.5" />
                {c.itens_verificados} informações do resumo conferidas no grafo
              </span>
            ) : (
              <span className="flex items-center gap-1 text-amber-800">
                <TriangleAlert className="h-3.5 w-3.5" />
                {c.itens_sem_suporte} informação(ões) do resumo sem apoio no grafo:{" "}
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
      <p className="text-xs text-stone-500">
        Os cartões estão em ordem de ano de publicação. A ordem não indica qual abordagem é melhor.
      </p>
    </section>
  );
}

function CartaoAbordagem({ alt }: { alt: Alternativa }) {
  const e = alt.estudo;
  return (
    <article className="flex flex-col rounded-xl border border-stone-200 bg-white p-5 shadow-sm">
      {e && (
        <p className="text-xs text-stone-500">
          <span className="font-medium text-stone-700">{e.autores}</span> · {e.ano} · {e.veiculo}
        </p>
      )}
      <h3 className="mt-1 text-lg font-semibold leading-snug">{alt.tecnica_nome}</h3>
      <p className="mt-2 text-sm leading-relaxed text-stone-700">{alt.descricao}</p>

      <dl className="mt-4 space-y-3 border-t border-stone-100 pt-4 text-sm">
        <Bloco titulo="Onde foi aplicada" itens={alt.cenarios} />
        <Bloco titulo="Como foi avaliada" itens={alt.metricas_avaliacao} />
        <Bloco titulo="Limitações relatadas" itens={alt.limitacoes} destaque />
      </dl>

      {alt.trechos_evidencia.length > 0 && (
        <div className="mt-4 space-y-2 border-t border-stone-100 pt-4">
          <p className="flex items-center gap-1.5 text-xs font-medium text-stone-500">
            <Quote className="h-3.5 w-3.5" /> Trechos do artigo (original em inglês)
          </p>
          {alt.trechos_evidencia.map((t) => (
            <blockquote key={t.id} className="border-l-2 border-teal-600/40 pl-3 text-[13px] italic leading-relaxed text-stone-600">
              “{t.texto}”
              <span className="ml-1 not-italic text-stone-400">(p. {t.pagina} do PDF)</span>
            </blockquote>
          ))}
        </div>
      )}

      <details className="group mt-4 border-t border-stone-100 pt-3 text-xs text-stone-500">
        <summary className="cursor-pointer list-none hover:text-stone-800">
          <span className="inline-flex items-center gap-1">
            <ChevronRight className="h-3.5 w-3.5 transition group-open:rotate-90" />
            Por que esta abordagem apareceu?
          </span>
        </summary>
        <ol className="mt-3 flex flex-wrap items-center gap-1.5">
          {alt.caminho.map((p, i) => (
            <li key={i} className="flex items-center gap-1.5">
              {i > 0 && <span className="text-stone-300">→</span>}
              <span className="rounded-md bg-stone-100 px-2 py-1">
                <span className="text-stone-400">{p.tipo}: </span>
                <span className="text-stone-700">{p.nome}</span>
              </span>
            </li>
          ))}
        </ol>
        {alt.estrategias.length > 0 && (
          <p className="mt-3 leading-relaxed">
            <span className="text-stone-400">Como o estudo recupera a informação: </span>
            {alt.estrategias.map((s) => separar(s).titulo).join("; ")}.
          </p>
        )}
      </details>
    </article>
  );
}

function Bloco({ titulo, itens, destaque = false }: { titulo: string; itens: string[]; destaque?: boolean }) {
  if (itens.length === 0) return null;
  return (
    <div>
      <dt className={`text-xs font-medium uppercase tracking-wide ${destaque ? "text-amber-700" : "text-stone-500"}`}>{titulo}</dt>
      {itens.map((item) => {
        const { titulo: t, texto } = separar(item);
        return (
          <dd key={item} className="mt-1 leading-relaxed text-stone-700">
            <span className="font-medium text-stone-800">{t}.</span> {texto}
          </dd>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Aba 2: Como avaliamos                                               */
/* ------------------------------------------------------------------ */
const TIPO_PERGUNTA: Record<string, string> = {
  direta: "Direta",
  parafrase: "Outras palavras",
  cruzada: "Cruza estudos",
  fora_do_escopo: "Fora do escopo",
};

function ComoAvaliamos() {
  const [dados, setDados] = useState<Avaliacao | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  const rodar = async () => {
    setCarregando(true);
    setErro("");
    try {
      const res = await fetch("/api/evaluate", { method: "POST" });
      if (!res.ok) throw new Error();
      setDados(await res.json());
    } catch {
      setErro("Não foi possível rodar a avaliação agora.");
    } finally {
      setCarregando(false);
    }
  };

  const nomeEstudo = (id: string) =>
    ({ est_rawat: "Rawat", est_niederhaus: "Niederhaus", est_dindukurthi: "Dindukurthi", est_elssa: "ELSSA" } as Record<string, string>)[id] ?? id;

  return (
    <div className="space-y-6">
      <section className="max-w-3xl space-y-3 text-[15px] leading-relaxed text-stone-700">
        <p>
          Para saber se o sistema funciona, usamos um banco de perguntas cuja resposta já conhecemos: perguntas diretas,
          perguntas com outras palavras, perguntas que cruzam estudos e perguntas <em>fora do escopo</em>, que nenhum
          estudo responde. Os números abaixo são calculados na hora, a cada execução.
        </p>
        <ul className="space-y-1 text-sm text-stone-600">
          <li><strong className="text-stone-800">Acerto (hit rate):</strong> dos estudos esperados, quantos apareceram.</li>
          <li><strong className="text-stone-800">Precisão:</strong> das abordagens mostradas, quantas eram esperadas.</li>
          <li><strong className="text-stone-800">Recusa correta:</strong> nas perguntas fora do escopo, quantas vezes o sistema disse que não encontrou nada.</li>
          <li><strong className="text-stone-800">Taxa de fabricação:</strong> das informações conferíveis do resumo (números, autores e citações), quantas não estão no grafo.</li>
        </ul>
        <button
          onClick={rodar}
          disabled={carregando}
          className="mt-2 flex items-center gap-2 rounded-lg bg-teal-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-teal-800 disabled:opacity-40"
        >
          {carregando ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <FlaskConical className="h-4 w-4" />}
          {carregando ? "Avaliando…" : dados ? "Rodar de novo" : "Rodar avaliação"}
        </button>
        {erro && <p className="text-sm text-red-700">{erro}</p>}
      </section>

      {dados && (
        <>
          <section className="overflow-hidden rounded-xl border border-stone-200 bg-white">
            <table className="w-full text-sm">
              <thead className="bg-stone-50 text-left text-xs text-stone-500">
                <tr>
                  <th className="px-4 py-2 font-medium">Medida</th>
                  <th className="px-4 py-2 font-medium">GraphRAG (com caminho no grafo)</th>
                  <th className="px-4 py-2 font-medium">Referência: só similaridade de texto</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                <Linha nome={`Acerto (${dados.perguntas_com_resposta} perguntas)`} a={pct(dados.graphrag.hit_rate_medio)} b={pct(dados.referencia_sem_grafo.hit_rate_medio)} />
                <Linha nome="Precisão" a={pct(dados.graphrag.precisao_media)} b={pct(dados.referencia_sem_grafo.precisao_media)} />
                <Linha nome={`Recusa correta (${dados.perguntas_fora_do_escopo} perguntas)`} a={pct(dados.graphrag.abstencao_correta)} b={pct(dados.referencia_sem_grafo.abstencao_correta)} />
                <Linha nome={`Taxa de fabricação (${dados.graphrag.afirmacoes_verificadas} informações conferidas)`} a={pct(dados.graphrag.taxa_fabricacao)} b="—" />
              </tbody>
            </table>
            <p className="border-t border-stone-100 px-4 py-2 text-xs text-stone-500">
              Similaridade usada nesta execução:{" "}
              {dados.modo_similaridade === "embedding"
                ? "embeddings do Gemini."
                : "comparação local de palavras (sem a chave do Gemini). Nesse modo, perguntas em português comparadas a trechos em inglês saem prejudicadas, inclusive na referência."}
            </p>
          </section>

          <section className="overflow-x-auto rounded-xl border border-stone-200 bg-white">
            <table className="w-full min-w-[640px] text-sm">
              <thead className="bg-stone-50 text-left text-xs text-stone-500">
                <tr>
                  <th className="px-4 py-2 font-medium">Pergunta</th>
                  <th className="px-4 py-2 font-medium">Esperado</th>
                  <th className="px-4 py-2 font-medium">Encontrado</th>
                  <th className="px-4 py-2 font-medium">Resultado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 align-top">
                {dados.detalhes.map((d) => {
                  const ok = d.estudos_esperados.length === 0 ? d.abstencao_correta : d.hit_rate === 1 && d.precisao === 1;
                  const parcial = !ok && (d.hit_rate ?? 0) > 0;
                  return (
                    <tr key={d.id}>
                      <td className="px-4 py-3">
                        <span className="mb-1 inline-block rounded bg-stone-100 px-1.5 py-0.5 text-[11px] text-stone-500">
                          {TIPO_PERGUNTA[d.tipo] ?? d.tipo}
                        </span>
                        <p className="text-stone-700">{d.pergunta}</p>
                      </td>
                      <td className="px-4 py-3 text-stone-600">{d.estudos_esperados.map(nomeEstudo).join(", ") || "Nada"}</td>
                      <td className="px-4 py-3 text-stone-600">{d.estudos_recuperados.map(nomeEstudo).join(", ") || "Nada"}</td>
                      <td className="px-4 py-3">
                        {ok ? (
                          <span className="flex items-center gap-1 text-teal-800"><CircleCheck className="h-4 w-4" /> Certo</span>
                        ) : parcial ? (
                          <span className="flex items-center gap-1 text-amber-700"><TriangleAlert className="h-4 w-4" /> Parcial</span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-700"><CircleX className="h-4 w-4" /> Errado</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
}

function Linha({ nome, a, b }: { nome: string; a: string; b: string }) {
  return (
    <tr>
      <td className="px-4 py-2.5 text-stone-700">{nome}</td>
      <td className="px-4 py-2.5 font-semibold text-stone-900">{a}</td>
      <td className="px-4 py-2.5 text-stone-600">{b}</td>
    </tr>
  );
}

/* ------------------------------------------------------------------ */
/* Aba 3: Sobre o acervo                                               */
/* ------------------------------------------------------------------ */
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
    <div className="space-y-8">
      <section className="max-w-3xl space-y-3 text-[15px] leading-relaxed text-stone-700">
        <p>
          O acervo contém <strong>apenas os estudos incluídos no mapeamento sistemático</strong>. As informações de cada
          estudo foram extraídas pelo grupo durante a leitura completa e organizadas em um grafo. Os trechos exibidos
          foram copiados dos PDFs e conferidos automaticamente.
        </p>
        <p className="text-sm text-stone-600">
          Este é um protótipo (MVP) com acervo pequeno e fechado. Enviar novos artigos pelo site e montar o grafo
          automaticamente fica como trabalho futuro: os próprios estudos revisados mostram que a extração automática
          ainda comete erros.
        </p>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-stone-500">Estudos no grafo ({estudos.length})</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {estudos.map((e) => (
            <div key={e.id} className="rounded-xl border border-stone-200 bg-white p-4">
              <p className="text-xs text-stone-500">
                <span className="font-medium text-stone-700">{e.metadados.autores}</span> · {e.metadados.ano} · {e.metadados.veiculo}
              </p>
              <p className="mt-1 text-sm font-medium leading-snug">{e.nome}</p>
              <p className="mt-2 text-sm leading-relaxed text-stone-600">{e.descricao}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-stone-500">Como o grafo é organizado</h2>
        <div className="rounded-xl border border-stone-200 bg-white p-5 text-sm leading-loose text-stone-700">
          <p>
            Cada <Tag>Estudo</Tag> <em>usa</em> uma <Tag>Abordagem</Tag>, que é <em>aplicada em</em> um{" "}
            <Tag>Cenário de decisão</Tag>, <em>avaliada por</em> uma <Tag>Forma de avaliação</Tag>, <em>tem</em>{" "}
            <Tag>Limitações</Tag> e <em>usa</em> uma <Tag>Estratégia de recuperação</Tag>. Cada estudo também tem{" "}
            <Tag>Trechos</Tag> copiados do artigo, com a página.
          </p>
          <p className="mt-2 text-stone-500">
            Total: {nos.length} nós · {contar("Tecnica")} abordagens · {contar("CenarioDecisao")} cenários ·{" "}
            {contar("Limitacao")} limitações · {contar("Snippet")} trechos.
          </p>
        </div>
      </section>
    </div>
  );
}

function Tag({ children }: { children: React.ReactNode }) {
  return <span className="rounded bg-stone-100 px-1.5 py-0.5 text-[13px] font-medium text-stone-800">{children}</span>;
}
