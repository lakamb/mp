from aiogram import Bot, Dispatcher, executor, types, filters
from wb_api import week_result, bestseller
from config import bot_TOKEN

TOKEN = bot_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Клавиатура
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttonlist = [types.KeyboardButton(text = 'Бестселлер за всё время'), types.KeyboardButton(text = 'Результаты за неделю')]
kb.add(*buttonlist)

@dp.message_handler(commands=['start'])
async def cmd_handler(message: types.Message):
    await message.answer('Выбрана команда "start"', reply_markup=kb)

@dp.message_handler(commands=['welcome', 'about'])
async def cmd_handler(message: types.Message):
    await message.answer('Выбрана какая-то команда')


@dp.message_handler(filters.Text(equals='Бестселлер за всё время'))
async def echo(message: types.Message):
    await message.answer(bestseller())
    #await message.answer('была нажата Кнопка_1')

@dp.message_handler(filters.Text(equals='Результаты за неделю'))
async def echo(message: types.Message):
    await message.answer(week_result())
    #await message.answer('была нажата Кнопка_1')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)