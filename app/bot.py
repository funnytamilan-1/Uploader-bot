import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import get_settings
from app.db import SessionLocal
from app.repositories import get_or_create_user
from app.security import is_admin
from app.logging import configure_logging, get_logger

log=get_logger("bot")

def buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings"), InlineKeyboardButton("📋 Queue", callback_data="queue")],
        [InlineKeyboardButton("🗓 Schedule", callback_data="schedule"), InlineKeyboardButton("⭐ Premium", callback_data="premium")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

def create_app():
    s=get_settings()
    app=Client("media_uploader_bot", api_id=s.api_id, api_hash=s.api_hash, bot_token=s.bot_token, workdir=s.media_root)

    @app.on_message(filters.command("start"))
    async def start(_, message):
        async with SessionLocal() as session:
            await get_or_create_user(session,message.from_user.id,message.from_user.username,message.from_user.first_name)
            await session.commit()
        await message.reply_text("Welcome to the Media Automation Bot.", reply_markup=buttons())

    @app.on_message(filters.command("help"))
    async def help_cmd(_, message):
        await message.reply_text("/start /help /settings /queue /status /schedule /premium /cancel")

    @app.on_message(filters.command("settings"))
    async def settings(_, message):
        await message.reply_text("Settings", reply_markup=buttons())

    @app.on_message(filters.command("queue"))
    async def queue(_, message):
        await message.reply_text("Queue status is available from the worker-backed dashboard.")

    @app.on_message(filters.command("status"))
    async def status(_, message):
        await message.reply_text("Service status: online")

    @app.on_message(filters.command("schedule"))
    async def schedule(_, message):
        await message.reply_text("Use the scheduler UI to create a persisted schedule.")

    @app.on_message(filters.command("premium"))
    async def premium(_, message):
        await message.reply_text("Premium plans are controlled server-side.")

    @app.on_message(filters.command("cancel"))
    async def cancel(_, message):
        await message.reply_text("Cancellation request received. Active job cancellation can be wired to the queue state.")

    @app.on_message(filters.command("admin"))
    async def admin(_, message):
        if not is_admin(message.from_user.id):
            return await message.reply_text("Not authorized.")
        await message.reply_text("Admin Dashboard", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Users",callback_data="admin_users"),InlineKeyboardButton("Premium",callback_data="admin_premium")],
            [InlineKeyboardButton("Channels",callback_data="admin_channels"),InlineKeyboardButton("Queue",callback_data="admin_queue")],
            [InlineKeyboardButton("Scheduler",callback_data="admin_scheduler"),InlineKeyboardButton("Logs",callback_data="admin_logs")],
        ]))

    @app.on_message(filters.command("stats") & filters.user(s.admin_id_set))
    async def stats(_, message): await message.reply_text("Stats endpoint ready.")

    @app.on_message(filters.command("channels") & filters.user(s.admin_id_set))
    async def channels(_, message): await message.reply_text("Channel administration endpoint ready.")

    @app.on_message(filters.command("users") & filters.user(s.admin_id_set))
    async def users(_, message): await message.reply_text("User administration endpoint ready.")

    @app.on_message(filters.command("broadcast") & filters.user(s.admin_id_set))
    async def broadcast(_, message): await message.reply_text("Broadcast requires an explicit admin workflow.")

    @app.on_callback_query()
    async def callbacks(_, query):
        await query.answer()
        await query.message.edit_text(f"Selected: {query.data}", reply_markup=buttons())

    return app

async def run_bot():
    configure_logging()
    app=create_app()
    async with app:
        log.info("bot_started")
        await asyncio.Event().wait()
