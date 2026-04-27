from io import BytesIO

import numpy as np
import pandas as pd


class MockDataGenerator:
    REQUIRED_COLUMNS = ("Loan_ID", "EAD", "PD", "LGD", "WAL")

    def __init__(self, seed: int = 42):
        self._rng = np.random.default_rng(seed)

    def generate(self, n_rows: int = 15) -> pd.DataFrame:
        loan_ids = [f"L{i:04d}" for i in range(1, n_rows + 1)]
        ead = self._rng.uniform(50_000, 5_000_000, size=n_rows).round(2)
        pd_values = self._rng.uniform(0.001, 0.20, size=n_rows).round(4)
        lgd = self._rng.uniform(0.20, 0.80, size=n_rows).round(4)
        wal = self._rng.uniform(0.5, 10.0, size=n_rows).round(2)
        return pd.DataFrame(
            {
                "Loan_ID": loan_ids,
                "EAD": ead,
                "PD": pd_values,
                "LGD": lgd,
                "WAL": wal,
            }
        )

    def to_excel_bytes(self, n_rows: int = 15) -> bytes:
        df = self.generate(n_rows=n_rows)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Loans")
        return buffer.getvalue()
