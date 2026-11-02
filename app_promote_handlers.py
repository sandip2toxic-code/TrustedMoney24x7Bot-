from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import uuid
import json

from states import PromoteApp
from keyboards import cancel_kb, main_menu_kb
from database import async_session, Order, User
from sqlalchemy import select
from config import OWNER_ID

router = Router()


# Start App Promotion Form
@router.callback_query(F.data.in_({
    "app_android", "app_ios", "app_web", "app_earning",
    "app_task", "app_reward", "app_sponsored", "app_packages"
}))
async def start_app_promo(callback: CallbackQuery, state: FSMContext):
    type_map = {
        "app_android": "Android App Promotion",
        "app_ios": "iOS App Promotion",
        "app_web": "Web App Promotion",
        "app_earning": "Earning App Promotion",
        "app_task": "Task-Based App Promotion",
        "app_reward": "Reward App Promotion",
        "app_sponsored": "Sponsored App Advertisement",
        "app_packages": "App Promotion Packages"
    }
    app_type = type_map.get(callback.data)

    await state.update_data(app_type=app_type)
    await state.set_state(PromoteApp.name)

    await callback.message.edit_text(
        f"📱 <b>{app_type}</b>\n\n"
        "Please enter the <b>App Name</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PromoteApp.name)
async def process_app_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(PromoteApp.logo)
    await message.answer(
        "🖼 Please send the <b>App Logo</b> (as photo).\n"
        "If you don't have logo now, type <b>Skip</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.logo)
async def process_app_logo(message: Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(logo=file_id)
    else:
        await state.update_data(logo="Not provided")

    await state.set_state(PromoteApp.category)
    await message.answer(
        "📂 Enter <b>App Category</b> (Example: Earning, Finance, Tools, Social etc.):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.category)
async def process_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text.strip())
    await state.set_state(PromoteApp.download_link)
    await message.answer(
        "📥 Official <b>Download Link</b> (Play Store / App Store / Direct):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.download_link)
async def process_download_link(message: Message, state: FSMContext):
    await state.update_data(download_link=message.text.strip())
    await state.set_state(PromoteApp.website)
    await message.answer(
        "🌐 Website Link (if available). If none, type <b>None</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.website)
async def process_website(message: Message, state: FSMContext):
    await state.update_data(website=message.text.strip())
    await state.set_state(PromoteApp.description)
    await message.answer(
        "📝 Write a short <b>App Description</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(PromoteApp.features)
    await message.answer(
        "✨ Main <b>Features</b> of the app (write briefly):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.features)
async def process_features(message: Message, state: FSMContext):
    await state.update_data(features=message.text.strip())
    await state.set_state(PromoteApp.target_audience)
    await message.answer(
        "🎯 <b>Target Audience</b> (Example: Students, Earners, Businessmen):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.target_audience)
async def process_audience(message: Message, state: FSMContext):
    await state.update_data(target_audience=message.text.strip())
    await state.set_state(PromoteApp.package)
    await message.answer(
        "📦 Preferred <b>Promotion Package</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.package)
async def process_package(message: Message, state: FSMContext):
    await state.update_data(package=message.text.strip())
    await state.set_state(PromoteApp.duration)
    await message.answer(
        "⏱ Required <b>Promotion Duration</b> (Example: 7 days / 15 days):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.duration)
async def process_duration(message: Message, state: FSMContext):
    await state.update_data(duration=message.text.strip())
    await state.set_state(PromoteApp.budget)
    await message.answer(
        "💰 Your <b>Budget</b> for promotion (Example: 500 BDT / 1000 BDT / Negotiate):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.budget)
async def process_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text.strip())
    await state.set_state(PromoteApp.contact)
    await message.answer(
        "👤 Your <b>Contact Username</b> (Example: @username):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text.strip())
    await state.set_state(PromoteApp.additional)
    await message.answer(
        "➕ Any <b>Additional Instructions</b>? (If none, type 'None'):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteApp.additional)
async def process_additional(message: Message, state: FSMContext):
    await state.update_data(additional=message.text.strip())
    data = await state.get_data()

    text = f"""
📋 <b>Please Confirm Your App Promotion Order</b>

🔹 Type: {data.get('app_type')}
🔹 App Name: {data.get('name')}
🔹 Category: {data.get('category')}
🔹 Download Link: {data.get('download_link')}
🔹 Website: {data.get('website')}
🔹 Description: {data.get('description')}
🔹 Features: {data.get('features')}
🔹 Target Audience: {data.get('target_audience')}
🔹 Package: {data.get('package')}
🔹 Duration: {data.get('duration')}
🔹 Budget: {data.get('budget')}
🔹 Contact: {data.get('contact')}
🔹 Additional: {data.get('additional')}

Do you want to submit this order?
"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm & Submit", callback_data="confirm_app_promo")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(PromoteApp.confirm)


@router.callback_query(F.data == "confirm_app_promo", PromoteApp.confirm)
async def confirm_app_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    order_id = "APP" + datetime.now().strftime("%y%m%d") + str(uuid.uuid4())[:5].upper()

    order_details = {
        "app_type": data.get("app_type"),
        "name": data.get("name"),
        "logo": data.get("logo"),
        "category": data.get("category"),
        "download_link": data.get("download_link"),
        "website": data.get("website"),
        "description": data.get("description"),
        "features": data.get("features"),
        "target_audience": data.get("target_audience"),
        "package": data.get("package"),
        "duration": data.get("duration"),
        "budget": data.get("budget"),
        "contact": data.get("contact"),
        "additional": data.get("additional")
    }

    async with async_session() as session:
        new_order = Order(
            order_id=order_id,
            user_id=user_id,
            order_type="app_promo",
            status="Pending",
            details=json.dumps(order_details),
            created_at=datetime.utcnow()
        )
        session.add(new_order)

        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.total_orders += 1
            user.pending_orders += 1

        await session.commit()

    # Notify Owner
    try:
        owner_text = f"""
🆕 <b>New App Promotion Order</b>

🆔 Order ID: <code>{order_id}</code>
👤 User ID: <code>{user_id}</code>
📱 App Name: {data.get('name')}
📂 Category: {data.get('category')}
💰 Budget: {data.get('budget')}
⏱ Duration: {data.get('duration')}
📞 Contact: {data.get('contact')}
"""
        await callback.bot.send_message(OWNER_ID, owner_text, parse_mode="HTML")
    except Exception:
        pass

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>App Promotion Order Submitted!</b>\n\n"
        f"Your Order ID: <code>{order_id}</code>\n\n"
        f"Our team will review your app and contact you soon.",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
