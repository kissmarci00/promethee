# PROMETHEE Playground

A tool for the PROMETHEE multi-criteria decision method. Set up alternatives
and criteria, enter data, and compute PROMETHEE I/II rankings — with a
step-by-step walkthrough of the math, weight sensitivity analysis, and the
GAIA plane for visualizing the whole decision at once. Import/export
problems as Excel or CSV. Available in English and Hungarian.

If you don't want to use a terminal at all, there are ready-to-run
Mac/Windows packages (no Python install needed) on the
[Releases](../../releases) page instead of the steps below.

## Installation

### 1. Open a terminal

- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter.
- **Windows:** press the Start key, type `cmd`, press Enter.

Every command below is typed into that same window, one line at a time,
pressing Enter after each.

### 2. Get the code

**Option A — with git:**
```
git clone https://github.com/kissmarci00/promethee.git
cd promethee
```

**Option B — without git:** click the green **Code** button near the top of
this page → **Download ZIP**, then unzip it. Back in the terminal, type
`cd ` (with a trailing space, don't press Enter yet), then drag the
unzipped folder into the terminal window — its path gets typed in for you —
and press Enter.

### 3. Install dependencies

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, use this instead for the second line:
```
.venv\Scripts\activate
```

## Running

```
streamlit run dashboard.py
```

Your browser should open automatically. If it doesn't, look in the
terminal for a line starting with `Local URL:` and open that address by
hand — usually `http://localhost:8501`, but it can be a different port if 8501 is already in use.

Next time you want to run the app, you don't need to reinstall anything:
open a terminal, `cd` into the `promethee` folder again, run
`source .venv/bin/activate` (Windows: `.venv\Scripts\activate`), then
`streamlit run dashboard.py`.
