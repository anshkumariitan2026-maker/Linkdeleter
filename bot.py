import os
import asyncio
import time
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import (
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

load_dotenv()

warnings = {}
spam_tracker = {}

bughunter0 = Client(
    "NoLink-BOT",
    bot_token=os.getenv("BOT_TOKEN"),
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH")
)

link_filter = filters.regex(r"(http|www|t\.me)")

# ---------------- START COMMAND ---------------- #

@bughunter0.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    me = await bot.get_me()

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add Me In A Group", url=f"https://t.me/{me.username}?startgroup=true")],
            [
                InlineKeyboardButton("👑 Owner", url="https://t.me/yourusername"),
                InlineKeyboardButton("💬 Support Group", url="https://t.me/yourgroup")
            ],
            [
                InlineKeyboardButton("📢 Support Channel", url="https://t.me/yourchannel")
            ],
            [
                InlineKeyboardButton("📖 Help", callback_data="help_menu")
            ]
        ]
    )

    await message.reply_text(
        f"👋 Hello {message.from_user.mention}!\n\n"
        "🔒 I protect groups from:\n"
        "• Links 🚫\n"
        "• Spam ⚡\n"
        "• Edited Messages ✏️\n\n"
        "Click below to setup 👇",
        reply_markup=buttons
    )

# ---------------- HELP MENU ---------------- #

@bughunter0.on_callback_query(filters.regex("help_menu"))
async def help_menu(bot, callback_query):

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚙ Uses", callback_data="uses_info")],
            [InlineKeyboardButton("✨ Features", callback_data="features_info")],
            [InlineKeyboardButton("⬅ Back", callback_data="back_start")]
        ]
    )

    await callback_query.message.edit_text(
        "📖 Help Menu\n\nSelect an option:",
        reply_markup=buttons
    )

# ---------------- USES ---------------- #

@bughunter0.on_callback_query(filters.regex("uses_info"))
async def uses_info(bot, callback_query):

    text = (
        "⚙ How To Use Me?\n\n"
        "1️⃣ Add me to your group.\n"
        "2️⃣ Make me Admin.\n\n"
        "🔑 Required Permissions:\n"
        "• Delete Messages\n"
        "• Restrict Members\n"
        "• Manage Chat Permissions\n\n"
        "Then I will automatically protect your group."
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅ Back", callback_data="help_menu")]]
    )

    await callback_query.message.edit_text(text, reply_markup=buttons)

# ---------------- FEATURES ---------------- #

@bughunter0.on_callback_query(filters.regex("features_info"))
async def features_info(bot, callback_query):

    text = (
        "✨ Features\n\n"
        "🚫 All Links Blocked (Only Admin Allowed)\n"
        "⚠ 3 Warnings → 5 Min Mute\n"
        "🔓 Manual Unmute Button\n"
        "❌ Remove Warn Button\n"
        "✏ Edited Messages Deleted\n"
        "⚡ Anti-Spam Protection\n"
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅ Back", callback_data="help_menu")]]
    )

    await callback_query.message.edit_text(text, reply_markup=buttons)

# ---------------- BACK ---------------- #

@bughunter0.on_callback_query(filters.regex("back_start"))
async def back_start(bot, callback_query):
    await start_cmd(bot, callback_query.message)

# ---------------- MAIN MESSAGE HANDLER ---------------- #

@bughunter0.on_message(filters.group)
async def message_handler(bot, message):

    user = message.from_user
    if not user:
        return

    chat_id = message.chat.id
    user_id = user.id

    member = await bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in ["administrator", "creator"]

    # ---------- SPAM SYSTEM ---------- #

    if not is_admin:
        spam_tracker.setdefault(chat_id, {})
        spam_tracker[chat_id].setdefault(user_id, [])

        now = time.time()
        spam_tracker[chat_id][user_id].append(now)

        spam_tracker[chat_id][user_id] = [
            t for t in spam_tracker[chat_id][user_id]
            if now - t <= 5
        ]

        if len(spam_tracker[chat_id][user_id]) >= 5:
            await bot.restrict_chat_member(chat_id, user_id, ChatPermissions())
            await message.reply_text(f"🚫 {user.mention} spam detected! 5 min mute.")
            await asyncio.sleep(300)

            await bot.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )

            spam_tracker[chat_id][user_id] = []
            return

    # ---------- LINK SYSTEM ---------- #

    if not is_admin and link_filter(message):
        try:
            await message.delete()
        except:
            return

        warnings.setdefault(chat_id, {})
        warnings[chat_id].setdefault(user_id, 0)
        warnings[chat_id][user_id] += 1

        warn_count = warnings[chat_id][user_id]

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Remove Warn", callback_data=f"removewarn_{chat_id}_{user_id}")]]
        )

        await message.reply_text(
            f"⚠ {user.mention} link allowed nahi!\nWarning: {warn_count}/3",
            reply_markup=buttons
        )

        if warn_count >= 3:
            await bot.restrict_chat_member(chat_id, user_id, ChatPermissions())

            unmute_button = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔓 Unmute", callback_data=f"unmute_{chat_id}_{user_id}")]]
            )

            await message.reply_text(
                f"🚫 {user.mention} muted for 5 minutes.",
                reply_markup=unmute_button
            )

            warnings[chat_id][user_id] = 0
            await asyncio.sleep(300)

            await bot.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )

# ---------------- DELETE EDITED ---------------- #

@bughunter0.on_edited_message(filters.group)
async def delete_edited(bot, message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        await message.delete()

# ---------------- REMOVE WARN ---------------- #

@bughunter0.on_callback_query(filters.regex("removewarn"))
async def remove_warn(bot, callback_query):

    data = callback_query.data.split("_")
    chat_id = int(data[1])
    user_id = int(data[2])

    admin = await bot.get_chat_member(chat_id, callback_query.from_user.id)
    if admin.status not in ["administrator", "creator"]:
        await callback_query.answer("Admin only!", show_alert=True)
        return

    if chat_id in warnings and user_id in warnings[chat_id]:
        if warnings[chat_id][user_id] > 0:
            warnings[chat_id][user_id] -= 1

    await callback_query.message.edit_text("✅ Warning removed.")
    await callback_query.answer("Removed!")

# ---------------- UNMUTE ---------------- #

@bughunter0.on_callback_query(filters.regex("unmute"))
async def unmute_user(bot, callback_query):

    data = callback_query.data.split("_")
    chat_id = int(data[1])
    user_id = int(data[2])

    admin = await bot.get_chat_member(chat_id, callback_query.from_user.id)
    if admin.status not in ["administrator", "creator"]:
        await callback_query.answer("Admin only!", show_alert=True)
        return

    await bot.restrict_chat_member(
        chat_id,
        user_id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    await callback_query.message.edit_text("🔓 User unmuted.")
    await callback_query.answer("Done!")

bughunter0.run()
