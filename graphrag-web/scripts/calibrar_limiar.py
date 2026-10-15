"""
Ajuda a escolher o limiar de similaridade (quando o sistema deve dizer "não encontrei").

Uso (na pasta graphrag-web), com e sem GEMINI_API_KEY configurada:
    python scripts/calibrar_limiar.py

Mostra a maior similaridade obtida em cada pergunta do banco de testes. O limiar bom fica
ENTRE as perguntas fora do escopo (que devem ficar abaixo) e as perguntas com resposta
(que devem ficar acima). Depois configure LIMIAR_SIMILARIDADE (com Gemini) ou
LIMIAR_SIMILARIDADE_LOCAL (sem Gemini) nas variáveis de ambiente da Vercel.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv  # noqa: E402
load_dotenv()
from api.ontology import NoGrafo  # noqa: E402
from api.engine.gemini_service import GeminiService  # noqa: E402

base = os.path.join(os.path.dirname(__file__), "..", "api", "data")
corpus = json.load(open(os.path.join(base, "seed_corpus.json"), encoding="utf-8"))
testes = json.load(open(os.path.join(base, "test_scenarios.json"), encoding="utf-8"))
nos = [NoGrafo(**n) for n in corpus["nos"]]
g = GeminiService()

dentro, fora = [], []
for t in testes:
    melhor_no, melhor = g.pontuar_nos(t["pergunta"], nos)[0]
    (fora if not t["estudos_esperados"] else dentro).append(melhor)
    marca = "FORA " if not t["estudos_esperados"] else "COM  "
    print(f"{marca} {melhor:.3f}  {t['pergunta'][:70]}  ->  {melhor_no.nome[:40]}")

print(f"\nModo: {g.ultimo_modo}")
print(f"Menor similaridade entre perguntas COM resposta: {min(dentro):.3f}")
print(f"Maior similaridade entre perguntas FORA do escopo: {max(fora):.3f}")
if max(fora) < min(dentro):
    print(f"Sugestão de limiar: {(max(fora) + min(dentro)) / 2:.2f}")
else:
    print("As faixas se sobrepõem: escolha um valor que erre o mínimo e registre isso como limitação.")
