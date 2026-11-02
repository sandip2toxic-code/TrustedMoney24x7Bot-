from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy import select, func
import json

from config import OWNER_ID
from database import async_session, User, Order, AppListing, Loot, News
from keyboards import admin_main_kb, back_home_kb, main_menu_kb

router = Router()


def owner_only(func):
    async def wrapper(event, *args, **kwargs):
        user_id = event.from_user.id if hasattr(event, "from_user") else None
        if user_id != OWNER_ID:
            if hasattr(event, "answer"):
                await event.answer("⛔ Access denied", show_alert=True)
            return
        return await func(event, *args, **kwargs)
    return wrapper


@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    async with async_session() as session:
        total_users = await session.scalar(select(func.count()).select_from(User))
        total_orders = await session.scalar(select(func.count()).select_from(Order))
        pending_orders = await session.scalar(
            select(func.count()).select_from(Order).where(Order.status == "Pending")
        )
        completed_orders = await session.scalar(
            select(func.count()).select_from(Order).where(Order.status == "Completed")
        )
        total_apps = await session.scalar(select(func.count()).select_from(AppListing))
        total_loots = await session.scalar(select(func.count()).select_from(Loot))

    text = f"""
📊 <b>Admin Dashboard</b>

👥 Total Users: {total_users or 0}
📦 Total Orders: {total_orders or 0}
🟡 Pending Orders: {pending_orders or 0}
🟢 Completed Orders: {completed_orders or 0}
📱 Total App Listings: {total_apps or 0}
🎁 Total Loot Listings: {total_loots or 0}
"""
    await callback.message.edit_text(text, reply_markup=admin_main_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.status == "Pending").order_by(Order.created_at.desc()).limit(10)
        )
        orders = result.scalars().all()

    if not orders:
        await callback.message.edit_text(
            "📦 <b>No Pending Orders</b>",
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    text = "📦 <b>Pending Orders</b> (Latest 10)\n\n"
    kb_buttons = []

    for order in orders:
        text += f"🆔 <code>{order.order_id}</code> | {order.order_type} | User: {order.user_id}\n"
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"View {order.order_id}",
                callback_data=f"view_order:{order.order_id}"
            )
        ])

    kb_buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_dashboard")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("view_order:"))
async def view_order(callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    order_id = callback.data.split(":")[1]

    async with async_session() as session:
        result = await session.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()

    if not order:
        await callback.answer("Order not found", show_alert=True)
        return

    try:
        details = json.loads(order.details)
        details_text = "\n".join([f"• {k}: {v}" for k, v in details.items()])
    except Exception:
        details_text = order.details

    text = f"""
📋 <b>Order Details</b>

🆔 Order ID: <code>{order.order_id}</code>
👤 User ID: <code>{order.user_id}</code>
📌 Type: {order.order_type}
📊 Status: {order.status}
📅 Created: {order.created_at.strftime('%d %b %Y %H:%M') if order.created_at else 'N/A'}

<b>Details:</b>
{details_text}
"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"order_approve:{order.order_id}"),
            InlineKeyboardButton(text="🔴 Reject", callback_data=f"order_reject:{order.order_id}")
        ],
        [InlineKeyboardButton(text="🟣 In Progress", callback_data=f"order_progress:{order.order_id}")],
        [InlineKeyboardButton(text="🟢 Completed", callback_data=f"order_complete:{order.order_id}")],
        [InlineKeyboardButton(text="🔙 Back to Orders", callback_data="admin_orders")]
    ])

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("order_"))
async def update_order_status(callback: CallbackQuery):
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⛔ Access denied", show_alert=True)
        return

    action, order_id = callback.data.split(":")[0], callback.data.split(":")[1]
    status_map = {
        "order_approve": "Under Review",
        "order_reject": "Rejected",
        "order_progress": "In Progress",
        "order_complete": "Completed"
    }
    new_status = status_map.get(action)

    if not new_status:
        await callback.answer("Invalid action")
        return

    async with async_session() as session:
        result = await session.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalar_one_or_none()

        if order:
            old_status = order.status
            order.status = new_status

            # Update user counters
            user_result = await session.execute(select(User).where(User.telegram_id == order.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                if old_status == "Pending":
                    user.pending_orders = max(0, user.pending_orders - 1)
                if new_status == "Completed":
                    user.completed_orders += 1
                elif new_status in ["Under Review", "In Progress"]:
                    user.approved_orders += 1

            await session.commit()

            # Notify user
            try:
                await callback.bot.send_message(
                    order.user_id,
                    f"📢 <b>Order Status Updated</b>\n\n"
                    f"Order ID: <code>{order.order_id}</code>\n"
                    f"New Status: <b>{new_status}</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    await callback.answer(f"Status updated to {new_status}")
    await admin_orders(callback)
