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

# Bumps once per *full* run of this page script (first visit, browser refresh,
# navigating back from another page) but not on fragment-only reruns (cell
# edits) — fragment reruns skip everything outside the fragment function,
# including this line. Lets the fragment tell "still the same mounted grid
# instance" apart from "freshly (re)mounted, no memory of past edits" below.
st.session_state["data_entry_visit"] = st.session_state.get("data_entry_visit", 0) + 1
visit_id = st.session_state["data_entry_visit"]


# Scoped to its own fragment: editing a cell reruns *only* this function, not
# the whole page. Without this, every single cell commit was a full-script
# rerun (re-importing, recomputing everything below, and re-running the
# autosave write), which is what made fast Tab-through-cells entry feel like
# it hung after each value. Inside a fragment, a cell edit is a small,
# localized update — the rest of the page (title, captions above) never
# re-renders at all — while autosaving still happens automatically after
# every edit, exactly as before.
@st.fragment
def data_entry_grid() -> None:
    # `value=` passed to st.data_editor must stay the *exact same object* across
    # every rerun of this fragment, full stop — not "the same content", the same
    # object — for as long as the grid stays mounted. If it ever differs (even
    # to a fresh DataFrame with identical values, e.g. by feeding back the
    # editor's own last output as the next value=), Streamlit treats that as
    # "the underlying data changed externally" and resets the widget's own
    # accumulated edit-tracking. That reset can silently swallow the very edit
    # that triggered this rerun. So within one mounted instance, `base` is
    # built once and never reassigned; we only ever read edits back out
    # through the widget's return value, never feed them back in.
    #
    # But the grid *does* get freshly remounted with no memory of past edits
    # whenever you navigate away and back (or refresh the browser) — at that
    # point `base` must be rebuilt from problem.values (which autosave already
    # persisted), or the fresh, edit-less mount would report "no edits" and
    # overwrite the saved data back to stale values. `visit_id` (bumped once
    # per full page run, untouched by fragment-only reruns) tells these two
    # cases apart. Namespaced by generation too, so loading a new/sample/
    # imported problem starts fresh instead of reusing a stale buffer.
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
