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

bot = Bot(token="1016195496:AAEUoyFq40hbT6rd9oNSK-JoTfv1FLg8d8w", parse_mode=types.ParseMode.HTML)
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

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

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


#Property Devision
#Area
@dp.message_handler(state=states.Area.started)
async def sale_area_room_count_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]
    
    if _type!="search":
    
        if recieved_text.isdigit():
            try:
                async with state.proxy() as data:
                    _type = data["online"]

                await states.Area.state.set()

                async with state.proxy() as data:
                    _type = data["type"]
                    data["{} room_count".format(_type)] = recieved_text

                # text = Messages(user)["area_rooms_added"]
                text = Messages(user, lan)["prop_state"]
                # "Состояние ремонта недвижимости (например: Евро ремонт)"
                markup = keyboards.BackKeyboard(user, lan)
                await bot.send_message(user, text, reply_markup=markup)

            except Exception as e:

                await states.Area.square.set()

                async with state.proxy() as data:
                    _type = data["type"]
                    data["{} room_count".format(_type)] = recieved_text

                text = Messages(user, lan)["area_rooms_added"]
                markup = keyboards.BackKeyboard(user, lan)
                await bot.send_message(user, text, reply_markup=markup)

        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        async with state.proxy() as data:
            _type = data["online"]

        await states.Area.state.set()

        async with state.proxy() as data:
            _type = data["type"]
            data["{} room_count".format(_type)] = recieved_text

        # text = Messages(user)["area_rooms_added"]
        text = Messages(user, lan)["prop_state"]
        # "Состояние ремонта недвижимости (например: Евро ремонт)"
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Area.square)
async def sale_area_square_handler(message: types.Message, state: FSMContext):

    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]

    data = recieved_text.replace(",", "")
    data = data.replace(".", "")

    if _type != "search":

        if data.isdigit():
            recieved_text = recieved_text.replace(",", ".")

            await states.Area.area.set()

            async with state.proxy() as data:
                _type = data["type"]
                data["{} square".format(_type)] = recieved_text

            text = Messages(user, lan)["area_square_added"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        recieved_text = recieved_text.replace(",", ".")

        await states.Area.area.set()

        async with state.proxy() as data:
            _type = data["type"]
            data["{} square".format(_type)] = recieved_text

        text = Messages(user, lan)["area_square_added"]
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Area.area)
async def sale_area_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]

    data = recieved_text.replace(",","")
    data = data.replace(".","")

    if _type != "search":

        if data.isdigit():
            recieved_text = recieved_text.replace(",",".")

            await states.User.photo.set()

            async with state.proxy() as data:
                _type = data["type"]
                data["{} area".format(_type)] = recieved_text

            # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_photo.mp4")))

            text = Messages(user, lan)["photo1"]
            await bot.send_message(user, text, reply_markup=None)

            text = Messages(user, lan)["photo2"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        recieved_text = recieved_text.replace(",",".")

        async with state.proxy() as data:
            _type = data["type"]
            data["{} area".format(_type)] = recieved_text

        text = Messages(user, lan)["price"]
        await states.User.priceSet.set()

        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


#Flat
@dp.message_handler(state=states.Flat.started)
async def sale_flat_room_count_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]
    
    if _type != "search":
        if recieved_text.isdigit():
            try:
                async with state.proxy() as data:
                    _type = data["online"]

                await states.Flat.state.set()

                async with state.proxy() as data:
                    _type = data["type"]
                    data["{} room_count".format(_type)] = recieved_text

                # text = Messages(user)["area_rooms_added"]
                text = Messages(user, lan)["prop_state"]
                markup = keyboards.BackKeyboard(user, lan)
                await bot.send_message(user, text, reply_markup=markup)

            except Exception as e:

                await states.Flat.square.set()

                async with state.proxy() as data:
                    _type = data["type"]
                    data["{} room_count".format(_type)] = recieved_text

                text = Messages(user, lan)["flat_rooms_added"]
                markup = keyboards.BackKeyboard(user, lan)
                await bot.send_message(user, text, reply_markup=markup)
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        async with state.proxy() as data:
            _type = data["online"]

        await states.Flat.state.set()

        async with state.proxy() as data:
            _type = data["type"]
            data["{} room_count".format(_type)] = recieved_text

        # text = Messages(user)["area_rooms_added"]
        text = Messages(user, lan)["prop_state"]
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Flat.state)
async def sale_flat_state_handler(message: types.Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"
    
    user = message.from_user.id
    recieved_text = message.text

    async with state.proxy() as data:
        _type = data["type"]
        data["{} prop_state".format(_type)] = recieved_text
        
    await states.Flat.square.set()

    # text = Messages(user)["area_square_added"]
    text = Messages(user, lan)["flat_rooms_added"]
    markup = keyboards.BackKeyboard(user, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Flat.square)
async def sale_flat_square_handler(message: types.Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    user = message.from_user.id
    recieved_text = message.text

    async with state.proxy() as data:
        _type = data["type"]

    data = recieved_text.replace(",", "")
    data = data.replace(".", "")

    if _type != "search":
        if data.isdigit():
            recieved_text = recieved_text.replace(",", ".")

            async with state.proxy() as data:
                _type = data["type"]
                data["{} square".format(_type)] = recieved_text

            await states.Flat.main_floor.set()

            text = Messages(user, lan)["main_floor"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=None)

        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        recieved_text = recieved_text.replace(",", ".")

        async with state.proxy() as data:
            _type = data["type"]
            data["{} square".format(_type)] = recieved_text

        await states.Flat.main_floor.set()

        text = Messages(user, lan)["main_floor"]
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=None)


@dp.message_handler(state=states.Flat.main_floor)
async def sale_flat_main_floor_handler(message: types.Message, state: FSMContext):
    
    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    user = message.from_user.id
    recieved_text = message.text
    async with state.proxy() as data:
        _type = data["type"]
    
    if _type!="search":
        if recieved_text.isdigit():

            await states.Flat.floor.set()

            async with state.proxy() as data:
                _type = data["type"]
                data["{} main_floor".format(_type)] = recieved_text

            text = Messages(user, lan)["floor"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=None)
            
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        await states.Flat.floor.set()

        async with state.proxy() as data:
            _type = data["type"]
            data["{} main_floor".format(_type)] = recieved_text

        text = Messages(user, lan)["floor"]
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=None)

