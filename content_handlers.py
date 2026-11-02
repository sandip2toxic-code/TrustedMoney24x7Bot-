from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from database import async_session, AppListing, Loot, News
from keyboards import back_home_kb, main_menu_kb

router = Router()


@router.callback_query(F.data == "earning_apps")
async def earning_apps(callback: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(AppListing).order_by(AppListing.created_at.desc()).limit(15)
        )
        apps = result.scalars().all()

    if not apps:
        await callback.message.edit_text(
            "🆕 <b>Latest Earning Apps</b>\n\nNo verified apps listed yet. Please check back later.",
            reply_markup=back_home_kb(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=f"{app.name} ({app.platform or 'App'})", callback_data=f"app:{app.id}")]
        for app in apps
    ]
    buttons.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])
    await callback.message.edit_text(
        "🆕 <b>Latest Earning Apps</b>\n\nSelect an app to view details.\n\n"
        "⚠️ Never share passwords or OTP. Earnings are not guaranteed.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("app:"))
async def app_detail(callback: CallbackQuery):
    app_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        result = await session.execute(select(AppListing).where(AppListing.id == app_id))
        app = result.scalar_one_or_none()

    if not app:
        await callback.answer("App not found", show_alert=True)
        return

    text = (
        f"📱 <b>{app.name}</b>\n"
        f"{'✅ Verified' if app.is_verified else '⚠️ Not verified'}\n\n"
        f"📂 Category: {app.category or 'N/A'}\n"
        f"📲 Platform: {app.platform or 'N/A'}\n"
        f"💸 Earning Method: {app.earning_method or 'N/A'}\n"
        f"💳 Minimum Withdrawal: {app.min_withdrawal or 'N/A'}\n"
        f"🌍 Countries: {app.countries or 'N/A'}\n"
        f"📅 Last Verified: {app.last_verified or 'N/A'}\n\n"
        f"📝 {app.description or ''}\n\n"
        f"✨ Features:\n{app.features or 'N/A'}\n\n"
        f"🔗 Download: {app.download_link}\n"
        f"🌐 Website: {app.website or 'N/A'}\n\n"
        "⚠️ Read the app terms yourself. This bot does not guarantee profit or withdrawal."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Apps", callback_data="earning_apps")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")],
    ])
    if app.logo_file_id:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer_photo(
            app.logo_file_id,
            caption=text[:1024],
            reply_markup=kb,
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "free_loots")
async def free_loots(callback: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(Loot).where(Loot.is_active == True).order_by(Loot.created_at.desc()).limit(15)
        )
        loots = result.scalars().all()

    if not loots:
        await callback.message.edit_text(
            "🎁 <b>Free Loots & Rewards</b>\n\nNo active offers right now.",
            reply_markup=back_home_kb(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=loot.title[:60], callback_data=f"loot:{loot.id}")]
        for loot in loots
    ]
    buttons.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])
    await callback.message.edit_text(
        "🎁 <b>Free Loots & Rewards</b>\n\nSelect an offer. Check expiry and terms before joining.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("loot:"))
async def loot_detail(callback: CallbackQuery):
    loot_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        result = await session.execute(select(Loot).where(Loot.id == loot_id))
        loot = result.scalar_one_or_none()

    if not loot:
        await callback.answer("Offer not found", show_alert=True)
        return

    text = (
        f"🎁 <b>{loot.title}</b>\n"
        f"{'✅ Verified' if loot.is_verified else '⚠️ Unverified'}\n\n"
        f"💸 Reward: {loot.reward_details}\n"
        f"✅ Eligibility: {loot.eligibility or 'N/A'}\n"
        f"📝 Steps:\n{loot.steps or 'N/A'}\n"
        f"📅 Expiry: {loot.expiry_date or 'N/A'}\n"
        f"📜 Terms: {loot.terms or 'N/A'}\n"
        f"🔗 Link: {loot.official_link}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Loots", callback_data="free_loots")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "app_news")
async def app_news(callback: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(News).where(News.is_active == True).order_by(News.created_at.desc()).limit(15)
        )
        items = result.scalars().all()

    if not items:
        await callback.message.edit_text(
            "📰 <b>App News & Launches</b>\n\nNo news published yet.",
            reply_markup=back_home_kb(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=item.title[:60], callback_data=f"news:{item.id}")]
        for item in items
    ]
    buttons.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])
    await callback.message.edit_text(
        "📰 <b>App News & Launches</b>\n\nSelect a story. This is information only, not a profit guarantee.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("news:"))
async def news_detail(callback: CallbackQuery):
    news_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        result = await session.execute(select(News).where(News.id == news_id))
        item = result.scalar_one_or_none()

    if not item:
        await callback.answer("News not found", show_alert=True)
        return

    text = (
        f"📰 <b>{item.title}</b>\n\n"
        f"📂 Category: {item.category or 'N/A'}\n"
        f"📱 App: {item.app_name or 'N/A'}\n"
        f"📅 Published: {item.created_at.strftime('%d %b %Y') if item.created_at else 'N/A'}\n\n"
        f"{item.content}\n\n"
        f"🔗 Source: {item.source or 'N/A'}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 News", callback_data="app_news")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")],
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "earning_opportunities")
async def earning_opportunities(callback: CallbackQuery):
    await callback.message.edit_text(
        "💰 <b>Earning Opportunities</b>\n\n"
        "This section lists platforms and task ideas only.\n"
        "No income is guaranteed. Avoid anyone who asks for an upfront fee to 'unlock' earnings.\n\n"
        "New listings will appear here when the admin publishes them.",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
