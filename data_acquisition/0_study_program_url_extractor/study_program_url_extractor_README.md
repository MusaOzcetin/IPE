# TU Berlin Study Program URL Extractor

## Overview

This python script downloads TU Berlin's paginated “All programs offered” pages and extracts the URLs/links that correspond to **study program pages**.  
It then saves all extracted program links into a `.txt` file (one url per line).

---

## Functionality

- Takes a list of **URLs**. As of February 2026, the pages that list all of the TU Berlin study programs 10 pages / URLs with the first one and **base URL** being: https://www.tu.berlin/en/studying/study-programs/all-programs-offered
- Downloads each page’s HTML
- Finds all `<a>` (anchor) tags on the page
- Keeps only links that contain `"study-course"` in their URL
- Removes duplicate links automatically
- Writes all unique study program links into a file named:
  `study_program_urls.txt`

---

## Inputs

At the beginning of the script, there is a python list called `pages` which contains all the pages that list study programs in the current TU berlin website.

You have to add these links **MANUALLY** but it is **very easy** since, at least in the current (February 2026) TU Berlin website URL structure, you only need to add the page number at the end of the **base URL** like this `/x` for pages 1-9 and `/xx` for pages equal or greater than 10. Do this for all the available pages. As of February 2026 the pages are 10.

Example below:

```python
pages = [
  "https://www.tu.berlin/en/studying/study-programs/all-programs-offered",
  "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/2",
  ...
  "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/10",
]
```

This is the only input you need.

## Output

The script generates a simple txt file:

- Filename: study_program_urls.txt
- Structure: one URL per line
- Example lines:

```
https://www.tu.berlin/en/studying/study-programs/all-programs-offered/study-course/brewing-and-beverage-technology-b-sc
https://www.tu.berlin/en/studying/study-programs/all-programs-offered/study-course/building-sustainability-m-ba
https://www.tu.berlin/en/studying/study-programs/all-programs-offered/study-course/chemical-engineering-m-sc

```

## Requirements

You need:

- Python 3.8+ (Python 3 is required)
- Two Python libraries:
  - `requests`
  - `beautifulsoup4`

## Setup (first time only)

### 1) Check that Python is installed

Run:

```bash
python --version
```

OR

```bash
python3 --version
```

You should see something like:

```bash
Python 3.10.12
```

### 2) Install required libraries

Run:

```bash
pip install requests beautifulsoup4
```

If pip does not work, try:

```bash
python -m pip install requests beautifulsoup4
```

or

```bash
python3 -m pip install requests beautifulsoup4
```

## How to run the script

Run:

```
python study_program_url_extractor.py
```

(or)

```
python3 study_program_url_extractor.py
```

As it runs, it prints its progress in the terminal like this:

```
Now downloading: https://www.tu.berlin/en/studying/study-programs/all-programs-offered
Now downloading: https://www.tu.berlin/en/studying/study-programs/all-programs-offered/2
...
Done!
Total unique links found: 123
Saved to file: study_program_urls.txt
```

(The number 123 is just an example — your number may differ.)

## Change the output file name to your liking

In the script, line 42, change:

```
output_file = "study_program_urls.txt"
```

to any file name you want, e.g.:

```
output_file = "tu_berlin_program_urls_2026_02_28_2054.txt"
```

## Troubleshooting

### Problem:

- `ModuleNotFoundError: No module named 'bs4'`

### Explanation:

- You did not install BeautifulSoup.

### Fix:

```
pip install beautifulsoup4
```

### Problem:

- Script prints HTTP status codes like:

  `404`: page not found
  - Check if the URL is be wrong.

  `403`: blocked
  - TU Berlin has started blocking automated requests. In that case you need to contact the TU Berlin website admins and ask them for permission to move on and possibly alter this script accordingly.

  `500`: server error (problem with the website)
  - You can try again later.

### Problem:

- File is created but it is empty

### Explanation

- This could happen if:
  - the page structure has changed, OR
  - the TU Berlin no longer uses `"study-course"` as part of the URLs

### Fix

- In that case you will need to update the filter logic of the script to cater to the changes.
