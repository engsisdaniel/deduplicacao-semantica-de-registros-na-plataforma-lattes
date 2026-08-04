"""Ablação do código de projeto no título (viés de identificador compartilhado).

Os títulos da base sintética carregam um código de cadastro no início
(``"12045.21.00001.03 - "``). Esse código é **constante dentro de cada
quíntupla** e, além disso, é o mesmo do registro não-duplicata (5xx) daquela
quíntupla. Isso levanta duas objeções distintas:

1. o código acrescenta ~18% de caracteres idênticos a todo par intra-quíntupla,
   inflando artificialmente a similaridade de título na fase de *blocking*;
2. dois projetos distintos (base e 5xx) compartilharem um número de cadastro é
   impossível na base real, onde o código identifica unicamente o registro.

Este script mede o efeito rodando as mesmas 8 configurações do artigo sobre três
variantes da base:

``original``      — a base como publicada (código compartilhado na quíntupla);
``sem_codigo``    — o código removido de todos os 600 títulos;
``codigo_unico``  — cada registro recebe um código próprio, cenário fiel à base
                    real, em que cadastros distintos do mesmo projeto têm
                    números de registro diferentes.

Uso::

    .venv/bin/python scripts/ablacao_codigo.py
    .venv/bin/python scripts/ablacao_codigo.py --experimentos 4 7
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from pathlib import Path

from deduply import Deduplicator, Record

_RAIZ = Path(__file__).resolve().parent.parent
_TEST_JSON = _RAIZ / "base_sintetica.json"
_SAIDA = _RAIZ / "ablacao-codigo.json"
# Cache de embeddings próprio: uma ablação não deve contaminar (nem herdar) o
# cache compartilhado em ~/.deduply.
_CACHE_DIR = _RAIZ / ".cache_ablacao"

T, D, A = "titulo_projeto", "descricao_projeto", "nomes_integrante"

# As 8 configurações da Tabela 1 do artigo. A #4 é a que gerou os agrupamentos
# da base real (tau_g = 0,935; tau_v = 0,70); a #7 é a de melhor F1 reportado.
CONFIGS: list[tuple[int, float, float, list[str], list[str]]] = [
    (1, 0.8500, 0.700, [T, D], [A]),
    (2, 0.8500, 0.700, [T], [A, D]),
    (3, 0.8500, 0.700, [T], [A]),
    (4, 0.9350, 0.700, [T], [A]),
    (5, 0.7650, 0.700, [T], [A]),
    (6, 0.7650, 0.770, [T], [A]),
    (7, 0.7650, 0.630, [T], [A]),
    (8, 0.6885, 0.567, [T], [A]),
]

# "12045.21.00001.03 - Título" e a variante com vírgulas produzida por
# make_duplicate_v1 quando (id - 100) % 10 in (4, 5).
_CODIGO = re.compile(r"^\s*\d{4,6}[.,]\d{2}[.,]\d{5}[.,]\d{2}\s*(?:-|:)\s*")


def remove_codigo(titulo: str) -> str:
    """Remove o código de cadastro do início do título, se houver."""
    return _CODIGO.sub("", titulo)


def codigo_unico(record_id: int) -> str:
    """Gera um código de cadastro distinto para cada registro.

    Reproduz o formato da base real sem qualquer correlação com a quíntupla:
    dois cadastros do mesmo projeto recebem números não relacionados, como
    ocorre quando cada registro é inserido independentemente na plataforma.
    """
    orgao = 10000 + (record_id * 137 + 4211) % 89999
    ano = 20 + (record_id * 31) % 5
    seq = (record_id * 7919) % 100000
    versao = 1 + (record_id * 13) % 9
    return f"{orgao}.{ano}.{seq:05d}.{versao:02d}"


# --------------------------------------------------------------------------
# Variantes da base
# --------------------------------------------------------------------------


def carrega_base() -> list[dict]:
    with open(_TEST_JSON, encoding="utf-8") as f:
        return json.load(f)


def monta_variante(base: list[dict], variante: str) -> list[Record]:
    """Constrói os ``Record`` de uma variante, alterando apenas o título."""
    registros: list[Record] = []
    for item in base:
        titulo = item[T]
        if variante == "sem_codigo":
            titulo = remove_codigo(titulo)
        elif variante == "codigo_unico":
            titulo = f"{codigo_unico(item['id'])} - {remove_codigo(titulo)}"
        elif variante != "original":
            raise ValueError(f"variante desconhecida: {variante}")
        registros.append(
            Record(
                id=str(item["id"]),
                fields={
                    T: titulo,
                    D: item[D],
                    A: item[A],
                    "lattes_ids": item["lattes_ids"],
                },
            )
        )
    return registros


# --------------------------------------------------------------------------
# Protocolo de medição (idêntico ao calc_acuracy de app.py)
# --------------------------------------------------------------------------


def pares_referencia() -> set[tuple[int, int]]:
    pares: set[tuple[int, int]] = set()
    for n in range(1, 101):
        for a, b in combinations([n, n + 100, n + 200, n + 300, n + 400], 2):
            pares.add((a, b))
    return pares


def classifica_par(a: int, b: int) -> str:
    """Categoria de um par, para diagnóstico dos erros."""
    lo, hi = min(a, b), max(a, b)
    if hi > 500:
        return "nao_duplicata(5xx)"
    if lo <= 100:
        return {
            100: "base-v1",
            200: "base-v2",
            300: "base-v3(sem_desc)",
            400: "base-v4(1_autor)",
        }.get(hi - lo, "outro")
    if (hi - lo) == 100 and 101 <= lo <= 400:
        return f"v{(lo - 1) // 100}-v{(hi - 1) // 100}"
    return "outro"


@dataclass
class Metricas:
    tp: int
    fp: int
    fn: int
    precisao: float
    recall: float
    f1: float
    fp_por_categoria: dict[str, int]
    fn_por_categoria: dict[str, int]


def avalia(clusters, verdadeiros: set[tuple[int, int]]) -> Metricas:
    preditos: set[tuple[int, int]] = set()
    for c in clusters:
        ids = [int(r) for r in c.record_ids]
        if len(ids) < 2:
            continue
        for a, b in combinations(ids, 2):
            preditos.add((min(a, b), max(a, b)))

    tp_pares = preditos & verdadeiros
    fp_pares = preditos - verdadeiros
    fn_pares = verdadeiros - preditos
    tp, fp, fn = len(tp_pares), len(fp_pares), len(fn_pares)

    precisao = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precisao * recall / (precisao + recall) if precisao + recall else 0.0

    def conta(pares) -> dict[str, int]:
        acc: dict[str, int] = {}
        for a, b in pares:
            cat = classifica_par(a, b)
            acc[cat] = acc.get(cat, 0) + 1
        return dict(sorted(acc.items(), key=lambda kv: -kv[1]))

    return Metricas(tp, fp, fn, precisao, recall, f1, conta(fp_pares), conta(fn_pares))


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------


def roda(registros: list[Record], tau_g: float, tau_v: float,
         grupo: list[str], validacao: list[str]):
    dedup = Deduplicator(
        group_by=grupo,
        validate_by=validacao,
        group_threshold=tau_g,
        validate_threshold=tau_v,
        embedding_batch_size=10000,
        cache_dir=_CACHE_DIR,
        rep_selector=lambda r: len(r.fields.get(T, "") + r.fields.get(D, "")),
    )
    return dedup.deduplicate(records=registros).clusters


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experimentos", type=int, nargs="*", default=None,
        help="Subconjunto de experimentos a rodar (padrão: todos os 8).",
    )
    parser.add_argument(
        "--variantes", nargs="*",
        default=["original", "sem_codigo", "codigo_unico"],
        help="Variantes da base a avaliar.",
    )
    args = parser.parse_args()

    configs = CONFIGS
    if args.experimentos:
        alvo = set(args.experimentos)
        configs = [c for c in CONFIGS if c[0] in alvo]

    base = carrega_base()
    verdadeiros = pares_referencia()

    faltando = [i["id"] for i in base if not _CODIGO.match(i[T])]
    if faltando:
        print(f"AVISO: {len(faltando)} títulos sem código reconhecido: {faltando[:10]}",
              file=sys.stderr)

    resultados: dict[str, dict[str, dict]] = {}
    for variante in args.variantes:
        registros = monta_variante(base, variante)
        resultados[variante] = {}
        for num, tau_g, tau_v, grupo, validacao in configs:
            print(f"\n=== variante={variante} experimento={num} "
                  f"tau_g={tau_g} tau_v={tau_v} Fg={grupo} Fv={validacao}", file=sys.stderr)
            clusters = roda(registros, tau_g, tau_v, grupo, validacao)
            m = avalia(clusters, verdadeiros)
            resultados[variante][str(num)] = {
                "tau_g": tau_g, "tau_v": tau_v,
                "F_g": grupo, "F_v": validacao,
                "tp": m.tp, "fp": m.fp, "fn": m.fn,
                "precisao": round(m.precisao, 4),
                "recall": round(m.recall, 4),
                "f1": round(m.f1, 4),
                "fp_por_categoria": m.fp_por_categoria,
                "fn_por_categoria": m.fn_por_categoria,
                "num_clusters": len(clusters),
            }
            print(f"    P={m.precisao:.4f}  R={m.recall:.4f}  F1={m.f1:.4f}  "
                  f"(TP={m.tp} FP={m.fp} FN={m.fn})", file=sys.stderr)

    _SAIDA.parent.mkdir(parents=True, exist_ok=True)
    _SAIDA.write_text(
        json.dumps(
            {"gerado_em": datetime.now().isoformat(timespec="seconds"),
             "resultados": resultados},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    # --- Tabela comparativa ------------------------------------------------
    print("\n")
    cab = f"{'#':>2}  {'tau_g':>6} {'tau_v':>6}  "
    for v in args.variantes:
        cab += f"| {v:^24} "
    print(cab)
    print("-" * len(cab))
    for num, tau_g, tau_v, _, _ in configs:
        linha = f"{num:>2}  {tau_g:>6.4f} {tau_v:>6.3f}  "
        for v in args.variantes:
            r = resultados[v][str(num)]
            linha += f"| P{r['precisao']:.4f} R{r['recall']:.4f} F{r['f1']:.4f} "
        print(linha)

    print(f"\nResultados salvos em {_SAIDA.relative_to(_RAIZ)}")


if __name__ == "__main__":
    main()
