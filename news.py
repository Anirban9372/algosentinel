import requests
import xml.etree.ElementTree as ET

FEEDS = [
    "https://news.google.com/rss/search?q=SPY+stock+market&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=S%26P+500+market&hl=en-US&gl=US&ceid=US:en",
]


def fetch_headlines(max_items=10):
    headlines = []
    for url in FEEDS:
        try:
            r = requests.get(url, timeout=10)
            root = ET.fromstring(r.content)
            for item in root.iter('item'):
                title = item.find('title')
                if title is not None:
                    headlines.append(title.text)
        except Exception as e:
            print(f"[NEWS] Error: {e}")
    return headlines[:max_items]
