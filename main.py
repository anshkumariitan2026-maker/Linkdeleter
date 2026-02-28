import os
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import (
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

warnings = {}
spam_tracker = {}

bughunter0 = Client(
    "NoLink-BOT",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"]
)

link_filter = filters.regex(r"(http|www|t\.me)")

# ---------------- LINK + NORMAL MESSAGE HANDLER ---------------- #

@bughunter0.on_message(filters.group)
async def message_handler(bot, message):
    user = message.from_user
    if not user:
        return

    chat_id = message.chat.id
    user_id = user.id

    member = await bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in ["administrator", "creator"]

    # ---------------- SPAM SYSTEM ---------------- #

    if not is_admin:
        spam_tracker.setdefault(chat_id, {})
        spam_tracker[chat_id].setdefault(user_id, [])

        current_time = time.time()
        spam_tracker[chat_id][user_id].append(current_time)

        # Last 5 seconds messages filter
        spam_tracker[chat_id][user_id] = [
            t for t in spam_tracker[chat_id][user_id]
            if current_time - t <= 5
        ]

        if len(spam_tracker[chat_id][user_id]) >= 5:
            await bot.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions()
            )

            await message.reply_text(
                f"🚫 {user.mention} spam karne ki wajah se 5 minute mute!"
            )

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

    # ---------------- LINK SYSTEM ---------------- #

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
            f"⚠️ {user.mention} link allowed nahi!\nWarning: {warn_count}/3",
            reply_markup=buttons
        )

        if warn_count >= 3:
            await bot.restrict_chat_member(chat_id, user_id, ChatPermissions())

            unmute_button = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔓 Unmute", callback_data=f"unmute_{chat_id}_{user_id}")]]
            )

            await message.reply_text(
                f"🚫 {user.mention} 3 warning ke baad 5 min mute!",
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

# ---------------- DELETE EDITED MESSAGE ---------------- #

@bughunter0.on_edited_message(filters.group)
async def delete_edited(bot, message):
    user = message.from_user
    if not user:
        return

    member = await bot.get_chat_member(message.chat.id, user.id)
    if member.status in ["administrator", "creator"]:
        return

    try:
        await message.delete()
    except:
        pass

# ---------------- REMOVE WARN ---------------- #

@bughunter0.on_callback_query(filters.regex("removewarn"))
async def remove_warn(bot, callback_query):
    data = callback_query.data.split("_")
    chat_id = int(data[1])
    user_id = int(data[2])

    admin = await bot.get_chat_member(chat_id, callback_query.from_user.id)
    if admin.status not in ["administrator", "creator"]:
        await callback_query.answer("❌ Sirf admin!", show_alert=True)
        return

    if chat_id in warnings and user_id in warnings[chat_id]:
        if warnings[chat_id][user_id] > 0:
            warnings[chat_id][user_id] -= 1

    await callback_query.message.edit_text("✅ Warning remove kar diya gaya.")
    await callback_query.answer("Warn removed!")

# ---------------- UNMUTE ---------------- #

@bughunter0.on_callback_query(filters.regex("unmute"))
async def unmute_user(bot, callback_query):
    data = callback_query.data.split("_")
    chat_id = int(data[1])
    user_id = int(data[2])

    admin = await bot.get_chat_member(chat_id, callback_query.from_user.id)
    if admin.status not in ["administrator", "creator"]:
        await callback_query.answer("❌ Sirf admin unmute kar sakta hai!", show_alert=True)
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

    await callback_query.message.edit_text("🔓 User unmute.")
    await callback_query.answer("Unmuted!")

bughunter0.run()
