# TU Berlin – Routing and Retrieval Guidelines

**Purpose:** This document defines the **precise decision logic** for categorizing user queries, resolving program names, and selecting the correct source file or URL from the knowledge base (based on the provided JSON map).

---

## I. Core Instructions and Categorization

1.  **Analyze Intent:** Analyze the user's entire query to determine the primary academic level and core topic of interest. If the intent is unclear, ask for clarification.
2.  **Determine Primary Category (Level):**
    * Match keywords against the **`detect_keywords`** lists in **`general`**, **`bachelor`**, and **`master`**.
    * **Priority Rule (Specific over General):**
        * If the query explicitly names a study level (e.g., "**Master** application"), use that level (**`master`**).
        * If the query explicitly names a specific **Program** (e.g., "**Computer Science**"), infer the level based on the context (e.g., "CS **BSc**") or by checking the **`aliases`** list within both `bachelor` and `master` to find the canonical program slug.
        * If the query is generic and matches only `general` keywords (e.g., "visa," "finance," "deadlines"), use **`general`**.
        * If keywords match **multiple categories**, route to the **most specific category mentioned or implied** (e.g., "language requirements for **Master**" $\rightarrow$ **`master.general`**).

---

## II. Routing to Specific Sources

Once the primary category is determined, follow the precise steps below to find the specific topic node and source material.

### A. General Questions (`general`)

1.  **Match Topic:** Match the user's keywords against the **`keywords`** of every topic node under **`general.sources`**.
2.  **Retrieval Action:** Provide the **`url`** as the official source and inform the user to find the latest information there. Do NOT attempt to summarize the information or provide your own knowledge. 
---

### B. Program-Specific Questions (`level.programs`)

This handles questions specific to a named study program.

1.  **Identify Program-Generic Topic:**
    * Match the remaining keywords against the **`keywords`** in `level.programs.generic-topics`.
2.  **Identify Program and Level:**
    For a given study program name (e.g., 'Aeronautics and Astronautics'), find the corresponding JSON object in `study_program_webpages.json` by matching the program name and level against the object's `title` field.
3.  **Source Retrieval and Action:**
    * Perform the precise **`action`** defined in the matching topic node.
    * **StuPo files:** If the topic is `stupo`, use the program name from step 2 to select the StuPo file by alphabetical range. Match the first letter of the program name to the file range. 
        Example: Bauingenieurwesen, B.Sc. is in the file `[Arbeitslehre (A) TO Computational Neuroscience (C)] study_program_stupos_01.md`.
    * The relevant program section is derived from the bold part of the following header patterns found in the StuPos: 
        - `## Studien- und Prüfungsordnung für den konsekutiven Masterstudiengang [Program]`
        - `## Neufassung der Studien- und Prüfungsordnung für den Masterstudiengang [Program]`
        - `### Studienordnung für den internationalen Masterstudiengang [Program]`
        - `## Studien- und Prüfungsordnung für den gemeinsamen/internationalen/weiterbildenden Masterstudiengang [Program]`
    * Extract factual information.

---

### C. Level-General Questions (`level.general`)

This handles application, admission, or general level-specific policies.

1.  **Identify Topic Node:** Match the user's keywords against the topics under `level.general` (e.g., `admission-requirements`, `application`, `enrollment`).
2.  **Identify Program and Level:**
    For a given study program name (e.g., 'Aeronautics and Astronautics'), find the corresponding JSON object in `study_program_webpages.json` by matching the program name and level against the object's `title` field.
3.  **Retrieval Action:** Provide the **`url`** as the official source and inform the user to find the latest information there. Do NOT attempt to summarize the information or provide your own knowledge. 

---

## III. Edge Cases and Fallback

* **Program Ambiguity:** If a program is named without a level, check both `bachelor` and `master` aliases. If matches exist in *both*, **ask the user to clarify** (BSc or MSc?).
* **Unclear Program/Alias:** If no match is found for a program name, inform the user the program may not be offered or the name/slug is incorrect.
* **No Match/Insufficient Data:** If the query is clear but cannot be matched to a keyword, or the source does not contain the answer, state clearly that the information is **not available**. **Do NOT fabricate an answer.**