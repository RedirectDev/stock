import requests
import time
import asyncio
from xml.etree import ElementTree as ET
from datetime import datetime, timezone, timedelta

from services.tickers import TICKERS
from services.cache import set_cache


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def parse_date(pub_date_str: str):
    try:
        return datetime.strptime(
            pub_date_str,
            "%a, %d %b %Y %H:%M:%S %Z"
        ).replace(tzinfo=timezone.utc)
    except:
        return None


def is_recent(pub_date_str: str):
    pub_date = parse_date(pub_date_str)
    if not pub_date:
        return False

    return datetime.now(timezone.utc) - pub_date <= timedelta(hours=1)


def format_time(pub_date_str: str):
    pub_date = parse_date(pub_date_str)
    if not pub_date:
        return "неизвестно"

    # переводим в локальное время (примерно)
    local_time = pub_date + timedelta(hours=5)
    return local_time.strftime("%H:%M")


def fetch_company_news(company: str):
    url = f"https://news.google.com/rss/search?q={company}&hl=ru&gl=RU&ceid=RU:ru"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        root = ET.fromstring(r.content)
    except:
        return []

    results = []

    for item in root.findall(".//item"):
        try:
            title = item.find("title").text
            link = item.find("link").text
            pub_date = item.find("pubDate").text
        except:
            continue

        if not is_recent(pub_date):
            continue

        results.append({
            "company": company,
            "title": title,
            "url": link,
            "time_raw": pub_date,
            "time": format_time(pub_date)
        })

        if len(results) >= 2:
            break

    return results


# 🔥 обновление + сортировка
def update_all_news():
    all_news = []

    print("🔄 Обновление новостей...")

    for company in TICKERS:

        news_list = fetch_company_news(company)
        all_news.extend(news_list)

        time.sleep(2)

    # 🔥 СОРТИРОВКА ПО ВРЕМЕНИ (самые свежие сверху)
    all_news.sort(
        key=lambda x: parse_date(x["time_raw"]) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    set_cache(all_news)

    print(f"✅ Обновлено: {len(all_news)} новостей")


async def background_news_loop():
    while True:
        update_all_news()
        await asyncio.sleep(1800)  # 30 минут