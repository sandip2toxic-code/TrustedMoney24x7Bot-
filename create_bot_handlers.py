from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime
import uuid
import json

from states import CreateBot
from keyboards import cancel_kb, main_menu_kb
from database import async_session, Order, User
from sqlalchemy import select
from config import OWNER_ID

router = Router()


@router.callback_query(F.data == "create_bot")
async def create_bot_menu(callback: CallbackQuery, state: FSMContext):
    text = """
🤖 <b>Create Your Telegram Bot</b>

We offer the following types of bots:

• Basic Telegram Bot
• Business Bot
• Earning Information Bot
• Referral Bot
• Auto-Reply Bot
• Channel Management Bot
• Custom Telegram Bot

Please select the type of bot you need or type your requirement.
"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Basic Bot", callback_data="bot_basic")],
        [InlineKeyboardButton(text="Business Bot", callback_data="bot_business")],
        [InlineKeyboardButton(text="Earning Info Bot", callback_data="bot_earning")],
        [InlineKeyboardButton(text="Referral Bot", callback_data="bot_referral")],
        [InlineKeyboardButton(text="Auto-Reply Bot", callback_data="bot_auto")],
        [InlineKeyboardButton(text="Channel Management Bot", callback_data="bot_channel")],
        [InlineKeyboardButton(text="Custom Bot", callback_data="bot_custom")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("bot_"))
async def start_bot_form(callback: CallbackQuery, state: FSMContext):
    type_map = {
        "bot_basic": "Basic Telegram Bot",
        "bot_business": "Business Bot",
        "bot_earning": "Earning Information Bot",
        "bot_referral": "Referral Bot",
        "bot_auto": "Auto-Reply Bot",
        "bot_channel": "Channel Management Bot",
        "bot_custom": "Custom Telegram Bot"
    }
    bot_type = type_map.get(callback.data, "Custom Telegram Bot")

    await state.update_data(bot_type=bot_type)
    await state.update_data(cancel_return_to="create_bot")
    await state.set_state(CreateBot.name)

    await callback.message.edit_text(
        f"🤖 <b>{bot_type}</b>\n\n"
        "Please enter the preferred <b>Bot Name</b>:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CreateBot.name)
async def process_bot_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(CreateBot.features)
    await message.answer(
        "⚙️ What <b>features</b> do you need in the bot? (Write in detail)",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(CreateBot.features)
async def process_features(message: Message, state: FSMContext):
    await state.update_data(features=message.text.strip())
    await state.set_state(CreateBot.purpose)
    await message.answer(
        "🎯 What is the <b>Main Purpose</b> of this bot?",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(CreateBot.purpose)
async def process_purpose(message: Message, state: FSMContext):
    await state.update_data(purpose=message.text.strip())
    await state.set_state(CreateBot.design)
    await message.answer(
        "🎨 Any <b>Design Preferences</b>? (Example: colors, style, buttons). Type 'None' if no preference:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(CreateBot.design)
async def process_design(message: Message, state: FSMContext):
    await state.update_data(design=message.text.strip())
    await state.set_state(CreateBot.budget)
    await message.answer(
        "💰 Your <b>Budget</b> for bot development:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(CreateBot.budget)
async def process_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text.strip())
    await state.set_state(CreateBot.delivery_time)
    await message.answer(
        "⏱ Expected <b>Delivery Time</b> (Example: 3 days / 7 days / Flexible):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(CreateBot.delivery_time)
async def process_delivery(message: Message, state: FSMContext):
    await state.update_data(delivery_time=message.text.strip())
    await state.set_state(CreateBot.additional)
    await message.answer(
        "➕ Any <b>Additional Requirements</b>? (Type 'None' if nothing):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(CreateBot.additional)
async def process_additional(message: Message, state: FSMContext):
    await state.update_data(additional=message.text.strip())
    await state.set_state(CreateBot.contact)
    await message.answer(
        "👤 Your <b>Contact Username</b> (Example: @username):",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(CreateBot.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text.strip())
    data = await state.get_data()

    text = f"""
📋 <b>Please Confirm Your Bot Development Request</b>

🔹 Bot Type: {data.get('bot_type')}
🔹 Bot Name: {data.get('name')}
🔹 Features: {data.get('features')}
🔹 Purpose: {data.get('purpose')}
🔹 Design: {data.get('design')}
🔹 Budget: {data.get('budget')}
🔹 Delivery Time: {data.get('delivery_time')}
🔹 Additional: {data.get('additional')}
🔹 Contact: {data.get('contact')}

Do you want to submit this request?
"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm & Submit", callback_data="confirm_create_bot")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(CreateBot.confirm)


@router.callback_query(F.data == "confirm_create_bot", CreateBot.confirm)
async def confirm_bot_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    order_id = "BOT" + datetime.now().strftime("%y%m%d") + str(uuid.uuid4())[:5].upper()

    order_details = {
        "bot_type": data.get("bot_type"),
        "name": data.get("name"),
        "features": data.get("features"),
        "purpose": data.get("purpose"),
        "design": data.get("design"),
        "budget": data.get("budget"),
        "delivery_time": data.get("delivery_time"),
        "additional": data.get("additional"),
        "contact": data.get("contact")
    }

    async with async_session() as session:
        new_order = Order(
            order_id=order_id,
            user_id=user_id,
            order_type="bot_development",
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
🆕 <b>New Bot Development Request</b>

🆔 Order ID: <code>{order_id}</code>
👤 User ID: <code>{user_id}</code>
🤖 Bot Type: {data.get('bot_type')}
📛 Name: {data.get('name')}
💰 Budget: {data.get('budget')}
⏱ Delivery: {data.get('delivery_time')}
📞 Contact: {data.get('contact')}
"""
        await callback.bot.send_message(OWNER_ID, owner_text, parse_mode="HTML")
    except Exception:
        pass

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Bot Development Request Submitted!</b>\n\n"
        f"Your Order ID: <code>{order_id}</code>\n\n"
        f"Our team will review your requirements and contact you soon with a quotation.",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
