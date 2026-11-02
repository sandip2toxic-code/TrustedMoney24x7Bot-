from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="📢 Join Official Channel", callback_data="join_channel"))
    builder.row(InlineKeyboardButton(text="📣 Promote Your Channel / Group / Bot", callback_data="promote_telegram"))
    builder.row(InlineKeyboardButton(text="📱 Promote Your App", callback_data="promote_app"))
    builder.row(InlineKeyboardButton(text="🆕 Latest Earning Apps", callback_data="earning_apps"))
    builder.row(InlineKeyboardButton(text="🎁 Free Loots & Rewards", callback_data="free_loots"))
    builder.row(InlineKeyboardButton(text="💰 Earning Opportunities", callback_data="earning_opportunities"))
    builder.row(InlineKeyboardButton(text="📰 App News & Launches", callback_data="app_news"))
    builder.row(InlineKeyboardButton(text="🤖 Create Your Telegram Bot", callback_data="create_bot"))
    builder.row(InlineKeyboardButton(text="👤 My Profile", callback_data="my_profile"))
    builder.row(InlineKeyboardButton(text="📞 Contact Support", callback_data="contact_support"))
    
    return builder.as_markup()


def back_home_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="back"),
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    )
    return builder.as_markup()


def join_channel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 Join Channel", url="https://t.me/Trusted_Money_India"))
    builder.row(InlineKeyboardButton(text="✅ Verify Membership", callback_data="verify_membership"))
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu"))
    return builder.as_markup()


def promote_telegram_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 Channel Promotion", callback_data="promo_channel"))
    builder.row(InlineKeyboardButton(text="👥 Group Promotion", callback_data="promo_group"))
    builder.row(InlineKeyboardButton(text="🤖 Bot Promotion", callback_data="promo_bot"))
    builder.row(InlineKeyboardButton(text="📌 Sponsored Post", callback_data="promo_sponsored"))
    builder.row(InlineKeyboardButton(text="📦 Custom Package", callback_data="promo_custom"))
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu"))
    return builder.as_markup()


def promote_app_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📱 Android App", callback_data="app_android"))
    builder.row(InlineKeyboardButton(text="🍎 iOS App", callback_data="app_ios"))
    builder.row(InlineKeyboardButton(text="🌐 Web App", callback_data="app_web"))
    builder.row(InlineKeyboardButton(text="💰 Earning App", callback_data="app_earning"))
    builder.row(InlineKeyboardButton(text="🎯 Task-Based App", callback_data="app_task"))
    builder.row(InlineKeyboardButton(text="🎁 Reward App", callback_data="app_reward"))
    builder.row(InlineKeyboardButton(text="📢 Sponsored Ad", callback_data="app_sponsored"))
    builder.row(InlineKeyboardButton(text="📦 Promotion Packages", callback_data="app_packages"))
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu"))
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
    return builder.as_markup()


def admin_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_dashboard"))
    builder.row(InlineKeyboardButton(text="📱 Manage Apps", callback_data="admin_apps"))
    builder.row(InlineKeyboardButton(text="🎁 Manage Loots", callback_data="admin_loots"))
    builder.row(InlineKeyboardButton(text="📰 Manage News", callback_data="admin_news"))
    builder.row(InlineKeyboardButton(text="📦 Orders", callback_data="admin_orders"))
    builder.row(InlineKeyboardButton(text="👥 Users", callback_data="admin_users"))
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu"))
    return builder.as_markup()
