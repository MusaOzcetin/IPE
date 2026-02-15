#!/usr/bin/env python3
# =============================================================================
# Offline "TU Berlin Dates & Deadlines" HTML file → Offline JSON file, MD file
#
# [FUNCTIONALITY]
#
# This python3 script:
#
# A) Reads an offline, locally saved HTML file
#    of the TU Berlin "Dates & Deadlines" page.
#
# B) Extracts, per semester:
#   1) Application and Enrollment Deadlines (all subsections)
#   2) Semester Dates
#
# C) Writes two offline files:
#   - JSON (machine-readable)
#   - Markdown (human-readable)
#
# [DEPENDENCIES]
#
# - This script relies on BeautifulSoup and optionally on lxml as dependencies.
#   It will still run without lxml because it falls back to html.parser,
#   but lxml is recommended.
#
# - The dependencies are to be found int he dependencies.txt
#   (see dates_deadlines_README.md)
#
# [NOTES]
#
# - This script is intended to run completely offline (no web requests).
#
# - The subsection titled "For exchange students" is included but intentionally
#   left empty (because it's an external link and you will fill it manually).
# =============================================================================

from bs4 import BeautifulSoup, Tag
from pathlib import Path
import json, re
from datetime import datetime, timezone

# -----------------------------------------------------------------------------
# [MANUAL CONFIG SECTION]
# You only need to edit these paths for your machine / repo setup:
#
# 1) html_path: Points to the locally saved TU Berlin HTML page that will be #
#               fed as input tho this script
#
# 2) json_out:  Where to write the generated JSON.
#               This option can be found at the end of this script.
#
# 3) md_out:    Where to write the generated Markdown.
#               This option is also at the bottom.
# -----------------------------------------------------------------------------

# Manual change option 1: Here you can change the path and fine-name
# where the HTML file with the TU berlin Dates and Deadlines which
# you downloaded ans saved, is going to be red from.
html_path = Path("/mnt/data/tu_berlin_dates_deadlines.html")
html = html_path.read_text(encoding="utf-8", errors="ignore")

# Parse HTML with lxml if available (faster & more robust), otherwise fallback.
try:
    soup = BeautifulSoup(html, "lxml")
except Exception:
    soup = BeautifulSoup(html, "html.parser")

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def clean_text_node(node):
    # Converts any BeautifulSoup node's text into a normalized one-line string:
    # - joins with spaces
    # - strips leading/trailing whitespace
    # - collapses repeated whitespace
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""


def extract_links(cell):
    # Extracts all <a href="..."> links from a cell and returns a list of
    # dictionaries: {"text": "...", "href": "..."}.
    # This is useful because some date cells contain URLs to additional info.
    links = []
    if cell:
        for a in cell.find_all("a"):
            href = a.get("href")
            txt = clean_text_node(a)
            if href:
                links.append({"text": txt, "href": href})
    return links


# Regex to detect German-style dates "dd.mm.yyyy" anywhere inside a string.
date_re = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")


def parse_date_info(text):
    # Converts a free-text date cell into a parse-friendly dictionary:
    # - If it contains exactly one dd.mm.yyyy → {"raw": ..., "iso": "YYYY-MM-DD"}
    # - If it contains two or more dd.mm.yyyy → treat first two as range:
    #       {"raw": ..., "start_iso": ..., "end_iso": ...}
    # - Otherwise → {"raw": ...} only
    #
    # This makes downstream parsing reliable while preserving original text.
    raw = " ".join((text or "").split()).strip()
    if not raw:
        return {"raw": ""}
    matches = list(date_re.finditer(raw))
    if len(matches) >= 2:
        d1, m1, y1 = map(int, matches[0].groups())
        d2, m2, y2 = map(int, matches[1].groups())
        return {
            "raw": raw,
            "start_iso": f"{y1:04d}-{m1:02d}-{d1:02d}",
            "end_iso": f"{y2:04d}-{m2:02d}-{d2:02d}",
        }
    if len(matches) == 1:
        d, m, y = map(int, matches[0].groups())
        return {"raw": raw, "iso": f"{y:04d}-{m:02d}-{d:02d}"}
    return {"raw": raw}


def is_semester_heading_text(txt: str) -> bool:
    # Identifies heading text that indicates a semester section.
    t = (txt or "").lower()
    return "winter semester" in t or "summer semester" in t


def find_heading(predicate):
    # Searches for the first <h2> or <h3> in the document such that
    # predicate(clean_text_node(heading)) returns True.
    for h in soup.find_all(["h2", "h3"]):
        if predicate(clean_text_node(h)):
            return h
    return None


# Locate the two top-level anchor headings that separate the page sections.
h2_app = find_heading(
    lambda t: "application and enrollment deadlines" in t.lower()
)
h2_sem = find_heading(
    lambda t: (
        t.lower().strip() == "semester dates" or "semester dates" in t.lower()
    )
)


