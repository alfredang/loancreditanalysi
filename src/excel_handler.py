from io import BytesIO
from typing import Iterable

import pandas as pd


class ExcelHandler:
    DEFAULT_REQUIRED = ("EAD", "PD", "LGD", "WAL")

    def read_upload(self, file) -> pd.DataFrame:
        df = pd.read_excel(file, engine="openpyxl")
        if df.empty:
            raise ValueError("The uploaded Excel file contains no rows.")
        return df

    def validate_schema(
        self, df: pd.DataFrame, required: Iterable[str] = DEFAULT_REQUIRED
    ) -> None:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(
                f"Missing required column(s): {', '.join(missing)}. "
                f"Required columns are: {', '.join(required)}."
            )

    def to_excel_bytes(self, df: pd.DataFrame, sheet_name: str = "Results") -> bytes:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        return buffer.getvalue()
