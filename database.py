from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Text, Integer, Boolean, DateTime, ForeignKey, Float
from datetime import datetime
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=True)
    username: Mapped[str] = mapped_column(String(64), nullable=True)
    referral_code: Mapped[str] = mapped_column(String(20), unique=True)
    referred_by: Mapped[int] = mapped_column(BigInteger, nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    pending_orders: Mapped[int] = mapped_column(Integer, default=0)
    approved_orders: Mapped[int] = mapped_column(Integer, default=0)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_channel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    order_type: Mapped[str] = mapped_column(String(50))  # channel, group, bot, app, bot_dev
    status: Mapped[str] = mapped_column(String(30), default="Pending")  # Pending, Under Review, Awaiting Payment, In Progress, Completed, Rejected, Cancelled
    details: Mapped[str] = mapped_column(Text)  # JSON string of form data
    price: Mapped[float] = mapped_column(Float, default=0)
    admin_note: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AppListing(Base):
    __tablename__ = "app_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    logo_file_id: Mapped[str] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(String(50))
    download_link: Mapped[str] = mapped_column(String(300))
    website: Mapped[str] = mapped_column(String(300), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    features: Mapped[str] = mapped_column(Text, nullable=True)
    platform: Mapped[str] = mapped_column(String(50))  # Android / iOS / Web
    earning_method: Mapped[str] = mapped_column(Text, nullable=True)
    min_withdrawal: Mapped[str] = mapped_column(String(50), nullable=True)
    countries: Mapped[str] = mapped_column(String(200), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    launch_date: Mapped[str] = mapped_column(String(30), nullable=True)
    last_verified: Mapped[str] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Loot(Base):
    __tablename__ = "loots"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    reward_details: Mapped[str] = mapped_column(Text)
    eligibility: Mapped[str] = mapped_column(Text, nullable=True)
    steps: Mapped[str] = mapped_column(Text, nullable=True)
    expiry_date: Mapped[str] = mapped_column(String(30), nullable=True)
    terms: Mapped[str] = mapped_column(Text, nullable=True)
    official_link: Mapped[str] = mapped_column(String(300))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))  # launch, warning, update, etc.
    app_name: Mapped[str] = mapped_column(String(150), nullable=True)
    source: Mapped[str] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
