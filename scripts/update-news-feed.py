import sys
from datetime import datetime

from bs4 import BeautifulSoup
from include.utils import (
    LANGUAGE_MAP,
    cleanup_text_description,
    create_chrome_driver,
    fetch_page_content,
    get_date_format,
    get_feed_file_path,
    is_feed_up_to_date,
    update_rss_feed,
)

base_url = "https://www.counter-strike.net"
content_url = base_url + "/news"

driver = create_chrome_driver()

for language_name, (language_code, language_locale) in LANGUAGE_MAP.items():
    url = f"{content_url}?l={language_name}"
    html_content = fetch_page_content(
        driver, url, 'div[class^="blogoverviewpage_SubEntries"]'
    )

    soup = BeautifulSoup(html_content, "html.parser")
    capsules = soup.select('a[class*="blogcapsule_BlogCapsule"]')

    date_format = get_date_format(language_locale)
    news_items: list[dict] = []

    for capsule in capsules:
        unique_relative_url = capsule.get("href")

        if not unique_relative_url or type(unique_relative_url) is not str:
            continue

        if not unique_relative_url.startswith("/newsentry/"):
            continue

        unique_url = f"{base_url}{unique_relative_url}?l={language_name}"
        unique_identifier = unique_relative_url.replace("/newsentry/", "")

        news_html_content = fetch_page_content(
            driver, unique_url, 'div[class^="blogentrypage_BlogEntryPage"]'
        )

        news_soup = BeautifulSoup(news_html_content, "html.parser")
        news_page = news_soup.select_one(
            'div[class*="blogentrypage_BlogEntryPage"]'
        )

        if not news_page:
            continue

        title_div = news_page.select_one('div[class*="blogentrypage_Title_"]')
        date_div = news_page.select_one('div[class*="blogentrypage_Date"]')
        body_div = news_page.select_one('div[class*="blogentrypage_Body"]')

        if not title_div or not date_div or not body_div:
            continue

        title = title_div.getText().strip()
        date = datetime.strptime(date_div.getText().strip(), date_format)
        body = cleanup_text_description(body_div.decode_contents().strip())

        news_items.append(
            {
                "guid": unique_identifier,
                "url": unique_url,
                "title": title,
                "date": date,
                "content": body,
            }
        )

    if not news_items:
        continue

    rss_feed_file = get_feed_file_path(f"news-feed-{language_code}.xml")

    if is_feed_up_to_date(rss_feed_file, news_items[0]["guid"]):
        continue

    try:
        update_rss_feed(
            rss_feed_file,
            f"https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-{language_code}.xml",
            url,
            f"Counter-Strike 2 - News ({language_name.capitalize()})",
            "Counter-Strike 2 News Feed",
            language_code,
            news_items,
        )
    except Exception as e:
        print(f"Error updating RSS feed for {language_name}: {e}")
        continue

driver.quit()
sys.exit(0)
