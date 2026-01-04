# === Telegram ===
BOT_TOKEN = "8423336284:AAGL68Qqz36p8yLpSv2DEPT_xkrnh39bSCA"
ADMIN_IDS = [398958635]

# === Database ===
DB_DSN = "postgresql+psycopg2://postgres:Aleajda2307@localhost:5432/avito"

# === Avito ===
BASE_URL = "https://www.avito.ru"
CITY = "kazan"
CATEGORY_PATH = "/kvartiry/prodam-ASgBAgICAUSSA8gQ"

DISTRICTS = {
    "Вахитовский": 653230,
    "Советский": 653240,
    "Приволжский": 653250,
    "Ново-Савиновский": 653260,
}

# === Parsing behaviour ===
INITIAL_MAX_PAGES = 200
UPDATE_MAX_PAGES = 3
PARSE_INTERVAL_MINUTES = 15
REQUEST_DELAY_RANGE = (2.5, 5.5)

# === Filters (расширяемо) ===
PRICE_MIN = None
PRICE_MAX = None
ROOMS = None  # например [1,2,3]
