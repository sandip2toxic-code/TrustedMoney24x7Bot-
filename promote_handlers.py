from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import uuid
import json

from states import PromoteTelegram
from keyboards import cancel_kb, main_menu_kb, back_home_kb
from database import async_session, Order, User
from sqlalchemy import select
from config import OWNER_ID

router = Router()


# Start Promotion Form
@router.callback_query(F.data.in_({
    "promo_channel", "promo_group", "promo_bot", "promo_sponsored", "promo_custom"
}))
async def start_promo_form(callback: CallbackQuery, state: FSMContext):
    promo_map = {
        "promo_channel": "Telegram Channel Promotion",
        "promo_group": "Telegram Group Promotion",
        "promo_bot": "Telegram Bot Promotion",
        "promo_sponsored": "Sponsored Telegram Post",
        "promo_custom": "Custom Promotion Package"
    }
    promo_type = promo_map.get(callback.data)

    await state.update_data(promo_type=promo_type)
    await state.set_state(PromoteTelegram.name)

    await callback.message.edit_text(
        f"📣 <b>{promo_type}</b>\n\n"
        "Please enter the <b>Name</b> of your Channel / Group / Bot:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PromoteTelegram.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(PromoteTelegram.link)
    await message.answer(
        "🔗 Please send the <b>Telegram Link</b> of your Channel / Group / Bot:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteTelegram.link)
async def process_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text.strip())
    await state.set_state(PromoteTelegram.description)
    await message.answer(
        "📝 Please write a short <b>Description</b> of your service / channel:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteTelegram.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(PromoteTelegram.target_audience)
    await message.answer(
        "🎯 Who is your <b>Target Audience</b>? (Example: Earners, Students, Business etc.)",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteTelegram.target_audience)
async def process_audience(message: Message, state: FSMContext):
    await state.update_data(target_audience=message.text.strip())
    await state.set_state(PromoteTelegram.package)
    await message.answer(
        "📦 Preferred <b>Promotion Package</b> (Example: Basic / Standard / Premium / Custom):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteTelegram.package)
async def process_package(message: Message, state: FSMContext):
    await state.update_data(package=message.text.strip())
    await state.set_state(PromoteTelegram.duration)
    await message.answer(
        "⏱ Preferred <b>Promotion Duration</b> (Example: 3 days / 7 days / 15 days):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteTelegram.duration)
async def process_duration(message: Message, state: FSMContext):
    await state.update_data(duration=message.text.strip())
    await state.set_state(PromoteTelegram.additional)
    await message.answer(
        "➕ Any <b>Additional Requirements</b>? (If none, type 'None')",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteTelegram.additional)
async def process_additional(message: Message, state: FSMContext):
    await state.update_data(additional=message.text.strip())
    await state.set_state(PromoteTelegram.contact)
    await message.answer(
        "👤 Your <b>Contact Username</b> (Example: @username):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(PromoteTelegram.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text.strip())
    data = await state.get_data()

    # Show confirmation
    text = f"""
📋 <b>Please Confirm Your Order</b>

🔹 Type: {data.get('promo_type')}
🔹 Name: {data.get('name')}
🔹 Link: {data.get('link')}
🔹 Description: {data.get('description')}
🔹 Target Audience: {data.get('target_audience')}
🔹 Package: {data.get('package')}
🔹 Duration: {data.get('duration')}
🔹 Additional: {data.get('additional')}
🔹 Contact: {data.get('contact')}

Do you want to submit this order?
"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm & Submit", callback_data="confirm_promo")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(PromoteTelegram.confirm)


@router.callback_query(F.data == "confirm_promo", PromoteTelegram.confirm)
async def confirm_promo_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    # Generate unique Order ID
    order_id = "TM" + datetime.now().strftime("%y%m%d") + str(uuid.uuid4())[:5].upper()

    order_details = {
        "promo_type": data.get("promo_type"),
        "name": data.get("name"),
        "link": data.get("link"),
        "description": data.get("description"),
        "target_audience": data.get("target_audience"),
        "package": data.get("package"),
        "duration": data.get("duration"),
        "additional": data.get("additional"),
        "contact": data.get("contact")
    }

    async with async_session() as session:
        # Save Order
        new_order = Order(
            order_id=order_id,
            user_id=user_id,
            order_type="telegram_promo",
            status="Pending",
            details=json.dumps(order_details),
            created_at=datetime.utcnow()
        )
        session.add(new_order)

        # Update user order count
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.total_orders += 1
            user.pending_orders += 1

        await session.commit()

    # Notify Owner
    try:
        owner_text = f"""
🆕 <b>New Promotion Order</b>

🆔 Order ID: <code>{order_id}</code>
👤 User ID: <code>{user_id}</code>
📌 Type: {data.get('promo_type')}
📛 Name: {data.get('name')}
🔗 Link: {data.get('link')}
📦 Package: {data.get('package')}
⏱ Duration: {data.get('duration')}
📞 Contact: {data.get('contact')}
"""
        await callback.bot.send_message(OWNER_ID, owner_text, parse_mode="HTML")
    except Exception:
        pass

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Order Submitted Successfully!</b>\n\n"
        f"Your Order ID: <code>{order_id}</code>\n\n"
        f"Our team will review it soon. You can check status from My Profile.",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
