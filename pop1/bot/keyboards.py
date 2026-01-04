from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 История цен")],
        [KeyboardButton(text="🔄 Обновить сейчас")],
    ],
    resize_keyboard=True,
)
