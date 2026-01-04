from pop1.db.session import SessionLocal
from pop1.db.crud import create_flat, get_app_state, set_app_state
from pop1.parser.avito import parse_page
from pop1.parser.utils import sleep_random
from pop1.config import DISTRICTS, INITIAL_MAX_PAGES, BASE_URL, CITY, CATEGORY_PATH
import random
import time
import requests

def build_url(district_id: int, page: int) -> str:
    return f"{BASE_URL}/{CITY}{CATEGORY_PATH}?district={district_id}&p={page}"

def initial_parse():
    db = SessionLocal()

    if get_app_state(db, "initial_parse_done") == "true":
        db.close()
        return

    for district, district_id in DISTRICTS.items():
        for page in range(1, INITIAL_MAX_PAGES + 1):
            url = build_url(district_id, page)
            success = False

            while not success:
                try:
                    flats = parse_page(url)
                    success = True  # Запрос успешен
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        wait_time = random.uniform(5, 10)  # ждем 5–10 секунд
                        print(f"429 Too Many Requests, ждем {wait_time:.1f} секунд...")
                        time.sleep(wait_time)
                    else:
                        raise  # Любая другая ошибка — поднимаем дальше

            if not flats:
                break

            for f in flats:
                create_flat(db, f, district)

            # Случайная пауза между страницами
            sleep_random()

    set_app_state(db, "initial_parse_done", "true")
    db.close()
