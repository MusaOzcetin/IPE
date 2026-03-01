"""
This script collects study-program URLs from TU Berlin's paginated "All programs offered" pages.

What it does:
- You manually provide a list of 10 page URLs (the paginated list of pages).
- For each page:
  - Downloads the HTML
  - Parses it
  - Finds all <a> (link) tags
  - Keeps only those whose href contains "study-course"
- Saves all unique program URLs to a text file (one link per line)
"""

# Import dependencies
# requests = library that lets Python download web pages (HTTP requests)
# BeautifulSoup = tool to parse (read) HTML and let us search it easily
import requests
from bs4 import BeautifulSoup


# 1) Input: the list of pages.
# You need to MANUALLY PASTE the URLs here
# ----------------------------------------------------------
# These are the (currently) 10 pages that contain the study-program listings.
# NOTE: page 1 is the base URL without "/1" at the end.
pages = [
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/2",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/3",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/4",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/5",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/6",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/7",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/8",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/9",
    "https://www.tu.berlin/en/studying/study-programs/all-programs-offered/10",
]

# 2) Output
# ----------------------------------------------------------
# This is the file that will be created (or overwritten if it already exists).
output_file = "study_program_urls.txt"

# 3) Storage for results
# ----------------------------------------------------------
# Since sometimes the same program link may appear more than once we use a "set" instead of a "list" to avoid duplicates.
all_program_links = set()


# 4) Loop over each page URL. Go through one page at a time, download it, and extract links.
# ----------------------------------------------------------
for page_url in pages:
    # Print progress so the user can see what is happening
    print("Now downloading:", page_url)

    # 4a) Download the page using the HTTP GET method
    # ------------------------------------
    # requests.get() sends a request to the website and returns a "response" object.
    # response contains:
    # - response.status_code (200 means OK)
    # - response.text (the HTML content as a string)
    try:
        response = requests.get(page_url)
    except requests.RequestException as e:
        # This catches errors like:
        # - no internet
        # - DNS issues
        # - connection errors
        print("ERROR: Could not reach the page:", page_url)
        print("Reason:", e)
        continue  # skip this page and go to the next one

    # 4b) Check the HTTP status code
    # ------------------------------------
    # If the status code is not 200, something went wrong (404, 500, etc.)
    if response.status_code != 200:
        print("WARNING: Could not download:", page_url)
        print("HTTP status code:", response.status_code)
        continue  # skip this page and go to the next one

    # 4c) Parse the HTML using BeautifulSoup
    # ------------------------------------
    # BeautifulSoup takes raw HTML text and turns it into a searchable structure (a parse tree).
    soup = BeautifulSoup(response.text, "html.parser")

    # 4d) Find all <a> tags
    # ------------------------------------
    # soup.find_all("a") returns a list of all <a> elements on the page.
    links = soup.find_all("a")

    # 4e) Inspect each <a> tag and keep the ones we want
    # ------------------------------------
    for link in links:
        # Get the href attribute from the <a> tag.
        # If the <a> tag does not have href, .get("href") returns None.
        href = link.get("href")

        # We only want program pages.
        # Program URLs contain: ".../study-course/<program-name>"
        # So we filter by checking if "study-course" exists inside the href.
        if href and "study-course" in href:
            # Some websites use "relative links" like:
            #   /en/studying/study-programs/...
            # instead of full links like:
            #   https://www.tu.berlin/en/studying/study-programs/...
            #
            # If it starts with "/", it is relative, so we add the domain.
            if href.startswith("/"):
                href = "https://www.tu.berlin" + href

            # Add to the set (duplicates will automatically be ignored)
            all_program_links.add(href)

# 5) Save results to the .txt file declared in the beginning
# ----------------------------------------------------------
# Write the links to the output file and sort them so the file is consistent and easy to read.
with open(output_file, "w", encoding="utf-8") as f:
    for link in sorted(all_program_links):
        f.write(link + "\n")

# Final message: number of links found and where they were saved
print("Done!")
print("Total unique links found:", len(all_program_links))
print("Saved to file:", output_file)
