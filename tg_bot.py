import logging

from aiogram import Bot, Dispatcher, executor, types, filters
from metrics import week_result, bestseller
from config import bot_TOKEN

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import db_start, create_profile, edit_profile

async def on_startup(_):
    await db_start()

logging.basicConfig(level=logging.INFO)

TOKEN = bot_TOKEN


storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)


# datefrom = 0
datefrom = []

# States

class Form(StatesGroup):
    date_from = State()  # Will be represented in storage as 'Form:name'
    # age = State()  # Will be represented in storage as 'Form:age'
    # gender = State()  # Will be represented in storage as 'Form:gender'

Forms = dict()

# Клавиатура
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttonlist = [types.KeyboardButton(text = 'Бестселлер за всё время'),
              types.KeyboardButton(text = 'Результаты за неделю'),
              types.KeyboardButton(text = 'Указать дату')]

kb.add(*buttonlist)

@dp.message_handler(commands=['start'])
async def cmd_handler(message: types.Message):
    await message.answer('Выбрана команда "start"', reply_markup=kb)
    await create_profile(user_id=message.from_user.id)

@dp.message_handler(commands=['welcome', 'about'])
async def cmd_handler(message: types.Message):
    await message.answer('Выбрана какая-то команда')


@dp.message_handler(filters.Text(equals='Бестселлер за всё время'))
async def echo(message: types.Message):
    await message.answer(bestseller())

@dp.message_handler(filters.Text(equals='Результаты за неделю'))
async def echo(message: types.Message):
    await message.answer(week_result())





###
@dp.message_handler(filters.Text(equals='Указать дату'))
async def cmd_date_from(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.date_from.set()
    await message.reply("Укажите дату")

# You can use state '*' if you need to handle all states

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.date_from)
async def process_date_from(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['date_from'] = message.text
    await edit_profile(state, user_id=message.from_user.id)
    # await Form.next()
    await message.reply("Отлично, дата задана")

    # Finish conversation
    await state.finish()
###


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
