[![Generate RSS feeds](https://github.com/IceQ1337/CS2-RSS-Feed/actions/workflows/update-rss-feeds.yaml/badge.svg)](https://github.com/IceQ1337/CS2-RSS-Feed/actions/workflows/update-rss-feeds.yaml)

# Counter-Strike RSS-Feed Repository
This repository provides a collection of RSS feeds for news and updates on the [new Counter-Strike website](https://counter-strike.net) as the new website unfortunately lacks this feature.  

Using [Github Workflows](https://docs.github.com/en/actions/using-workflows), the website is checked for new entries every 10 minutes. The RSS feeds are only updated when there are actually new entries to reduce repository noise. Please note that during periods of high load on GitHub Actions, scheduled workflow runs may be delayed or skipped.  

Updating each feed requires one API request per language to the website. This means that generating both the news and updates feed for a single language (e.g., English) takes only one request total, as both feeds are created from the same data source.

## Available RSS-Feeds
### News
-  [English](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-en.xml)
-  [German](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-de.xml)
-  [French](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-fr.xml)

### Updates
-  [English](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-en.xml)
-  [German](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-de.xml)
-  [French](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-fr.xml)

**Notes:**
Valve does not localize all of their posts before they are published. Translations are partly driven by the community and may be available at a later date. We are currently filtering out untranslated posts from the non-English feeds, so they may contain less entries than the English feed.

## Local Usage

### Requirements
- Python 3.12 or higher

### Setup & Usage

#### 1. Create venv (optional) and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `./venv/Scripts/activate`
pip install -r src/requirements.txt
```

#### 2. Run the script to generate the feeds:

```bash
python src/update-rss-feeds.py
```

### Linting & Formatting

You can run the following commands to lint and format the code:

```bash
black --check -l 79 src/
isort --check --profile black --line-length 79 src/
flake8 --ignore=E501 src/
```

```bash
black -l 79 src/
isort --profile black --line-length 79 src/
```

## Contribution Guidelines
There are currently no contributing guidelines, but I am open to any kind of improvements.  
In order to contribute to the project, please follow the GitHub Standard Fork & Pull Request Workflow  

**Note:** Do not make direct changes to *.xml files in the feeds directory.

## Acknowledgements
- [lkiesow/python-feedgen](https://github.com/lkiesow/python-feedgen)
- [kurtmckee/feedparser](https://github.com/kurtmckee/feedparser)
- [dcwatson/bbcode](https://github.com/dcwatson/bbcode)
- [stefanzweifel/git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action)
