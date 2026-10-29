import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reconcile  # noqa: E402


def frame(rows):
    return pd.DataFrame(rows, columns=["id", "valor"])


class TestReconcile(unittest.TestCase):
    def test_identical_bases_have_no_exceptions(self):
        a = frame([(1, 10.0), (2, 20.0)])
        self.assertTrue(reconcile.reconcile(a, a.copy(), "id", ["valor"]).empty)

    def test_detects_missing_both_sides(self):
        a, b = frame([(1, 10.0), (2, 20.0)]), frame([(2, 20.0), (3, 30.0)])
        exc = reconcile.reconcile(a, b, "id", ["valor"]).set_index("chave")["tipo_excecao"]
        self.assertEqual(exc[1], "ausente_na_base_b")
        self.assertEqual(exc[3], "ausente_na_base_a")

    def test_detects_duplicates(self):
        a, b = frame([(1, 10.0)]), frame([(1, 10.0), (1, 10.0)])
        exc = reconcile.reconcile(a, b, "id", ["valor"])
        self.assertEqual(list(exc["tipo_excecao"]), ["duplicado_na_base_b"])

    def test_tolerance(self):
        a, b = frame([(1, 10.000), (2, 20.0)]), frame([(1, 10.004), (2, 21.0)])
        exc = reconcile.reconcile(a, b, "id", ["valor"], tol=0.01)
        self.assertEqual(list(exc["chave"]), [2])
        self.assertEqual(float(exc["diferenca"].iloc[0]), -1.0)

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            reconcile.reconcile(frame([(1, 1.0)]), frame([(1, 1.0)]), "id", ["inexistente"])


if __name__ == "__main__":
    unittest.main()