def iter_between(start: Tag, end: Tag):
    # Iterates through the HTML document elements starting at `start`
    # and stops before reaching `end`.
    #
    # This lets us scan only the relevant region of the page for each section.
    cur = start
    while cur:
        if cur == end:
            break
        yield cur
        cur = cur.next_element


# NOTE: region_html() exists in the original code and remains unchanged.
# It is currently not used later, but it is preserved as-is.
def region_html(start_h: Tag, end_h: Tag | None):
    parts = []
    if not start_h:
        return ""
    for el in iter_between(start_h, end_h):
        if isinstance(el, Tag):
            parts.append(str(el))
    return "".join(parts)


# -----------------------------------------------------------------------------
# Extract 1) Application & Enrollment Deadlines (accordion subsections per semester)
# -----------------------------------------------------------------------------

app_semesters = []
if h2_app:
    # Find all semester <h3> headings after the Application section heading
    # and before the Semester Dates section heading.
    sem_h3s = []
    el = h2_app
    while el and el != h2_sem:
        if isinstance(el, Tag) and el.name == "h3":
            txt = clean_text_node(el)
            if is_semester_heading_text(txt):
                sem_h3s.append(el)
        el = el.next_element

    # For each semester heading, find the accordion block and parse each
    # accordion subsection into structured data.
    for idx, sem_h3 in enumerate(sem_h3s):
        sem_title = clean_text_node(sem_h3)
        boundary = sem_h3s[idx + 1] if idx + 1 < len(sem_h3s) else h2_sem

        # Locate the first accordion container after this semester header.
        acc = None
        el = sem_h3
        while el and el != boundary:
            if (
                isinstance(el, Tag)
                and el.name == "div"
                and el.get("class")
                and "ui-accordion" in el.get("class")
            ):
                acc = el
                break
            el = el.next_element

        subsections = []
        if acc:
            # Accordion structure pattern:
            #   h3.ui-accordion-header  (subsection title)
            #   div.ui-accordion-content (subsection content)
            # repeated...
            children = [c for c in acc.children if isinstance(c, Tag)]
            i = 0
            while i < len(children):
                ch = children[i]
                if ch.name == "h3" and "ui-accordion-header" in (
                    ch.get("class") or []
                ):
                    sub_title = clean_text_node(ch)
                    content_div = (
                        children[i + 1]
                        if i + 1 < len(children)
                        and children[i + 1].name == "div"
                        else None
                    )
                    entry = {"title": sub_title, "groups": []}

                    # Special rule required by you:
                    # "For exchange students" must exist but contain no values.
                    if "exchange students" in sub_title.lower():
                        entry["groups"] = []
                    else:
                        if content_div:
                            # Tables are typically wrapped in "frame--type-table" divs.
                            frames = content_div.find_all(
                                "div",
                                class_=lambda c: c and "frame--type-table" in c,
                            )
                            # If not found, fallback to raw tables.
                            if not frames:
                                frames = content_div.find_all("table")
                                frames = [
                                    t.find_parent("div") or t for t in frames
                                ]
                            for fr in frames:
                                # Group title is often in h4/h5 above the table.
                                h4 = fr.find(["h4", "h5"])
                                gtitle = (
                                    clean_text_node(h4) if h4 else "General"
                                )
                                table = (
                                    fr.find("table")
                                    if isinstance(fr, Tag)
                                    else fr
                                )
                                items = []
                                if table:
                                    # Parse each row as (label, date/info, links)
                                    for tr in table.find_all("tr"):
                                        tds = tr.find_all(["td", "th"])
                                        if len(tds) < 2:
                                            continue
                                        label = clean_text_node(tds[0])
                                        val_text = clean_text_node(tds[1])
                                        items.append(
                                            {
                                                "label": label,
                                                "value": parse_date_info(
                                                    val_text
                                                ),
                                                "links": extract_links(tds[1]),
                                            }
                                        )
                                entry["groups"].append(
                                    {"title": gtitle, "items": items}
                                )
                    subsections.append(entry)
                    i += 2
                else:
                    i += 1

        app_semesters.append(
            {"semester": sem_title, "subsections": subsections}
        )

# -----------------------------------------------------------------------------
# Extract 2) Semester Dates (table per semester)
# -----------------------------------------------------------------------------

semester_dates_by_sem = {}
if h2_sem:
    # Find semester <h3> headings after the "Semester dates" heading.
    sem_h3s = []
    el = h2_sem
    while el:
        if isinstance(el, Tag) and el.name == "h3":
            txt = clean_text_node(el)
            if is_semester_heading_text(txt):
                sem_h3s.append(el)
        el = el.next_element

    # For each semester heading, find the first table that follows it and parse rows.
    for idx, sem_h3 in enumerate(sem_h3s):
        sem_title = clean_text_node(sem_h3)
        boundary = sem_h3s[idx + 1] if idx + 1 < len(sem_h3s) else None
        table = None
        el = sem_h3
        while el:
            el = el.next_element
            if boundary and el == boundary:
                break
            if isinstance(el, Tag) and el.name == "table":
                table = el
                break
        items = []
        if table:
            for tr in table.find_all("tr"):
                tds = tr.find_all(["td", "th"])
                if len(tds) < 2:
                    continue
                items.append(
                    {
                        "label": clean_text_node(tds[0]),
                        "value": parse_date_info(clean_text_node(tds[1])),
                        "links": extract_links(tds[1]),
                    }
                )
        semester_dates_by_sem[sem_title] = items

