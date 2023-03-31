[![Generate RSS feeds for CS2 news](https://github.com/IceQ1337/CS2-RSS-Feed/actions/workflows/generate-news-feed.yaml/badge.svg)](https://github.com/IceQ1337/CS2-RSS-Feed/actions/workflows/generate-news-feed.yaml) [![Generate RSS feeds for CS2 updates](https://github.com/IceQ1337/CS2-RSS-Feed/actions/workflows/generate-updates-feed.yaml/badge.svg)](https://github.com/IceQ1337/CS2-RSS-Feed/actions/workflows/generate-updates-feed.yaml)

# Counter-Strike RSS-Feed Repository
This repository provides a collection of RSS feeds for news and updates on the [new Counter-Strike website](https://counter-strike.net), which is updated several times a day as the new website unfortunately lacks this feature.  

Using [Github Workflows](https://docs.github.com/en/actions/using-workflows), the website is checked for new entries every 4 hours. The RSS feeds are only updated when there are actually new entries to reduce repository noise.  

Updating the updates feed requires only one request to the website.  
Updating the news feed requires 16 requests to the website.  

## Available RSS-Feeds
### News
-  [English](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-en.xml)
-  [German](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/news-feed-de.xml)

### Updates
-  [English](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-en.xml)
-  [German](https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-de.xml)

**Notes:**
- Valve does not localize all of their blog/update posts immediately.
  - Translations are partly driven by the community and may be available at a later date.
- Time information on the website is generally not localized.
  - When running the python scripts locally, you may have issues parsing dates.

## Contribution Guidelines
There are currently no contributing guidelines, but I am open to any kind of improvements.  
In order to contribute to the project, please follow the GitHub Standard Fork & Pull Request Workflow  

**Note:** Do not make direct changes to *.xml files in the feeds directory.

## Acknowledgements
- [Selenium](https://github.com/SeleniumHQ/selenium)
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/)
- [Feedgen](https://feedgen.kiesow.be/)
- [Feedparser](https://github.com/kurtmckee/feedparser)
- [stefanzweifel/git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action)
