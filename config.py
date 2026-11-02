import os
from dotenv import load_dotenv

load_dotenv()

# ====================== BOT SETTINGS ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8778723393

# ====================== CHANNEL & SUPPORT ======================
OFFICIAL_CHANNEL = "@Trusted_Money_India"
OFFICIAL_CHANNEL_LINK = "https://t.me/Trusted_Money_India"
SUPPORT_USERNAME = "@TM_24x7_SERVICE"

# ====================== BOT INFO ======================
BOT_NAME = "Trusted Money 💸"
BOT_USERNAME = "@TrustedMoney24x7Bot"

# ====================== DATABASE ======================
# SQLite for easy start (later you can change to PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///trusted_money.db")

# ====================== OTHER ======================
# Referral reward (you can change later)
REFERRAL_REWARD = 0
