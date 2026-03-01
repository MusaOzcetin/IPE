# Study Program HTML Extractor

## Overview

This script extracts structured information from a pre-existing JSON file that contains the full unstructured HTML markup of all the TU Berlin study programs that was saved in the previous step.

The output is a new clean and structured JSON in which the important information contained in the unstructured HTML markup "soup" of the input JSON is being extracted and normalized in order to be easier for our chatbot to parse as part of its knowledge base.

## Functionality

- Reads an input JSON with study program URLs and HTML content named `study_program_url_and_html_content.json`
  For each study program found in the input JSON it:
- Extracts the `<h1>` study program title
- Finds every `<h2>` section headings
- Collects:
  - All `<p>` elements until the next `<h2>`
  - All `<table>` rows and converts them into key-value JSON format
- Saves a new normalized JSON file named `study_program_webpages.json`

## Files

```
study_program_JSON_summarizer/
│
├── study_program_JSON_summarizer.py
├── input.json
├── output.json
└── study_program_JSON_summarizer_README.md

```

Where

- **`input.json`** is the file that contains the html "soup". In our current use case this is the `study_program_url_and_html_content.json` that was generated in the previous step.
- **`output.json`** is the clean, normalized JSON that is produced. In our current use case this is the `study_program_webpages.json` which it the file that will be uploaded to the chatbot to become part of its knowledge base.

## Input

The input JSON is just a list of objects structured like this:

```json
[
  {
    "url": "https://example.com/study-program-1",
    "html": "<!DOCTYPE html> ... full HTML content ..."
  },
  ...
]
```

Each object contains:

- a URL. A specific TU Berlin study program URL
- an HTML "soup". The complete HTML content of that study program webpage.

## Output

The output JSON looks like this:

```json
[
  {
    "url": "https://example.com/study-program-1",
    "title": "Information Systems Management (Wirtschaftsinformatik), M.Sc.",
    "sections": [
      {
        "heading": "Program Overview",
        "paragraphs": ["This program combines business and IT..."],
        "tables": [
          {
            "rows": [
              { "Degree": "Master of Science" },
              { "Duration": "4 semesters" }
            ]
          }
        ]
      }
    ]
  }
]
```

## How to Run

```bash
python3 study_program_JSON_normalizer.py <input.json> <output.json>

```

Example:

```bash
python3 study_program_JSON_normalizer.py study_program_url_and_html_content.json study_program_webpages.json
```
