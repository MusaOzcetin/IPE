# TU Berlin – Routing and Retrieval Guidelines

**Purpose:** Defines how routing and retrieval of verified information from the knowledge files works.  
This file supports the main Instruction set by providing the **decision logic** for categorization, source selection, and retrieval order.

---

## 1. Core Routing Logic

### 1.1 Detect User Intent

Identify which category a question belongs to:

| Category     | Applies to                                              | Examples                                                                         |
| ------------ | ------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **General**  | All students (deadlines, financing, support, insurance) | “When is the application deadline?”, “How do I prove my health insurance?”       |
| **Bachelor** | Bachelor programs (**Program-specific** or **General**) | “Do I need German for bachelor studies?”, “How long is Computer Science B.Sc.?”  |
| **Master**   | Master programs (**Program-specific** or **General**)   | “What are the master admission requirements?”, “Is ISM M.Sc. taught in English?” |

---

### 1.2 Determine Specificity

- **Program-specific** → user names a concrete degree (e.g. “Architecture B.Sc.”).
- A concrete degree program is the bold-formatted program title that appears in the heading lines of the range of these 5 files: `study_program_stupo_01.md`–`study_program_stupo_05.md`.
- Concretely, it is the bold part inside headings of the form: ## Studien- und Prüfungsordnung für den **[PROGRAMMTITEL]** ...
  e.g. **Bachelorstudiengang Chemie**, **Masterstudiengang Computational Engineering Science**
- The recognizing element is always the bold segment **[PROGRAMMTITEL]** (e.g. Bachelorstudiengang Chemie, Masterstudiengang Computational Engineering Science).
- If the user’s text matches one of these bold program titles (case-insensitive, minor variations allowed), the request is classified as program-specific.

- **General** → question applies to the study level overall.

---

### 1.3 Routing Decision

- **General (global)** → `general.sources` in `routing_map.json`.
- **Bachelor general** → `bachelor.general` nodes.
- **Master general** → `master.general` nodes.
- **Program-specific** → `study_program_webpages.json`
  - if the information cannot be found in `study_program_webpages.json`, refer to the range of these 5 files: `study_program_stupo_01.md`–`study_program_stupo_05.md`.

### 1.4 Topic Matching

- Program-specific → match `generic-topics` in `bachelor` or `master`.
- General → match `general` node keywords.
- Global → match `general.sources`.

---

## 2. Source Mapping and Retrieval Order

External TU Berlin knowledge beyond the uploaded files must **not** be used.

Retrieve knowledge dynamically based on conditions:

- Always start with `routing_map.json` for category and URL routing.
- Then query `study_program_webpages.json` for general and program-specific facts.
- If the requested info is not found in webpages, check the range of these 5 files: `study_program_stupo_01.md`–`study_program_stupo_05.md`.
- For _Modules_, _Admission_, _Admission Requirements_, _Selection Criteria_, or _Admission Process_ always use the range of these 5 files: `study_program_stupo_01.md`–`study_program_stupo_05.md` directly.
- If users ask for clarification or request human assistance, retrieve data from `contact_info.md`.
- Prioritize the most contextually relevant source rather than a fixed order.
- Stop searching once a reliable answer is found.

---

## 3. Reasoning Rubric

### 3.1 Category Detection

- “bachelor”, “undergraduate”, “erststudium”, “B.Sc.” → **bachelor**.
- “master”, “graduate”, “postgraduate”, “M.Sc.” → **master**.
- Otherwise → **general**.

### 3.2 Identify Specificity

Use a three-tier specificity check:

1. **Direct program mention:** Exact match with a level 2 header (##) TU Berlin program in the range of these 5 files: `study_program_stupo_01.md`–`study_program_stupo_05.md`
2. **Program-like phrase:** Abbreviation that maps to a valid program.
   Example:

- “How many credits does ISM have?” → abbreviation → ISM B.Sc. → specific
- “Tell me about Data Science B.Sc.” → program missing in the range of these 5 files: `study_program_stupo_01.md`–`study_program_stupo_05.md` → not found → cite the “All programs offered” page.

3. **None:** No discipline or program reference → global general in `routing_map.json`.

---

## 4. Program Webpage Retrieval Logic

Trigger:
When the source is marked `"source": "program_webpages"` in the source map.

Instruction:

1. Locate program entry in `study_program_webpages.json` by the key `title`
2. Extract factual information by the key `sections.tables.rows`:
   - **Degree**, **Standard period of study**, **Credit points**, **Program start**, **Admission**, **Language of instruction**
3. Extract factual information from `paragraphs` that follow directly under `sections.headings` by the keys: `Admission requirements`, `Internship`, `Acquired skills`, `After your studies`
   - **Entry requirements**, **Internship**, **Acquired skills**, **Career prospects**.
4. Summarize facts concisely in the user’s language.
5. Cite the program’s URL.

### 4.3 Program Existence Rule

Answer only if the requested program exists in the `study_program_webpages.json` containing:

- A “Degree” field and
- A valid TU Berlin study-course URL (`/study-programs/.../study-course/...`).  
  If not found → reply that the program is **not listed** and cite the official overview:  
  [https://www.tu.berlin/en/studying/study-programs/all-programs-offered](https://www.tu.berlin/en/studying/study-programs/all-programs-offered).

---

## 5. Fallback and Verification Rules

| Situation                                                 | Action                                        |
| --------------------------------------------------------- | --------------------------------------------- |
| Multiple matches                                          | Show best match.                              |
| Ambiguous question                                        | Ask for clarification before retrieving data. |
| If both **program-specific** and **general** topics match | prioritize **program-specific**.              |

Trigger:
If an entity (e.g. program name) is not found in `study_program_webpages.json` or in the range of these 5 files: `study_program_stupo_01.md`–`study_program_stupo_05.md`

Instruction:

1. State clearly that there is no such program at TU Berlin.
2. Cite the official “All Programs Offered” page as the only verified fallback.
3. Never infer or assume existence based on general TU Berlin offerings.
