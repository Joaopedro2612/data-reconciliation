"""Concilia duas bases (CSV) por chave e lista exceções: ausências, duplicidades e divergências de valor."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

EXC_COLUMNS = ["tipo_excecao", "chave", "campo", "valor_a", "valor_b", "diferenca"]


def reconcile(a: pd.DataFrame, b: pd.DataFrame, key: str, values: list[str], tol: float = 0.01) -> pd.DataFrame:
    """Retorna um DataFrame de exceções (vazio se as bases batem dentro da tolerância)."""
    for name, df in (("A", a), ("B", b)):
        missing = {key, *values} - set(df.columns)
        if missing:
            raise ValueError(f"Base {name} sem as colunas: {sorted(missing)}")

    parts = []
    # 1) duplicidades (chaves repetidas na mesma base)
    for label, df in (("duplicado_na_base_a", a), ("duplicado_na_base_b", b)):
        dups = df.loc[df.duplicated(key, keep=False), key].drop_duplicates()
        if not dups.empty:
            parts.append(pd.DataFrame({"tipo_excecao": label, "chave": dups}))

    a1, b1 = a.drop_duplicates(key), b.drop_duplicates(key)

    # 2) ausências entre as bases
    only_a = a1.loc[~a1[key].isin(b1[key]), key]
    only_b = b1.loc[~b1[key].isin(a1[key]), key]
    if not only_a.empty:
        parts.append(pd.DataFrame({"tipo_excecao": "ausente_na_base_b", "chave": only_a}))
    if not only_b.empty:
        parts.append(pd.DataFrame({"tipo_excecao": "ausente_na_base_a", "chave": only_b}))

    # 3) divergências de valor nas chaves presentes nas duas bases
    both = a1.merge(b1, on=key, suffixes=("_a", "_b"))
    for col in values:
        va, vb = both[f"{col}_a"], both[f"{col}_b"]
        diff = va - vb
        bad = diff.abs().gt(tol) | (va.isna() ^ vb.isna())
        if bad.any():
            parts.append(
                pd.DataFrame(
                    {
                        "tipo_excecao": "valor_divergente",
                        "chave": both.loc[bad, key],
                        "campo": col,
                        "valor_a": va[bad],
                        "valor_b": vb[bad],
                        "diferenca": diff[bad],
                    }
                )
            )

    if not parts:
        return pd.DataFrame(columns=EXC_COLUMNS)
    return pd.concat(parts, ignore_index=True).reindex(columns=EXC_COLUMNS)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a", default="data/base_a.csv")
    p.add_argument("--b", default="data/base_b.csv")
    p.add_argument("--key", default="trade_id")
    p.add_argument("--values", nargs="+", default=["notional", "price"])
    p.add_argument("--tol", type=float, default=0.01, help="tolerância absoluta para divergências")
    p.add_argument("--out", default="outputs")
    a = p.parse_args()

    exc = reconcile(pd.read_csv(a.a), pd.read_csv(a.b), a.key, a.values, a.tol)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    exc.to_csv(out / "excecoes.csv", index=False)

    print(f"{len(exc)} exceções encontradas.\n")
    if not exc.empty:
        print(exc["tipo_excecao"].value_counts().to_string(), "\n")
        print(exc.head(15).to_string(index=False))
    print(f"\nLista completa em {out / 'excecoes.csv'}")


if __name__ == "__main__":
    main()
