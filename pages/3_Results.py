"""PROMETHEE results: preference matrices, flows, and rankings."""
import pandas as pd
import streamlit as st

from app_state import get_problem, style_download_buttons
from i18n import t
from promethee_core.core import compute_promethee
from promethee_core.table_export import export_table_to_excel, export_tables_to_excel

style_download_buttons()
st.title(t("results.title"))

problem = get_problem()
active_alts = problem.active_alternatives()
active_crits = problem.active_criteria()

if len(active_alts) < 2 or not active_crits:
    st.info(t("common.need_2alt_1crit"))
    st.stop()

result = compute_promethee(problem)

st.subheader(t("results.flows_subheader"))
flow_df = pd.DataFrame(
    {
        "Phi+ (positive flow)": result.phi_plus,
        "Phi- (negative flow)": result.phi_minus,
        "Phi (net flow)": result.phi_net,
    },
    index=result.alternative_names,
).sort_values("Phi (net flow)", ascending=False)
flow_df.insert(0, "Rank", range(1, len(flow_df) + 1))
st.dataframe(
    flow_df.style.format({
        "Phi+ (positive flow)": "{:.4f}",
        "Phi- (negative flow)": "{:.4f}",
        "Phi (net flow)": "{:.4f}",
    }),
    width='stretch',
)

rank_col1, rank_col2, rank_col3 = st.columns(3)
rank_col1.markdown(t("results.ranking_positive"))
rank_col1.write(" > ".join(result.ranking_positive))
rank_col2.markdown(t("results.ranking_negative"))
rank_col2.write(" > ".join(result.ranking_negative))
rank_col3.markdown(t("results.ranking_final"))
rank_col3.write(" > ".join(result.ranking_net))

st.download_button(
    t("results.download_flows"),
    data=export_table_to_excel(
        flow_df, sheet_name="Flows", title="Net, positive and negative flows", index_label="Alternative",
        number_format="0.0000",
        notes=[
            ("Ranking by Phi+", " > ".join(result.ranking_positive)),
            ("Ranking by Phi-", " > ".join(result.ranking_negative)),
            ("Final ranking (net flow)", " > ".join(result.ranking_net)),
        ],
    ),
    file_name=f"{problem.name or 'promethee'}_flows.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.divider()
st.subheader(t("results.aggregated_subheader"))
st.caption(t("results.aggregated_caption"))
aggregated_df = pd.DataFrame(
    result.aggregated_matrix, index=result.alternative_names, columns=result.alternative_names
)
st.dataframe(aggregated_df.style.format("{:.4f}"), width='stretch')
st.download_button(
    t("results.download_aggregated"),
    data=export_table_to_excel(
        aggregated_df, sheet_name="Aggregated P", title="Aggregated preference matrix P", index_label="Ai \\ Aj",
        number_format="0.0000",
    ),
    file_name=f"{problem.name or 'promethee'}_aggregated_matrix.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.divider()
st.subheader(t("results.per_criterion_subheader"))
criterion_matrix_dfs = {
    name: pd.DataFrame(matrix, index=result.alternative_names, columns=result.alternative_names)
    for name, matrix in result.criterion_matrices.items()
}
tabs = st.tabs(list(criterion_matrix_dfs.keys()))
for tab, (name, matrix_df) in zip(tabs, criterion_matrix_dfs.items()):
    with tab:
        st.caption(t("results.weight_normalized", weight=f"{result.weights[name]:.4f}"))
        st.dataframe(matrix_df.style.format("{:.4f}"), width='stretch')

st.download_button(
    t("results.download_all_matrices"),
    data=export_tables_to_excel(
        [
            (
                name, matrix_df, f"Preference matrix P — {name}",
                [("Weight (normalized)", f"{result.weights[name]:.4f}")],
            )
            for name, matrix_df in criterion_matrix_dfs.items()
        ],
        index_label="Ai \\ Aj",
        number_format="0.0000",
    ),
    file_name=f"{problem.name or 'promethee'}_criteria_matrices.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