# -----------------------------------------------------------------------------
# Merge both extracted parts into final structure (per semester)
# -----------------------------------------------------------------------------

all_sem_titles = []
for s in app_semesters:
    if s["semester"] not in all_sem_titles:
        all_sem_titles.append(s["semester"])
for t in semester_dates_by_sem.keys():
    if t not in all_sem_titles:
        all_sem_titles.append(t)

app_map = {s["semester"]: s for s in app_semesters}
semesters_out = []
for title in all_sem_titles:
    semesters_out.append(
        {
            "semester": title,
            "application_and_enrollment_deadlines": app_map.get(
                title, {"subsections": []}
            )["subsections"],
            "semester_dates": semester_dates_by_sem.get(title, []),
        }
    )

data = {
    "source": {
        "url": "https://www.tu.berlin/en/studying/applying-and-enrolling/dates-deadlines",
        "local_html_file": html_path.name,
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
    },
    "semesters": semesters_out,
}

# -----------------------------------------------------------------------------
# Markdown renderer (converts extracted structured data into human-readable MD)
# -----------------------------------------------------------------------------


def md_value(v):
    if "start_iso" in v and "end_iso" in v:
        return f"{v.get('raw', '')} (`{v['start_iso']}` → `{v['end_iso']}`)"
    if "iso" in v:
        return f"{v.get('raw', '')} (`{v['iso']}`)"
    return v.get("raw", "")


md_lines = []
md_lines.append("# TU Berlin — Dates & Deadlines (offline)")
md_lines.append("")
md_lines.append(f"Source: {data['source']['url']}")
md_lines.append(
    f"Generated from local HTML: `{data['source']['local_html_file']}`"
)
md_lines.append(f"Generated at (UTC): `{data['source']['generated_at']}`")
md_lines.append("")

for sem in data["semesters"]:
    md_lines.append(f"## {sem['semester']}")
    md_lines.append("")
    md_lines.append("### Application and Enrollment Deadlines")
    md_lines.append("")
    subs = sem["application_and_enrollment_deadlines"]
    if not subs:
        md_lines.append("_No data found in the HTML for this section._")
        md_lines.append("")
    else:
        for sub in subs:
            md_lines.append(f"#### {sub['title']}")
            md_lines.append("")
            if "exchange students" in sub["title"].lower():
                md_lines.append("_TODO: external link — fill manually._")
                md_lines.append("")
                continue
            for g in sub.get("groups", []):
                gtitle = g.get("title", "General")
                if gtitle and gtitle != "General":
                    md_lines.append(f"##### {gtitle}")
                    md_lines.append("")
                md_lines.append("| Item | Date / Info | Links |")
                md_lines.append("|---|---|---|")
                for it in g.get("items", []):
                    links = it.get("links") or []
                    link_str = (
                        ", ".join(
                            [
                                f"[{l['text']}]({l['href']})"
                                if l.get("text")
                                else f"[link]({l['href']})"
                                for l in links
                            ]
                        )
                        if links
                        else ""
                    )
                    md_lines.append(
                        f"| {it['label']} | {md_value(it['value'])} | {link_str} |"
                    )
                md_lines.append("")
    md_lines.append("### Semester Dates")
    md_lines.append("")
    rows = sem["semester_dates"]
    if not rows:
        md_lines.append("_No data found in the HTML for this section._")
        md_lines.append("")
    else:
        md_lines.append("| Item | Date / Info | Links |")
        md_lines.append("|---|---|---|")
        for r in rows:
            links = r.get("links") or []
            link_str = (
                ", ".join(
                    [
                        f"[{l['text']}]({l['href']})"
                        if l.get("text")
                        else f"[link]({l['href']})"
                        for l in links
                    ]
                )
                if links
                else ""
            )
            md_lines.append(
                f"| {r['label']} | {md_value(r['value'])} | {link_str} |"
            )
        md_lines.append("")

md_text = "\n".join(md_lines)

# -----------------------------------------------------------------------------
# Output write (JSON + MD)
# -----------------------------------------------------------------------------

# Manual change option 2: Here you can change the path and fine-name
# where the JSON file is going to be saved to reflect your own setup.
json_out = Path("/mnt/data/dates_deadlines.json")

# Manual change option 3: Here you can change the path and fine-name
# where the MARKDOWN file is going to be saved to reflect your own setup.
md_out = Path("/mnt/data/dates_deadlines.md")
json_out.write_text(
    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
)
md_out.write_text(md_text, encoding="utf-8")