@dp.message_handler(state=states.Flat.floor)
async def sale_flat_floor_handler(message: types.Message, state: FSMContext):
    
    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    user = message.from_user.id
    recieved_text = message.text
    async with state.proxy() as data:
        _type = data["type"]
    
    if _type!="search":
        if recieved_text.isdigit():

            await states.User.photo.set()

            async with state.proxy() as data:
                _type = data["type"]
                data["{} floor".format(_type)] = recieved_text

            # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_photo.mp4")))

            text = Messages(user, lan)["photo1"]
            await bot.send_message(user, text, reply_markup=None)

            text = Messages(user, lan)["photo2"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
            
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:

        async with state.proxy() as data:
            _type = data["type"]
            data["{} floor".format(_type)] = recieved_text

        text = Messages(user, lan)["price"]
        await states.User.priceSet.set()

        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

#Land
@dp.message_handler(state=states.Land.square)
async def sale_land_area_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text
    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]

    data = recieved_text.replace(",", "")
    data = data.replace(".", "")
    
    if _type!="search":
        if data.isdigit():
            try:
                async with state.proxy() as data:
                    _type = data["online"]

                await states.Land.state.set()

                async with state.proxy() as data:
                    _type = data["type"]
                    data["{} area".format(_type)] = recieved_text

                # text = Messages(user)["area_rooms_added"]
                text = Messages(user, lan)["prop_state"]
                markup = keyboards.BackKeyboard(user, lan)
                await bot.send_message(user, text, reply_markup=markup)
            except Exception as e:
                recieved_text = recieved_text.replace(",",".")

                await states.User.photo.set()

                async with state.proxy() as data:
                    _type = data["type"]
                    data["{} area".format(_type)] = recieved_text

                # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_photo.mp4")))

                text = Messages(user, lan)["photo1"]
                await bot.send_message(user, text, reply_markup=None)

                text = Messages(user, lan)["photo2"]
                markup = keyboards.BackKeyboard(user, lan)
                await bot.send_message(user, text, reply_markup=markup)
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        async with state.proxy() as data:
            _type = data["online"]

        await states.Land.state.set()

        async with state.proxy() as data:
            _type = data["type"]
            data["{} area".format(_type)] = recieved_text

        # text = Messages(user)["area_rooms_added"]
        text = Messages(user, lan)["prop_state"]
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Land.state)
async def sale_land_state_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]
        data["{} prop_state".format(_type)] = recieved_text
        
    if _type!="search":

        await states.User.photo.set()
        # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_photo.mp4")))

        text = Messages(user, lan)["photo1"]
        await bot.send_message(user, text, reply_markup=None)

        text = Messages(user, lan)["photo2"]
        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)
    
    else:

        text = Messages(user, lan)["price"]
        await states.User.priceSet.set()
        

        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

