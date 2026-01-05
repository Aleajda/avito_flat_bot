import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, func

import config
from database import init_db, async_session, User, Listing
from scraper import AvitoScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == message.chat.id))
        user = result.scalar_one_or_none()
        if not user:
            session.add(User(telegram_id=message.chat.id))
            await session.commit()
            await message.answer("✅ Вы подписались на обновления!")
        else:
            await message.answer("Вы уже в базе.")


async def notify_users(user_ids, text):
    for chat_id in user_ids:
        try:
            await bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Notify error: {e}")


async def check_updates():
    # Защита от наслоения проверок
    if getattr(check_updates, "is_running", False):
        logger.warning("Предыдущая проверка еще не завершена, пропускаю.")
        return
    check_updates.is_running = True

    try:
        logger.info("--- Начинаю проверку обновлений ---")
        scraper = AvitoScraper(config.AVITO_URL)

        loop = asyncio.get_running_loop()
        items = await loop.run_in_executor(None, scraper.get_listings)

        if not items:
            logger.warning("Объявления не найдены (0 шт.)")
            return

        async with async_session() as session:
            # Проверяем, есть ли уже данные в базе (для режима "первого запуска")
            count_result = await session.execute(select(func.count(Listing.id)))
            db_is_empty = count_result.scalar() == 0

            users_result = await session.execute(select(User))
            user_ids = [u.telegram_id for u in users_result.scalars().all()]

            if not user_ids:
                logger.warning("В базе 0 пользователей! Напиши боту /start.")

            counter_new = 0
            for item in items:
                try:
                    result = await session.execute(select(Listing).where(Listing.avito_id == str(item.avito_id)))
                    exist = result.scalar_one_or_none()

                    if not exist:
                        # СОХРАНЯЕМ НОВОЕ
                        new_item = Listing(
                            avito_id=str(item.avito_id),
                            title=item.title,
                            price=item.price,
                            price_per_meter=item.price_per_meter,  # Новое поле
                            url=item.url,
                            address=item.address,
                            published_at=item.published_at
                        )
                        session.add(new_item)
                        await session.commit()
                        counter_new += 1

                        # Уведомляем только если это не первый массовый залив базы
                        if user_ids and not db_is_empty:
                            ppm_text = f"{int(item.price_per_meter):,}".replace(",", " ")
                            msg = (
                                f"🏠 <b>Новое объявление!</b>\n\n"
                                f"📝 {item.title}\n"
                                f"💰 <b>{item.price:,} ₽</b>\n"
                                f"Цена за м²: <b>{ppm_text} ₽</b>\n"
                                f"Адрес: {item.address}\n"
                                f"Дата публикации: {item.published_at}\n\n"
                                f"🔗 <a href='{item.url}'>Открыть на Avito</a>"
                            ).replace(",", " ")
                            await notify_users(user_ids, msg)
                            await asyncio.sleep(0.1)  # Чуть больше задержка для ТГ

                    elif exist.price != item.price:
                        # ОБНОВЛЯЕМ ЦЕНУ
                        diff = item.price - exist.price
                        exist.price = item.price
                        exist.price_per_meter = item.price_per_meter
                        exist.published_at = item.published_at
                        await session.commit()

                        logger.info(f"Цена изменилась для: {item.avito_id}")

                        if user_ids:
                            icon = "📉" if diff < 0 else "📈"
                            msg = (
                                f"{icon} <b>Изменение цены!</b>\n\n"
                                f"📝 {item.title}\n"
                                f"💰 <b>{item.price:,} ₽</b> ({diff:+,} ₽)\n"
                                f"Цена за м²: <b>{int(item.price_per_meter):,} ₽</b>\n\n"
                                f"Адрес: {item.address}\n"
                                f"Дата публикации: {item.published_at}\n\n"
                                f"🔗 <a href='{item.url}'>Открыть на Avito</a>"
                            ).replace(",", " ")
                            await notify_users(user_ids, msg)

                except Exception as e:
                    logger.error(f"Ошибка при обработке {item.avito_id}: {e}")
                    await session.rollback()
                    continue

            if db_is_empty:
                logger.info(f"Первичная база наполнена: {counter_new} записей.")
                if user_ids:
                    await notify_users(user_ids,
                                       f"✅ База данных успешно инициализирована! Собрано {counter_new} объявлений. Теперь я буду присылать только новые.")

            logger.info(f"--- Проверка завершена. Добавлено новых: {counter_new} ---")

    finally:
        check_updates.is_running = False


async def main():
    await init_db()
    # Планировщик
    scheduler.add_job(check_updates, 'interval', seconds=config.CHECK_INTERVAL)
    scheduler.start()

    # Запуск первой проверки
    asyncio.create_task(check_updates())

    logger.info("Bot started.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())