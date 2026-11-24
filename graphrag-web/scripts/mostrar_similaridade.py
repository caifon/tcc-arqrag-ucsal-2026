"""Mostra, para uma pergunta, os nós mais parecidos e se o sistema responde ou recusa.

Uso (na pasta graphrag-web):
    python scripts/mostrar_similaridade.py "sua pergunta"
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("NEO4J_URI", "bolt://127.0.0.1:1")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import contextlib, io  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from api.index import gemini_service, nos_iniciais  # noqa: E402

LIMIAR = float(os.getenv("LIMIAR_SIMILARIDADE", "0.74"))
pergunta = " ".join(sys.argv[1:])

if not pergunta:
    print("Informe uma pergunta entre aspas. Exemplo:")
    print('  python scripts/mostrar_similaridade.py "sua pergunta"')
    sys.exit(1)

pontuados = gemini_service.pontuar_nos(pergunta, nos_iniciais)
print(f"Modo: {gemini_service.ultimo_modo} | limiar: {LIMIAR:.2f}\n")
print("Nós mais parecidos com a pergunta:")
for no, s in pontuados[:3]:
    print(f"  {s:.3f}  {no.nome[:60]}")
melhor = pontuados[0][1]
if melhor >= LIMIAR:
    print(f"Resultado: {melhor:.3f} >= {LIMIAR:.2f} -> RESPONDE")
else:
    print(f"Resultado: {melhor:.3f} < {LIMIAR:.2f} -> RECUSA (nenhum estudo trata disso)")
