from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime

from config import OWNER_ID
from states import AdminAddApp, AdminAddLoot, AdminAddNews
from keyboards import cancel_kb, admin_main_kb
from database import async_session, AppListing, Loot, News

router = Router()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


# ====================== MENUS ======================
@router.callback_query(F.data == "admin_apps")
async def admin_apps_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add New App", callback_data="add_app")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_dashboard")],
    ])
    await callback.message.edit_text(
        "📱 <b>Manage Apps</b>\n\nAdd a verified earning app listing.",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_loots")
async def admin_loots_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add New Loot", callback_data="add_loot")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_dashboard")],
    ])
    await callback.message.edit_text(
        "🎁 <b>Manage Loots</b>\n\nAdd a verified free loot or reward offer.",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_news")
async def admin_news_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add News", callback_data="add_news")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_dashboard")],
    ])
    await callback.message.edit_text(
        "📰 <b>Manage News</b>\n\nAdd app launch news or a warning.",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


# ====================== ADD APP ======================
@router.callback_query(F.data == "add_app")
async def add_app_start(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    await state.set_state(AdminAddApp.name)
    await callback.message.edit_text(
        "📱 Enter the <b>App Name</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminAddApp.name)
async def add_app_name(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminAddApp.logo)
    await message.answer(
        "🖼 Send the <b>App Logo</b> as a photo, or type <b>Skip</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(AdminAddApp.logo)
async def add_app_logo(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    if message.photo:
        await state.update_data(logo=message.photo[-1].file_id)
    else:
        await state.update_data(logo=None)
    await state.set_state(AdminAddApp.category)
    await message.answer(
        "📂 <b>Category</b> (Example: Reward, Task, Referral):",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(AdminAddApp.category)
async def add_app_category(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(category=message.text.strip())
    await state.set_state(AdminAddApp.download_link)
    await message.answer("📥 Official <b>Download Link</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddApp.download_link)
async def add_app_link(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(download_link=message.text.strip())
    await state.set_state(AdminAddApp.website)
    await message.answer("🌐 Website (or type <b>None</b>):", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddApp.website)
async def add_app_website(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(website=message.text.strip())
    await state.set_state(AdminAddApp.description)
    await message.answer("📝 Short <b>Description</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddApp.description)
async def add_app_desc(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(description=message.text.strip())
    await state.set_state(AdminAddApp.features)
    await message.answer("✨ Main <b>Features</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddApp.features)
async def add_app_features(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(features=message.text.strip())
    await state.set_state(AdminAddApp.platform)
    await message.answer(
        "📲 <b>Platform</b> (Android / iOS / Web):",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(AdminAddApp.platform)
async def add_app_platform(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(platform=message.text.strip())
    await state.set_state(AdminAddApp.earning_method)
    await message.answer("💸 <b>Earning Method</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddApp.earning_method)
async def add_app_earn(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(earning_method=message.text.strip())
    await state.set_state(AdminAddApp.min_withdrawal)
    await message.answer("💳 <b>Minimum Withdrawal</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddApp.min_withdrawal)
async def add_app_min(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(min_withdrawal=message.text.strip())
    await state.set_state(AdminAddApp.countries)
    await message.answer("🌍 <b>Available Countries</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddApp.countries)
async def add_app_countries(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(countries=message.text.strip())
    data = await state.get_data()
    text = (
        "📋 <b>Confirm App Listing</b>\n\n"
        f"Name: {data.get('name')}\n"
        f"Category: {data.get('category')}\n"
        f"Platform: {data.get('platform')}\n"
        f"Link: {data.get('download_link')}\n"
        f"Min Withdrawal: {data.get('min_withdrawal')}\n"
        f"Countries: {data.get('countries')}\n\n"
        "Save this listing?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Save", callback_data="save_app")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")],
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(AdminAddApp.confirm)


@router.callback_query(F.data == "save_app", AdminAddApp.confirm)
async def save_app(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        return
    data = await state.get_data()
    async with async_session() as session:
        session.add(AppListing(
            name=data.get("name"),
            logo_file_id=data.get("logo"),
            category=data.get("category"),
            download_link=data.get("download_link"),
            website=None if data.get("website") in (None, "None", "none") else data.get("website"),
            description=data.get("description"),
            features=data.get("features"),
            platform=data.get("platform"),
            earning_method=data.get("earning_method"),
            min_withdrawal=data.get("min_withdrawal"),
            countries=data.get("countries"),
            is_verified=True,
            last_verified=datetime.utcnow().strftime("%d %b %Y"),
            created_at=datetime.utcnow(),
        ))
        await session.commit()
    await state.clear()
    await callback.message.edit_text(
        "✅ <b>App listing saved.</b>\nUsers can now see it under Latest Earning Apps.",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ====================== ADD LOOT ======================
@router.callback_query(F.data == "add_loot")
async def add_loot_start(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    await state.set_state(AdminAddLoot.title)
    await callback.message.edit_text(
        "🎁 Enter the <b>Offer Title</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminAddLoot.title)
async def loot_title(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAddLoot.reward_details)
    await message.answer("💸 <b>Reward Details</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddLoot.reward_details)
async def loot_reward(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(reward_details=message.text.strip())
    await state.set_state(AdminAddLoot.eligibility)
    await message.answer("✅ <b>Eligibility</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddLoot.eligibility)
async def loot_elig(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(eligibility=message.text.strip())
    await state.set_state(AdminAddLoot.steps)
    await message.answer("📝 <b>Required Steps</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddLoot.steps)
async def loot_steps(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(steps=message.text.strip())
    await state.set_state(AdminAddLoot.expiry_date)
    await message.answer("📅 <b>Expiry Date</b> (Example: 30 Nov 2026):", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddLoot.expiry_date)
async def loot_expiry(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(expiry_date=message.text.strip())
    await state.set_state(AdminAddLoot.terms)
    await message.answer("📜 <b>Terms & Conditions</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddLoot.terms)
async def loot_terms(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(terms=message.text.strip())
    await state.set_state(AdminAddLoot.official_link)
    await message.answer("🔗 <b>Official Link</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddLoot.official_link)
async def loot_link(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(official_link=message.text.strip())
    data = await state.get_data()
    text = (
        "📋 <b>Confirm Loot</b>\n\n"
        f"Title: {data.get('title')}\n"
        f"Reward: {data.get('reward_details')}\n"
        f"Expiry: {data.get('expiry_date')}\n"
        f"Link: {data.get('official_link')}\n\n"
        "Save this offer?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Save", callback_data="save_loot")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")],
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(AdminAddLoot.confirm)


@router.callback_query(F.data == "save_loot", AdminAddLoot.confirm)
async def save_loot(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        return
    data = await state.get_data()
    async with async_session() as session:
        session.add(Loot(
            title=data.get("title"),
            reward_details=data.get("reward_details"),
            eligibility=data.get("eligibility"),
            steps=data.get("steps"),
            expiry_date=data.get("expiry_date"),
            terms=data.get("terms"),
            official_link=data.get("official_link"),
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow(),
        ))
        await session.commit()
    await state.clear()
    await callback.message.edit_text(
        "✅ <b>Loot saved.</b>\nUsers can now see it under Free Loots & Rewards.",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ====================== ADD NEWS ======================
@router.callback_query(F.data == "add_news")
async def add_news_start(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    await state.set_state(AdminAddNews.title)
    await callback.message.edit_text(
        "📰 Enter the <b>News Title</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminAddNews.title)
async def news_title(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAddNews.content)
    await message.answer("📝 <b>News Content</b>:", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddNews.content)
async def news_content(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(content=message.text.strip())
    await state.set_state(AdminAddNews.category)
    await message.answer(
        "📂 <b>Category</b> (launch / warning / update / withdrawal):",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(AdminAddNews.category)
async def news_category(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(category=message.text.strip())
    await state.set_state(AdminAddNews.app_name)
    await message.answer("📱 Related <b>App Name</b> (or None):", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddNews.app_name)
async def news_app(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(app_name=message.text.strip())
    await state.set_state(AdminAddNews.source)
    await message.answer("🔗 <b>Official Source</b> link (or None):", reply_markup=cancel_kb(), parse_mode="HTML")


@router.message(AdminAddNews.source)
async def news_source(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    await state.update_data(source=message.text.strip())
    data = await state.get_data()
    text = (
        "📋 <b>Confirm News</b>\n\n"
        f"Title: {data.get('title')}\n"
        f"Category: {data.get('category')}\n"
        f"App: {data.get('app_name')}\n\n"
        "Publish this news?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Publish", callback_data="save_news")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")],
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(AdminAddNews.confirm)


@router.callback_query(F.data == "save_news", AdminAddNews.confirm)
async def save_news(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        return
    data = await state.get_data()
    async with async_session() as session:
        session.add(News(
            title=data.get("title"),
            content=data.get("content"),
            category=data.get("category"),
            app_name=None if data.get("app_name") in ("None", "none") else data.get("app_name"),
            source=None if data.get("source") in ("None", "none") else data.get("source"),
            is_active=True,
            created_at=datetime.utcnow(),
        ))
        await session.commit()
    await state.clear()
    await callback.message.edit_text(
        "✅ <b>News published.</b>\nUsers can see it under App News & Launches.",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
