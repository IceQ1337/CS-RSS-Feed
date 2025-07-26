import hashlib
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
content_url = base_url + "/news/updates"

driver = create_chrome_driver()

for language_name, (language_code, language_locale) in LANGUAGE_MAP.items():
    url = f"{content_url}?l={language_name}"
    html_content = fetch_page_content(
        driver, url, 'div[class^="blogoverviewpage_SubUpdates"]'
    )

    soup = BeautifulSoup(html_content, "html.parser")
    capsule_divs = soup.select('div[class*="updatecapsule_UpdateCapsule"]')

    date_format = get_date_format(language_locale)
    updates: list[dict] = []

    for capsule in capsule_divs:
        title_div = capsule.select_one('div[class*="updatecapsule_Title"]')
        date_div = capsule.select_one('div[class*="updatecapsule_Date"]')
        desc_div = capsule.select_one('div[class*="updatecapsule_Desc"]')

        if not title_div or not date_div or not desc_div:
            continue

        title = title_div.getText().strip()
        date = datetime.strptime(date_div.getText().strip(), date_format)
        desc = cleanup_text_description(desc_div.decode_contents().strip())

        updates.append(
            {
                "guid": hashlib.sha256(
                    f"{date.day}{date.month}{date.year}".encode()
                ).hexdigest(),
                "title": title,
                "date": date,
                "content": desc,
            }
        )

    if not updates:
        continue

    rss_feed_file = get_feed_file_path(f"updates-feed-{language_code}.xml")

    if is_feed_up_to_date(rss_feed_file, updates[0]["guid"]):
        continue

    try:
        update_rss_feed(
            rss_feed_file,
            f"https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-{language_code}.xml",
            url,
            f"Counter-Strike 2 - Updates ({language_name.capitalize()})",
            "Counter-Strike 2 Updates Feed",
            language_code,
            updates,
        )
    except Exception as e:
        print(f"Error updating RSS feed for {language_name}: {e}")
        continue

driver.quit()
sys.exit(0)
