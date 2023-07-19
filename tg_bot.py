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


# States
class Form(StatesGroup):
    name = State() # Will be represented in storage as 'Form:name
    wb_token = State()  
    from_dt = State()  

Forms = dict()

# Клавиатура
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttonlist = [
              types.KeyboardButton(text = 'demo')
              , types.KeyboardButton(text = 'create profile')
              # , types.KeyboardButton(text = 'Бестселлер за всё время'),
              # , types.KeyboardButton(text = 'Результаты за неделю'),
              # , types.KeyboardButton(text = 'Указать дату')
              ]

kb.add(*buttonlist)

@dp.message_handler(commands=['start'])
async def cmd_handler(message: types.Message):
    await message.answer('Начни с demo. Но можно и создать профиль', reply_markup=kb)
    await create_profile(user_id=message.from_user.id)

# @dp.message_handler(commands=['welcome', 'about'])
# async def cmd_handler(message: types.Message):
#     await message.answer('Выбрана какая-то команда')


# @dp.message_handler(filters.Text(equals='Бестселлер за всё время'))
# async def echo(message: types.Message):
#     await message.answer(bestseller())

# @dp.message_handler(filters.Text(equals='Результаты за неделю'))
# async def echo(message: types.Message):
#     await message.answer(week_result())


@dp.message_handler(filters.Text(equals='demo'))
async def echo(message: types.Message):
    await message.answer('тут будет demo-дашборд')



###
# Ветка 'create profile'
# Введи имя
@dp.message_handler(filters.Text(equals='create profile'))
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """

    # Set state
    await Form.name.set()
    await message.reply("Как тебя зовут?")



# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()

    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply("Введи wb-токен")

### Введи токен
@dp.message_handler(state=Form.wb_token)
async def process_from_dt(message: types.Message, state: FSMContext):
    """
    Process wb_token
    """
    async with state.proxy() as data:
        data['wb_token'] = message.text
    # await edit_profile(state, user_id=message.from_user.id)

    await Form.next()
    await message.reply("Отлично, и последнее - давай зададим дату числом в формате 'ГГГГММДД'")

# from_dt
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.from_dt)
async def process_from_dt_invalid(message: types.Message):
    """
    If from_dt is invalid
    """
    return await message.reply("Дата должна быть представлена в виде числа в формате 'ГГГГММДД'\nДавай еще раз")

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.from_dt)
async def process_from_dt(message: types.Message, state: FSMContext):
    # Update state and data
    # await Form.next()
    await state.update_data(from_dt=int(message.text))

    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Посмотреть на результаты", "--")
    markup.add("Other")

    async with state.proxy() as data:
        data['from_dt'] = message.text
    await edit_profile(state, user_id=message.from_user.id)

    await edit_profile(state, user_id=message.from_user.id)
    await message.reply("Отлично, че там есть?", reply_markup=markup)




    # Finish conversation
    await state.finish()
###

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
