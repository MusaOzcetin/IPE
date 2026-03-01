# study_program_webpage_content_downloader.py

# Import dependencies
# ---------------------------------------
import json
import time
import requests
from urllib.parse import urlparse, urljoin
import urllib.robotparser
from bs4 import BeautifulSoup  # install with: pip install beautifulsoup4


# Helper functions
# ---------------------------------------
def fetch_robots_parser(base_url, user_agent="*"):
    """
    Downloads and parses the site's robots.txt file.
    """
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        print(f"Warning: could not read robots.txt at {robots_url}: {e}")
    return rp


def is_url_allowed(rp, user_agent, url):
    """
    Checks whether the robots.txt rules allow crawling this URL.
    """
    return rp.can_fetch(user_agent, url)


def get_crawl_delay(rp, user_agent, default_delay=1.0):
    """
    Checks if robots.txt specifies a “crawl-delay” for this crawler.
    If not, uses a default delay between requests.
    """
    try:
        delay = rp.crawl_delay(user_agent)
    except Exception:
        delay = None
    if delay is None:
        return default_delay
    try:
        return float(delay)
    except ValueError:
        return default_delay


def extract_links(html, base_url):
    """
    Uses BeautifulSoup to find all <a href="…"> links in the HTML.
    Then converts them to absolute URLs and removes fragments (#…).
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        abs_url = urljoin(base_url, href)  # make absolute
        abs_url = abs_url.split("#")[0]  # remove any fragment
        links.append(abs_url)
    return links


def read_urls_from_file(file_path):
    """
    Reads a simple text file, one URL per line,
    and returns them as a list of strings.
    """
    urls = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            urls.append(line)
    return urls


# Crawling and saving logic
# ---------------------------------------


def crawl(
    urls,
    output_file,
    user_agent="MyCrawler/1.0",
    max_pages=100,
    default_delay=1.0,
):
    """
    Reads a text file containing a list of input URLs
        "study_program_urls.txt" and crawls the URLs
    Writes a single JSON file:
        "study_program_url_and_html_content.json" which contains:
            - URL of each page
            - full HTML of each page
    """
    if not urls:
        print("No input URLs provided. Exiting.")
        return

    # Use the domain of the first URL to stay on the same website
    parsed0 = urlparse(urls[0])
    base_domain = parsed0.netloc

    # Get robots.txt rules for this domain
    rp = fetch_robots_parser(urls[0], user_agent=user_agent)
    delay = get_crawl_delay(rp, user_agent, default_delay)
    print(f"Using crawl delay: {delay} seconds")

    visited = set()
    to_visit = list(urls)
    results = []

    count = 0
    while to_visit and count < max_pages:
        url = to_visit.pop(0)

        # Avoid revisiting the same page
        if url in visited:
            continue
        visited.add(url)

        # Check robots.txt for permission
        if not is_url_allowed(rp, user_agent, url):
            print(f"Skipping disallowed by robots.txt: {url}")
            continue

        # Fetch the HTML content
        try:
            print(f"Fetching ({count + 1}/{max_pages}): {url}")
            headers = {"User-Agent": user_agent}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        # Add this page’s URL + HTML to results
        results.append({"url": url, "html": html})

        count += 1

        # Extract all inner page links and queue same-domain ones
        for link in extract_links(html, url):
            try:
                parsed_link = urlparse(link)
                if parsed_link.netloc == base_domain and link not in visited:
                    to_visit.append(link)
            except Exception:
                pass

        # Respect crawl-delay between requests
        time.sleep(delay)

    # Write all results to a single JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(
        f"Crawling finished. Visited {count} pages. Output in '{output_file}'"
    )


# Entry point
# ---------------------------------------

if __name__ == "__main__":
    INPUT_FILE = "./study_program_urls.txt"  # source URLs (one per line)
    OUTPUT_FILE = "./study_program_url_and_html_content.json"

    # Read starting URLs from text file
    start_urls = read_urls_from_file(INPUT_FILE)

    # Run the crawler
    crawl(start_urls, OUTPUT_FILE)
