import requests
from bs4 import BeautifulSoup
from pop1.config import BASE_URL
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Referer": "https://www.avito.ru/"
}

def extract_avito_id(url: str) -> str:
    return url.split("_")[-1].split("?")[0]

def parse_page(url: str) -> list[dict]:
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                wait_time = random.uniform(5, 10)
                print(f"429 Too Many Requests, ждем {wait_time:.1f} секунд...")
                time.sleep(wait_time)
                retries += 1
            else:
                raise
        except requests.exceptions.RequestException as e:
            # Любая другая ошибка сети
            wait_time = random.uniform(3, 6)
            print(f"Ошибка запроса: {e}, ждем {wait_time:.1f} секунд...")
            time.sleep(wait_time)
            retries += 1
    else:
        print(f"Не удалось получить страницу {url} после {max_retries} попыток")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    flats = []

    for item in soup.select("[data-marker='item']"):
        a = item.select_one("a")
        price_tag = item.select_one("[itemprop='price']")
        title_tag = item.select_one("[itemprop='name']")

        if not a or not price_tag or not title_tag:
            continue

        link = BASE_URL + a["href"]

        try:
            price = int(price_tag["content"])
        except (KeyError, ValueError):
            price = 0

        flats.append({
            "url": link,
            "avito_id": extract_avito_id(link),
            "title": title_tag.text.strip(),
            "price": price,
        })

    # Рандомная пауза после обработки страницы, чтобы не бить сервер слишком часто
    time.sleep(random.uniform(1, 3))

    return flats
