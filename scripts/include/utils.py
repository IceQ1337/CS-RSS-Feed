import locale
import os
import sys
from datetime import datetime

import feedparser
from feedgen.feed import FeedGenerator
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# List of languages to fetch and parse
LANGUAGE_MAP = {"english": ("en", "en_US"), "german": ("de", "de_DE")}


def create_chrome_driver() -> webdriver.Chrome:
    """Initialize and return a headless Chrome WebDriver."""

    options = Options()
    options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        sys.exit(f"Failed to initialize the headless web browser: {e}")


def fetch_page_content(
    driver: webdriver.Chrome, url: str, selector: str, timeout=15
) -> str:
    """Load the page and wait for the specified selector to appear, then return the HTML content."""

    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        html_content = driver.page_source

        return html_content
    except TimeoutException:
        driver.quit()
        sys.exit("Unable to find the container in the given time frame.")
    except Exception as e:
        driver.quit()
        sys.exit(f"Failed to extract the HTML data: {e}")


def get_date_format(language_locale: str) -> str:
    """Return the date format used by the website based on the locale."""

    # Dates are currently not localized, so we just use English (Thanks Valve)
    # Switch to language_locale after it's fixed (if ever)

    # English
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
    date_format = "%B %d, %Y"

    # German
    # locale.setlocale(locale.LC_TIME, "de_DE")
    # date_format = "%d. %B %Y"

    return date_format


def cleanup_text_description(desc: str) -> str:
    """Cleanup the description text by removing specific markup."""

    # Remove trailing <br/> tags at the beginning of the description
    while desc.startswith("<br"):
        index = desc.index(">") + 1
        desc = desc[index:]

    return desc.strip()


def get_feed_file_path(feed_name: str) -> str:
    """Return the path to the feed file based on the environment."""

    github_workspace = os.getenv("GITHUB_WORKSPACE")

    if github_workspace:
        return os.path.join(github_workspace, "feeds", feed_name)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "..", "..", "feeds", feed_name)


def is_feed_up_to_date(feed_file_path: str, guid: str) -> bool:
    """Check if the current feed is up to date by comparing the latest GUID."""

    if not os.path.exists(feed_file_path):
        return False

    current_feed = feedparser.parse(feed_file_path)
    current_entries = current_feed.entries if current_feed.entries else []

    if not current_entries:
        return False

    return current_entries[0].guid == guid


def update_rss_feed(
    file_path: str,
    feed_link: str,
    source_url: str,
    title: str,
    description: str,
    language_code: str,
    items: list[dict],
) -> None:
    """Create or update the RSS feed with the provided items."""

    fg = FeedGenerator()
    fg.id(feed_link)
    fg.title(title)
    fg.description(description)
    fg.link(href=feed_link, rel="self")
    fg.language(language_code)

    for item in reversed(items):
        fe = fg.add_entry()
        fe.source(source_url)

        if "url" in item:
            fe.id(item["url"])

        fe.guid(item["guid"])
        fe.title(item["title"])
        fe.link(
            {
                "href": item["url"] if item.get("url") else source_url,
                "rel": "alternate",
                "type": "text/html",
                "hreflang": language_code,
                "title": item["title"],
            }
        )
        fe.pubDate(datetime.strftime(item["date"], "%Y-%m-%dT%H:%M:%SZ"))
        fe.author(
            {"name": "Valve Corporation", "email": "support@steampowered.com"}
        )
        fe.content(item["content"], None, "CDATA")
        fe.rights("Valve Corporation")

    rss_content = fg.rss_str(pretty=True)

    with open(file_path, "wb") as f:
        f.write(rss_content)
