"""English/Hungarian text for every Streamlit page's UI chrome.

Hungarian terminology follows the reference material for this course
(PROMETHEE_GUI_specifikáció.docx and PROMETHEE.pdf) — notably "szempont"
for "criterion" (not "kritérium"), "folyamérték" for "flow" (not
"áramlás"), and the reference's exact preference-function names (e.g.
"trapéz alakú" for Linear, "lépcsős" for Level).

Scope, deliberately: page chrome only — titles, captions, labels, buttons,
alerts. Two things stay in English regardless of the selected language:

- Plotly figure content (axis titles, legend, hover text, in-chart labels):
  these are exported as standalone images, so they should read the same no
  matter what language the app UI happens to be in when they're saved.
- Excel export content (sheet names, column headers, titles/notes passed to
  export_to_excel / export_table_to_excel / export_gaia_to_excel): same
  reasoning — a downloaded file should be self-describing in one language,
  not whatever the UI was set to at export time.

Exception messages raised from ``promethee_core`` also stay in English:
that package is deliberately kept free of any Streamlit (or i18n) dependency
so the math stays reusable outside this GUI.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

LANGUAGES = {"en": "English", "hu": "Magyar"}

# Persisted language choice: session_state alone resets on a fresh browser
# session (new tab, reload, server restart), so a plain-text sidecar file
# — same idea as app_state.py's problem autosave — carries the choice across
# those, instead of always falling back to English.
_LANGUAGE_PATH = Path(__file__).parent / ".promethee_language.txt"

TRANSLATIONS: dict[str, dict[str, str]] = {
    # -- shared across pages ---------------------------------------------------
    "common.name": {"en": "Name", "hu": "Név"},
    "common.description": {"en": "Description", "hu": "Leírás"},
    "common.active": {"en": "Active", "hu": "Aktív"},
    "common.color": {"en": "Color", "hu": "Szín"},
    "common.delete": {"en": "Delete", "hu": "Törlés"},
    "common.add": {"en": "Add", "hu": "Hozzáadás"},
    "common.weight": {"en": "Weight", "hu": "Súly"},
    "common.direction": {"en": "Direction", "hu": "Irány"},
    "common.direction_max": {"en": "max", "hu": "max"},
    "common.direction_min": {"en": "min", "hu": "min"},
    "common.please_provide_name": {"en": "Please provide a name.", "hu": "Adjon meg egy nevet."},
    "common.need_2alt_1crit": {
        "en": "Activate at least two alternatives and one criterion on the Problem Setup page.",
        "hu": "Aktiváljon legalább két alternatívát és egy szempontot a Probléma beállítása oldalon.",
    },
    "common.pref_function": {"en": "Preference function", "hu": "Preferenciafüggvény"},
    "common.pref_usual": {"en": "Usual", "hu": "Egyszerű"},
    "common.pref_u_shape": {"en": "U-shape", "hu": "U alakú"},
    "common.pref_v_shape": {"en": "V-shape", "hu": "V alakú"},
    "common.pref_level": {"en": "Level", "hu": "Lépcsős"},
    "common.pref_linear": {"en": "Trapezoid", "hu": "Trapéz alakú"},
    "common.pref_gaussian": {"en": "Gaussian", "hu": "Gauss"},

    # -- dashboard.py (sidebar navigation labels) --------------------------------
    "nav.home": {"en": "Home", "hu": "Kezdőlap"},
    "nav.problem_setup": {"en": "Problem Setup", "hu": "Probléma definiálása"},
    "nav.data_entry": {"en": "Data Entry", "hu": "Adatbevitel"},
    "nav.results": {"en": "Results", "hu": "Eredmények"},
    "nav.step_by_step": {"en": "Step-by-Step", "hu": "Lépésről lépésre"},
    "nav.sensitivity": {"en": "Sensitivity", "hu": "Érzékenységvizsgálat"},
    "nav.gaia": {"en": "GAIA", "hu": "GAIA"},

    # -- pages/0_Home.py ----------------------------------------------------
    "home.title": {"en": "PROMETHEE Playground", "hu": "PROMETHEE"},
    "home.caption": {
        "en": "A tool for the PROMETHEE multi-criteria decision method. "
        "Use the sidebar to set up alternatives and criteria, enter data, "
        "compute results, and explore sensitivity and the GAIA plane.",
        "hu": "Eszköz a PROMETHEE többszempontú döntési módszerhez. "
        "Az oldalsávon állíthatja be az alternatívákat és szempontokat, viheti be az adatokat, "
        "számíthatja ki az eredményeket, és vizsgálhatja az érzékenységet és a GAIA síkot.",
    },
    "home.current_problem": {"en": "Current problem", "hu": "Jelenlegi probléma"},
    "home.metric_name": {"en": "Name", "hu": "Név"},
    "home.metric_alt_crit": {"en": "Alternatives / Criteria", "hu": "Alternatívák / Szempontok"},
    "home.start_fresh": {"en": "**Start fresh**", "hu": "**Kezdés elölről**"},
    "home.create_new": {"en": "Create a new, empty problem", "hu": "Új, üres probléma létrehozása"},
    "home.load_builtin": {"en": "**Load the built-in example**", "hu": "**Beépített példa betöltése**"},
    "home.example_caption": {"en": "The car-purchase example.", "hu": "Az autóvásárlási példa."},
    "home.load_example": {"en": "Load example problem", "hu": "Példaprobléma betöltése"},
    "home.import_problem": {"en": "Import a problem", "hu": "Probléma importálása"},
    "home.import_caption": {
        "en": "Excel (.xlsx) files can contain everything in a predifined format: name, description, criteria settings "
        "(direction, weight, preference function, thresholds) and the raw data. "
        "CSV files only carry the raw data table (alternatives x criteria values); "
        "imported criteria get default settings you can adjust on the Problem Setup page.",
        "hu": "Az Excel (.xlsx) fájlok előre meghatározott formátumban mindent tartalmazhatnak: nevet, leírást, "
        "szempontbeállításokat (irány, súly, preferenciafüggvény, küszöbértékek) és a nyers adatokat. "
        "A CSV fájlok csak a nyers adattáblát tartalmazzák (alternatívák x szempontok értékei); "
        "az importált szempontok alapértelmezett beállításokat kapnak, amelyeket a Probléma beállítása oldalon módosíthat.",
    },
    "home.import_excel_label": {"en": "Import from Excel (.xlsx)", "hu": "Importálás Excelből (.xlsx)"},
    "home.excel_import_error": {
        "en": "Could not import this Excel file: {error}", "hu": "Nem sikerült importálni az Excel fájlt: {error}"
    },
    "home.excel_import_success": {
        "en": "Imported '{name}' from Excel.", "hu": "'{name}' sikeresen importálva Excelből."
    },
    "home.import_notes_lead": {
        "en": "Some values were missing or blank, so defaults were used:",
        "hu": "Néhány érték hiányzott vagy üres volt, ezért alapértelmezett értékek kerültek felhasználásra:",
    },
    "home.import_csv_label": {"en": "Import raw data from CSV", "hu": "Nyers adatok importálása CSV-ből"},
    "home.csv_import_error": {
        "en": "Could not import this CSV file: {error}", "hu": "Nem sikerült importálni a CSV fájlt: {error}"
    },
    "home.csv_import_success": {
        "en": "Imported raw data from CSV. Adjust criteria settings on the Problem Setup page.",
        "hu": "A nyers adatok importálva CSV-ből. A szempontbeállításokat a Probléma beállítása oldalon módosíthatja.",
    },
    "home.export_problem": {"en": "Export the current problem", "hu": "Jelenlegi probléma exportálása"},
    "home.download_excel": {"en": "Download as Excel (.xlsx)", "hu": "Letöltés Excelként (.xlsx)"},
    "home.download_csv": {"en": "Download raw data as CSV", "hu": "Nyers adatok letöltése CSV-ként"},

    # -- pages/1_Problem_Setup.py ------------------------------------------------
    "problem_setup.title": {"en": "Problem Setup", "hu": "Probléma beállítása"},
    "problem_setup.details": {"en": "Problem details", "hu": "Probléma adatai"},
    "problem_setup.alternatives": {"en": "Alternatives", "hu": "Alternatívák"},
    "problem_setup.alt_name_exists": {
        "en": "An alternative named '{name}' already exists.", "hu": "Már létezik '{name}' nevű alternatíva."
    },
    "problem_setup.add_alternative": {"en": "Add a new alternative", "hu": "Új alternatíva hozzáadása"},
    "problem_setup.criteria": {"en": "Criteria", "hu": "Szempontok"},
    "problem_setup.crit_name_exists": {
        "en": "A criterion named '{name}' already exists.", "hu": "Már létezik '{name}' nevű szempont."
    },
    "problem_setup.advanced_settings": {
        "en": "Advanced settings",
        "hu": "Speciális beállítások",
    },
    "problem_setup.q_label": {"en": "q (indifference threshold)", "hu": "q (indifferencia-küszöb)"},
    "problem_setup.p_label": {"en": "p (preference threshold)", "hu": "p (preferencia-küszöb)"},
    "problem_setup.s_label": {"en": "s (Gaussian parameter)", "hu": "s (Gauss-paraméter)"},
    "problem_setup.delete_criterion": {"en": "Delete criterion", "hu": "Szempont törlése"},
    "problem_setup.weights_caption": {
        "en": "Weights are automatically normalized to sum to 1 in all computations:",
        "hu": "A súlyok minden számításnál automatikusan úgy vannak normalizálva, hogy összegük 1 legyen:",
    },
    "problem_setup.add_criterion": {"en": "Add a new criterion", "hu": "Új szempont hozzáadása"},

    # -- pages/2_Data_Entry.py ---------------------------------------------------
    "data_entry.title": {"en": "Data Entry", "hu": "Adatbevitel"},
    "data_entry.need_setup": {
        "en": "Add at least one alternative and one criterion on the Problem Setup page first.",
        "hu": "Először adjon hozzá legalább egy alternatívát és egy szempontot a Probléma beállítása oldalon.",
    },
    "data_entry.raw_data": {"en": "Raw data", "hu": "Nyers adatok"},
    "data_entry.raw_data_caption": {
        "en": "One row per alternative, one column per criterion. Inactive alternatives/criteria "
        "(unchecked on the Problem Setup page) are still shown here but excluded from computations.",
        "hu": "Soronként egy alternatíva, oszloponként egy szempont. Az inaktív alternatívák/szempontok "
        "(a Probléma beállítása oldalon kikapcsolva) itt is megjelennek, de a számításokból kimaradnak.",
    },
    "data_entry.stats": {
        "en": "Descriptive statistics (active alternatives & criteria)",
        "hu": "Leíró statisztika (aktív alternatívák és szempontok)",
    },
    "data_entry.no_active": {
        "en": "No active alternatives/criteria to summarize.", "hu": "Nincs aktív alternatíva/szempont az összegzéshez."
    },

    # -- pages/3_Results.py -------------------------------------------------------
    "results.title": {"en": "Results", "hu": "Eredmények"},
    "results.flows_subheader": {
        "en": "Net, positive and negative flows", "hu": "Nettó, pozitív és negatív folyamértékek"
    },
    "results.ranking_positive": {"en": "**Ranking by Phi+**", "hu": "**Rangsor Phi+ szerint**"},
    "results.ranking_negative": {
        "en": "**Ranking by Phi-** (ascending is better)", "hu": "**Rangsor Phi- szerint** (kisebb a jobb)"
    },
    "results.ranking_final": {"en": "**Final ranking (net flow)**", "hu": "**Végső rangsor (nettó folyamérték)**"},
    "results.download_flows": {
        "en": "Download flows & rankings as Excel", "hu": "Folyamértékek és rangsorok letöltése Excelként"
    },
    "results.aggregated_subheader": {
        "en": "Aggregated preference matrix P", "hu": "Összesített P preferenciamátrix"
    },
    "results.aggregated_caption": {
        "en": "P(Ai, Aj): how much Ai is preferred to Aj overall, across all active criteria.",
        "hu": "P(Ai, Aj): mennyivel részesül előnyben Ai Aj-vel szemben összességében, minden aktív szempont alapján.",
    },
    "results.download_aggregated": {
        "en": "Download aggregated matrix as Excel", "hu": "Összesített mátrix letöltése Excelként"
    },
    "results.per_criterion_subheader": {
        "en": "Per-criterion preference matrices", "hu": "Szempontonkénti preferenciamátrixok"
    },
    "results.weight_normalized": {
        "en": "Weight (normalized): {weight}", "hu": "Súly (normalizált): {weight}"
    },
    "results.download_all_matrices": {
        "en": "Download all criteria matrices as Excel", "hu": "Összes szempontmátrix letöltése Excelként"
    },

    # -- pages/4_Step_by_Step.py --------------------------------------------------
    "step.title": {"en": "Step-by-Step Walkthrough", "hu": "Lépésről lépésre bemutató"},
    "step.caption": {
        "en": "Pick a criterion and two alternatives below; every step traces exactly "
        "what happens to them during the calculation.",
        "hu": "Válasszon lent egy szempontot és két alternatívát; minden lépés pontosan végigköveti, "
        "mi történik velük a számítás során.",
    },
    "step.pref_usual_explanation": {
        "en": "Any positive difference at all counts as full preference — there's no zone of indifference.",
        "hu": "Bármilyen pozitív különbség teljes preferenciának számít — nincs közömbösségi zóna.",
    },
    "step.pref_u_shape_explanation": {
        "en": "Below the indifference threshold **q**, there's no preference. From **q** onward, it's immediately full preference.",
        "hu": "A **q** indifferencia-küszöb alatt nincs preferencia. **q**-tól kezdve azonnal teljes a preferencia.",
    },
    "step.pref_v_shape_explanation": {
        "en": "Preference grows in a straight line from 0 up to the preference threshold **p**, where it becomes full preference.",
        "hu": "A preferencia egyenes vonalban nő 0-tól a **p** preferencia-küszöbig, ahol teljessé válik.",
    },
    "step.pref_level_explanation": {
        "en": "Below **q**: no preference. Between **q** and **p**: a flat 'half preference' (0.5). From **p** onward: full preference.",
        "hu": "**q** alatt: nincs preferencia. **q** és **p** között: állandó 'félpreferencia' (0,5). **p**-től kezdve: teljes preferencia.",
    },
    "step.pref_linear_explanation": {
        "en": "Below **q**: no preference. Between **q** and **p**: preference grows in a straight line from 0 to 1. From **p** onward: full preference.",
        "hu": "**q** alatt: nincs preferencia. **q** és **p** között: a preferencia egyenes vonalban nő 0-tól 1-ig. **p**-től kezdve: teljes preferencia.",
    },
    "step.pref_gaussian_explanation": {
        "en": "Preference grows smoothly along an S-shaped curve controlled by **s** — no sharp corners.",
        "hu": "A preferencia egy **s** paraméterrel szabályozott, S-alakú görbe mentén, simán nő — nincsenek éles törések.",
    },
    "step.interpret_none": {
        "en": "no preference — on this criterion alone, the two are considered equal (or the first is worse)",
        "hu": "nincs preferencia — e szempont alapján a kettő egyenlőnek számít (vagy az első rosszabb)",
    },
    "step.interpret_full": {
        "en": "full preference — the first alternative completely dominates on this criterion",
        "hu": "teljes preferencia — az első alternatíva teljesen dominál ezen a szemponton",
    },
    "step.interpret_partial": {
        "en": "a partial preference ({pct} of the way to full preference)",
        "hu": "részleges preferencia (a teljes preferencia {pct}-áig jutott)",
    },
    "step.pick_subheader": {
        "en": "Pick two alternatives and a criterion to trace", "hu": "Válasszon ki két alternatívát és egy szempontot"
    },
    "step.criterion_label": {"en": "Criterion", "hu": "Szempont"},
    "step.alt_a_label": {"en": "Alternative A", "hu": "A alternatíva"},
    "step.alt_b_label": {"en": "Alternative B", "hu": "B alternatíva"},
    "step.pick_different": {
        "en": "Pick two different alternatives to compare.", "hu": "Válasszon két különböző alternatívát az összehasonlításhoz."
    },
    "step.step1_subheader": {
        "en": "Step 1 — Turn a raw value difference into a preference degree",
        "hu": "1. lépés — A nyers értékkülönbség átalakítása preferencia értékké",
    },
    "step.maximized": {"en": "maximized", "hu": "maximalizált"},
    "step.minimized": {"en": "minimized", "hu": "minimalizált"},
    "step.crit_direction_intro": {
        "en": "**{crit_name}** is {direction}, using the **{pref_label}** preference function. ",
        "hu": "**{crit_name}** {direction}, a **{pref_label}** preferenciafüggvényt használva. ",
    },
    "step.thresholds_caption": {"en": "Thresholds: {bits}", "hu": "Küszöbértékek: {bits}"},
    "step.scores_line": {
        "en": "**{alt_a}** scores **{v_a}** and **{alt_b}** scores **{v_b}** on {crit_name}.",
        "hu": "**{alt_a}** pontszáma **{v_a}**, **{alt_b}** pontszáma **{v_b}** a(z) {crit_name} szemponton.",
    },
    "step.step2_subheader": {
        "en": "Step 2 — Do that for every pair: the '{crit_name}' preference matrix",
        "hu": "2. lépés — Ugyanez minden párra: a(z) '{crit_name}' preferenciamátrix",
    },
    "step.step2_caption": {
        "en": "P_{crit_name}(Ai, Aj) computed for every pair of alternatives. The cell you just traced is highlighted.",
        "hu": "P_{crit_name}(Ai, Aj) minden alternatívapárra kiszámítva. Az imént végigkövetett cella ki van emelve.",
    },
    "step.step3_subheader": {
        "en": "Step 3 — Combine every criterion, weighted", "hu": "3. lépés — Minden szempont súlyozott kombinálása"
    },
    "step.step3_caption": {
        "en": "The same pair, but now bringing in every active criterion with its normalized weight.",
        "hu": "Ugyanaz a pár, de most minden aktív szempontot bevonva, normalizált súlyával.",
    },
    "step.step3_sum": {
        "en": "Sum of contributions = **P({alt_a}, {alt_b}) = {sum}** "
        "— the same value sitting at row {alt_a}, column {alt_b} of the Results page's aggregated matrix "
        "(**{aggregated}**).",
        "hu": "A hozzájárulások összege = **P({alt_a}, {alt_b}) = {sum}** "
        "— ugyanez az érték szerepel az Eredmények oldal összesített mátrixának {alt_a} sorában, {alt_b} oszlopában "
        "(**{aggregated}**).",
    },
    "step.step4_subheader": {
        "en": "Step 4 — From the matrix to one score: {alt_a}'s net flow",
        "hu": "4. lépés — A mátrixtól egyetlen pontszámig: {alt_a} nettó folyamértéke",
    },
    "step.step4_caption": {
        "en": "Phi+({alt_a}) averages how much {alt_a} beats everyone else; Phi-({alt_a}) averages how much everyone "
        "else beats {alt_a}. The net flow is the difference — the higher, the better {alt_a} ranks overall.",
        "hu": "Phi+({alt_a}) azt átlagolja, mennyivel jobb {alt_a} a többieknél; Phi-({alt_a}) azt, mennyivel jobbak "
        "a többiek {alt_a}-nál. A nettó folyamérték a kettő különbsége — minél nagyobb, annál jobb {alt_a} helyezése.",
    },
    "step.final_ranking": {
        "en": "**{alt_a}** ends up ranked **#{rank}** of {m} by net flow. Final ranking: {ranking}",
        "hu": "**{alt_a}** végső helyezése **#{rank}.** a(z) {m} alternatíva közül nettó folyamérték szerint. Végső rangsor: {ranking}",
    },

    # -- pages/5_Sensitivity.py ----------------------------------------------------
    "sensitivity.title": {"en": "Sensitivity Analysis", "hu": "Érzékenységvizsgálat"},
    "sensitivity.caption": {
        "en": "How does each alternative's net flow change if one criterion's weight changes, "
        "while the relative weights of the other criteria stay the same? The chart shows "
        "the exact (linear) relationship, and the stability interval is the widest range "
        "of weights around the current value that keeps the top-x ranking unchanged.",
        "hu": "Hogyan változik az egyes alternatívák nettó folyamértéke, ha egy szempont súlya megváltozik, "
        "miközben a többi szempont relatív súlya változatlan marad? A grafikon a pontos (lineáris) "
        "összefüggést mutatja, a stabilitási intervallum pedig a jelenlegi érték körüli legszélesebb "
        "súlytartomány, amely mellett az első x helyezett rangsora nem változik.",
    },
    "sensitivity.need_2alt_2crit": {
        "en": "Sensitivity analysis needs at least two active alternatives and two active criteria.",
        "hu": "Az érzékenységvizsgálathoz legalább két aktív alternatíva és két aktív szempont szükséges.",
    },
    "sensitivity.criterion_to_analyze": {"en": "Criterion to analyze", "hu": "Vizsgálandó szempont"},
    "sensitivity.stability_slider": {
        "en": "Stability level: preserve the ranking of the top-x alternatives",
        "hu": "Stabilitási szint: az első x helyezett rangsorának megőrzése",
    },
    "sensitivity.current_weight": {"en": "Current normalized weight", "hu": "Jelenlegi normalizált súly"},
    "sensitivity.stability_success": {
        "en": "The top-{top_x} ranking stays the same while the weight of **{criterion_name}** "
        "is between **{w_low}** and **{w_high}** (other criteria rescaled proportionally).",
        "hu": "Az első {top_x} helyezett rangsora változatlan marad, amíg a(z) **{criterion_name}** súlya "
        "**{w_low}** és **{w_high}** között van (a többi szempont arányosan átskálázva).",
    },
    "sensitivity.no_reversal_at_0": {
        "en": "There is no rank reversal at 0.", "hu": "A 0 értéknél nincs rangsorváltás.",
    },
    "sensitivity.no_reversal_at_1": {
        "en": "There is no rank reversal at 1.", "hu": "Az 1 értéknél nincs rangsorváltás.",
    },
    "sensitivity.crossings_caption": {
        "en": "Rank crossings considered for this stability level:", "hu": "Az ehhez a stabilitási szinthez figyelembe vett rangsorváltások:"
    },
    "sensitivity.summary_subheader": {
        "en": "Weight stability summary for all criteria", "hu": "Súlystabilitási összefoglaló minden szemponthoz",
    },
    "sensitivity.summary_caption": {
        "en": "For this stability level, how far each criterion's weight can move before the top-{top_x} "
        "ranking changes (other criteria rescaled proportionally).",
        "hu": "Ehhez a stabilitási szinthez mennyit mozdulhat el az egyes szempontok súlya, amíg az első "
        "{top_x} helyezett rangsora megváltozik (a többi szempont arányosan átskálázva).",
    },
    "sensitivity.col_criterion": {"en": "Criterion", "hu": "Szempont"},
    "sensitivity.col_current_weight": {"en": "Current weight", "hu": "Jelenlegi súly"},
    "sensitivity.col_can_decrease_to": {"en": "Can decrease to", "hu": "Meddig csökkenthető"},
    "sensitivity.col_can_increase_to": {"en": "Can increase to", "hu": "Meddig növelhető"},
    "sensitivity.col_max_change": {"en": "Max change", "hu": "Legfeljebb ennyit változhat"},
    "sensitivity.unbounded": {"en": "no rank reversal", "hu": "bármeddig"},
    "sensitivity.most_sensitive": {
        "en": "The ranking is most sensitive to **{criterion_name}**'s weight — it can change by only "
        "**{max_change}** before the top-{top_x} ranking changes.",
        "hu": "A rangsor a(z) **{criterion_name}** szempont súlyára a legérzékenyebb — ennek súlya csak "
        "**{max_change}**-ot változhat, mielőtt az első {top_x} helyezett rangsora megváltozna.",
    },
    "sensitivity.download_subheader": {"en": "Download", "hu": "Letöltés"},
    "sensitivity.generate_png": {"en": "Generate PNG for download", "hu": "PNG előállítása letöltéshez"},
    "sensitivity.download_png": {"en": "Download plot as PNG", "hu": "Grafikon letöltése PNG-ként"},
    "sensitivity.stale_png": {
        "en": "The criterion or stability level changed since this PNG was generated — regenerate to download the current chart.",
        "hu": "A szempont vagy a stabilitási szint megváltozott a PNG előállítása óta — állítsa elő újra az aktuális grafikon letöltéséhez.",
    },
    "sensitivity.no_renderer": {
        "en": "Could not render the chart image (no local renderer available).",
        "hu": "Nem sikerült előállítani a grafikon képét (nincs elérhető helyi renderelő).",
    },

    # -- pages/6_GAIA.py -------------------------------------------------------------
    "gaia.title": {"en": "GAIA Plane", "hu": "GAIA sík"},
    "gaia.caption": {
        "en": "A 2D projection (principal component analysis) of the alternatives and criteria. "
        "Criteria vectors pointing the same way are statistically similar; vectors at "
        "roughly 90° are independent; vectors pointing opposite ways are conflicting. "
        "An alternative near a criterion's vector performs well on that criterion. "
        "The **π vector** (bold, dark) is the weighted sum of the criteria vectors — "
        "the direction favored by the current weighting.",
        "hu": "Az alternatívák és szempontok 2D vetülete (főkomponens-elemzés). "
        "Az azonos irányba mutató szempontvektorok statisztikailag hasonlóak; a kb. 90°-os "
        "szöget bezáró vektorok függetlenek; az ellentétes irányba mutató vektorok ellentmondanak egymásnak. "
        "Egy szempont vektorához közeli alternatíva jól teljesít azon a szemponton. "
        "A **π vektor** (vastag, sötét) a szempontvektorok súlyozott összege — "
        "a jelenlegi súlyozás által preferált irány.",
    },
    "gaia.quality_metric": {
        "en": "Plane quality (variance explained by these 2 dimensions)",
        "hu": "Sík minősége (a 2 dimenzió által magyarázott variancia)",
    },
    "gaia.download_subheader": {"en": "Download", "hu": "Letöltés"},
    "gaia.download_caption": {
        "en": "The Excel file has one sheet per element (Alternatives, Criteria, Pi vector) with "
        "their exact PC1/PC2 coordinates and assigned colors, plus a Plot sheet with the "
        "chart image exactly as shown above.",
        "hu": "Az Excel fájl elemenként egy munkalapot tartalmaz (Alternatívák, Szempontok, Pi vektor) "
        "a pontos PC1/PC2 koordinátákkal és a hozzárendelt színekkel, valamint egy Plot munkalapot "
        "a fent látható grafikon képével.",
    },
    "gaia.no_renderer": {
        "en": "Could not render the chart image for the Excel file (no local renderer available); "
        "the download will still include all coordinates.",
        "hu": "Nem sikerült előállítani a grafikon képét az Excel fájlhoz (nincs elérhető helyi renderelő); "
        "a letöltés így is tartalmazni fogja az összes koordinátát.",
    },
    "gaia.prepare_download": {"en": "Prepare download", "hu": "Letöltés előkészítése"},
    "gaia.download_button": {"en": "Download GAIA plane as Excel", "hu": "GAIA sík letöltése Excelként"},
    "gaia.stale_download": {
        "en": "The plane changed since this file was prepared — prepare again to download the current version.",
        "hu": "A sík megváltozott a fájl előkészítése óta — készítse elő újra az aktuális verzió letöltéséhez.",
    },
}

# Preference-function enum -> translation key, used to localize
# PREFERENCE_FUNCTION_LABELS (defined in promethee_core.model, which stays
# English since that package has no i18n dependency) for display here.
PREF_FUNCTION_KEYS = {
    "usual": "common.pref_usual",
    "u_shape": "common.pref_u_shape",
    "v_shape": "common.pref_v_shape",
    "level": "common.pref_level",
    "linear": "common.pref_linear",
    "gaussian": "common.pref_gaussian",
}


def current_language() -> str:
    return st.session_state.get("language", "en")


def t(key: str, **kwargs) -> str:
    entry = TRANSLATIONS[key]
    text = entry.get(current_language(), entry["en"])
    return text.format(**kwargs) if kwargs else text


def _load_saved_language() -> str:
    try:
        code = _LANGUAGE_PATH.read_text(encoding="utf-8").strip()
        return code if code in LANGUAGES else "en"
    except Exception:
        return "en"


def _save_language(code: str) -> None:
    try:
        _LANGUAGE_PATH.write_text(code, encoding="utf-8")
    except Exception:
        pass


def language_switcher() -> None:
    """Sidebar language picker. Bound directly to st.session_state['language']
    via its widget key, so every page just needs to call this once at the top
    (before any t() calls) to pick up whatever was last selected. Defaults
    from (and saves to) disk so a fresh session starts in the last-picked
    language instead of always resetting to English.

    Note: the default is only ever passed via `index`, never by pre-assigning
    st.session_state["language"] before creating the widget — doing both
    triggers a Streamlit warning ("widget created with a default value but
    also had its value set via the Session State API"), since it can't tell
    which of the two should win.
    """
    codes = list(LANGUAGES.keys())
    default_code = st.session_state.get("language") or _load_saved_language()
    selected = st.sidebar.selectbox(
        "🌐 Language / Nyelv",
        options=codes,
        format_func=lambda code: LANGUAGES[code],
        index=codes.index(default_code),
        key="language",
    )
    # Deliberately unconditional: by the time this line runs, session_state
    # already reflects *this* rerun's value (Streamlit applies a widget
    # interaction to session_state before the script body re-executes), so
    # comparing `selected` against session_state/default_code can never
    # detect "the user just changed it" — it's always already in sync. A
    # plain small text-file write is cheap enough to not need that guard.
    _save_language(selected)
