from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from datetime import datetime
from sqlalchemy import select

from config import OWNER_ID
from states import (
    AdminAddApp,
    AdminAddLoot,
    AdminAddNews,
    AdminEditApp,
    AdminEditLoot,
    AdminEditNews
)
from keyboards import cancel_kb, admin_main_kb
from database import async_session, AppListing, Loot, News

router = Router()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def back_button(callback_data: str):
    return [
        InlineKeyboardButton(
            text="🔙 Back",
            callback_data=callback_data
        )
    ]


# =========================
# ADMIN MENUS
# =========================

@router.callback_query(F.data == "admin_apps")
async def admin_apps_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add New App", callback_data="add_app")],
        [InlineKeyboardButton(text="📋 Manage Apps", callback_data="list_apps")],
        back_button("admin_dashboard")
    ])

    await callback.message.edit_text(
        "📱 <b>Manage Apps</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_loots")
async def admin_loots_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add New Loot", callback_data="add_loot")],
        [InlineKeyboardButton(text="📋 Manage Loots", callback_data="list_loots")],
        back_button("admin_dashboard")
    ])

    await callback.message.edit_text(
        "🎁 <b>Manage Loots</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_news")
async def admin_news_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add News", callback_data="add_news")],
        [InlineKeyboardButton(text="📋 Manage News", callback_data="list_news")],
        back_button("admin_dashboard")
    ])

    await callback.message.edit_text(
        "📰 <b>Manage News</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()
    # =========================
# LIST APPS
# =========================

@router.callback_query(F.data == "list_apps")
async def list_apps(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    async with async_session() as session:
        result = await session.execute(
            select(AppListing).order_by(AppListing.id.desc()).limit(20)
        )
        apps = result.scalars().all()

    buttons = []

    for app in apps:
        buttons.append([
            InlineKeyboardButton(
                text=f"📱 {app.name} (ID: {app.id})",
                callback_data=f"manage_app:{app.id}"
            )
        ])

    buttons.append(back_button("admin_apps"))

    await callback.message.edit_text(
        "📱 <b>Apps List</b>\n\nSelect an app to manage:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()


# =========================
# LIST LOOTS
# =========================

@router.callback_query(F.data == "list_loots")
async def list_loots(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    async with async_session() as session:
        result = await session.execute(
            select(Loot).order_by(Loot.id.desc()).limit(20)
        )
        loots = result.scalars().all()

    buttons = []

    for loot in loots:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎁 {loot.title} (ID: {loot.id})",
                callback_data=f"manage_loot:{loot.id}"
            )
        ])

    buttons.append(back_button("admin_loots"))

    await callback.message.edit_text(
        "🎁 <b>Loots List</b>\n\nSelect a loot to manage:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()


# =========================
# LIST NEWS
# =========================

@router.callback_query(F.data == "list_news")
async def list_news(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    async with async_session() as session:
        result = await session.execute(
            select(News).order_by(News.id.desc()).limit(20)
        )
        news_items = result.scalars().all()

    buttons = []

    for news in news_items:
        buttons.append([
            InlineKeyboardButton(
                text=f"📰 {news.title} (ID: {news.id})",
                callback_data=f"manage_news:{news.id}"
            )
        ])

    buttons.append(back_button("admin_news"))

    await callback.message.edit_text(
        "📰 <b>News List</b>\n\nSelect news to manage:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()
    # =========================
# MANAGE APP MENU
# =========================

@router.callback_query(F.data.startswith("manage_app:"))
async def manage_app(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(AppListing, item_id)

    if not item:
        await callback.answer("App not found", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit App", callback_data=f"edit_app:{item_id}")],
        [InlineKeyboardButton(text="🗑 Delete App", callback_data=f"delete_app:{item_id}")],
        back_button("list_apps")
    ])

    await callback.message.edit_text(
        f"📱 <b>{item.name}</b>\n\n"
        f"Category: {item.category}\n"
        f"Platform: {item.platform}",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


# =========================
# MANAGE LOOT MENU
# =========================

@router.callback_query(F.data.startswith("manage_loot:"))
async def manage_loot(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(Loot, item_id)

    if not item:
        await callback.answer("Loot not found", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit Loot", callback_data=f"edit_loot:{item_id}")],
        [InlineKeyboardButton(text="🗑 Delete Loot", callback_data=f"delete_loot:{item_id}")],
        back_button("list_loots")
    ])

    await callback.message.edit_text(
        f"🎁 <b>{item.title}</b>\n\n"
        f"Reward: {item.reward_details}",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


# =========================
# MANAGE NEWS MENU
# =========================

@router.callback_query(F.data.startswith("manage_news:"))
async def manage_news(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(News, item_id)

    if not item:
        await callback.answer("News not found", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit News", callback_data=f"edit_news:{item_id}")],
        [InlineKeyboardButton(text="🗑 Delete News", callback_data=f"delete_news:{item_id}")],
        back_button("list_news")
    ])

    await callback.message.edit_text(
        f"📰 <b>{item.title}</b>\n\n"
        f"Category: {item.category}",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()
    # =========================
# DELETE APP CONFIRMATION
# =========================

@router.callback_query(F.data.startswith("delete_app:"))
async def confirm_delete_app(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(AppListing, item_id)

    if not item:
        await callback.answer("App not found", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Yes, Delete",
            callback_data=f"confirm_delete_app:{item_id}"
        )],
        [InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=f"manage_app:{item_id}"
        )]
    ])

    await callback.message.edit_text(
        f"⚠️ <b>Delete App?</b>\n\n{item.name}\n\nAre you sure?",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


# =========================
# DELETE LOOT CONFIRMATION
# =========================

@router.callback_query(F.data.startswith("delete_loot:"))
async def confirm_delete_loot(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(Loot, item_id)

    if not item:
        await callback.answer("Loot not found", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Yes, Delete",
            callback_data=f"confirm_delete_loot:{item_id}"
        )],
        [InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=f"manage_loot:{item_id}"
        )]
    ])

    await callback.message.edit_text(
        f"⚠️ <b>Delete Loot?</b>\n\n{item.title}\n\nAre you sure?",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


# =========================
# DELETE NEWS CONFIRMATION
# =========================

@router.callback_query(F.data.startswith("delete_news:"))
async def confirm_delete_news(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(News, item_id)

    if not item:
        await callback.answer("News not found", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Yes, Delete",
            callback_data=f"confirm_delete_news:{item_id}"
        )],
        [InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=f"manage_news:{item_id}"
        )]
    ])

    await callback.message.edit_text(
        f"⚠️ <b>Delete News?</b>\n\n{item.title}\n\nAre you sure?",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()
    # =========================
# CONFIRM DELETE APP
# =========================

@router.callback_query(F.data.startswith("confirm_delete_app:"))
async def confirm_delete_app_final(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(AppListing, item_id)

        if not item:
            await callback.answer("App not found", show_alert=True)
            return

        await session.delete(item)
        await session.commit()

    await callback.answer("App deleted successfully")
    await callback.message.edit_text(
        "✅ <b>App deleted successfully.</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            back_button("list_apps")
        ]),
        parse_mode="HTML"
    )


