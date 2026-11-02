from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from datetime import datetime
import uuid

from config import OWNER_ID, OFFICIAL_CHANNEL, SUPPORT_USERNAME, BOT_NAME
from keyboards import (
    main_menu_kb, join_channel_kb, promote_telegram_kb, promote_app_kb,
    back_home_kb, cancel_kb, admin_main_kb
)
from database import async_session, User
from sqlalchemy import select

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()

    user_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    username = message.from_user.username or ""
    payload = (command.args or "").strip()

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            referral_code = str(user_id)[-6:] + str(uuid.uuid4())[:4]
            referred_by = None

            if payload:
                ref_result = await session.execute(
                    select(User).where(User.referral_code == payload)
                )
                referrer = ref_result.scalar_one_or_none()
                if referrer and referrer.telegram_id != user_id:
                    referred_by = referrer.telegram_id
                    referrer.referral_count += 1
                    try:
                        await message.bot.send_message(
                            referrer.telegram_id,
                            f"👥 New referral joined.\nYour referral count is now {referrer.referral_count}.",
                        )
                    except Exception:
                        pass

            user = User(
                telegram_id=user_id,
                first_name=first_name,
                username=username,
                referral_code=referral_code,
                referred_by=referred_by,
                created_at=datetime.utcnow(),
            )
            session.add(user)
            await session.commit()

    text = f"""
👋 <b>Welcome {first_name}!</b>

🚀 Welcome to <b>{BOT_NAME}</b>

Here you can find:
• Latest Earning Apps
• Free Loots & Rewards
• Channel / Group / Bot Promotion
• App Promotion Services
• Telegram Bot Development

Please select an option from the menu below ⬇️
"""
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"🏠 <b>Main Menu</b>\n\nWelcome to {BOT_NAME}!\nPlease select an option:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "join_channel")
async def join_channel(callback: CallbackQuery):
    text = f"""
📢 <b>Join Official Channel</b>

Our Official Channel: {OFFICIAL_CHANNEL}

Please join the channel and then click the <b>Verify Membership</b> button below.
"""
    await callback.message.edit_text(text, reply_markup=join_channel_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "verify_membership")
async def verify_membership(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        member = await callback.bot.get_chat_member(chat_id=OFFICIAL_CHANNEL, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            async with async_session() as session:
                result = await session.execute(select(User).where(User.telegram_id == user_id))
                user = result.scalar_one_or_none()
                if user:
                    user.joined_channel = True
                    await session.commit()

            await callback.message.edit_text(
                "✅ <b>Verification Successful!</b>\n\nYou can now access all features.",
                reply_markup=main_menu_kb(),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ You have not joined the channel yet!", show_alert=True)
    except Exception:
        await callback.answer("❌ Verification failed. Please try again.", show_alert=True)


@router.callback_query(F.data == "promote_telegram")
async def promote_telegram_menu(callback: CallbackQuery):
    text = """
📣 <b>Promote Your Channel / Group / Bot</b>

Please select what you want to promote:
"""
    await callback.message.edit_text(text, reply_markup=promote_telegram_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "promote_app")
async def promote_app_menu(callback: CallbackQuery):
    text = """
📱 <b>Promote Your App</b>

Please select the type of app you want to promote:
"""
    await callback.message.edit_text(text, reply_markup=promote_app_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "my_profile")
async def my_profile(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

    if not user:
        await callback.answer("Profile not found", show_alert=True)
        return

    link = f"https://t.me/TrustedMoney24x7Bot?start={user.referral_code}"
    text = f"""
👤 <b>My Profile</b>

🆔 Telegram ID: <code>{user.telegram_id}</code>
👤 Name: {user.first_name or 'N/A'}
🔗 Username: @{user.username or 'N/A'}
📅 Registration: {user.created_at.strftime('%d %b %Y') if user.created_at else 'N/A'}

📊 <b>Order Status</b>
• Total Orders: {user.total_orders}
• Pending: {user.pending_orders}
• Approved: {user.approved_orders}
• Completed: {user.completed_orders}

👥 Referral Count: {user.referral_count}
🎁 Your referral link:
{link}

Share this link. A new user's first visit increases your count by 1.
No cash is paid automatically.

✅ Joined Channel: {'Yes' if user.joined_channel else 'No'}
"""
    await callback.message.edit_text(text, reply_markup=back_home_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "contact_support")
async def contact_support(callback: CallbackQuery):
    text = f"""
📞 <b>Contact Support</b>

Official Support: {SUPPORT_USERNAME}

You can contact us for:
• App Promotion Support
• Channel / Group / Bot Promotion
• Bot Development
• Payment & Order Related
• Report a Problem
"""
    await callback.message.edit_text(text, reply_markup=back_home_kb(), parse_mode="HTML")
    await callback.answer()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("⛔ You do not have admin access.")
        return

    await message.answer(
        "🔐 <b>Owner Admin Panel</b>\n\nPlease select an option:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Cancelled.\n\nReturning to Main Menu:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
