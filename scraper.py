import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import random
import logging
import os
from dataclasses import dataclass
import re

import config


@dataclass
class AvitoItem:
    avito_id: str
    url: str
    title: str
    price: int
    address: str
    published_at: str
    price_per_meter: float  # <--- Добавили поле


class AvitoScraper:
    def __init__(self, url):
        self.url = url
        self.options = uc.ChromeOptions()

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(curr_dir, "avito_profile")
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)

        self.options.add_argument(f'--user-data-dir={profile_path}')
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

    def _get_last_page_number(self, soup):
        """Улучшенный поиск последней страницы"""
        try:
            # Метод 1: Ищем по data-marker (самый надежный)
            pagination = soup.find('div', attrs={'data-marker': 'pagination-button'})
            if pagination:
                pages = pagination.find_all('span', {'class': lambda x: x and 'styles-module-item' in x})
                nums = [int(p.text) for p in pages if p.text.isdigit()]
                if nums:
                    return max(nums)

            # Метод 2: Если первый не сработал, ищем любую ссылку с параметром p=
            all_links = soup.find_all('a', href=True)
            page_nums = []
            for link in all_links:
                href = link['href']
                if 'p=' in href:
                    try:
                        # Вытаскиваем число после p=
                        num = int(href.split('p=')[-1].split('&')[0])
                        page_nums.append(num)
                    except:
                        continue

            return max(page_nums) if page_nums else 1
        except Exception as e:
            logging.debug(f"Error parsing pages: {e}")
            return 1

    def get_listings(self):
        logging.info(f"Starting Deep Scan (Headless: {config.HEADLESS_MODE})...")
        driver = uc.Chrome(options=self.options, headless=config.HEADLESS_MODE)
        all_listings = []
        current_page = 1
        total_pages = 1

        try:
            # 1. Прогрев куков
            driver.get("https://www.avito.ru")
            time.sleep(random.uniform(3, 5))

            while True:
                # Генерируем URL для текущей страницы
                page_separator = "&" if "?" in self.url else "?"
                target_url = f"{self.url}{page_separator}p={current_page}"

                logging.info(f"Scraping page {current_page} of {total_pages if current_page > 1 else '?'}")
                driver.get(target_url)

                # Ожидание загрузки (на первой странице дольше)
                time.sleep(12 if current_page == 1 else random.uniform(5, 7))

                # !!! КРИТИЧЕСКИЙ МОМЕНТ: Скроллим вниз, чтобы пагинация прогрузилась в HTML !!!
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # На первой странице определяем, сколько всего страниц
                if current_page == 1:
                    total_pages = self._get_last_page_number(soup)
                    logging.info(f"!!! DETECTED TOTAL PAGES: {total_pages} !!!")

                # Парсинг объявлений
                items = soup.find_all('div', attrs={'data-marker': 'item'})
                if not items:
                    logging.warning(f"No items found on page {current_page}. Stopping.")
                    break

                for item in items:
                    try:
                        avito_id = item.get('data-item-id')
                        link_tag = item.find('a', attrs={'data-marker': 'item-title'})
                        if not link_tag: continue

                        url = "https://www.avito.ru" + link_tag.get('href')
                        title = link_tag.text.strip()

                        # Парсинг цены
                        price_tag = item.find('meta', attrs={'itemprop': 'price'})
                        price = int(price_tag.get('content')) if price_tag else 0

                        # --- РАСЧЕТ ЦЕНЫ ЗА КВАДРАТ ---
                        price_per_meter = 0.0
                        try:
                            # Ищем число перед "м²" (поддерживает 54, 54.5 и 54,5)
                            area_match = re.search(r'(\d+[.,]?\d*)\s*м²', title)
                            if area_match and price > 0:
                                area_str = area_match.group(1).replace(',', '.')
                                area = float(area_str)
                                price_per_meter = round(price / area, 2)
                        except Exception as e:
                            logging.debug(f"Error calculating area for {title}: {e}")

                        geo_tag = item.find('div', attrs={'data-marker': 'item-address'})
                        address = geo_tag.text.strip() if geo_tag else "Казань"

                        date_tag = item.find('p', attrs={'data-marker': 'item-date'})
                        published_at = date_tag.text.strip() if date_tag else "Только что"

                        all_listings.append(AvitoItem(
                            avito_id=avito_id,
                            url=url,
                            title=title,
                            price=price,
                            address=address,
                            published_at=published_at,
                            price_per_meter=price_per_meter  # <--- Передаем
                        ))
                    except Exception as e:
                        continue

                # --- ЛОГИКА ПЕРЕХОДА НА СЛЕДУЮЩУЮ СТРАНИЦУ ---
                if current_page >= total_pages:
                    logging.info(f"Finish. Reached last page {current_page} of {total_pages}")
                    break

                current_page += 1
                # Пауза перед следующей страницей
                time.sleep(random.uniform(2, 4))

        except Exception as e:
            logging.error(f"Global Scraper Error: {e}")
        finally:
            driver.quit()

        logging.info(f"Total items found: {len(all_listings)}")
        return all_listings