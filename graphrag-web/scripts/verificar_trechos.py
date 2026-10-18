"""
Confere se cada trecho (nó Snippet) do acervo existe LITERALMENTE no PDF, na página indicada.

Uso (na pasta graphrag-web):
    pip install pypdf
    python scripts/verificar_trechos.py --pdfs ..

O parâmetro --pdfs aponta para a pasta onde estão os PDFs dos estudos
(por padrão, a raiz do repositório). A comparação ignora maiúsculas, espaços,
quebras de linha, hifenização e pontuação, para não acusar erro só por causa
da extração de texto do PDF. Sai com código 1 se algum trecho não for encontrado.
"""
import argparse
import json
import os
import re
import sys
import unicodedata


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKC", texto).lower()
    return re.sub(r"[^a-z0-9]", "", texto)


def main() -> int:
    raiz = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdfs", default=os.path.join(raiz, "..", ".."))
    parser.add_argument("--corpus", default=os.path.join(raiz, "..", "api", "data", "seed_corpus.json"))
    args = parser.parse_args()

    from pypdf import PdfReader

    with open(args.corpus, encoding="utf-8") as f:
        corpus = json.load(f)

    cache = {}
    falhas = 0
    trechos = [n for n in corpus["nos"] if n["tipo"] == "Snippet"]
    for n in trechos:
        arquivo = os.path.join(args.pdfs, n["metadados"]["arquivo_pdf"])
        if not os.path.exists(arquivo):
            alt = os.path.join(args.pdfs, "Artigos Selecionados", n["metadados"]["arquivo_pdf"])
            if os.path.exists(alt):
                arquivo = alt
        pagina = int(n["metadados"]["pagina"])
        if arquivo not in cache:
            if not os.path.exists(arquivo):
                print(f"[SEM PDF]  {n['id']}: arquivo não encontrado ({arquivo})")
                falhas += 1
                continue
            cache[arquivo] = [normalizar(p.extract_text() or "") for p in PdfReader(arquivo).pages]
        paginas = cache[arquivo]
        alvo = normalizar(n["descricao"])
        if pagina - 1 < len(paginas) and alvo in paginas[pagina - 1]:
            print(f"[OK]       {n['id']}: encontrado na página {pagina}")
        else:
            outras = [i + 1 for i, p in enumerate(paginas) if alvo in p]
            dica = f" (aparece na página {outras})" if outras else ""
            print(f"[FALHOU]   {n['id']}: não encontrado na página {pagina}{dica}")
            falhas += 1

    print(f"\n{len(trechos) - falhas} de {len(trechos)} trechos conferidos.")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
