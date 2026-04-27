import pandas as pd


class LoanPortfolio:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def as_dataframe(self) -> pd.DataFrame:
        return self._df

    def summary(self) -> dict:
        df = self._df
        total_ead = float(df["EAD"].sum())
        total_el = float(df["Expected_Loss"].sum())
        total_ecl = float(df["ECL_Lifetime"].sum())
        weighted_avg_pd = (
            float((df["PD"] * df["EAD"]).sum() / total_ead) if total_ead > 0 else 0.0
        )
        rating_counts = df["Risk_Rating"].value_counts().to_dict()
        return {
            "total_ead": total_ead,
            "total_expected_loss": total_el,
            "total_ecl_lifetime": total_ecl,
            "weighted_avg_pd": weighted_avg_pd,
            "rating_counts": rating_counts,
            "loan_count": len(df),
        }
