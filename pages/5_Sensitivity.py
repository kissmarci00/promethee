"""Weight sensitivity analysis: stability intervals for a chosen criterion,
plus a chart of every alternative's net flow as that criterion's weight varies."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app_state import get_problem, style_download_buttons
from i18n import t
from promethee_core.core import compute_promethee
from promethee_core.sensitivity import compute_weight_sensitivity

style_download_buttons()
st.title(t("sensitivity.title"))
st.caption(t("sensitivity.caption"))

problem = get_problem()
active_crits = problem.active_criteria()
active_alts = problem.active_alternatives()

if len(active_alts) < 2 or len(active_crits) < 2:
    st.info(t("sensitivity.need_2alt_2crit"))
    st.stop()

result = compute_promethee(problem)

criterion_name = st.selectbox(t("sensitivity.criterion_to_analyze"), [c.name for c in active_crits])
top_x = st.slider(t("sensitivity.stability_slider"), 1, len(active_alts), 1)

try:
    sens = compute_weight_sensitivity(result, criterion_name)
except ValueError as exc:
    st.warning(str(exc))
    st.stop()

w_low, w_high, crossings = sens.stability_interval(top_x)

st.metric(t("sensitivity.current_weight"), f"{sens.w0:.4f}")
st.success(
    t(
        "sensitivity.stability_success",
        top_x=top_x, criterion_name=criterion_name, w_low=f"{w_low:.4f}", w_high=f"{w_high:.4f}",
    )
)
# 0.0/1.0 here mean stability_interval() found no crossing on that side at
# all — stable to the extreme, not just up to a boundary that happens to
# land on 0 or 1. Call it out explicitly rather than printing a plain number.
if w_low == 0.0:
    st.caption(t("sensitivity.no_reversal_at_0"))
if w_high == 1.0:
    st.caption(t("sensitivity.no_reversal_at_1"))

ws = np.linspace(0.0, 1.0, 201)
flows = sens.flow_at(ws)

# -- publishable style tokens (fixed light "paper" surface, independent of the
# viewer's OS/browser theme), matching the GAIA page's export styling --------
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRIDLINE = "#e1e0d9"
FONT_FAMILY = 'system-ui, -apple-system, "Segoe UI", sans-serif'

fig = go.Figure()
for idx, name in enumerate(sens.alt_names):
    fig.add_trace(go.Scatter(x=ws, y=flows[:, idx], mode="lines", name=name))
fig.add_vline(x=sens.w0, line_dash="dash", line_color=INK_SECONDARY, annotation_text="current weight")
fig.add_vrect(x0=w_low, x1=w_high, fillcolor="LightGreen", opacity=0.15, line_width=0)
fig.update_xaxes(gridcolor=GRIDLINE, color=INK_SECONDARY, title_font=dict(color=INK_SECONDARY, family=FONT_FAMILY))
fig.update_yaxes(gridcolor=GRIDLINE, color=INK_SECONDARY, title_font=dict(color=INK_SECONDARY, family=FONT_FAMILY))
fig.update_layout(
    title=dict(
        text=f"Sensitivity of '{criterion_name}' — {problem.name}",
        font=dict(color=INK_PRIMARY, size=18, family=FONT_FAMILY),
    ),
    xaxis_title=f"Weight of '{criterion_name}'",
    yaxis_title="Net flow Phi(Ai)",
    xaxis_range=[0, 1],
    legend_title="Alternative",
    font=dict(family=FONT_FAMILY, color=INK_PRIMARY),
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    legend=dict(bgcolor=SURFACE, font=dict(color=INK_PRIMARY, family=FONT_FAMILY)),
    margin=dict(l=60, r=40, t=60, b=60),
)
st.plotly_chart(
    fig, width="stretch", theme=None,
    config={
        "toImageButtonOptions": {
            "format": "png", "filename": f"{problem.name or 'sensitivity'}_{criterion_name}_sensitivity",
            "width": 1600, "height": 900, "scale": 2,
        }
    },
)

if crossings:
    st.caption(t("sensitivity.crossings_caption"))
    st.table(
        [{"Alternatives": f"{c['a']} <-> {c['b']}", "Weight at crossing": round(c["w"], 4)} for c in crossings]
    )

st.divider()
st.subheader(t("sensitivity.summary_subheader"))
st.caption(t("sensitivity.summary_caption", top_x=top_x))

summary_rows = []
for c in active_crits:
    try:
        c_sens = compute_weight_sensitivity(result, c.name)
    except ValueError:
        continue
    c_w_low, c_w_high, _ = c_sens.stability_interval(top_x)
    # A side at 0/1 means truly unbounded, not "weight happens to be near the
    # edge" — treat it as infinite rather than w0 - 0 / 1 - w0, or a small w0
    # could wrongly look like the binding constraint. Both sides unbounded
    # means this criterion never flips the ranking, so it has no max change
    # and should never be picked as most sensitive.
    decrease_amount = float("inf") if c_w_low == 0.0 else c_sens.w0 - c_w_low
    increase_amount = float("inf") if c_w_high == 1.0 else c_w_high - c_sens.w0
    max_change = None if decrease_amount == increase_amount == float("inf") else min(decrease_amount, increase_amount)
    summary_rows.append({"name": c.name, "w0": c_sens.w0, "w_low": c_w_low, "w_high": c_w_high, "max_change": max_change})

if summary_rows:
    unbounded_text = t("sensitivity.unbounded")
    table_rows = [
        {
            t("sensitivity.col_criterion"): r["name"],
            t("sensitivity.col_current_weight"): f"{r['w0']:.4f}",
            t("sensitivity.col_can_decrease_to"): unbounded_text if r["w_low"] == 0.0 else f"{r['w_low']:.4f}",
            t("sensitivity.col_can_increase_to"): unbounded_text if r["w_high"] == 1.0 else f"{r['w_high']:.4f}",
            t("sensitivity.col_max_change"): "—" if r["max_change"] is None else f"{r['max_change']:.4f}",
        }
        for r in summary_rows
    ]
    st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

    sensitive_rows = [r for r in summary_rows if r["max_change"] is not None]
    if sensitive_rows:
        most_sensitive = min(sensitive_rows, key=lambda r: r["max_change"])
        st.info(
            t(
                "sensitivity.most_sensitive",
                criterion_name=most_sensitive["name"], max_change=f"{most_sensitive['max_change']:.4f}",
                top_x=top_x,
            )
        )