#Free Area
@dp.message_handler(state=states.Free_area.area)
async def sale_free_area_square_handler(message: types.Message, state: FSMContext):

    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]

    data = recieved_text.replace(",","")
    data = data.replace(".","")
    
    if _type!="search":

        if data.isdigit():

            await states.Free_area.square.set()

            async with state.proxy() as data:
                _type = data["type"]
                data["{} square".format(_type)] = recieved_text

            text = Messages(user, lan)["free_area_square_added"]
            markup = keyboards.BackNextKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        await states.Free_area.square.set()

        async with state.proxy() as data:
            _type = data["type"]
            data["{} square".format(_type)] = recieved_text

        text = Messages(user, lan)["free_area_square_added"]
        markup = keyboards.BackNextKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Free_area.square)
async def sale_free_area_area_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"
    
    async with state.proxy() as data:
        _type = data["type"]

    data = recieved_text.replace(",", "")
    data = data.replace(".", "")
    
    if _type != "search":

        if data.isdigit():
            recieved_text = recieved_text.replace(",", ".")

            await states.User.photo.set() 

            async with state.proxy() as data:
                _type = data["type"]
                data["{} area".format(_type)] = recieved_text

            # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_photo.mp4")))

            text = Messages(user, lan)["photo1"]
            await bot.send_message(user, text, reply_markup=None)

            text = Messages(user, lan)["photo2"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)

        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        recieved_text = recieved_text.replace(",",".")

        

        async with state.proxy() as data:
            _type = data["type"]
            data["{} area".format(_type)] = recieved_text

        text = Messages(user, lan)["price"]
        await states.User.priceSet.set()

        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


#Photo recieve
@dp.message_handler(state=states.User.photo, content_types=types.ContentType.PHOTO)
async def sale_area_photo_added_handler(message: types.Message, state: FSMContext):

    user = message.from_user.id

    count = len(os.listdir(os.path.join(os.getcwd(), "Users", str(user))))

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if count + 1 < 10:

        photo = await bot.get_file(message.photo[-1].file_id)
        await photo.download(os.path.join(os.getcwd(), "Users", str(user), "{}.jpg".format(message.photo[-1].file_id)))

        count = len(os.listdir(os.path.join(os.getcwd(), "Users", str(user))))
        text = Messages(user, lan)["photo3"].format(count)

        markup = keyboards.BackNextKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)
    else:
        photo = await bot.get_file(message.photo[-1].file_id)
        await photo.download(os.path.join(os.getcwd(), "Users", str(user), "{}.jpg".format(message.photo[-1].file_id)))

        text = Messages(user, lan)["price"]
        await states.User.priceSet.set()

        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.User.priceSet)
async def user_ammount_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"
    
    async with state.proxy() as data:
        _type = data["type"]

    data = recieved_text.replace(".", "")
    data = data.replace(",", "")
    data = data.replace(" ", "")
    data = data.replace("у", "")
    data = data.replace("е", "")
    data = data.replace("y", "")
    data = data.replace("e", "")
    data = data.replace("-", "")
    
    if _type != "search":

        if data.isdigit():
            await states.User.add_info.set()
            async with state.proxy() as data1:
                data1['ammount'] = data

            text = Messages(user, lan)["ammount_set"]
            markup = keyboards.BackNextKeyboard(user, lan)

            await bot.send_message(user, text, reply_markup=markup)
        else:
            text = Messages(user, lan)["digits_only"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
    else:
        await states.User.add_info.set()
        async with state.proxy() as data1:
            data1['ammount'] = recieved_text

        text = Messages(user, lan)["ammount_set"]
        markup = keyboards.BackNextKeyboard(user, lan)

        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.User.add_info)
async def user_info_handler(message: types.Message, state: FSMContext):
    user = message.from_user.id
    recieved_text = message.text

    if not recieved_text in ["Дальше", "Ўтказиб юбориш"]:

        await states.User.contact.set()
        async with state.proxy() as data:
            data['add_info'] = recieved_text

        text = Messages(user, lan)["contacts"]
        markup = keyboards.ContactKeyboard(user, lan)
        # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_contact.mp4")))


        await bot.send_message(user, text, reply_markup=markup)
    else:
        # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_contact.mp4")))

        text = Messages(user, lan)["contacts"]
        await states.User.contact.set()
        async with state.proxy() as data:
            data['add_info'] = "None"

        markup = keyboards.ContactKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Area.state)
