from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import back_home_kb, main_menu_kb

router = Router()


# ====================== LATEST EARNING APPS ======================
@router.callback_query(F.data == "earning_apps")
async def earning_apps(callback: CallbackQuery):
    text = """
🆕 <b>Latest Earning Apps</b>

Currently we are preparing verified earning apps list.

Categories coming soon:
• Newly Launched Apps
• Trending Apps
• Reward Apps
• Task-Based Apps
• Referral Apps
• Featured Apps

Please check back later. New apps will be added regularly by admin.
"""
    await callback.message.edit_text(text, reply_markup=back_home_kb(), parse_mode="HTML")
    await callback.answer()


# ====================== FREE LOOTS & REWARDS ======================
@router.callback_query(F.data == "free_loots")
async def free_loots(callback: CallbackQuery):
    text = """
🎁 <b>Free Loots & Rewards</b>

Currently no active loots available.

Categories:
• Free Registration Rewards
• Cashback Offers
• Task Rewards
• Promo Codes
• Limited-Time Offers

Admin will add verified offers soon. Stay tuned!
"""
    await callback.message.edit_text(text, reply_markup=back_home_kb(), parse_mode="HTML")
    await callback.answer()


# ====================== EARNING OPPORTUNITIES ======================
@router.callback_query(F.data == "earning_opportunities")
async def earning_opportunities(callback: CallbackQuery):
    text = """
💰 <b>Earning Opportunities</b>

We are collecting genuine opportunities.

Coming soon:
• Mobile-Based Tasks
• Typing & Microtasks
• Online Task Platforms
• Referral Programs
• Freelancing Resources
• Learn & Earn

Please check this section later.
"""
    await callback.message.edit_text(text, reply_markup=back_home_kb(), parse_mode="HTML")
    await callback.answer()


# ====================== APP NEWS & LAUNCHES ======================
@router.callback_query(F.data == "app_news")
async def app_news(callback: CallbackQuery):
    text = """
📰 <b>App News & Launches</b>

No news available at the moment.

Sections:
• Today's New App Launches
• Yesterday's App Launches
• Upcoming App Launches
• Trending App News
• App Warnings & Scam Alerts
• Withdrawal Updates

Admin will post important updates here.
"""
    await callback.message.edit_text(text, reply_markup=back_home_kb(), parse_mode="HTML")
    await callback.answer()
