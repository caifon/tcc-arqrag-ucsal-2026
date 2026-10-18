"""
Calibra o limiar de similaridade (quando o sistema deve dizer "não encontrei") e a margem.

Uso (na pasta graphrag-web, com GEMINI_API_KEY no .env para calibrar o modo Gemini):
    python scripts/calibrar_limiar.py

O script:
1. Mostra a maior similaridade de cada pergunta do banco de testes.
2. Roda a avaliação completa para vários valores de limiar e margem e mostra
   acerto, precisão e recusa correta de cada combinação.
3. Sugere a combinação com melhor equilíbrio.

Os embeddings ficam em cache durante a execução, então testar várias combinações
custa quase o mesmo que uma avaliação.

Depois, configure na Vercel:
    LIMIAR_SIMILARIDADE  (modo Gemini)  ou  LIMIAR_SIMILARIDADE_LOCAL  (sem Gemini)
    MARGEM_SIMILARIDADE
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

os.environ.setdefault("NEO4J_URI", "bolt://127.0.0.1:1")  # calibração usa o grafo em memória

try:
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from api.index import traversal_engine, gemini_service, caminho_testes, nos_iniciais  # noqa: E402
from api.evaluation.metrics import Evaluator  # noqa: E402

testes = json.load(open(caminho_testes, encoding="utf-8"))

# 1. Maior similaridade por pergunta
# Pré-carrega todos os textos para garantir que 100% estejam no cache de embeddings
textos_para_cache = [gemini_service.texto_do_no(no) for no in nos_iniciais] + [t["pergunta"] for t in testes]
if gemini_service.api_key:
    gemini_service.obter_embeddings_lote(textos_para_cache)

print("Maior similaridade de cada pergunta:\n")
dentro, fora = [], []
for t in testes:
    melhor_no, melhor = gemini_service.pontuar_nos(t["pergunta"], nos_iniciais)[0]
    (fora if not t["estudos_esperados"] else dentro).append(melhor)
    marca = "FORA" if not t["estudos_esperados"] else "COM "
    print(f"  {marca} {melhor:.3f}  {t['pergunta'][:65]:<65} -> {melhor_no.nome[:35]}")

modo = gemini_service.ultimo_modo
var = "LIMIAR_SIMILARIDADE" if modo == "embedding" else "LIMIAR_SIMILARIDADE_LOCAL"
print(f"\nModo: {modo}")
print(f"Menor similaridade entre perguntas COM resposta: {min(dentro):.3f}")
print(f"Maior similaridade entre perguntas FORA do escopo: {max(fora):.3f}")

# 2. Varredura de limiar e margem
# Cache de pontuação de nós para não recalcular similaridades a cada iteração
_cache_pontuados = {}
_orig_pontuar = gemini_service.pontuar_nos
def _fast_pontuar(query, nos):
    chave = (query, id(nos))
    if chave not in _cache_pontuados:
        _cache_pontuados[chave] = _orig_pontuar(query, nos)
    return _cache_pontuados[chave]
gemini_service.pontuar_nos = _fast_pontuar

# Desativa chamadas de geração LLM na calibração (a síntese não afeta a recuperação, que usa os embeddings em cache)
gemini_service._chamar_gemini_formatador = lambda *args, **kwargs: None

# Cache de recuperação e busca de referência para a varredura
_cache_recup = {}
_orig_exec = traversal_engine.executar_recuperacao

def _fast_exec(query, top_k_entrada=3, max_saltos=2, limiar=None):
    candidatos = traversal_engine.repo.obter_todos_nos()
    entradas = gemini_service.encontrar_nos_entrada(query, candidatos, top_k=top_k_entrada, threshold=limiar)
    if not entradas:
        from api.ontology import SubgrafoEvidencia
        return SubgrafoEvidencia(nos_entrada=[], nos_recuperados=[], arestas=[], snippets=[]), []
    chave = (query, tuple((n.id, round(s, 4)) for n, s in entradas))
    if chave not in _cache_recup:
        _cache_recup[chave] = _orig_exec(query, top_k_entrada, max_saltos, limiar)
    return _cache_recup[chave]

traversal_engine.executar_recuperacao = _fast_exec

_cache_busca_so = {}
_orig_busca_so = Evaluator.busca_so_similaridade
def _fast_busca_so(engine, pergunta, top_k=3):
    lim_ref = os.getenv(var)
    chave = (pergunta, lim_ref)
    if chave not in _cache_busca_so:
        _cache_busca_so[chave] = _orig_busca_so(engine, pergunta, top_k)
    return _cache_busca_so[chave]
Evaluator.busca_so_similaridade = _fast_busca_so

base = max(0.25, round(min(fora + dentro), 2))
limiares = sorted({round(base + i * 0.03, 2) for i in range(0, int((max(fora + dentro) - base) / 0.03) + 2)})
margens = [0.03, 0.05, 0.08]

print(f"\n{'limiar':>7} {'margem':>7} {'acerto':>7} {'precisão':>9} {'recusa':>7}", flush=True)
resultados = []
for lim in limiares:
    os.environ[var] = str(lim)
    for mg in margens:
        os.environ["MARGEM_SIMILARIDADE"] = str(mg)
        r = Evaluator.avaliar_banco_completo(traversal_engine, caminho_testes)["graphrag"]
        resultados.append((lim, mg, r["hit_rate_medio"], r["precisao_media"], r["abstencao_correta"]))
        print(f"{lim:>7.2f} {mg:>7.2f} {r['hit_rate_medio']:>7.0%} {r['precisao_media']:>9.0%} {r['abstencao_correta']:>7.0%}", flush=True)

# 3. Sugestão: maior média entre acerto, precisão e recusa (desempate: maior acerto)
melhor = max(resultados, key=lambda x: ((x[2] + x[3] + x[4]) / 3, x[2]))
print("\nSugestão (melhor equilíbrio entre acerto, precisão e recusa):")
print(f"  {var}={melhor[0]:.2f}")
print(f"  MARGEM_SIMILARIDADE={melhor[1]:.2f}")
print(f"  -> acerto {melhor[2]:.0%}, precisão {melhor[3]:.0%}, recusa correta {melhor[4]:.0%}")
print("\nAtenção: o limiar foi escolhido olhando o próprio banco de testes. Registre isso como limitação")
print("na monografia e, se possível, valide com perguntas novas escritas por outra pessoa.")