async def sale_area_state_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    async with state.proxy() as data:
        _type = data["type"]
        data["{} prop_state".format(_type)] = recieved_text
        
    await states.Area.square.set()

    text = Messages(user, lan)["area_rooms_added"]
    markup = keyboards.BackKeyboard(user)
    await bot.send_message(user, text, reply_markup=markup)

#rent section
@dp.message_handler(state=states.Rent.started)
async def rent_handler(message: types.Message):
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if recieved_text in ["Подать объявление", "Эълон бериш"]:
        await states.Rent.announcement.set()

        text = Messages(user, lan)['choose_action_rent_inner']
        markup = keyboards.SaleSearchAndannouncementKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)
    elif recieved_text in ["Поиск 🔍", "Қидирув 🔍"]:
        await states.Rent.search.set()

        # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "after_search.mp4")))
        

        text = Messages(user, lan)['choose_action_search']
        markup = keyboards.SaleSearchAndannouncementKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Rent.announcement)
async def rent_type_choosen_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if recieved_text in keyboards.SaleSearchAndannouncementKeyboardList:

        MessageDict = {'🏠 Участок': Messages(user, lan)['area'], '🏬 Квартира': Messages(user, lan)['flat'], '🏡 Участок земли': Messages(user, lan)['land'], '🏗 Коммерческая недвижимость': Messages(user, lan)['free_area'],
                        '🏠 Ховли': Messages(user, lan)['area'], '🏡 Ер': Messages(user, lan)['land'], '🏗 Тижорат кўчмас мулки': Messages(user, lan)['free_area'] }

        await states.Rent.type_choosen.set()

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


