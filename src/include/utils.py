import os
from datetime import datetime, timezone

import feedparser
from feedgen.feed import FeedGenerator

from .constants import PUB_DATE_FORMAT
from .types import EventType, FeedItem, LanguageItem


# TODO: Figure out what we need to clean up here with the new data source.
# We basically need to conver the entire "markdown"-ish body with all the tags
def cleanup_text_description(desc: str) -> str:
    """Cleanup the description text by removing specific markup."""
    return desc.strip()


def get_feed_file_path(feed_name: str) -> str:
    """Return the path to the feed file based on the environment."""

    github_workspace = os.getenv("GITHUB_WORKSPACE")

    if github_workspace:
        return os.path.join(github_workspace, "feeds", feed_name)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "..", "..", "feeds", feed_name)


def is_feed_up_to_date(feed_file_path: str, feed_item: FeedItem) -> bool:
    """Check if the current feed is up to date based on the latest event."""

    if not os.path.exists(feed_file_path):
        return False

    current_feed = feedparser.parse(feed_file_path)
    current_entries = current_feed.entries if current_feed.entries else []

    if not current_entries:
        return False

    latest_entry = current_entries[0]

    if latest_entry.guid != feed_item["guid"]:
        return False

    oldPubDate = latest_entry.get("published")

    if not oldPubDate:
        return False

    date = datetime.fromtimestamp(feed_item["updatetime"])
    newPubdate = datetime.strftime(date, PUB_DATE_FORMAT)

    return oldPubDate == newPubdate


def update_rss_feed(
    file_path: str,
    feed_link: str,
    title: str,
    description: str,
    language: LanguageItem,
    items: list[FeedItem],
) -> None:
    """Create or update an RSS feed with the provided feed items."""

    fg = FeedGenerator()
    fg.id(feed_link)
    fg.title(title)
    fg.description(description)
    fg.link(href=feed_link, rel="self")
    fg.language(language["code"])

    for item in reversed(items):
        fe = fg.add_entry()
        fe.source(item["url"])

        if "url" in item:
            fe.id(item["url"])

        fe.guid(item["guid"])
        fe.title(item["headline"])
        fe.link(
            {
                "href": (
                    item["url"]
                    if item["event_type"] == EventType.NEWS.value
                    else f"{item["url"]}?l={language["lang"]}"
                ),
                "rel": "alternate",
                "type": "text/html",
                "hreflang": language["code"],
                "title": item["headline"],
            }
        )

        date = datetime.fromtimestamp(item["updatetime"], tz=timezone.utc)
        fe.pubDate(datetime.strftime(date, PUB_DATE_FORMAT))
        fe.author(
            {"name": "Valve Corporation", "email": "support@steampowered.com"}
        )
        fe.content(item["body"], None, "CDATA")
        fe.rights("Valve Corporation")

    rss_content = fg.rss_str(pretty=True)

    with open(file_path, "wb") as f:
        f.write(rss_content)
