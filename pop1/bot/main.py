import asyncio
from aiogram import Dispatcher
from pop1.bot.handlers import router
from pop1.bot.runtime import bot
from pop1.services.initial_parse import initial_parse
from pop1.services.scheduler import start_scheduler


async def main():
    # Первый полный парсинг (sync)
    initial_parse()

    # Запуск scheduler
    start_scheduler()

    # Подключаем router к dispatcher
    dp = Dispatcher()
    dp.include_router(router)

    # Старт polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
