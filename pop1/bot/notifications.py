import asyncio
from pop1.config import ADMIN_IDS
from pop1.bot.runtime import bot

# Все уведомления теперь через asyncio.create_task
def notify_new_flat(flat: dict):
    text = (
        "🏠 Новая квартира\n"
        f"{flat['title']}\n"
        f"💰 {flat['price']} ₽\n"
        f"{flat['url']}"
    )
    for admin in ADMIN_IDS:
        asyncio.create_task(bot.send_message(admin, text))


def notify_price_change(flat: dict, old_price: int):
    text = (
        "💸 Изменилась цена\n"
        f"{flat['title']}\n"
        f"{old_price} → {flat['price']} ₽\n"
        f"{flat['url']}"
    )
    for admin in ADMIN_IDS:
        asyncio.create_task(bot.send_message(admin, text))
