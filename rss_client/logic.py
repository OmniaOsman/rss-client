import feedparser


def fetch_news_from_rss(rss_url, limit):
    feed = feedparser.parse(rss_url)
    return feed.entries[:limit]


def get_news_from_multiple_sources():
    rss_urls = {
        'AlJazeera': "https://www.ajnet.me/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9",
        'RT': "https://arabic.rt.com/rss/",
        'UN': 'https://news.un.org/feed/subscribe/ar/news/all/rss.xml'
    }

    all_news = {}
    limit = 10
    for source, url in rss_urls.items():
        news_entries = fetch_news_from_rss(url, limit)
        all_news[source] = news_entries
        print(source[])

    return all_news
