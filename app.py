import pandas as pd
import streamlit as st

from src.excel_handler import ExcelHandler
from src.mock_data import MockDataGenerator
from src.portfolio import LoanPortfolio
from src.risk_calculator import CreditRiskCalculator

REQUIRED_COLUMNS = ("EAD", "PD", "LGD", "WAL")

st.set_page_config(page_title="Credit Risk Rating", layout="wide")


def clean_inputs(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    nan_mask = cleaned[list(REQUIRED_COLUMNS)].isna().any(axis=1)
    if nan_mask.any():
        st.warning(f"Dropped {int(nan_mask.sum())} row(s) with NaN in required columns.")
        cleaned = cleaned.loc[~nan_mask].copy()

    for col in ("PD", "LGD"):
        out_of_range = (cleaned[col] < 0) | (cleaned[col] > 1)
        if out_of_range.any():
            offenders = cleaned.index[out_of_range].tolist()
            st.warning(f"Clipped {col} to [0, 1] for row indices: {offenders}")
            cleaned[col] = cleaned[col].clip(lower=0, upper=1)

    bad_ead = cleaned["EAD"] <= 0
    if bad_ead.any():
        st.warning(f"EAD <= 0 found at row indices: {cleaned.index[bad_ead].tolist()}")

    return cleaned


def render_summary(summary: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total EAD", f"${summary['total_ead']:,.0f}")
    c2.metric("Total Expected Loss", f"${summary['total_expected_loss']:,.0f}")
    c3.metric("Total Lifetime ECL", f"${summary['total_ecl_lifetime']:,.0f}")
    c4.metric("Weighted-Avg PD", f"{summary['weighted_avg_pd']:.2%}")


def render_rating_chart(summary: dict) -> None:
    rating_order = ["Low", "Medium", "High", "Critical", "Unknown"]
    counts = summary["rating_counts"]
    chart_df = pd.DataFrame(
        {"Count": [counts.get(r, 0) for r in rating_order]},
        index=rating_order,
    )
    chart_df = chart_df[chart_df["Count"] > 0]
    st.bar_chart(chart_df)


def main() -> None:
    st.title("Credit Risk Rating")
    st.caption(
        "Upload a loan portfolio (Excel) with columns EAD, PD, LGD, WAL "
        "to compute Expected Loss, Lifetime ECL, and a Risk Rating per loan."
    )

    with st.sidebar:
        st.header("Sample data")
        st.write("Download a mock portfolio to test the app.")
        mock_bytes = MockDataGenerator().to_excel_bytes()
        st.download_button(
            label="Download mock Excel",
            data=mock_bytes,
            file_name="mock_loan_portfolio.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    uploaded = st.file_uploader(
        "Upload loan portfolio (.xlsx)", type=["xlsx"], accept_multiple_files=False
    )

    if uploaded is None:
        st.info("Awaiting an Excel upload. Use the sidebar to grab a sample file.")
        return

    handler = ExcelHandler()
    try:
        raw_df = handler.read_upload(uploaded)
        handler.validate_schema(raw_df, required=REQUIRED_COLUMNS)
    except ValueError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"Could not read Excel file: {exc}")
        return

    cleaned_df = clean_inputs(raw_df)
    if cleaned_df.empty:
        st.error("No usable rows remain after cleaning.")
        return

    enriched = CreditRiskCalculator().enrich(cleaned_df)
    portfolio = LoanPortfolio(enriched)
    summary = portfolio.summary()

    st.subheader("Portfolio summary")
    render_summary(summary)

    st.subheader("Risk rating distribution")
    render_rating_chart(summary)

    st.subheader("Enriched loans")
    st.dataframe(portfolio.as_dataframe(), use_container_width=True)

    st.download_button(
        label="Download enriched results",
        data=handler.to_excel_bytes(portfolio.as_dataframe()),
        file_name="credit_risk_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def render_footer() -> None:
    st.markdown(
        """
        <hr style="margin-top: 3rem; margin-bottom: 1rem; border: none; border-top: 1px solid rgba(255,255,255,0.15);" />
        <div style="text-align: center; color: rgba(255,255,255,0.55); font-size: 0.85rem; padding-bottom: 1rem;">
            Powered by <a href="https://www.tertiarycourses.com.sg/" target="_blank" rel="noopener noreferrer" style="color: inherit; text-decoration: underline;">Tertiary Infotech Academy Pte Ltd</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
    render_footer()
