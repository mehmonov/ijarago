from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_save_filter_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💾 Saqlash", callback_data="save_filter")
    builder.button(text="❌ Yopish", callback_data="close")
    return builder.as_markup()
