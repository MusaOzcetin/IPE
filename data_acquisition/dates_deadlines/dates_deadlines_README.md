# TU Berlin Dates & Deadlines

## Offline saved HTML file → Offline JSON file, Offline Markdown file

This script converts a locally saved copy of TU Berlin's "Dates & Deadlines" html page into:

- `dates_deadlines.json` (structured, parseable)
- `dates_deadlines.md` (readable summary)

It runs **offline**: you first save the webpage as an HTML file, then run the script.

## 1) Prerequisites

- Python **3.10+** (required because the script uses `Tag | None` type syntax)
- pip (comes with most Python installs)

## 2) Suggested file tree structure

```
dates_deadlines/
├─ dates_deadlines_README.md
├─ script/
│  └─ extract_tu_berlin_dates_deadlines.py
│  └─ dependencies.txt
├─ input/
│  └─ tu_berlin_dates_deadlines.html # (example name; user provided)
└─ output/
   └─ # (generated files appear here)
```
### Suggested script values for this repo layout:

```
html_path = Path("input/tu_berlin_dates_deadlines.html")
json_out = Path("output/dates_deadlines.json")
md_out = Path("output/dates_deadlines.md")
```

Make sure the `output/` directory exists (create it if not).

## 3) Setup (first time only)

From the repo root:

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r dependencies.txt
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r dependencies.txt
```

## 4) Save the TU Berlin webpage locally

Example parent directory:
`input/`

Example file name inside the parent directory:
`input/tu_berlin_dates_deadlines.html`

## 5) Update the script paths (manual hardcoding step)

Open `extract_tu_berlin_dates_deadlines.py` and edit **ONLY** the 3 lines where the one input file is located and where the two output files are to be saved:

`html_path = Path("...")` → point to your local HTML file directory

`json_out = Path("...")` → choose output path for json file

`md_out = Path("...")` → choose output path for markdown file


## 6) Run

### macOS / Linux

```bash
source .venv/bin/activate
python3 extract_tu_berlin_dates_deadlines.py
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
py extract_tu_berlin_dates_deadlines.py
```

## 7) Results

After running, you should have:

`output/dates_deadlines.json`

`output/dates_deadlines.md`

## 8) Notes / expected behavior

- The section "For exchange students" in the output files is intentionally present but empty.

- If TU Berlin changes the page structure, extraction might need adjustment.

- **Important**: The HTML snapshot currently contains **Winter 2025/2026**, **Summer 2026**, **Winter 2026/2027**. If someone saves the page later, they might get different semesters — the script will simply extract what is present in _their_ saved HTML.
