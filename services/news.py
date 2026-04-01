import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from tickers import TICKERS


def fetch_company_news(company):
    url = f"https://news.google.com/rss/search?q={company}&hl=ru&gl=RU&ceid=RU:ru"

    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
    except:
        return []

    news_list = []

    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text
        source = item.find("source").text if item.find("source") is not None else "Unknown"

        try:
            pub_time = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
        except:
            continue

        # только за последний 1 час
        if datetime.utcnow() - pub_time > timedelta(hours=1):
            continue

        news_list.append({
            "company": company,
            "title": title,
            "link": link,
            "source": source,
            "time": pub_time.strftime("%H:%M")
        })

    return news_list


def get_all_news():
    all_news = []

    for company in TICKERS:
        news = fetch_company_news(company)
        all_news.extend(news)

    # сортировка по времени
    all_news.sort(key=lambda x: x["time"], reverse=True)

    return all_news