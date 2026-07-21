"""PROMETHEE GUI — app entrypoint: sidebar language switcher and page routing.

Uses st.navigation/st.Page (rather than the implicit pages/ auto-discovery)
so the sidebar's page labels themselves can be translated — st.navigation
re-reads the current language on every rerun and rebuilds the labels, since
this entrypoint runs in full before delegating to whichever page is selected.
"""
import streamlit as st

from i18n import language_switcher, t

st.set_page_config(page_title="PROMETHEE GUI", page_icon="📊", layout="wide")
language_switcher()

pages = [
    st.Page("pages/0_Home.py", title=t("nav.home"), default=True),
    st.Page("pages/1_Problem_Setup.py", title=t("nav.problem_setup")),
    st.Page("pages/2_Data_Entry.py", title=t("nav.data_entry")),
    st.Page("pages/3_Results.py", title=t("nav.results")),
    st.Page("pages/4_Step_by_Step.py", title=t("nav.step_by_step")),
    st.Page("pages/5_Sensitivity.py", title=t("nav.sensitivity")),
    st.Page("pages/6_GAIA.py", title=t("nav.gaia")),
]
st.navigation(pages).run()
