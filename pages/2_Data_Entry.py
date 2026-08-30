"""Raw data entry: an editable alternatives x criteria grid, plus a
descriptive-statistics summary (mean/min/max/std) for the active data."""
import streamlit as st

from app_state import get_problem, problem_generation, save_problem
from i18n import t
from promethee_core.stats import summarize

st.title(t("data_entry.title"))

problem = get_problem()
gen = problem_generation()

if not problem.alternatives or not problem.criteria:
    st.info(t("data_entry.need_setup"))
    st.stop()

st.subheader(t("data_entry.raw_data"))
st.caption(t("data_entry.raw_data_caption"))

alt_names = [a.name for a in problem.alternatives]
crit_names = [c.name for c in problem.criteria]

# Increments on a full page run (visit, refresh, navigating back), not on
# fragment-only reruns from cell edits. Used below to tell those two apart.
st.session_state["data_entry_visit"] = st.session_state.get("data_entry_visit", 0) + 1
visit_id = st.session_state["data_entry_visit"]


# Fragment-scoped so a cell edit reruns only this function, not the whole
# page/autosave — without it, fast tab-through entry felt like it hung.
@st.fragment
def data_entry_grid() -> None:
    # `value=` must stay the same object across reruns of this fragment while
    # the grid stays mounted, or Streamlit thinks the data changed externally
    # and resets its edit tracking (silently dropping the edit that triggered
    # the rerun). So `base` is built once and never reassigned here; edits are
    # only ever read back through the widget's return value.
    #
    # On a fresh mount (navigated away and back, or refreshed), `base` does
    # need rebuilding from problem.values, otherwise the edit-less grid would
    # report "no edits" and overwrite saved data with stale values. `visit_id`
    # distinguishes a fresh mount from a same-instance fragment rerun.
    base_key = f"data_entry_base_{gen}"
    base_visit_key = f"data_entry_base_visit_{gen}"
    base = st.session_state.get(base_key)
    if (
        base is None
        or list(base.index) != alt_names
        or list(base.columns) != crit_names
        or st.session_state.get(base_visit_key) != visit_id
    ):
        base = problem.values.reindex(index=alt_names, columns=crit_names).fillna(0.0).astype(float)
        st.session_state[base_key] = base
        st.session_state[base_visit_key] = visit_id

    prior = problem.values.reindex(index=alt_names, columns=crit_names).fillna(0.0).astype(float)
    edited = st.data_editor(base, width='stretch', num_rows="fixed", key=f"data_editor_{gen}").astype(float)

    data_changed = not edited.equals(prior)
    problem.values = edited

    st.divider()
    st.subheader(t("data_entry.stats"))

    active_values = problem.active_values()
    if active_values.empty:
        st.info(t("data_entry.no_active"))
    else:
        st.dataframe(summarize(active_values), width='stretch')

    if data_changed:
        save_problem(problem)


data_entry_grid()
