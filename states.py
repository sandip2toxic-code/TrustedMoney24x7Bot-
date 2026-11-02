from aiogram.fsm.state import State, StatesGroup


class PromoteTelegram(StatesGroup):
    promo_type = State()
    name = State()
    link = State()
    description = State()
    target_audience = State()
    package = State()
    duration = State()
    additional = State()
    contact = State()
    confirm = State()


class PromoteApp(StatesGroup):
    app_type = State()
    name = State()
    logo = State()
    category = State()
    download_link = State()
    website = State()
    description = State()
    features = State()
    target_audience = State()
    package = State()
    duration = State()
    budget = State()
    contact = State()
    additional = State()
    confirm = State()


class CreateBot(StatesGroup):
    bot_type = State()
    name = State()
    features = State()
    purpose = State()
    design = State()
    budget = State()
    delivery_time = State()
    additional = State()
    contact = State()
    confirm = State()
