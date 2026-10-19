"""Testes rápidos do MVP. Rodar na pasta graphrag-web:  python -m pytest tests -q"""
import os
import sys

os.environ.pop("GEMINI_API_KEY", None)  # testes usam a similaridade local, sem internet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.index import traversal_engine, sobrenomes, nos_iniciais  # noqa: E402
from api.evaluation.metrics import verificar_fabricacao  # noqa: E402
from api.ontology import TipoNo  # noqa: E402


def estudos(pergunta):
    _, alts = traversal_engine.executar_recuperacao(pergunta)
    return [a.estudo.id for a in alts if a.estudo], alts


def test_acervo_so_tem_estudos_incluidos():
    ids = {n.id for n in nos_iniciais if n.tipo == TipoNo.ESTUDO}
    assert ids == {
        "est_rawat",
        "est_niederhaus",
        "est_dindukurthi",
        "est_elssa",
        "est_lu_pipeline",
        "est_zheng_tcm",
        "est_zheng_ev",
        "est_liu_fusionom",
        "est_yan_uuv",
        "est_mallala_robot",
    }


def test_pergunta_direta_traz_estudo_certo():
    ids, alts = estudos("Quero um sistema que recomende ações para corrigir falhas em máquinas usando os manuais técnicos da fábrica.")
    assert "est_niederhaus" in ids
    alt = next(a for a in alts if a.estudo.id == "est_niederhaus")
    assert alt.estudo.autores and alt.estudo.ano == 2025
    assert alt.trechos_evidencia and all(t["pagina"] for t in alt.trechos_evidencia)


def test_fora_do_escopo_nao_responde():
    ids, _ = estudos("Como usar GraphRAG para prever o preço de ações na bolsa de valores?")
    assert ids == []


def test_verificador_pega_informacao_inventada():
    _, alts = estudos("Quero um sistema que recomende ações para corrigir falhas em máquinas usando os manuais técnicos da fábrica.")
    r = verificar_fabricacao("Niederhaus et al. (2025) reduziu o tempo em 45%.", alts, sobrenomes)
    assert r["itens_sem_suporte"] == 1 and r["detalhes_sem_suporte"][0]["valor"] == "45"
