"""A student-friendly, interactive walkthrough of the PROMETHEE calculation:
from one raw value difference, to a preference degree, to the full matrix,
to the weighted aggregate, to the final net flow ranking. Every number here
is computed with the exact same functions as the Results page, so it always
matches — this page just narrates the steps in between.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app_state import get_problem
from i18n import PREF_FUNCTION_KEYS, t
from promethee_core.core import compute_promethee, preference_matrix_for_criterion
from promethee_core.model import PREFERENCE_FUNCTION_PARAMS, Direction, PreferenceFunctionType
from promethee_core.preference_functions import compute_preference

st.title(t("step.title"))
st.caption(t("step.caption"))

problem = get_problem()
active_alts = problem.active_alternatives()
active_crits = problem.active_criteria()

if len(active_alts) < 2 or not active_crits:
    st.info(t("common.need_2alt_1crit"))
    st.stop()

result = compute_promethee(problem)
alt_names = result.alternative_names
values = problem.active_values()

EXPLANATION_KEYS = {
    PreferenceFunctionType.USUAL: "step.pref_usual_explanation",
    PreferenceFunctionType.U_SHAPE: "step.pref_u_shape_explanation",
    PreferenceFunctionType.V_SHAPE: "step.pref_v_shape_explanation",
    PreferenceFunctionType.LEVEL: "step.pref_level_explanation",
    PreferenceFunctionType.LINEAR: "step.pref_linear_explanation",
    PreferenceFunctionType.GAUSSIAN: "step.pref_gaussian_explanation",
}


def interpret(p_value: float) -> str:
    if p_value <= 0:
        return t("step.interpret_none")
    if p_value >= 1:
        return t("step.interpret_full")
    return t("step.interpret_partial", pct=f"{p_value:.0%}")


def highlight_cells(df: pd.DataFrame, cells: list[tuple[int, int]], color: str) -> pd.DataFrame:
    styles = pd.DataFrame("", index=df.index, columns=df.columns)
    for r, c in cells:
        styles.iloc[r, c] = f"background-color: {color}; font-weight: 700"
    return styles


st.divider()
st.subheader(t("step.pick_subheader"))
pick_cols = st.columns(3)
crit_name = pick_cols[0].selectbox(t("step.criterion_label"), [c.name for c in active_crits])
alt_a = pick_cols[1].selectbox(t("step.alt_a_label"), alt_names, index=0)
b_options = [n for n in alt_names if n != alt_a] or alt_names
alt_b = pick_cols[2].selectbox(t("step.alt_b_label"), b_options, index=0)

if alt_a == alt_b:
    st.warning(t("step.pick_different"))
    st.stop()

criterion = next(c for c in active_crits if c.name == crit_name)
i = alt_names.index(alt_a)
j = alt_names.index(alt_b)
v_a, v_b = float(values.loc[alt_a, crit_name]), float(values.loc[alt_b, crit_name])
sign = 1.0 if criterion.direction == Direction.MAX else -1.0
d = sign * (v_a - v_b)
p_value = compute_preference(d, criterion.preference_function, q=criterion.q, p=criterion.p, s=criterion.s)

st.divider()
st.subheader(t("step.step1_subheader"))
# Minimized criteria flip the sign of the raw difference before it ever reaches
# the preference function (see the "d = ..." line below) — easy to miss, so
# call it out visually rather than leaving it to blend into the sentence.
if criterion.direction == Direction.MAX:
    direction_word = f"**{t('step.maximized')}**"
else:
    direction_word = f":orange[**{t('step.minimized')}**]"
st.markdown(
    t(
        "step.crit_direction_intro",
        crit_name=crit_name, direction=direction_word,
        pref_label=t(PREF_FUNCTION_KEYS[criterion.preference_function.value]),
    )
    + t(EXPLANATION_KEYS[criterion.preference_function])
)
needed = PREFERENCE_FUNCTION_PARAMS[criterion.preference_function]
if needed:
    threshold_bits = []
    if "q" in needed:
        threshold_bits.append(f"q = {criterion.q:g}")
    if "p" in needed:
        threshold_bits.append(f"p = {criterion.p:g}")
    if "s" in needed:
        threshold_bits.append(f"s = {criterion.s:g}")
    st.caption(t("step.thresholds_caption", bits=", ".join(threshold_bits)))

st.markdown(t("step.scores_line", alt_a=alt_a, v_a=f"{v_a:g}", alt_b=alt_b, v_b=f"{v_b:g}", crit_name=crit_name))
sign_text = f"{v_a:g} - {v_b:g}" if sign > 0 else f"-({v_a:g} - {v_b:g})"
st.latex(rf"d = {sign_text} = {d:g}")
st.latex(rf"P_{{{crit_name}}}(\text{{{alt_a}}}, \text{{{alt_b}}}) = {p_value:.3f}")

col_vals = values[crit_name].to_numpy()
all_diffs = [sign * (col_vals[a] - col_vals[b]) for a in range(len(col_vals)) for b in range(len(col_vals)) if a != b]
span = max([abs(x) for x in all_diffs] + [criterion.q, criterion.p, criterion.s, 1.0])
d_grid = np.linspace(-0.25 * span, 1.15 * span, 300)
p_grid = [
    compute_preference(float(x), criterion.preference_function, q=criterion.q, p=criterion.p, s=criterion.s)
    for x in d_grid
]

# Usual/U-shape/Level are genuine step functions (instant jumps, no ramp) — draw
# them with actual vertical edges instead of Plotly's default straight-line
# interpolation between sampled points, which would draw a sloped diagonal
# through any jump narrower than the sampling grid. V-shape/Linear/Gaussian are
# truly continuous, so they keep the default linear interpolation.
STEP_FUNCTIONS = {PreferenceFunctionType.USUAL, PreferenceFunctionType.U_SHAPE, PreferenceFunctionType.LEVEL}
line_shape = "hv" if criterion.preference_function in STEP_FUNCTIONS else "linear"

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=d_grid, y=p_grid, mode="lines", line=dict(width=2, color="#2a78d6", shape=line_shape), name="Preference"
    )
)
fig.add_trace(
    go.Scatter(
        x=[d], y=[p_value], mode="markers+text", marker=dict(size=12, color="#e34948", line=dict(width=2, color="white")),
        text=[f"{alt_a} vs {alt_b}"], textposition="top center", name="Your pair",
    )
)
for label, thresh in (("q", criterion.q), ("p", criterion.p)):
    if label in needed:
        fig.add_vline(x=thresh, line_dash="dot", line_color="gray", annotation_text=label)
fig.update_layout(
    xaxis_title="d (oriented difference)", yaxis_title=f"P_{crit_name}(A, B)",
    # Extra headroom above 1.0 (rather than the tighter 1.05) so the "A1 vs A2"
    # text label isn't clipped by the plot area when the point sits at P=1.
    yaxis_range=[-0.05, 1.3], showlegend=False, margin=dict(l=40, r=20, t=30, b=40),
)
st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader(t("step.step2_subheader", crit_name=crit_name))
st.caption(t("step.step2_caption", crit_name=crit_name))
matrix = result.criterion_matrices[crit_name]
matrix_df = pd.DataFrame(matrix, index=alt_names, columns=alt_names)
st.dataframe(
    matrix_df.style.format("{:.3f}").apply(highlight_cells, cells=[(i, j)], color="#ffe08a", axis=None),
    width="stretch",
)

st.divider()
st.subheader(t("step.step3_subheader"))
st.caption(t("step.step3_caption"))
st.latex(r"P(A_i, A_j) = \sum_k w_k \cdot P_k(A_i, A_j)")
contrib_rows = [
    {
        "Criterion": name,
        f"P_k({alt_a}, {alt_b})": mat[i, j],
        "Weight": result.weights[name],
        "Contribution": result.weights[name] * mat[i, j],
    }
    for name, mat in result.criterion_matrices.items()
]
contrib_df = pd.DataFrame(contrib_rows)
st.dataframe(
    contrib_df.style.format({f"P_k({alt_a}, {alt_b})": "{:.3f}", "Weight": "{:.4f}", "Contribution": "{:.4f}"}),
    width="stretch",
    hide_index=True,
)
aggregated_value = result.aggregated_matrix[i, j]
st.markdown(
    t(
        "step.step3_sum",
        alt_a=alt_a, alt_b=alt_b, sum=f"{contrib_df['Contribution'].sum():.4f}",
        aggregated=f"{aggregated_value:.4f}",
    )
)

st.divider()
st.subheader(t("step.step4_subheader", alt_a=alt_a))
st.caption(t("step.step4_caption", alt_a=alt_a))
m = len(alt_names)
others = [n for n in alt_names if n != alt_a]
row = result.aggregated_matrix[i, :]
col = result.aggregated_matrix[:, i]
flow_rows = [
    {"Compared with": other, f"P({alt_a}, other)": row[k], f"P(other, {alt_a})": col[k]}
    for k, other in enumerate(alt_names)
    if other != alt_a
]
flow_df = pd.DataFrame(flow_rows)
st.dataframe(
    flow_df.style.format({f"P({alt_a}, other)": "{:.3f}", f"P(other, {alt_a})": "{:.3f}"}),
    width="stretch",
    hide_index=True,
)
st.latex(rf"\Phi^+({alt_a}) = \frac{{1}}{{{m}-1}} \sum_{{other}} P({alt_a}, other) = {result.phi_plus[i]:.4f}")
st.latex(rf"\Phi^-({alt_a}) = \frac{{1}}{{{m}-1}} \sum_{{other}} P(other, {alt_a}) = {result.phi_minus[i]:.4f}")
st.latex(rf"\Phi({alt_a}) = \Phi^+({alt_a}) - \Phi^-({alt_a}) = {result.phi_net[i]:.4f}")

rank = result.ranking_net.index(alt_a) + 1
st.success(t("step.final_ranking", alt_a=alt_a, rank=rank, m=m, ranking=" > ".join(result.ranking_net)))
