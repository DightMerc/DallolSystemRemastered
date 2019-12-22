from aiogram.dispatcher.filters.state import State, StatesGroup


class User(StatesGroup):
    started = State()
    languageSet = State()

class Search(StatesGroup):
    started = State() 
    price = State()
    region = State()
    main_region = State()
    room_count = State()
    area = State()

    set = State()

class Edit(StatesGroup):
    started = State()
    second = State()
    property = State()
    photo = State()
    photoNew = State()

class Sale(StatesGroup):
    started = State()
    announcement = State()
    search = State()
    type_choosen = State()
    title_added = State()
    main_region_added = State()
    region_added = State()
    reference = State()
    location_True_or_False = State()


class Rent(StatesGroup):
    started = State()
    announcement = State()
    search = State()
    type_choosen = State()
    title_added = State()
    region_added = State()
    reference = State()
    location_True_or_False = State()
    main_region_added = State()


class Online(StatesGroup):
    started = State()
    mode = State()
    order = State()