@dp.message_handler(state=states.Rent.type_choosen)
async def rent_title_handler(message: types.Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"
    
    user = message.from_user.id
    recieved_text = message.text

    await states.Rent.title_added.set()

    async with state.proxy() as data:
        data["rent title"] = recieved_text

    text = Messages(user, lan)["title_added"]
    markup = keyboards.MainRegionKeyboard(user, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Rent.title_added)
async def sale_region_handler(message: types.Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"
    
    user = message.from_user.id
    recieved_text = message.text

    await states.Rent.main_region_added.set()

    async with state.proxy() as data:
        data["rent main_region"] = recieved_text

    text = Messages(user, lan)["title_added"]
    markup = keyboards.RegionKeyboard(user, recieved_text, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Rent.main_region_added)
async def sale_region_handler(message: types.Message, state: FSMContext):

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"
    
    user = message.from_user.id
    recieved_text = message.text

    await states.Rent.region_added.set()

    async with state.proxy() as data:
        data["rent region"] = recieved_text

    text = Messages(user, lan)["region_added"]
    markup = keyboards.BackKeyboard(user, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Rent.region_added)
async def rent_reference_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    await states.Rent.reference.set()

    async with state.proxy() as data:
        data["rent reference"] = recieved_text

    # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_geo.mp4")))

    text = Messages(user, lan)["geo1"]
    await bot.send_message(user, text)

    text = Messages(user, lan)["geo2"]
    await bot.send_message(user, text)

    text = Messages(user, lan)["geo3"]
    markup = keyboards.LocationKeyboard(user, lan)
    await bot.send_message(user, text, reply_markup=markup)


@dp.message_handler(state=states.Rent.reference, content_types=types.ContentType.LOCATION)
async def rent_location_added_handler(message: types.Message, state: FSMContext):
    
    user = message.from_user.id
    recieved_text = message.text

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    await states.Rent.location_True_or_False.set()

    async with state.proxy() as data:
        data["rent location"] = "{} {}".format(message.location.latitude, message.location.longitude)

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


#next button handler
@dp.message_handler(text="Дальше", state="*")
async def next_button_handler(message: types.Message, state: FSMContext):
    user = message.from_user.id
    my_state = await dp.current_state(user=message.from_user.id).get_state()

    try:
        async with state.proxy() as data:
            lan = data['lan']
    except Exception as e:
        lan = "ru"

    if my_state in "Rent:reference":
        user = message.from_user.id
        recieved_text = message.text

        await states.Rent.location_True_or_False.set()

        async with state.proxy() as data:
            data["rent location"] = "0 0"

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
    elif my_state in "Sale:reference":
        user = message.from_user.id
        recieved_text = message.text

        await states.Sale.location_True_or_False.set()

        async with state.proxy() as data:
            data["sale location"] = "0 0"

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

    elif my_state in "User:photo":

        text = Messages(user, lan)["price"]
        await states.User.priceSet.set()

        markup = keyboards.BackKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)
    
    elif my_state in "Edit:photoNew":

        async with state.proxy() as data:

            _type = data['type']
            
            _property = data['property']
            _title = data['{} title'.format(_type)]
            _region = data['{} region'.format(_type)]
            _reference = data['{} reference'.format(_type)]
            try:
                _location = data['{} location'.format(_type)]
            except Exception as e:
                _location = "0 0"
            try:
                _room_count = data['{} room_count'.format(_type)]
            except Exception as e:
                _room_count = 0

            try:
                _square = data['{} square'.format(_type)]
            except Exception as e:
                _square = 0

            
            
            try:
                _area = data['{} area'.format(_type)]
            except Exception as e:
                _area = 0
            
            try:
                _state = data['{} state'.format(_type)]
            except Exception as e:
                _state = ""

            try:
                _main_floor = data['{} main_floor'.format(_type)]
            except Exception as e:
                _main_floor = 0

            try:
                _floor = data['{} floor'.format(_type)]
            except Exception as e:
                _floor = 0

            _ammount = data['ammount']
            _add_info = data['add_info']
            _contact = data['phone']



            user_data = []
            user_data.append(_type)
            user_data.append(_property)
            user_data.append(_title)
            user_data.append(_region)
            user_data.append(_reference)
            user_data.append(_location)
            user_data.append(_room_count)
            user_data.append(_square)
            user_data.append(_area)
            user_data.append(_state)
            user_data.append(_ammount)
            user_data.append(_add_info)
            user_data.append(_contact)
            user_data.append(_main_floor)
            user_data.append(_floor)

            try:
                _type = data['type']
                _online_status = data["online"]
                user_data.append(data['master'])
                try:
                    user_data.append(data['{} prop_state'.format(_type)])
                except Exception as e:
                    user_data.append("")

                text = OnlineGenerateEndText(user_data, user)
            except Exception as e:
                print("\n\n{}\n\n".format(e))

                text = GenerateEndText(user_data, False, user)


        await states.User.edit.set()

        if _location != "0 0":
            X = _location.split(" ")[0]
            Y = _location.split(" ")[1]
            await bot.send_chat_action(user, action="find_location")

            await bot.send_location(user, latitude=X, longitude=Y)

        photoes = os.listdir(os.getcwd()+"/Users/" + str(user)+"/")
        markup = keyboards.EditApplyKeyboard(user, lan)

        if len(photoes)!=0:

            media = []
            for photo in photoes:
                media.append(InputMediaPhoto(str(photo).replace(".jpg", "")))
            

            if len(media)!=1:
                await bot.send_chat_action(user, action="upload_photo")
                await bot.send_media_group(user, media)
            else:
                await bot.send_chat_action(user, action="upload_photo")
                await bot.send_photo(user, str(photoes[0]).replace(".jpg",""))
        await bot.send_message(user, text, reply_markup=markup)

        
    
    elif my_state in "User:add_info":

        # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_contact.mp4")))


        text = Messages(user, lan)["contacts"]
        await states.User.contact.set()

        markup = keyboards.ContactKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

    elif my_state in "Free_area:area":
        await states.Free_area.square.set()

        text = Messages(user, lan)["free_area_square_added"]
        markup = keyboards.BackNextKeyboard(user, lan)
        await bot.send_message(user, text, reply_markup=markup)

    elif my_state in "Free_area:square":
        async with state.proxy() as data:
            _type = data['type']

        if _type!="search":
            # await bot.send_video(user, InputFile(os.path.join(os.getcwd(), "Instructions", "how_to_photo.mp4")))

            await states.User.photo.set() 

            text = Messages(user, lan)["photo1"]
            await bot.send_message(user, text, reply_markup=None)

            text = Messages(user, lan)["photo2"]
            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)
        
        else:

            text = Messages(user, lan)["price"]
            await states.User.priceSet.set()
            

            markup = keyboards.BackKeyboard(user, lan)
            await bot.send_message(user, text, reply_markup=markup)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    if not os.path.exists(os.path.join(os.getcwd(), "Users")):
        os.mkdir(os.path.join(os.getcwd(), "Users"), 0o777)
        
    executor.start_polling(dp, on_shutdown=shutdown)

