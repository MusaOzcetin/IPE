"""
extract_study_programs.py

This script takes as input a JSON file containing study program webpages.
Each entry in the JSON must contain:
    - "url": the webpage URL
    - "html": the full HTML content of that webpage

The script extracts structured information from each HTML page:
    - The URL (unchanged)
    - The H1 title (study program name)
    - All H2 sections
        - Paragraphs belonging to each H2
        - Tables belonging to each H2 (converted to key-value JSON format)

It then saves a new cleaned JSON file without the full HTML.
"""

# Import dependencies
import json
import sys
from bs4 import BeautifulSoup


# Extraction Logic
# -------------------------------------------------
def simplify_item(item):
    """
    Extracts structured content from a single study program entry.

    Parameters:
        item (dict): A dictionary with keys:
            - "url"
            - "html"

    Returns:
        dict: A cleaned dictionary containing:
            - url
            - title (H1 content)
            - sections (H2 headings with paragraphs and tables)
    """

    # Extract the URL directly (no modification required)
    url = item["url"]

    # Parse the HTML content using BeautifulSoup
    # This converts raw HTML text into a navigable tree structure
    soup = BeautifulSoup(item["html"], "html.parser")

    # 1. Extract the H1 title
    # -------------------------
    # The H1 tag contains the study program name
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else None

    # This list will contain all extracted H2 sections
    sections = []

    # 2. Extract all H2 sections
    # -------------------------
    for h2 in soup.find_all("h2"):
        # Get clean text of the H2 heading
        heading = h2.get_text(" ", strip=True)

        # Create lists to store content belonging to this H2
        paragraphs = []
        tables = []

        # Avoid processing the same table multiple times
        seen_tables = set()

        # Move forward through the HTML after the H2 until we reach the next H2.
        # This ensures we only collect content that belongs to the current section.
        for element in h2.next_elements:
            # Stop when we reach the next H2
            if getattr(element, "name", None) == "h2" and element is not h2:
                break

            # Skip non-tag elements (like plain text nodes)
            if not hasattr(element, "name"):
                continue

            # 2a️ Extract paragraphs
            # -------------------------
            if element.name == "p":
                text = element.get_text(" ", strip=True)
                if text:
                    paragraphs.append(text)

            # 2b️ Extract tables
            # -------------------------
            elif element.name == "table" and id(element) not in seen_tables:
                # Mark table as processed
                seen_tables.add(id(element))

                rows_json = []

                # Process each table row
                # Assuming typical layout:
                # <tr>
                #   <th>Label</th>
                #   <td>Value</td>
                # </tr>
                for tr in element.find_all("tr"):
                    th = tr.find("th")
                    td = tr.find("td")

                    if th and td:
                        key = th.get_text(" ", strip=True)
                        value = td.get_text(" ", strip=True)

                        if key:
                            rows_json.append({key: value})

                # Only add table if it contains useful rows
                if rows_json:
                    tables.append({"rows": rows_json})

        # Store structured section
        sections.append(
            {"heading": heading, "paragraphs": paragraphs, "tables": tables}
        )

    # Final cleaned structure for one study program
    return {"url": url, "title": title, "sections": sections}


def main(input_path, output_path):
    """
    Main execution function.

    Parameters:
        input_path (str): Path to input JSON file
        output_path (str): Path where cleaned JSON will be saved
    """

    # Load the original JSON file
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Apply simplify_item() to every study program
    simplified_all = [simplify_item(item) for item in data]

    # Save cleaned JSON to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(simplified_all, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully processed {len(simplified_all)} study programs.")
    print(f"📁 Output written to: {output_path}")


# Script entry point
# -------------------------------------------------
if __name__ == "__main__":
    # The script expects exactly 2 command-line arguments:
    # 1) input JSON file
    # 2) output JSON file

    if len(sys.argv) != 3:
        print("Usage:")
        print("python study_program_JSON_normalizer.py input.json output.json")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
