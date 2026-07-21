"""Problem setup: name/description, alternatives, and criteria (direction,
weight, preference function, thresholds, active flag)."""
import streamlit as st

from app_state import get_problem, problem_generation, save_problem
from i18n import PREF_FUNCTION_KEYS, t
from promethee_core.model import (
    PREFERENCE_FUNCTION_PARAMS,
    Direction,
    PreferenceFunctionType,
)
from promethee_core.palette import default_color

st.title(t("problem_setup.title"))

problem = get_problem()
gen = problem_generation()

st.subheader(t("problem_setup.details"))
problem.name = st.text_input(t("common.name"), value=problem.name)
problem.description = st.text_area(t("common.description"), value=problem.description)

st.divider()
st.subheader(t("problem_setup.alternatives"))

# The checkbox has no separate input box below its label like the text fields
# next to it do, so by default it sits near the top of the row instead of
# level with the middle of those taller text boxes. Nudge it down to match.
st.markdown(
    """
    <style>
    div[class*="st-key-alt_active_"], div[class*="st-key-crit_active_"] {
        margin-top: 1.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

alt_default_colors = problem.alternative_colors()
for i, alt in enumerate(list(problem.alternatives)):
    cols = st.columns([3, 4, 1, 1, 1])
    new_name = cols[0].text_input(t("common.name"), value=alt.name, key=f"alt_name_{gen}_{i}")
    new_desc = cols[1].text_input(t("common.description"), value=alt.description, key=f"alt_desc_{gen}_{i}")
    new_active = cols[2].checkbox(t("common.active"), value=alt.active, key=f"alt_active_{gen}_{i}")
    new_color = cols[3].color_picker(
        t("common.color"), value=alt.color or alt_default_colors.get(alt.name, default_color(i)),
        key=f"alt_color_{gen}_{i}",
    )
    cols[4].write("")
    if cols[4].button(t("common.delete"), key=f"alt_del_{gen}_{i}"):
        problem.remove_alternative(alt.name)
        st.rerun()

    if new_name and new_name != alt.name:
        if new_name in [a.name for a in problem.alternatives if a is not alt]:
            st.error(t("problem_setup.alt_name_exists", name=new_name))
        else:
            problem.rename_alternative(alt.name, new_name)
    alt.description = new_desc
    alt.active = new_active
    alt.color = new_color

with st.form("add_alternative_form", clear_on_submit=True):
    st.write(t("problem_setup.add_alternative"))
    cols = st.columns([3, 4, 1])
    name = cols[0].text_input(t("common.name"))
    desc = cols[1].text_input(t("common.description"))
    submitted = cols[2].form_submit_button(t("common.add"))
    if submitted:
        if not name:
            st.error(t("common.please_provide_name"))
        elif name in [a.name for a in problem.alternatives]:
            st.error(t("problem_setup.alt_name_exists", name=name))
        else:
            problem.add_alternative(name, desc)
            st.rerun()

st.divider()
st.subheader(t("problem_setup.criteria"))

crit_default_colors = problem.criterion_colors()
for i, crit in enumerate(list(problem.criteria)):
    # Name, direction, weight, preference function and active are the settings
    # you touch for nearly every criterion, so they're always visible in this
    # row; only the less-frequently-needed settings (thresholds, color, delete)
    # sit behind the expander below.
    cols = st.columns([2.3, 1.5, 1.1, 2.3, 1.0])
    new_name = cols[0].text_input(t("common.name"), value=crit.name, key=f"crit_name_{gen}_{i}")
    new_direction = cols[1].radio(
        t("common.direction"), ["max", "min"], index=0 if crit.direction == Direction.MAX else 1,
        format_func=lambda d: t("common.direction_max") if d == "max" else t("common.direction_min"),
        key=f"crit_dir_{gen}_{i}", horizontal=True,
    )
    new_weight = cols[2].number_input(
        t("common.weight"), value=float(crit.weight), min_value=0.0, step=1.0, key=f"crit_weight_{gen}_{i}"
    )
    pref_options = list(PreferenceFunctionType)
    new_pref = cols[3].selectbox(
        t("common.pref_function"),
        pref_options,
        index=pref_options.index(crit.preference_function),
        format_func=lambda p: t(PREF_FUNCTION_KEYS[p.value]),
        key=f"crit_pref_{gen}_{i}",
    )
    new_active = cols[4].checkbox(t("common.active"), value=crit.active, key=f"crit_active_{gen}_{i}")

    with st.expander(t("problem_setup.advanced_settings"), expanded=False, key=f"crit_expander_{gen}_{i}"):
        needed_params = PREFERENCE_FUNCTION_PARAMS[new_pref]
        param_cols = st.columns(3)
        new_q, new_p, new_s = crit.q, crit.p, crit.s
        if "q" in needed_params:
            new_q = param_cols[0].number_input(
                t("problem_setup.q_label"), value=float(crit.q), step=1.0, key=f"crit_q_{gen}_{i}"
            )
        if "p" in needed_params:
            new_p = param_cols[1].number_input(
                t("problem_setup.p_label"), value=float(crit.p), step=1.0, key=f"crit_p_{gen}_{i}"
            )
        if "s" in needed_params:
            new_s = param_cols[2].number_input(
                t("problem_setup.s_label"), value=float(max(crit.s, 1e-4)), min_value=1e-4, step=1.0,
                key=f"crit_s_{gen}_{i}",
            )

        color_col, delete_col = st.columns(2)
        new_color = color_col.color_picker(
            t("common.color"), value=crit.color or crit_default_colors.get(crit.name, default_color(i)),
            key=f"crit_color_{gen}_{i}",
        )
        delete_col.write("")
        if delete_col.button(t("problem_setup.delete_criterion"), key=f"crit_del_{gen}_{i}"):
            problem.remove_criterion(crit.name)
            st.rerun()

    if new_name and new_name != crit.name:
        if new_name in [c.name for c in problem.criteria if c is not crit]:
            st.error(t("problem_setup.crit_name_exists", name=new_name))
        else:
            problem.rename_criterion(crit.name, new_name)
    crit.direction = Direction.MAX if new_direction == "max" else Direction.MIN
    crit.weight = new_weight
    crit.preference_function = new_pref
    crit.q, crit.p, crit.s = new_q, new_p, new_s
    crit.active = new_active
    crit.color = new_color
    st.divider()

st.caption(t("problem_setup.weights_caption"))
normalized = problem.normalized_weights()
if normalized:
    st.write({name: round(w, 4) for name, w in normalized.items()})

with st.form("add_criterion_form", clear_on_submit=True):
    st.write(t("problem_setup.add_criterion"))
    cols = st.columns([3, 2, 2])
    name = cols[0].text_input(t("common.name"))
    direction_label = cols[1].radio(
        t("common.direction"), ["max", "min"], horizontal=True,
        format_func=lambda d: t("common.direction_max") if d == "max" else t("common.direction_min"),
    )
    weight = cols[2].number_input(t("common.weight"), value=1.0, min_value=0.0, step=1.0)
    submitted = st.form_submit_button(t("common.add"))
    if submitted:
        if not name:
            st.error(t("common.please_provide_name"))
        elif name in [c.name for c in problem.criteria]:
            st.error(t("problem_setup.crit_name_exists", name=name))
        else:
            problem.add_criterion(
                name, direction=Direction.MAX if direction_label == "max" else Direction.MIN, weight=weight
            )
            st.rerun()

save_problem(problem)
