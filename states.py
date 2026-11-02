
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


class AdminAddApp(StatesGroup):
    name = State()
    logo = State()
    category = State()
    download_link = State()
    website = State()
    description = State()
    features = State()
    platform = State()
    earning_method = State()
    min_withdrawal = State()
    countries = State()
    confirm = State()


class AdminAddLoot(StatesGroup):
    title = State()
    reward_details = State()
    eligibility = State()
    steps = State()
    expiry_date = State()
    terms = State()
    official_link = State()
    confirm = State()


class AdminAddNews(StatesGroup):
    title = State()
    content = State()
    category = State()
    app_name = State()
    source = State()
    confirm = State()


# Edit App
class AdminEditApp(StatesGroup):
    select_field = State()
    value = State()


# Edit Loot
class AdminEditLoot(StatesGroup):
    select_field = State()
    value = State()


# Edit News
class AdminEditNews(StatesGroup):
    select_field = State()
    value = State()
    
