import json
import re
import urllib.parse
import asyncio
import random
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
import config


async def get_avito_html(url: str):
    """Обход TLS-защиты и имитация реального пользователя."""
    await asyncio.sleep(random.uniform(3, 7))  # Увеличили паузу

    proxies = {"http": config.PROXY_URL, "https": config.PROXY_URL} if config.PROXY_URL else None

    # Расширенные заголовки
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "referer": "https://www.google.com/",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
    }

    try:
        async with AsyncSession(impersonate="chrome120", proxies=proxies) as s:
            response = await s.get(url, headers=headers, timeout=30)

            with open("avito_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)

            if response.status_code != 200:
                print(f"⚠️ Ошибка: статус {response.status_code}")
                return None
            return response.text
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
        return None


def parse_flats_from_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    flats = []

    # МЕТОД 1: Пытаемся взять JSON (самый точный способ)
    script = soup.find("script", string=re.compile(r"window\.__initialData__"))
    if script:
        try:
            raw_json = script.string.split('window.__initialData__ = "')[1].split('";')[0]
            json_data = json.loads(urllib.parse.unquote(raw_json))
            for key, value in json_data.items():
                if isinstance(value, dict) and 'items' in value:
                    for item in value['items']:
                        if 'id' in item and 'price' in item:
                            flats.append({
                                "id": str(item['id']),
                                "title": item.get('title', ''),
                                "price": item.get('price', 0),
                                "url": "https://www.avito.ru" + item.get('urlPath', ''),
                                "district": item.get('geo', {}).get('formattedAddress', '')
                            })
            if flats: return flats
        except:
            pass

    # МЕТОД 2: Если JSON нет, парсим карточки напрямую из HTML (fallback)
    print("🔄 JSON не найден, пробую прямой парсинг HTML-карточек...")
    items = soup.find_all("div", {"data-marker": "item"})
    for item in items:
        try:
            f_id = item.get("data-item-id")
            link = item.find("a", {"data-marker": "item-title"})
            url = "https://www.avito.ru" + link['href']
            title = link.text.strip()

            price_text = item.find("meta", {"itemprop": "price"})
            price = int(price_text['content']) if price_text else 0

            geo = item.find("div", {"class": re.compile(r"geo-address")})
            address = geo.text.strip() if geo else ""

            flats.append({
                "id": str(f_id), "title": title, "price": price, "url": url, "district": address
            })
        except:
            continue

    return flats


async def fetch_flats():
    target_url = f"{config.URL_BASE}?s=104"
    print(f"🔎 Запрос к Avito: {target_url}")
    html = await get_avito_html(target_url)

    if not html: return []

    all_items = parse_flats_from_html(html)

    # Фильтрация по конфигу
    filtered = []
    for f in all_items:
        if config.MIN_PRICE <= f['price'] <= config.MAX_PRICE:
            if config.TARGET_DISTRICTS:
                if any(d.lower() in f['district'].lower() for d in config.TARGET_DISTRICTS):
                    filtered.append(f)
            else:
                filtered.append(f)

    print(f"✅ Найдено: {len(all_items)} | После фильтров: {len(filtered)}")
    return filtered