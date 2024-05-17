import os
import sys
import locale
import feedparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

base_url = 'https://www.counter-strike.net'
content_url = base_url + '/news'

# Define a list of languages to fetch and parse
language_map = {
    'english': ('en', 'en_US'),
    'german': ('de', 'de_DE')
}

# Set up a Chrome WebDriver in headless mode
try:
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
except:
    sys.exit(f'Failed to initialize the headless web browser.')

# Loop over the languages and generate an RSS feed for each language
for language_name, (language_code, language_locale) in language_map.items():
    # Construct the URL for the current language
    url = f'{content_url}?l={language_name}'

    # Launch the browser and navigate to the website to fetch its HTML content
    try:
        driver.get(url)

        # Wait for the contents to appear (thanks Valve for using reactJS)
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class^="blogoverviewpage_SubEntries"]'))
        )

        # Extract the (hopefully) complete HTML
        html_content = driver.page_source
    except TimeoutException:
        driver.quit()
        sys.exit(f'Unable to find the news capsule container in the given time frame.')
    except Exception as e:
        driver.quit()
        print(e)
        sys.exit(f'Failed to extract the HTML data.')

    # Parse the HTML content with BeautifulSoup and extract all relevant information
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all containers with class names that contain "blogcapsule_BlogCapsule"
    capsules = soup.select('a[class*="blogcapsule_BlogCapsule"]')

    # Create an array of all news entries
    news_items = []

    # Set locale to parse the date, but dates are currently not localized anyways (Thanks Valve)
    locale.setlocale(locale.LC_TIME, f'en_US.UTF-8') # Switch to language_locale after it's fixed (if ever)
    date_format = '%B %d, %Y' # English
    
    #locale.setlocale(locale.LC_TIME, 'de_DE') # German
    #date_format = '%d. %B %Y' # German

    # For each news capsule, open the entry and find all div containers with relevant information
    for capsule in capsules:
        unique_relative_url = capsule.get('href')
        unique_url = f'{base_url}{unique_relative_url}?l={language_name}'
        unique_identifier = unique_relative_url.replace('/newsentry/', '')

        # Navigate the browser to the news entry
        try:
            driver.get(unique_url)

            # Wait for the contents to appear
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class^="blogentrypage_BlogEntryPage"]'))
            )

            # Extract the (hopefully) complete HTML
            news_html_content = driver.page_source
        except TimeoutException:
            driver.quit()
            sys.exit(f'Unable to open or find the news entry page in the given time frame.')
        except Exception as e:
            driver.quit()
            sys.exit(f'Failed to extract the HTML data of a news entry.')

        # Parse the HTML content with BeautifulSoup and extract all relevant information
        news_soup = BeautifulSoup(news_html_content, 'html.parser')
        news_page = news_soup.select_one('div[class*="blogentrypage_BlogEntryPage"]')

        title = news_page.select_one('div[class*="blogentrypage_Title_"]').text.strip()
        date = datetime.strptime(news_page.select_one('div[class*="blogentrypage_Date"]').text.strip(), date_format)
        body = news_page.select_one('div[class*="blogentrypage_Body"]').decode_contents().strip()

        # Remove trailing <br/> tags at the beginning of the news article
        while body.startswith('<br'):
            index = desc.index('>') + 1
            desc = desc[index:]

        news_items.append({
            'guid': unique_identifier,
            'url': unique_url,
            'title': title,
            'date': date,
            'content': body
        })

    # Parse an existing RSS feed file and compare the last entry
    github_workspace = os.getenv('GITHUB_WORKSPACE')

    if github_workspace:
        rss_feed_file = os.path.join(os.environ['GITHUB_WORKSPACE'], 'feeds', f'news-feed-{language_code}.xml')
    else:
        rss_feed_file = os.path.join(os.pardir, 'feeds', f'news-feed-{language_code}.xml')

    skip_file = False

    if os.path.exists(rss_feed_file):
        current_feed = feedparser.parse(rss_feed_file)
        if current_feed.entries and news_items and current_feed.entries[0].title == news_items[0]['title']:
            skip_file = True

    # Generate the RSS feed with feedgen if the latest entry is different from the current RSS feed
    if not skip_file:
        feed_link = f'https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-{language_code}.xml'

        fg = FeedGenerator()
        fg.title(f'Counter-Strike 2 - News ({language_name.capitalize()})')
        fg.description('Counter-Strike 2 News Feed')
        fg.link(href=feed_link, rel='self')
        fg.language(language_code)

        # Add the extracted information as entries to the RSS feed
        for news in reversed(news_items):
            fe = fg.add_entry()
            fe.source(url)
            fe.id(news['url'])
            fe.guid(news['guid'])
            fe.title(news['title'])
            fe.link({
                'href': news['url'],
                'rel': 'alternate',
                'type': 'text/html',
                'hreflang': language_code,
                'title': news['title']
            })
            fe.pubDate(datetime.strftime(news['date'], '%Y-%m-%dT%H:%M:%SZ'))
            fe.author({'name':'Valve Corporation', 'email':'support@steampowered.com'})
            fe.content(news['content'], None, 'CDATA')
            fe.rights('Valve Corporation')

        rss_content = fg.rss_str(pretty=True)

        # Create or update XML File
        with open(rss_feed_file, "wb") as f:
            f.write(rss_content)

driver.quit()
sys.exit(0)