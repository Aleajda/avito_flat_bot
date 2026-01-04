# config.py

# ===========================
# 🤖 НАСТРОЙКИ БОТА И БД
# ===========================
BOT_TOKEN = "8423336284:AAGL68Qqz36p8yLpSv2DEPT_xkrnh39bSCA"
ADMIN_ID = 398958635  # Твой ID (числом), узнай через @userinfobot

# Строка подключения к PostgreSQL (формат: postgresql+asyncpg://user:pass@host/dbname)

import os

# --- НАСТРОЙКИ POSTGRESQL ---
DB_USER = "postgres"
DB_PASS = "Aleajda2307"
DB_NAME = "avito_db"
DB_HOST = "localhost"
DB_PORT = "5432"

# Формируем строку подключения для SQLAlchemy (asyncpg)
# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}" ДЛЯ ПОСГРЕСА

DATABASE_URL = "sqlite+aiosqlite:///./avito_ads.db"

# --- НАСТРОЙКИ ПАРСЕРА ---
# Город: Казань
# Категория: Квартиры / Купить
# Сортировка: По дате (чтобы быстрее находить новые)
AVITO_URL = "https://www.avito.ru/kazan/kvartiry/prodam/vtorichka-ASgBAgICAkSSA8YQ5geMUg?district=782-783-784&f=ASgBAQECAkSSA8YQ5geMUgFAygg0hFmCWYBZAUXGvg0XeyJmcm9tIjoyMDAwLCJ0byI6bnVsbH0&localPriority=0&s=104"

# Интервал проверки (в секундах)
# Рекомендую ставить не меньше 600 (10 минут), чтобы избежать частых блокировок по IP
CHECK_INTERVAL = 1800  # 30 минут

# --- ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ---
HEADLESS_MODE = True  # Если False, будет открываться окно браузера (удобно для отладки)