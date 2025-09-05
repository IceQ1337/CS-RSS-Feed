import sys
from datetime import datetime

import requests

from include.constants import API_URL, LANGUAGE_MAP
from include.types import EventType, FeedItem, LanguageItem
from include.utils import (
    cleanup_text_description,
    get_feed_file_path,
    is_feed_up_to_date,
    update_rss_feed,
)


def fetch_events(language: str) -> dict:
    print(f"Fetching events for language: {language}")

    params = {
        "clan_accountid": 0,
        "appid": 730,
        "offset": 0,
        "count": 100,
        "l": language,
        "origin": "https://www.counter-strike.net",
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()


def extract_feed_items(events_data: dict) -> list:
    print("Extracting feed items from events data...")

    items = []
    events = events_data.get("events", [])

    for event in events:
        feed_item = parse_event(event)
        if feed_item:
            items.append(feed_item)

    return items


# entries may be missing data, so we're wrapping this in a custom parser...
def parse_event(event: dict) -> FeedItem | None:
    try:
        announcement_body: dict = event.get("announcement_body")  # type: ignore

        if not announcement_body:
            return None

        guid: str = event.get("gid")  # type: ignore
        event_type: int = event.get("event_type")  # type: ignore
        updatetime: int = announcement_body.get("updatetime")  # type: ignore
        headline: str = announcement_body.get("headline")  # type: ignore
        body: str = announcement_body.get("body")  # type: ignore

        # TODO: "language" may indicate if a post was translated or not. I wasn't able to
        # verify this yet, but if it does, we could filter out untranslated posts.
        language: int = announcement_body.get("language")  # type: ignore

        if (
            not all([guid, event_type, updatetime, headline, body])
            or language is None
        ):
            return None

        item: FeedItem = {
            "guid": guid,
            "event_type": event_type,
            "updatetime": updatetime,
            "headline": headline,
            "language": language,
            "body": body,
            "url": (
                f"https://www.counter-strike.net/newsentry/{guid}"
                if event_type == EventType.NEWS.value
                else f"https://www.counter-strike.net/news/updates"
            ),
        }

        return item

    except Exception as e:
        print(f"Error extracting feed item from event: {e}")
        return None


def refresh_news_feed(language: LanguageItem, news_items: list[FeedItem]):
    print(
        f"Refreshing news feed for language: {language['lang']} ({language['code']})"
    )

    if not news_items:
        print("No news items to process.")
        return

    rss_file_name = f"news-feed-{language["code"]}.xml"
    rss_file_path = get_feed_file_path(rss_file_name)

    if is_feed_up_to_date(rss_file_path, news_items[0]):
        print("Feed is up to date.")
        return

    try:
        update_rss_feed(
            rss_file_path,
            f"https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-{language["code"]}.xml",
            f"Counter-Strike 2 - News ({language["lang"].capitalize()})",
            "Counter-Strike 2 News Feed",
            language,
            news_items,
        )
    except Exception as e:
        print(f"Failed to update RSS feed: {e}")
        return


def refresh_updates_feed(language: LanguageItem, update_items: list[FeedItem]):
    print(
        f"Refreshing update feed for language: {language['lang']} ({language['code']})"
    )

    if not update_items:
        print("No update items to process.")
        return

    rss_file_name = f"updates-feed-{language["code"]}.xml"
    rss_file_path = get_feed_file_path(rss_file_name)

    if is_feed_up_to_date(rss_file_path, update_items[0]):
        print("Feed is up to date.")
        return

    try:
        update_rss_feed(
            rss_file_path,
            f"https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-{language["code"]}.xml",
            f"Counter-Strike 2 - Updates ({language["lang"].capitalize()})",
            "Counter-Strike 2 Updates Feed",
            language,
            update_items,
        )
    except Exception as e:
        print(f"Failed to update RSS feed: {e}")
        return


def main():
    for language in LANGUAGE_MAP:
        lang = language["lang"]
        code = language["code"]

        print(f"Processing language: {lang} ({code})")

        try:
            events_data = fetch_events(lang)
        except Exception as e:
            print(f"Failed to fetch events for language {lang}: {e}")
            continue

        feed_items = extract_feed_items(events_data)

        if not feed_items:
            print(f"No feed items found for language {lang}. Skipping.")
            continue

        news_items = [
            item
            for item in feed_items
            if item["event_type"] == EventType.NEWS.value
        ]
        update_items = [
            item
            for item in feed_items
            if item["event_type"] == EventType.UPDATE.value
        ]

        print(
            f"Found {len(news_items)} news items and {len(update_items)} update items for language {lang}."
        )

        if not news_items and not update_items:
            print(f"No news or update items for language {lang}. Skipping.")
            continue

        refresh_news_feed(language, news_items)
        refresh_updates_feed(language, update_items)


if __name__ == "__main__":
    main()
