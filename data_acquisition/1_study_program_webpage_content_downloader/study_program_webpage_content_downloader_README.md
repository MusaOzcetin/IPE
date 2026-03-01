# TU Berlin Study Program Webpage Content Downloader

## Overview
This is a simple HTML downloader (web crawler and scraper) written in python that reads a list of URLs from a text file, crawls each page and saves the HTML content of each page into a single JSON file.

## Functionality

The script lets you download the webpage of each of TU Berlin's study program starting from a list of study program URLs that are passed as input in a txt file.

- Reads one URL per line from an input text file called "study_program_urls.txt" (which was created in the previous step via the utilization of the TU Berlin study program URL extractor script, see parent directory).
- Downloads the HTML of each URL found in the input text file.
- Stores **only the URL and HTML content** of each visited page in a JSON file that generates as output.

### Additionally

- Respects site rules using `robots.txt`
- Whaits between requests if required
- Only crawls pages of the same domain

## Files

```
study_program_webpage_content_downloader/
├── study_program_webpage_content_downloader.py
├── study_program_urls.txt
├── study_program_url_and_html_content.json
└── study_program_webpage_content_downloader_README.md
```

Where:

- **`study_program_webpage_content_downloader.py`** the main python downloader script.
- **`study_program_urls.txt`** the text file generated in the previous step (study program URL extraction process, see parent directory) with one URL per line.
- **`study_program_url_and_html_content.json`** the output JSON with the downloaded pages.
- **`study_program_webpage_content_downloader_README.md`** this documentation.

## Requirements

- Python 3 installed (already from previous step)
- packages such as`requests` and `BeautifulSoup` (were installed in the previous step)
- packages such as `json`, `time`

## Important Notes

- The script continues crawling and downloading until:
  - there are no more pages to visit
  - or the value of the variable `max_pages`, set at the beginning of the crawling logic, is reached. For experimentation purposes, you can limit the number of pages the downloader visits. You can do this **MANUALLY** by changing the value of `max_pages`. The default is set arbitrarily to 100 BUT in our use case, the TU Berlin URLs are more than that (currently 143) and are equal to the number of the URLs in the txt input file (`study_program_urls.txt`). So please **MAKE SURE** you do not limit the the crawler to less than the number of URLs in that txt once you are done experimenting and want to have the final result. if you do so, you will not download all the study programs in the output JSON.

- You can adjust the crawling delay to avoid overloading tha TU Berlin server by adjusting the variable `default_delay` (also to be found right under the `max_pages` one).

## How to Run

In your terminal navigate to the folder containing the crawler script:

```bash
cd path/to/your/study_program_webpage_content_downloader.py
```

The txt file containing the URls `study_program_urls.txt` is generated in the previous step (see README of the extractor documentation) and lists one study program URL per line, for example:

```txt
https://www.tu.berlin/
https://www.example.org/about
...
```

This input file needs to be at the same directory as the current downloader script.

Run:

```bash
python study_program_webpage_content_downloader.py
```

or if you have both Python 2 and 3 installed, then run:

```bash
python3 study_program_webpage_content_downloader.py
```

## Output

The script creates:

`study_program_url_and_html_content.json`

This output file contains an array of saved pages, where each entry has a URL and the complete HTML content of that URL:

```
{
  "url": "https://www.example.org/page",
  "html": "<!DOCTYPE html> ... page source ..."
}
```

## Troubleshooting

### If you get a message such as

`Python not found`

- Ensure Python is installed and added to your `PATH`.

### If you get a message such as

`ImportError`

- make sure you have installed the required dependencies (e.g.`requests`, `beautifulSoup4`) as already instructed in the previous step (URL extractor script) before.

- If not then run:

  ```bash
  pip install requests beautifulSoup4
  ```
