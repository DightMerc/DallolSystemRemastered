import core

import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InputFile
from aiogram.types import ReplyKeyboardRemove

import keyboards
import os
import aioredis
from messages import Messages
import states

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                     level=logging.DEBUG)

bot = Bot(token="796303915:AAF4MJs2lqEYxUWtK-7VSjYVWGjeLhNEXnU", parse_mode=types.ParseMode.HTML)
# storage = RedisStorage2(db=8)
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'], state="*")
async def process_start_command(message: types.Message, state: FSMContext):
    user = message.from_user.id

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"


    if not os.path.exists(os.path.join(os.getcwd(), "Users", str(user))):
        os.mkdir(os.path.join(os.getcwd(), "Users", str(user)), 0o777)

    core.CreateNewUser(int(user))

    await state.set_data({})
    
    await states.User.started.set()
    
    await bot.send_chat_action(user, action="typing")

    text = Messages(user, lan)['start']
    text = text.replace("{}", message.from_user.first_name)
    markup = None
    await bot.send_message(user, text, reply_markup=markup)

    text = Messages(user, lan)['language']
    markup = keyboards.LanguageKeyboard(user)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.User.started)
async def language_handler(message: types.Message, state: FSMContext):
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if recieved_text == "Русский язык" or recieved_text == "Ўзбек тили":
        if recieved_text == "Русский язык":
            async with state.proxy() as data:
                lan = "ru"
                data['lan'] = lan
                
        else:
            async with state.proxy() as data:
                lan = "uz"
                data['lan'] = lan

        await states.User.languageSet.set()

        photoes = os.listdir(os.path.join(os.getcwd(), "Users", str(user)))
        for a in photoes:
            os.remove(os.path.join(os.getcwd(), "Users", str(user), str(a)))

        text = Messages(user, lan)['choose_action_after_language']
        markup = keyboards.MenuKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.User.languageSet)
async def menu_handler(message: types.Message, state: FSMContext):
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if recieved_text in ["Продажа", "Сотув"]:
        async with state.proxy() as data:
            data['type'] = "sale"

        await states.Sale.started.set()

        text = Messages(user, lan)['choose_action_sale']
        markup = keyboards.SaleAndRentKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

    elif recieved_text in ["Аренда", "Ижара"]:
        async with state.proxy() as data:
            data['type'] = "rent"

        await states.Rent.started.set()

        text = Messages(user, lan)['choose_action_rent']
        markup = keyboards.SaleAndRentKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

    elif recieved_text == "Онлайн риелтор":
        async with state.proxy() as data:
            data['online'] = "True"

        await states.Online.started.set()

        text = Messages(user, lan)['choose_action_online']
        markup = keyboards.OnlineSaleAndRentKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

    elif recieved_text in ["Помощь", "Йордам"]:
        
        await states.User.help.set()

        text = Messages(user, lan)['choose_action_help']
        markup = keyboards.HelpKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


#sale section
@dp.message_handler(state=states.Sale.started)
async def sale_handler(message: types.Message):
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if recieved_text in ["Подать объявление", "Эълон бериш"]:
        await states.Sale.announcement.set()

        text = Messages(user, lan)['choose_action_sale_inner']
        markup = keyboards.SaleSearchAndannouncementKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

    elif recieved_text in ["Поиск 🔍", "Қидирув 🔍"]:
        await states.Sale.search.set()

        text = Messages(user, lan)['choose_action_search']
        markup = keyboards.SaleSearchAndannouncementKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Sale.announcement)
async def sale_type_choosen_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if recieved_text in keyboards.SaleSearchAndannouncementKeyboardList:

        MessageDict = {
            '🏠 Участок': Messages(user, lan)['area'], 
            '🏬 Квартира': Messages(user, lan)['flat'], 
            '🏡 Участок земли': Messages(user, lan)['land'], 
            '🏗 Коммерческая недвижимость': Messages(user, lan)['free_area'],
            '🏠 Ховли': Messages(user, lan)['area'], 
            '🏡 Ер': Messages(user, lan)['land'], 
            '🏗 Тижорат кўчмас мулки': Messages(user, lan)['free_area'] 
            }

        await states.Sale.type_choosen.set()

        if recieved_text in ['🏠 Участок', "🏠 Ховли"]:
            prop = "Участок"
        if recieved_text in ["🏬 Квартира"]:
            prop = "Квартира"
        if recieved_text in ["🏡 Участок земли", "🏡 Ер"]:
            prop = "Участок земли"
        if recieved_text in ["🏗 Коммерческая недвижимость", "🏗 Тижорат кўчмас мулки"]:
            prop = "Коммерческая недвижимость"

        

        async with state.proxy() as data:
            data['property'] = prop
            
        text = MessageDict[recieved_text]
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

    
@dp.message_handler(state=states.Sale.type_choosen)
async def sale_title_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    await states.Sale.title_added.set()

    async with state.proxy() as data:
        data["sale title"] = recieved_text

    text = Messages(user, lan)["title_added"]
    markup = keyboards.MainRegionKeyboard(user, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Sale.title_added)
async def sale_region_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    await states.Sale.main_region_added.set()

    async with state.proxy() as data:
        data["sale main_region"] = recieved_text

    text = Messages(user, lan)["title_added"]
    markup = keyboards.RegionKeyboard(user, recieved_text, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Sale.main_region_added)
async def sale_region_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    await states.Sale.region_added.set()

    async with state.proxy() as data:
        data["sale region"] = recieved_text

    text = Messages(user, lan)["region_added"]
    markup = keyboards.BackKeyboard(user, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Sale.region_added)
async def sale_reference_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    await states.Sale.reference.set()

    async with state.proxy() as data:
        data["sale reference"] = recieved_text

    text = Messages(user, lan)["geo1"]
    await bot.send_message(user, text)

    text = Messages(user, lan)["geo2"]
    await bot.send_message(user, text)

    text = Messages(user, lan)["geo3"]
    markup = keyboards.LocationKeyboard(user, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Sale.reference, content_types=types.ContentType.LOCATION)
async def sale_location_added_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    await states.Sale.location_True_or_False.set()

    async with state.proxy() as data:
        data["sale location"] = "{} {}".format(message.location.latitude, message.location.longitude)

        _type = data['property']

    if _type == "Участок":
        await states.Area.started.set()
        text = Messages(user, lan)["area_started"]
        markup = keyboards.RoomCountKeyboard(user, lan)

    if _type == "Квартира":
        await states.Flat.started.set()
        text = Messages(user, lan)["flat_started"]
        markup = keyboards.RoomCountKeyboard(user, lan)

    if _type == "Участок земли":
        await states.Land.square.set()
        text = Messages(user, lan)["land_started"]
        markup = keyboards.BackKeyboard(user, lan)

    if _type == "Коммерческая недвижимость":
        await states.Free_area.area.set()

        text = Messages(user, lan)["flat_rooms_added"]
        markup = keyboards.BackNextKeyboard(user, lan)


    await bot.send_message(user, text, reply_markup=markup)

#sale devision


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    if not os.path.exists(os.getcwd()+"/Users/"):
        os.mkdir(os.getcwd()+"/Users/", 0o777)
        
    executor.start_polling(dp, on_shutdown=shutdown)