# =========================
# CONFIRM DELETE LOOT
# =========================

@router.callback_query(F.data.startswith("confirm_delete_loot:"))
async def confirm_delete_loot_final(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(Loot, item_id)

        if not item:
            await callback.answer("Loot not found", show_alert=True)
            return

        await session.delete(item)
        await session.commit()

    await callback.answer("Loot deleted successfully")
    await callback.message.edit_text(
        "✅ <b>Loot deleted successfully.</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            back_button("list_loots")
        ]),
        parse_mode="HTML"
    )


# =========================
# CONFIRM DELETE NEWS
# =========================

@router.callback_query(F.data.startswith("confirm_delete_news:"))
async def confirm_delete_news_final(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    item_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        item = await session.get(News, item_id)

        if not item:
            await callback.answer("News not found", show_alert=True)
            return

        await session.delete(item)
        await session.commit()

    await callback.answer("News deleted successfully")
    await callback.message.edit_text(
        "✅ <b>News deleted successfully.</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            back_button("list_news")
        ]),
        parse_mode="HTML"
    )
    # =========================
# ADD APP
# =========================

@router.callback_query(F.data == "add_app")
async def start_add_app(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    await state.clear()
    await state.set_state(AdminAddApp.name)
    await callback.message.edit_text(
        "Enter App Name:",
        reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(AdminAddApp.name)
async def app_name(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAddApp.logo)
    await message.answer(
        "Send App Logo or type Skip:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddApp.logo)
async def app_logo(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if message.photo:
        logo_id = message.photo[-1].file_id
    elif message.text and message.text.strip().lower() == "skip":
        logo_id = None
    else:
        await message.answer("Please send a photo or type Skip.")
        return

    await state.update_data(logo_file_id=logo_id)
    await state.set_state(AdminAddApp.category)
    await message.answer("Enter App Category:", reply_markup=cancel_kb())


@router.message(AdminAddApp.category)
async def app_category(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    await state.update_data(category=message.text.strip())
    await state.set_state(AdminAddApp.download_link)
    await message.answer("Enter Download Link:", reply_markup=cancel_kb())


@router.message(AdminAddApp.download_link)
async def app_download_link(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    await state.update_data(download_link=message.text.strip())
    await state.set_state(AdminAddApp.website)
    await message.answer(
        "Enter Website Link or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddApp.website)
async def app_website(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    value = message.text.strip()
    await state.update_data(
        website=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddApp.description)
    await message.answer("Enter App Description:", reply_markup=cancel_kb())


@router.message(AdminAddApp.description)
async def app_description(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    await state.update_data(description=message.text.strip())
    await state.set_state(AdminAddApp.features)
    await message.answer(
        "Enter App Features or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddApp.features)
async def app_features(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    value = message.text.strip()
    await state.update_data(
        features=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddApp.platform)
    await message.answer(
        "Enter Platform (Android / iOS / Web):",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddApp.platform)
async def app_platform(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    await state.update_data(platform=message.text.strip())
    await state.set_state(AdminAddApp.earning_method)
    await message.answer(
        "Enter Earning Method or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddApp.earning_method)
async def app_earning_method(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    value = message.text.strip()
    await state.update_data(
        earning_method=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddApp.min_withdrawal)
    await message.answer(
        "Enter Minimum Withdrawal or type None:",
        reply_markup=cancel_kb()
    )
@router.message(AdminAddApp.min_withdrawal)
async def app_min_withdrawal(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    value = message.text.strip()
    await state.update_data(
        min_withdrawal=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddApp.countries)
    await message.answer(
        "Enter Available Countries or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddApp.countries)
async def app_countries(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    value = message.text.strip()
    await state.update_data(
        countries=None if value.lower() == "none" else value
    )

    data = await state.get_data()
    summary = (
        "<b>Confirm New App</b>\n\n"
        f"Name: {data['name']}\n"
        f"Category: {data['category']}\n"
        f"Download Link: {data['download_link']}\n"
        f"Website: {data.get('website') or 'N/A'}\n"
        f"Description: {data['description']}\n"
        f"Features: {data.get('features') or 'N/A'}\n"
        f"Platform: {data['platform']}\n"
        f"Earning Method: {data.get('earning_method') or 'N/A'}\n"
        f"Minimum Withdrawal: {data.get('min_withdrawal') or 'N/A'}\n"
        f"Countries: {data.get('countries') or 'N/A'}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Save App",
                callback_data="save_new_app"
            ),
            InlineKeyboardButton(
                text="Cancel",
                callback_data="cancel"
            )
        ]
    ])

    await state.set_state(AdminAddApp.confirm)
    await message.answer(summary, reply_markup=keyboard)


@router.callback_query(
    F.data == "save_new_app",
    AdminAddApp.confirm
)
async def save_new_app(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    data = await state.get_data()

    async with async_session() as session:
        app = AppListing(
            name=data["name"],
            logo_file_id=data.get("logo_file_id"),
            category=data["category"],
            download_link=data["download_link"],
            website=data.get("website"),
            description=data["description"],
            features=data.get("features"),
            platform=data["platform"],
            earning_method=data.get("earning_method"),
            min_withdrawal=data.get("min_withdrawal"),
            countries=data.get("countries"),
        )
        session.add(app)
        await session.commit()

    await state.clear()
    await callback.message.edit_text(
        "App added successfully.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_button("list_apps")])
    )
    await callback.answer("Saved")
    # =========================
# ADD LOOT
# =========================

@router.callback_query(F.data == "add_loot")
async def start_add_loot(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    await state.clear()
    await state.set_state(AdminAddLoot.title)
    await callback.message.edit_text(
        "Enter Loot Title:",
        reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(AdminAddLoot.title)
async def loot_title(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter a text title.")
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAddLoot.reward_details)
    await message.answer(
        "Enter Reward Details:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddLoot.reward_details)
async def loot_reward_details(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter reward details.")
        return

    await state.update_data(reward_details=message.text.strip())
    await state.set_state(AdminAddLoot.eligibility)
    await message.answer(
        "Enter Eligibility or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddLoot.eligibility)
async def loot_eligibility(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter text or type None.")
        return

    value = message.text.strip()
    await state.update_data(
        eligibility=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddLoot.steps)
    await message.answer(
        "Enter Steps to Claim or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddLoot.steps)
async def loot_steps(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter text or type None.")
        return

    value = message.text.strip()
    await state.update_data(
        steps=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddLoot.expiry_date)
    await message.answer(
        "Enter Expiry Date or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddLoot.expiry_date)
async def loot_expiry_date(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter a date or type None.")
        return

    value = message.text.strip()
    await state.update_data(
        expiry_date=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddLoot.terms)
    await message.answer(
        "Enter Terms and Conditions or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddLoot.terms)
async def loot_terms(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter text or type None.")
        return

    value = message.text.strip()
    await state.update_data(
        terms=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddLoot.official_link)
    await message.answer(
        "Enter Official Loot Link:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddLoot.official_link)
async def loot_official_link(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter the official link.")
        return

    await state.update_data(official_link=message.text.strip())
    data = await state.get_data()

    summary = (
        "<b>Confirm New Loot</b>\n\n"
        f"Title: {data['title']}\n"
        f"Reward Details: {data['reward_details']}\n"
        f"Eligibility: {data.get('eligibility') or 'N/A'}\n"
        f"Steps: {data.get('steps') or 'N/A'}\n"
        f"Expiry Date: {data.get('expiry_date') or 'N/A'}\n"
        f"Terms: {data.get('terms') or 'N/A'}\n"
        f"Official Link: {data['official_link']}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Save Loot",
                callback_data="save_new_loot"
            ),
            InlineKeyboardButton(
                text="Cancel",
                callback_data="cancel"
            )
        ]
    ])

    await state.set_state(AdminAddLoot.confirm)
    await message.answer(summary, reply_markup=keyboard)


@router.callback_query(
    F.data == "save_new_loot",
    AdminAddLoot.confirm
)
async def save_new_loot(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    data = await state.get_data()

    async with async_session() as session:
        loot = Loot(
            title=data["title"],
            reward_details=data["reward_details"],
            eligibility=data.get("eligibility"),
            steps=data.get("steps"),
            expiry_date=data.get("expiry_date"),
            terms=data.get("terms"),
            official_link=data["official_link"],
        )
        session.add(loot)
        await session.commit()

    await state.clear()
    await callback.message.edit_text("Loot added successfully.")
    await callback.answer("Saved")
    # =========================
# ADD NEWS
# =========================

@router.callback_query(F.data == "add_news")
async def start_add_news(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    await state.clear()
    await state.set_state(AdminAddNews.title)
    await callback.message.edit_text(
        "Enter News Title:",
        reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(AdminAddNews.title)
async def news_title(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter a news title.")
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAddNews.content)
    await message.answer(
        "Enter News Content:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddNews.content)
async def news_content(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter news content.")
        return

    await state.update_data(content=message.text.strip())
    await state.set_state(AdminAddNews.category)
    await message.answer(
        "Enter News Category:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddNews.category)
async def news_category(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter a category.")
        return

    await state.update_data(category=message.text.strip())
    await state.set_state(AdminAddNews.app_name)
    await message.answer(
        "Enter App Name or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddNews.app_name)
async def news_app_name(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter an app name or type None.")
        return

    value = message.text.strip()
    await state.update_data(
        app_name=None if value.lower() == "none" else value
    )
    await state.set_state(AdminAddNews.source)
    await message.answer(
        "Enter News Source or type None:",
        reply_markup=cancel_kb()
    )


@router.message(AdminAddNews.source)
async def news_source(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter a source or type None.")
        return

    value = message.text.strip()
    await state.update_data(
        source=None if value.lower() == "none" else value
    )

    data = await state.get_data()
    summary = (
        "<b>Confirm New News</b>\n\n"
        f"Title: {data['title']}\n"
        f"Content: {data['content']}\n"
        f"Category: {data['category']}\n"
        f"App Name: {data.get('app_name') or 'N/A'}\n"
        f"Source: {data.get('source') or 'N/A'}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Save News",
                callback_data="save_new_news"
            ),
            InlineKeyboardButton(
                text="Cancel",
                callback_data="cancel"
            )
        ]
    ])

    await state.set_state(AdminAddNews.confirm)
    await message.answer(summary, reply_markup=keyboard)


@router.callback_query(
    F.data == "save_new_news",
    AdminAddNews.confirm
)
async def save_new_news(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    data = await state.get_data()

    async with async_session() as session:
        news = News(
            title=data["title"],
            content=data["content"],
            category=data["category"],
            app_name=data.get("app_name"),
            source=data.get("source"),
        )
        session.add(news)
        await session.commit()

    await state.clear()
    await callback.message.edit_text("News added successfully.")
    await callback.answer("Saved")
    # =========================
# EDIT APP
# =========================

@router.callback_query(F.data.startswith("edit_app:"))
async def edit_app_menu(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    app_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        app = await session.get(AppListing, app_id)

    if not app:
        await callback.answer("App not found", show_alert=True)
        return

    await state.clear()
    await state.update_data(item_id=app_id)

    fields = [
        ("Name", "name"),
        ("Logo", "logo_file_id"),
        ("Category", "category"),
        ("Download Link", "download_link"),
        ("Website", "website"),
        ("Description", "description"),
        ("Features", "features"),
        ("Platform", "platform"),
        ("Earning Method", "earning_method"),
        ("Minimum Withdrawal", "min_withdrawal"),
        ("Countries", "countries"),
    ]

    buttons = [
        [InlineKeyboardButton(
            text=label,
            callback_data=f"edit_app_field:{field}"
        )]
        for label, field in fields
    ]
    buttons.append(back_button(f"manage_app:{app_id}"))

    await callback.message.edit_text(
        f"<b>Edit App: {app.name}</b>\n\nSelect a field to update:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_app_field:"))
async def select_app_field(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    field = callback.data.split(":", 1)[1]
    allowed = {
        "name", "logo_file_id", "category", "download_link",
        "website", "description", "features", "platform",
        "earning_method", "min_withdrawal", "countries"
    }

    if field not in allowed:
        await callback.answer("Invalid field", show_alert=True)
        return

    data = await state.get_data()
    if not data.get("item_id"):
        await callback.answer("Please select an app again.", show_alert=True)
        return

    await state.update_data(edit_field=field)
    await state.set_state(AdminEditApp.value)

    prompt = (
        "Send the new logo photo or type Skip to remove it:"
        if field == "logo_file_id"
        else "Enter the new value. Type None to clear an optional field:"
    )

    await callback.message.answer(prompt, reply_markup=cancel_kb())
    await callback.answer()


@router.message(AdminEditApp.value)
async def update_app_field(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    data = await state.get_data()
    app_id = data.get("item_id")
    field = data.get("edit_field")

    if not app_id or not field:
        await state.clear()
        await message.answer("Edit session expired. Please try again.")
        return

    if field == "logo_file_id":
        if message.photo:
            value = message.photo[-1].file_id
        elif message.text and message.text.strip().lower() == "skip":
            value = None
        else:
            await message.answer("Please send a photo or type Skip.")
            return
    else:
        if not message.text:
            await message.answer("Please enter a text value.")
            return

        value = message.text.strip()
        if value.lower() == "none":
            if field not in {
                "website", "features", "earning_method",
                "min_withdrawal", "countries"
            }:
                await message.answer("This field cannot be empty.")
                return
            value = None

    async with async_session() as session:
        app = await session.get(AppListing, app_id)
        if not app:
            await state.clear()
            await message.answer("App not found.")
            return

        setattr(app, field, value)
        await session.commit()

    await state.clear()
    await message.answer(
        "App updated successfully.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            back_button(f"manage_app:{app_id}")
        ])
    )


# =========================
# EDIT LOOT
# =========================

@router.callback_query(F.data.startswith("edit_loot:"))
async def edit_loot_menu(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    loot_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        loot = await session.get(Loot, loot_id)

    if not loot:
        await callback.answer("Loot not found", show_alert=True)
        return

    await state.clear()
    await state.update_data(item_id=loot_id)

    fields = [
        ("Title", "title"),
        ("Reward Details", "reward_details"),
        ("Eligibility", "eligibility"),
        ("Steps", "steps"),
        ("Expiry Date", "expiry_date"),
        ("Terms", "terms"),
        ("Official Link", "official_link"),
    ]

    buttons = [
        [InlineKeyboardButton(
            text=label,
            callback_data=f"edit_loot_field:{field}"
        )]
        for label, field in fields
    ]
    buttons.append(back_button(f"manage_loot:{loot_id}"))

    await callback.message.edit_text(
        f"<b>Edit Loot: {loot.title}</b>\n\nSelect a field to update:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_loot_field:"))
async def select_loot_field(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    field = callback.data.split(":", 1)[1]
    allowed = {
        "title", "reward_details", "eligibility",
        "steps", "expiry_date", "terms", "official_link"
    }

    if field not in allowed:
        await callback.answer("Invalid field", show_alert=True)
        return

    data = await state.get_data()
    if not data.get("item_id"):
        await callback.answer("Please select a loot again.", show_alert=True)
        return

    await state.update_data(edit_field=field)
    await state.set_state(AdminEditLoot.value)
    await callback.message.answer(
        "Enter the new value. Type None to clear an optional field:",
        reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(AdminEditLoot.value)
async def update_loot_field(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter a text value.")
        return

    data = await state.get_data()
    loot_id = data.get("item_id")
    field = data.get("edit_field")

    if not loot_id or not field:
        await state.clear()
        await message.answer("Edit session expired. Please try again.")
        return

    value = message.text.strip()

    if value.lower() == "none":
        if field not in {
            "eligibility", "steps", "expiry_date", "terms"
        }:
            await message.answer("This field cannot be empty.")
            return
        value = None

    async with async_session() as session:
        loot = await session.get(Loot, loot_id)
        if not loot:
            await state.clear()
            await message.answer("Loot not found.")
            return

        setattr(loot, field, value)
        await session.commit()

    await state.clear()
    await message.answer(
        "Loot updated successfully.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            back_button(f"manage_loot:{loot_id}")
        ])
    )


# =========================
# EDIT NEWS
# =========================

@router.callback_query(F.data.startswith("edit_news:"))
async def edit_news_menu(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    news_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        news = await session.get(News, news_id)

    if not news:
        await callback.answer("News not found", show_alert=True)
        return

    await state.clear()
    await state.update_data(item_id=news_id)

    fields = [
        ("Title", "title"),
        ("Content", "content"),
        ("Category", "category"),
        ("App Name", "app_name"),
        ("Source", "source"),
    ]

    buttons = [
        [InlineKeyboardButton(
            text=label,
            callback_data=f"edit_news_field:{field}"
        )]
        for label, field in fields
    ]
    buttons.append(back_button(f"manage_news:{news_id}"))

    await callback.message.edit_text(
        f"<b>Edit News: {news.title}</b>\n\nSelect a field to update:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_news_field:"))
async def select_news_field(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return

    field = callback.data.split(":", 1)[1]
    allowed = {"title", "content", "category", "app_name", "source"}

    if field not in allowed:
        await callback.answer("Invalid field", show_alert=True)
        return

    data = await state.get_data()
    if not data.get("item_id"):
        await callback.answer("Please select news again.", show_alert=True)
        return

    await state.update_data(edit_field=field)
    await state.set_state(AdminEditNews.value)
    await callback.message.answer(
        "Enter the new value. Type None to clear an optional field:",
        reply_markup=cancel_kb()
    )
    await callback.answer()


@router.message(AdminEditNews.value)
async def update_news_field(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return

    if not message.text:
        await message.answer("Please enter a text value.")
        return

    data = await state.get_data()
    news_id = data.get("item_id")
    field = data.get("edit_field")

    if not news_id or not field:
        await state.clear()
        await message.answer("Edit session expired. Please try again.")
        return

    value = message.text.strip()

    if value.lower() == "none":
        if field not in {"app_name", "source"}:
            await message.answer("This field cannot be empty.")
            return
        value = None

    async with async_session() as session:
        news = await session.get(News, news_id)
        if not news:
            await state.clear()
            await message.answer("News not found.")
            return

        setattr(news, field, value)
        await session.commit()

    await state.clear()
    await message.answer(
        "News updated successfully.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            back_button(f"manage_news:{news_id}")
        ])
        )
