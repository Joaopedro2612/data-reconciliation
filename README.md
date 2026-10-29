# Conciliação de Bases

Cruza duas bases (CSV) por uma chave e gera uma **lista de exceções**: operações ausentes em um dos lados, chaves duplicadas e divergências de valor acima de uma tolerância.

> ⚠️ As bases de exemplo são **fictícias**, geradas com erros plantados para demonstrar o funcionamento.

## Tipos de exceção

| Tipo | Significado |
|---|---|
| `ausente_na_base_b` / `ausente_na_base_a` | a chave existe só de um lado |
| `duplicado_na_base_a` / `duplicado_na_base_b` | a mesma chave aparece mais de uma vez na base |
| `valor_divergente` | a diferença absoluta entre as bases passa da tolerância (`--tol`), ou só um lado tem o valor |

## Como rodar

```bash
git clone https://github.com/Joaopedro2612/data-reconciliation.git
cd data-reconciliation
pip install -r requirements.txt

python generate_sample_data.py
python reconcile.py                 # usa data/base_a.csv e data/base_b.csv
python -m unittest discover -s tests
```

Exemplo de resultado com as bases fictícias (20 exceções: 5 + 4 ausências, 3 duplicidades, 8 divergências).
Uma diferença de preço de 0,004 foi plantada de propósito e **não** aparece, pois está dentro da tolerância de 0,01.

Com seus próprios arquivos:

```bash
python reconcile.py --a base_a.csv --b base_b.csv --key id_operacao --values valor preco --tol 0.01
```

O resultado completo é salvo em `outputs/excecoes.csv`.

## Limitações e próximos passos

- Tolerância absoluta única para todos os campos (sem tolerância relativa).
- Campos de texto não são comparados, apenas numéricos.
- Ideias: tolerância por campo, relatório em Excel, chave composta.

## Licença

MIT
