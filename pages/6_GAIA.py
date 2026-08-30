"""GAIA plane: a 2D PCA view of alternatives, criteria, and the weighted
resultant vector (pi), styled for publication and exportable to Excel."""
import plotly.graph_objects as go
import streamlit as st

from app_state import get_problem, style_download_buttons
from i18n import t
from promethee_core.gaia import compute_gaia, export_gaia_to_excel

style_download_buttons()
st.title(t("gaia.title"))
st.caption(t("gaia.caption"))

problem = get_problem()
active_alts = problem.active_alternatives()
active_crits = problem.active_criteria()

if len(active_alts) < 2 or not active_crits:
    st.info(t("common.need_2alt_1crit"))
    st.stop()

gaia = compute_gaia(problem)
alt_colors = problem.alternative_colors()
crit_colors = problem.criterion_colors()
weights = problem.normalized_weights()

st.metric(t("gaia.quality_metric"), f"{gaia.quality:.1%}")

# -- publishable style tokens --------------------------------------------------
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
RING = SURFACE
PI_COLOR = "#0b0b0b"  # deliberately outside the categorical palette: this is the summary line, not an item
FONT_FAMILY = 'system-ui, -apple-system, "Segoe UI", sans-serif'

fig = go.Figure()

for name, (x, y) in zip(gaia.alternative_names, gaia.alternative_coords):
    color = alt_colors.get(name, INK_PRIMARY)
    fig.add_trace(
        go.Scatter(
            x=[x], y=[y], mode="markers+text", text=[name], textposition="top center",
            textfont=dict(color=INK_PRIMARY, size=13, family=FONT_FAMILY),
            marker=dict(size=14, color=color, line=dict(color=RING, width=2)),
            name=name, legendgroup="Alternatives", legendgrouptitle_text="Alternatives",
            hovertemplate=f"<b>{name}</b><br>PC1=%{{x:.3f}}<br>PC2=%{{y:.3f}}<extra></extra>",
        )
    )

def add_vector(legend_name, label, x, y, color, width, legendgroup, legendgrouptitle, label_font_size, hover):
    """A vector from the origin: a plain colored line (shaft, hover, legend swatch),
    a short arrowhead stub so it reads as a direction, and a label offset radially
    past the tip so it doesn't collide with anything sitting right at the tip."""
    fig.add_trace(
        go.Scatter(
            x=[0, x], y=[0, y], mode="lines", line=dict(color=color, width=width),
            name=legend_name, legendgroup=legendgroup, legendgrouptitle_text=legendgrouptitle,
            hovertemplate=hover,
        )
    )
    stub_start_x, stub_start_y = 0.7 * x, 0.7 * y
    fig.add_annotation(
        x=x, y=y, ax=stub_start_x, ay=stub_start_y, xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=width, arrowcolor=color,
    )
    label_x, label_y = 1.12 * x, 1.12 * y
    fig.add_annotation(
        x=label_x, y=label_y, text=label, showarrow=False,
        font=dict(color=INK_PRIMARY, size=label_font_size, family=FONT_FAMILY),
    )


for name, (x, y) in zip(gaia.criterion_names, gaia.criterion_coords):
    color = crit_colors.get(name, INK_SECONDARY)
    add_vector(
        name, name, x, y, color, width=2.5, legendgroup="Criteria", legendgrouptitle="Criteria",
        label_font_size=13,
        hover=f"<b>{name}</b> (weight {weights.get(name, 0):.1%})<br>PC1=%{{x:.3f}}<br>PC2=%{{y:.3f}}<extra></extra>",
    )

pi_x, pi_y = gaia.pi_vector
add_vector(
    "π vector", "<b>π</b>", pi_x, pi_y, PI_COLOR, width=5,
    legendgroup=None, legendgrouptitle=None, label_font_size=22,
    hover=f"<b>π</b><br>PC1=%{{x:.3f}}<br>PC2=%{{y:.3f}}<extra></extra>",
)

fig.add_hline(y=0, line_color=BASELINE, line_width=1)
fig.add_vline(x=0, line_color=BASELINE, line_width=1)
fig.update_xaxes(
    title_text="PC1", gridcolor=GRIDLINE, gridwidth=1, zeroline=False,
    color=INK_SECONDARY, title_font=dict(color=INK_SECONDARY, family=FONT_FAMILY),
)
fig.update_yaxes(
    title_text="PC2", gridcolor=GRIDLINE, gridwidth=1, zeroline=False, scaleanchor="x", scaleratio=1,
    color=INK_SECONDARY, title_font=dict(color=INK_SECONDARY, family=FONT_FAMILY),
)
fig.update_layout(
    title=dict(text=f"GAIA Plane — {problem.name}", font=dict(color=INK_PRIMARY, size=18, family=FONT_FAMILY)),
    font=dict(family=FONT_FAMILY, color=INK_PRIMARY),
    paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
    legend=dict(
        bgcolor=SURFACE, bordercolor=BASELINE, borderwidth=1, groupclick="togglegroup",
        font=dict(color=INK_PRIMARY, family=FONT_FAMILY),
    ),
    margin=dict(l=60, r=40, t=60, b=60),
)

# Fixed light "paper" surface for print/publication, independent of the
# viewer's theme. theme=None stops Streamlit's dark-mode overlay, which
# otherwise lightens text against our light legend background and makes it
# unreadable in dark mode. toImageButtonOptions sizes the chart's own
# (client-side, no server dependency) PNG export to match.
st.plotly_chart(
    fig, width="stretch", theme=None,
    config={
        "toImageButtonOptions": {
            "format": "png", "filename": f"{problem.name or 'gaia'}_gaia_plane",
            "width": 1200, "height": 900, "scale": 2,
        }
    },
)

st.divider()
st.subheader(t("gaia.download_subheader"))
st.caption(t("gaia.download_caption"))

st.download_button(
    t("gaia.download_button"),
    data=export_gaia_to_excel(gaia, alt_colors, crit_colors, weights),
    file_name=f"{problem.name or 'gaia'}_gaia_plane.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
