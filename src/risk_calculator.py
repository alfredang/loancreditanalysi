import pandas as pd


class CreditRiskCalculator:
    RATING_THRESHOLDS = (
        (0.01, "Low"),
        (0.05, "Medium"),
        (0.15, "High"),
    )
    CRITICAL_RATING = "Critical"

    @staticmethod
    def classify_rating(loss_ratio: float) -> str:
        if pd.isna(loss_ratio):
            return "Unknown"
        for threshold, label in CreditRiskCalculator.RATING_THRESHOLDS:
            if loss_ratio < threshold:
                return label
        return CreditRiskCalculator.CRITICAL_RATING

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["Expected_Loss"] = out["EAD"] * out["PD"] * out["LGD"]
        out["ECL_Lifetime"] = out["Expected_Loss"] * out["WAL"]
        out["Loss_Ratio"] = out["PD"] * out["LGD"]
        out["Risk_Rating"] = out["Loss_Ratio"].apply(self.classify_rating)
        return out
