# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from database import init_db, async_session, Flat
from sqlalchemy import select  # Импортируем select из библиотеки
from parser import fetch_flats

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def job_check_updates():
    """Периодическая задача"""
    logging.info("⏳ Запуск плановой проверки...")

    try:
        fresh_flats = await fetch_flats()
    except Exception as e:
        logging.error(f"Ошибка в парсере: {e}")
        return

    if not fresh_flats:
        return

    async with async_session() as session:
        for flat_data in fresh_flats:
            # Проверяем, есть ли квартира в базе
            stmt = select(Flat).where(Flat.avito_id == flat_data["id"])
            result = await session.execute(stmt)
            db_flat = result.scalar_one_or_none()

            # 1. Новая квартира
            if not db_flat:
                new_flat = Flat(
                    avito_id=flat_data["id"],
                    title=flat_data["title"],
                    price=flat_data["price"],
                    url=flat_data["url"],
                    district=flat_data["district"]
                )
                session.add(new_flat)

                # Уведомление
                msg = (
                    f"🔥 <b>Новая квартира!</b>\n"
                    f"🏙 {flat_data['district']}\n"
                    f"💰 <b>{flat_data['price']:,} ₽</b>\n"
                    f"📝 {flat_data['title']}\n"
                    f"👉 <a href='{flat_data['url']}'>Смотреть объявление</a>"
                )
                try:
                    await bot.send_message(config.ADMIN_ID, msg, parse_mode="HTML")
                    await asyncio.sleep(1)  # Чтобы телеграм не забанил за спам
                except Exception as e:
                    logging.error(f"Не удалось отправить сообщение: {e}")

            # 2. Изменилась цена
            elif db_flat.price != flat_data["price"]:
                old_price = db_flat.price
                diff = flat_data["price"] - old_price
                icon = "📈" if diff > 0 else "📉"

                db_flat.price = flat_data["price"]  # Обновляем в БД

                msg = (
                    f"{icon} <b>Цена изменилась!</b>\n"
                    f"Было: {old_price:,} ₽\n"
                    f"Стало: <b>{flat_data['price']:,} ₽</b>\n"
                    f"👉 <a href='{flat_data['url']}'>Ссылка</a>"
                )
                try:
                    await bot.send_message(config.ADMIN_ID, msg, parse_mode="HTML")
                except Exception:
                    pass

        await session.commit()
    logging.info("✅ Проверка завершена.")


async def main():
    # 1. Инициализация БД
    await init_db()

    # 2. Настройка планировщика
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_check_updates, "interval", minutes=config.CHECK_INTERVAL)
    scheduler.start()

    # 3. Первый прогон сразу при старте (чтобы проверить работу)
    await job_check_updates()

    # 4. Запуск бота
    logging.info("🚀 Бот запущен! Ожидаю обновлений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())