from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()
    i = 0
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"ans:{i}")
        )
        i += 1
    builder.adjust(1)
    return builder.as_markup()
