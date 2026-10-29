"""Gera duas bases FICTÍCIAS com erros plantados (para demonstrar a conciliação)."""
from pathlib import Path

import numpy as np
import pandas as pd


def generate(seed=11):
    rng = np.random.default_rng(seed)
    n = 204
    base = pd.DataFrame(
        {
            "trade_id": [f"OP{i + 1:04d}" for i in range(n)],
            "product": rng.choice(["NDF", "Swap", "Opção", "CDB"], size=n),
            "notional": np.round(rng.uniform(50_000, 5_000_000, size=n), 2),
            "price": np.round(rng.uniform(95, 105, size=n), 4),
        }
    )
    a = base.iloc[:200].copy()                         # OP0201-OP0204 só existem na base B
    b = base.copy()
    b = b.drop(index=rng.choice(200, size=5, replace=False))  # 5 operações ausentes na base B
    idx = rng.choice(b.index, size=9, replace=False)
    b.loc[idx[:6], "notional"] += 1_000                # 6 divergências de notional
    b.loc[idx[6:8], "price"] += 0.5                    # 2 divergências de preço
    b.loc[idx[8], "price"] += 0.004                    # diferença dentro da tolerância (não deve alertar)
    b = pd.concat([b, b.sample(3, random_state=1)])    # 3 duplicidades na base B
    return a, b.sample(frac=1, random_state=3)


if __name__ == "__main__":
    a, b = generate()
    Path("data").mkdir(exist_ok=True)
    a.to_csv("data/base_a.csv", index=False)
    b.to_csv("data/base_b.csv", index=False)
    print(f"base_a: {len(a)} linhas | base_b: {len(b)} linhas")
