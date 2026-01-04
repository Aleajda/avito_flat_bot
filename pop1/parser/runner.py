from pop1.db.session import SessionLocal
from pop1.db.crud import (
    get_flat_by_avito_id,
    create_flat,
    update_price,
    add_price_history,
)
from pop1.parser.avito import parse_page
from pop1.parser.utils import sleep_random
from pop1.bot.notifications import notify_new_flat, notify_price_change
from pop1.config import DISTRICTS, UPDATE_MAX_PAGES, BASE_URL, CITY, CATEGORY_PATH

def build_url(district_id: int, page: int) -> str:
    return f"{BASE_URL}/{CITY}{CATEGORY_PATH}?district={district_id}&p={page}"

def update_parse():
    db = SessionLocal()

    for district, district_id in DISTRICTS.items():
        for page in range(1, UPDATE_MAX_PAGES + 1):
            flats = parse_page(build_url(district_id, page))

            for f in flats:
                flat = get_flat_by_avito_id(db, f["avito_id"])

                if not flat:
                    create_flat(db, f, district)
                    notify_new_flat(f)

                elif flat.price != f["price"]:
                    add_price_history(db, flat.id, flat.price, f["price"])
                    update_price(db, flat, f["price"])
                    notify_price_change(f, flat.price)

            sleep_random()

    db.close()
