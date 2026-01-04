from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import asyncio

from pop1.bot.keyboards import main_kb
from pop1.parser.runner import update_parse

router = Router()


@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "Бот отслеживает покупку квартир в Казани 🏠",
        reply_markup=main_kb,
    )


@router.message(lambda m: m.text == "🔄 Обновить сейчас")
async def manual_update(msg: Message):
    # НЕ блокируем event loop
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, update_parse)
    await msg.answer("Парсинг выполнен")
