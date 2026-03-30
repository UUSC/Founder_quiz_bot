import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from config.question import quiz_data
from config.settings import API_TOKEN
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from telegram_functions.keybords import generate_options_keyboard
from database.db import get_quiz_index, update_quiz_index, create_table, add_score, get_stat, create_user

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Посмотреть статистику"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text=="Начать игру") #Декоратор на техт начать игру
@dp.message(Command("quiz")) #декоратор на команду quiz
#Функция пишет приветствие в чат и вызывает функцию newquiz
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

#Функция создает пользователя или перезаписывает его с нулем очков если он есть и дергает вопрос
async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await create_user(user_id, current_question_index)
    await get_question(message, user_id)

#Функция берет текущий ID Вопроса из БД берет ответы на вопросы, создает по ним клавиатуру, отправляет в чат вопрос и клавиатуру
async def get_question(message, user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

#Нажатие на клавиатуру вызывает callback ans: {ID_выбранного ответа}
@dp.callback_query(F.data.startswith("ans:")) #Данный декоратор реагирует на коллбеки, которые начинаются с ans:
#Функция проверяет корректность правильного ответа дает фидбек, верный не верный, дописывает очко в БД если ответ верный, и прибавляет 1 к индексу вопроса
#Если индекс текущего вопроса равен длине с массивом вопросов, функция выведет сообщение, что вопросы закончились
async def check_user_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    answer_id  = int(callback.data.split(":")[1])
    user_answer = quiz_data[current_question_index]["options"][answer_id]
    correct_answer_id = quiz_data[current_question_index]['correct_option']
    print(user_answer)
    if answer_id == quiz_data[current_question_index]['correct_option']:
        await callback.message.answer(f"Ваш ответ: {user_answer}\nВерно!")
        await add_score(callback.from_user.id)
    else:
        await callback.message.answer(f"Ваш ответ: {user_answer}\nНе верно!\n верный ответ: "
                                      f"{quiz_data[current_question_index]['options'][correct_answer_id]}")
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@dp.message(F.text=="Посмотреть статистику") #екоратор реагирует на кнопку посмотреть статистику
async def check_stat(message): #ункция дергает топ пять юзеров по правильным ответам и выводит их в сообщении
    top_score = await get_stat()
    await message.answer(top_score)


# Запуск процесса поллинга новых апдейтов
async def main():
    # Запускаем создание таблицы базы данных
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())