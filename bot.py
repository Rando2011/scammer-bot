from telethon import TelegramClient
from telethon.tl.types import MessageEntityCustomEmoji
from telegram import Update, MessageEntity
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import html
import sqlite3
import shutil
import os
from datetime import datetime
import time
import asyncio
from telegram.ext import CallbackQueryHandler

api_id = 31710604
api_hash = "b29777557d456a37369744e6398b9a95"
BOT_TOKEN = "8956385850:AAEnHdhdT9DAlFHTDlNRreBmgb5sQnjy27I"

client = TelegramClient("admin_session2", api_id, api_hash)

# ===== DATABASE =====
conn = sqlite3.connect("scam.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tracked_users (
    user_id INTEGER UNIQUE,
    old_username TEXT,
    current_username TEXT
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scams (
    user_id INTEGER,
    username TEXT,
    reason TEXT,
    reporter TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    username TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER UNIQUE
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vote_candidates (
    username TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
    username TEXT,
    user_id INTEGER,
    vote TEXT,
    UNIQUE(username, user_id)
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    reason TEXT,
    reporter_id INTEGER,
    reporter_username TEXT,
    status TEXT
)
""")
conn.commit()

OWNER_ID = 7104914546

def is_admin(user_id):

    if int(user_id) == OWNER_ID:
        return True

    cursor.execute(
        "SELECT * FROM admins WHERE user_id=?",
        (str(user_id),)
    )

    return cursor.fetchone() is not None

async def userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:

        await update.message.reply_text(
            "❌ Owner only"
        )

        return

    if not context.args:
        await update.message.reply_text(
            "သုံးနည်း:\n/userinfo user_id user_id user_id"
        )
        return

    loading = await update.message.reply_text("🔎 Searching user info...")

    await client.start()

    result = ""

    for target in context.args:

        try:
            user_id = int(target)

            user = await client.get_entity(user_id)

            username = (
                f"@{user.username}"
                if user.username
                else "No Username"
            )

            name = (
                f"{user.first_name or ''} {user.last_name or ''}"
            ).strip()

            result += (
                "╔═══━━━─── • ───━━━═══╗\n"
                "👤 USER INFO 👤\n"
                "╚═══━━━─── • ───━━━═══╝\n\n"
                f"👤 Name » {name}\n"
                f"🔗 Username » {username}\n"
                f"🆔 ID » <code>{user.id}</code>\n\n"
            )

        except Exception as e:
            result += (
                "╔═══━━━─── • ───━━━═══╗\n"
                "❌ USER NOT FOUND ❌\n"
                "╚═══━━━─── • ───━━━═══╝\n\n"
                f"🆔 ID » <code>{target}</code>\n\n"
            )

        if len(result) > 3500:
            await update.message.reply_text(
                result,
                parse_mode="HTML"
            )
            result = ""

    if result:
        await loading.edit_text(
            result,
            parse_mode="HTML"
        )
    else:
        await loading.delete()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO users VALUES (?)",
            (user_id,)
        )

        conn.commit()

    except Exception as e:
        print(e)

    text = """
╔═══━━━─── • ───━━━═══╗
🛡 𝗦𝗖𝗔𝗠𝗠𝗘𝗥 𝗔𝗟𝗘𝗥𝗧 𝗕𝗢𝗧 🛡
╚═══━━━─── • ───━━━═══╝

⚡ 𝗦𝘆𝘀𝘁𝗲𝗺 𝗥𝗲𝗮𝗱𝘆
🔎 𝗙𝗮𝘀𝘁 𝗦𝗲𝗮𝗿𝗰𝗵
📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗦𝗰𝗮𝗻𝗻𝗲𝗿
🚨 𝗦𝗰𝗮𝗺 𝗗𝗲𝘁𝗲𝗰𝘁𝗶𝗼𝗻

✅ 𝗕𝗼𝘁 𝗥𝗲𝗮𝗱𝘆
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Add To Groups",
                url="https://t.me/Scammer_onlybot?startgroup=true"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

async def groupscan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":

        await update.message.reply_text(
            "❌ Group ထဲမှာပဲ သုံးလို့ရပါတယ်"
        )

        return

    try:

        member = await context.bot.get_chat_member(
            chat.id,
            user.id
        )

        if member.status not in [
            "creator",
            "administrator"
        ]:

            await update.message.reply_text(
                "❌ Group Owner/Admin only"
            )

            return

        bot_member = await context.bot.get_chat_member(
            chat.id,
            context.bot.id
        )

        if bot_member.status not in [
            "creator",
            "administrator"
        ]:

            await update.message.reply_text(
                "╔═══━━━─── • ───━━━═══╗\n"
                "⚠️ GROUPSCAN REQUIREMENTS ⚠️\n"
                "╚═══━━━─── • ───━━━═══╝\n\n"
                "🤖 Bot ကို Admin ပေးပြီးမှ\n"
                "/groupscan အသုံးပြုနိုင်ပါတယ်။"
            )

            return

        await client.start()

        me = await client.get_me()

        try:

            await client.get_dialogs()

            telethon_member = await client.get_permissions(
                chat.id,
                me.id
            )

            if not telethon_member.is_admin:

                await update.message.reply_text(
                    "╔═══━━━─── • ───━━━═══╗\n"
                    "⚠️ GROUPSCAN REQUIREMENTS ⚠️\n"
                    "╚═══━━━─── • ───━━━═══╝\n\n"
                    "🔒 This group requires admin access.\n\n"
                    f"📌 Please promote:\n"
                    f"• Bot → Admin\n"
                    f"• @{me.username} → Admin\n\n"
                    "ပြီးရင် /groupscan ပြန်သုံးပါ။"
                )

                return

        except Exception as e:

            await update.message.reply_text(
                f"❌ Telethon Admin Check Error\n\n{e}"
            )

            return

    except Exception as e:

        await update.message.reply_text(
            f"❌ Admin Check Error\n\n{e}"
        )

        return

    loading = await update.message.reply_text(
        "╔═══━━━─── • ───━━━═══╗\n"
        "🔎 GROUP SCAN STARTED 🔎\n"
        "╚═══━━━─── • ───━━━═══╝\n\n"
        "⚡ Scanning Members...\n"
        "█▒▒▒▒▒▒▒▒▒ 10%"
    )

    try:

        cursor.execute(
            "SELECT user_id, username, reason FROM scams"
        )

        scam_rows = cursor.fetchall()

        scam_db = {}

        for row in scam_rows:

            try:

                scam_db[int(row[0])] = {
                    "username": row[1],
                    "reason": row[2]
                }

            except:
                pass

        found = []
        checked = 0

        async for m in client.iter_participants(chat.id):

            checked += 1

            if m.id in scam_db:

                current_username = (
                    f"@{m.username}"
                    if m.username
                    else "No Username"
                )

                found.append(
                    (
                        m.id,
                        current_username,
                        scam_db[m.id]["username"],
                        scam_db[m.id]["reason"]
                    )
                )

            if checked % 300 == 0:

                try:

                    await loading.edit_text(
                        "╔═══━━━─── • ───━━━═══╗\n"
                        "🔎 SCANNING MEMBERS 🔎\n"
                        "╚═══━━━─── • ───━━━═══╝\n\n"
                        "██████▒▒▒▒ 60%\n\n"
                        f"👥 Checked » {checked}\n"
                        f"🚨 Detected » {len(found)}"
                    )

                except:
                    pass

        if not found:

            await loading.edit_text(
                "╔═══━━━─── • ───━━━═══╗\n"
                "✅ SCAN COMPLETE ✅\n"
                "╚═══━━━─── • ───━━━═══╝\n\n"
                f"👥 Checked » {checked}\n"
                "🛡 No scammers detected."
            )

            return

        text = (
            "╔═══━━━─── • ───━━━═══╗\n"
            "🚨 GROUP SCAMMER DETECTED 🚨\n"
            "╚═══━━━─── • ───━━━═══╝\n\n"
            f"👥 Group » {chat.title}\n"
            f"🔎 Checked » {checked}\n"
            f"🚨 Detected » {len(found)}\n\n"
        )

        for i, item in enumerate(found, start=1):

            user_id, current_username, saved_username, reason = item

            text += (
                f"{i}. {current_username}\n"
                f"🆔 ID » <code>{user_id}</code>\n"
                f"📌 Saved » {saved_username}\n"
                f"📝 Reason » {reason}\n\n"
            )

        await loading.edit_text(
            text[:4000],
            parse_mode="HTML"
        )

    except Exception as e:

        await loading.edit_text(
            f"❌ Group Scan Error\n\n{e}"
        )

async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:


        await update.message.reply_text(
            "⌛ Owner only",
            entities=[
                MessageEntity(
                    type="custom_emoji",
                    offset=0,
                    length=1,
        custom_emoji_id="5386367538735104399"
                )
            ]
        )

        return

    if not context.args:

        await update.message.reply_text(
            "သုံးနည်း:\n/removeadmin user_id"
        )

        return

    admin_id = context.args[0]

    cursor.execute(
        "DELETE FROM admins WHERE user_id=?",
        (admin_id,)
    )

    conn.commit()

    await update.message.reply_text(
        f"✅ Admin Removed\n\n"
        f"🆔 ID » {admin_id}"
    )

async def scamlist(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute(
        "SELECT username, user_id FROM scams"
    )

    rows = cursor.fetchall()

    if not rows:

        await update.message.reply_text(
            "✅ Scam list empty"
        )

        return

    text = (

        "╔═══━━━─── • ───━━━═══╗\n"
        "🚨 𝗦𝗖𝗔𝗠 𝗟𝗜𝗦𝗧 🚨\n"
        "╚═══━━━─── • ───━━━═══╝\n\n"
    )

    count = 1

    for row in rows:

        username = row[0]

        user_id = row[1]

        text += (
            f"{count}. {username}\n"
            f" ID » <code>{user_id}</code>\n\n"
    )

        count += 1

    await update.message.reply_text(
        text[:4000],
        parse_mode="HTML"
    )


async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):


    loading = await update.message.reply_text(
        "🔎 Loading Admin List."
    )

    await asyncio.sleep(0.4)

    await loading.edit_text(
        "🔎 Loading Admin List.."
    )

    await asyncio.sleep(0.4)

    await loading.edit_text(
        "🔎 Loading Admin List..."
    )

    await asyncio.sleep(0.4)

    cursor.execute(
        "SELECT user_id FROM admins"
    )

    rows = cursor.fetchall()

    text = """
╔═══━━━─── • ───━━━═══╗
👑 𝗔𝗗𝗠𝗜𝗡 𝗟𝗜𝗦𝗧 👑
╚═══━━━─── • ───━━━═══╝

"""

    text += f"👑 Owner ID » {OWNER_ID}\n\n"

    if not rows:

        text += "❌ No Admins Found"

    else:

        for row in rows:

            admin_id = row[0]

            try:

                user = await client.get_entity(admin_id)

                username = (
                    f"@{user.username}"
                    if user.username
                    else "No Username"
                )

                fullname = (
                    f"{user.first_name}"
                    if user.first_name
                    else "Unknown"
                )

                text += (
                    f"🛡 Admin » {username}\n"
                    f"👤 Name » {fullname}\n"
                    f"🆔 ID » {admin_id}\n\n"
                )

            except Exception as e:

                text += (
                    f"🛡 Admin » Unknown User\n"
                    f"🆔 ID » {admin_id}\n\n"
                )

    await loading.delete()

    await update.message.reply_text(text)

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(
            "☄️ Owner only",
            entities=[
                MessageEntity(
                    type="custom_emoji",
                    offset=0,
                    length=2,
        custom_emoji_id="5224607267797606837"
                )
            ]
        )

        return

    try:

        now = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        backup_name = f"backup_{now}.db"

        shutil.copy(
            "scam.db",
            backup_name
        )

        await update.message.reply_document(
            document=open(backup_name, "rb"),
            caption="✅ Database Backup Ready"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Backup Error\n\n{e}"
        )

async def scam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = "⚠️ Scam Contacts List\n\n"

    await client.start()
    contacts = result_contacts.users

    found = False

    for user in contacts:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "No username"

        if "scam" in name.lower():
            found = True
            result += f"👤 {name}\n🔗 {username}\n\n"

    if not found:
        result = "✅ No scam contacts found."

    await update.message.reply_text(result)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("သုံးနည်း:\n/search @username")
        return

    query = " ".join(context.args).strip().lower()
    search_query = query.replace("@", "").lower()

    result = f"🔎 Search Result for {query}\n\n"
    found = 0
    loading = await update.message.reply_text(
    "🔎 Searching..."
    )

    await client.start()

    await loading.edit_text(
        "█▒▒▒▒▒▒▒▒▒ 10%\n"
        "⚡ Searching..."
    )

    await asyncio.sleep(4.2)

    await loading.edit_text(
        "███▒▒▒▒▒▒▒ 27%\n"
        "⚡ Searching..."
    )

    await asyncio.sleep(4.2)

    await loading.edit_text(
        "█████▒▒▒▒▒ 43%\n"
        "⚡ Searching..."
    )

    await asyncio.sleep(4.2)

    await loading.edit_text(
        "███████▒▒▒ 61%\n"
        "⚡ Searching..."
    )

    await asyncio.sleep(4.2)

    await loading.edit_text(
        "████████▒▒ 78%\n"
        "⚡ Searching..."
    )

    await asyncio.sleep(4.2)

    await loading.edit_text(
        "█████████▒ 91%\n"
        "☠⚡ Searching..."
    )


# =========================
    # DATABASE SEARCH
    # =========================

    search_user_id = None

    try:

        await client.start()

        entity_user = await client.get_entity(query)

        search_user_id = entity_user.id

    except Exception as e:

        print("GET ID ERROR:", e)

    try:

        cursor.execute(
            "SELECT * FROM scams"
        )

        for row in cursor.fetchall():

            db_user_id = row[0]

            db_username = (
                str(row[1])
                .lower()
                .replace("@", "")
            )

            db_reason = row[2]

            db_reporter = row[3]

            if (
                search_query in db_username
                or
                (
                    search_user_id is not None
                    and
                    int(search_user_id)
                    ==
                    int(db_user_id)
                )
            ):

                found += 1

                changed_text = ""

                searched_username = (
                    f"@{search_query}"
                    .lower()
                )

                saved_username = (
                    str(row[1])
                    .lower()
                )

                if (
                    search_user_id is not None
                    and
                    int(search_user_id)
                    ==
                    int(db_user_id)
                    and
                    searched_username
                    !=
                    saved_username
                ):

                    changed_text = (
                        "🔄 Username Changed Detected\n"
                        f"📛 Old Username » {row[1]}\n"
                        f"✨ Current Username » @{search_query}\n\n"
                    )

                result += (

                    "╔═══━━━─── • ───━━━═══╗\n"
                    "🚨 𝗦𝗖𝗔𝗠𝗠𝗘𝗥 𝗗𝗘𝗧𝗘𝗖𝗧𝗘𝗗 🚨\n"
                    "╚═══━━━─── • ───━━━═══╝\n\n"

                    f"👤 Saved Username » {row[1]}\n"

                    f"🆔 User ID » {row[0]}\n\n"

                    f"{changed_text}"

                    f"📝 Reason » {db_reason}\n"

                    f"👮 Added By » {db_reporter}\n\n"

                    "⚠️ Username ပြောင်းထားလည်း "
                    "ID နဲ့ detect ဖြစ်ပါတယ်。\n"

                    "━━━━━━━━━━━━━━━\n\n"
                )

    except Exception as e:

        print("DATABASE ERROR:", e)

# =========================
    # SAVED CHANNELS SEARCH
    # =========================

    try:

        cursor.execute("SELECT username FROM channels")
        channels = cursor.fetchall()

        for ch in channels:

            channel_username = ch[0]
            channel_found = 0

            try:

                entity = await client.get_entity(
                    channel_username
                )

                async for msg in client.iter_messages(
                    entity,
                    limit=300
                ):

                    text = msg.message or ""
                    text_lower = text.lower()

                    scam_keywords = [
                        "scam",
                        "scammer",
                        "fake"
                    ]

                    keyword_found = any(
                        word in text_lower
                        for word in scam_keywords
                    )

                    if (
                        search_query in text_lower.replace("@", "")
                        and keyword_found
                    ):

                        found += 1
                        channel_found += 1

                        result += (

                            "╔═══━━━─── • ───━━━═══╗\n"
                            "📢 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗠𝗔𝗧𝗖𝗛 📢\n"
                            "╚═══━━━─── • ───━━━═══╝\n\n"

                            f"🔗 Channel » {channel_username}\n\n"

                            f"📝 Evidence:\n"
                            f"{text[:300]}\n\n"

                            "━━━━━━━━━━━━━━━\n\n"
                        )

                        if channel_found >= 5:
                            break

            except Exception as e:
                print(
                    "CHANNEL ERROR:",
                    channel_username,
                    e
                )

    except Exception as e:
        print("CHANNEL DB ERROR:", e)

# 4) ALL GROUPS SEARCH
    try:
        async for dialog in client.iter_dialogs(limit=80):
            if not dialog.is_group:
                continue

            group_found = 0

            try:
                async for msg in client.iter_messages(dialog.id, limit=100):
                    text = msg.message or ""
                    text_lower = text.lower()

                    scam_keywords = [
                        "scam",
                        "scammer"
                    ]

                    keyword_found = any(
                        word in text_lower
                        for word in scam_keywords
                    )

                    if (
                        search_query in text_lower.replace("@", "")
                        and keyword_found
                    ):
                        found += 1
                        group_found += 1

                        result += (
                            f"👥 Group Match: {dialog.name}\n"
                            f"📝 {text[:250]}\n\n"
                        )

                        if group_found >= 3:
                            break

            except Exception as e:
                print("GROUP ERROR:", dialog.name, e)

    except Exception as e:
        print("GROUP SEARCH ERROR:", e)
    await asyncio.sleep(0.5)

    await loading.edit_text(
        "██████████ 100%\n"
        "✅ Complete"
    )

    await asyncio.sleep(0.5)

    if found == 0:
        result = "❌ မတွေ့ပါ(ဘာ၀ယ်၀ယ်ကြားခံ‌ေခါ်ပါ)"

    try:
        await loading.delete()
    except:
        pass

    await update.message.reply_text(result[:4000])

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:
        await update.message.reply_text(
            "သုံးနည်း:\n/report @username reason"
        )
        return

    target = context.args[0].strip()
    reason = " ".join(context.args[1:])

    reporter_id = update.effective_user.id

    cursor.execute(
        "SELECT * FROM scams WHERE user_id=?",
        (reporter_id,)
    )

    scammer_reporter = cursor.fetchone()

    if scammer_reporter:
        await update.message.reply_text(
            "❌ Scam database ထဲရှိသူများ report တင်လို့မရပါ"
        )
        return

    reporter_username = (
        f"@{update.effective_user.username}"
        if update.effective_user.username
        else "No Username"
    )

    try:
        await client.start()
        user = await client.get_entity(target)

        user_id = user.id
        username = f"@{user.username}" if user.username else target

    except Exception:
        user_id = 0
        username = target

    cursor.execute(
        """
        INSERT INTO reports
        (user_id, username, reason, reporter_id, reporter_username, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            username,
            reason,
            reporter_id,
            reporter_username,
            "pending"
        )
    )

    conn.commit()
    report_id = cursor.lastrowid

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"report_approve|{report_id}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"report_reject|{report_id}"
            )
        ]
    ]

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            "╔═══━━━─── • ───━━━═══╗\n"
            "🚨 NEW SCAM REPORT 🚨\n"
            "╚═══━━━─── • ───━━━═══╝\n\n"
            f"🆔 Report ID » {report_id}\n\n"
            f"👤 Reported User » {username}\n"
            f"🆔 User ID » {user_id}\n"
            f"📝 Reason » {reason}\n\n"
            f"👮 Reporter » {reporter_username}\n"
            f"🆔 Reporter ID » {reporter_id}"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "✅ Report တင်ပြီးပါပြီ။\n\n"
        "Owner စစ်ပြီး Approve/Reject လုပ်ပါမယ်။"
    )

async def report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_ID:
        await query.answer("Owner only", show_alert=True)
        return

    data = query.data

    if not data.startswith("report_"):
        return

    action, report_id = data.split("|")
    report_id = int(report_id)

    cursor.execute(
        """
        SELECT user_id, username, reason, reporter_id, reporter_username, status
        FROM reports
        WHERE report_id=?
        """,
        (report_id,)
    )

    report_data = cursor.fetchone()

    if not report_data:
        await query.edit_message_text("❌ Report မတွေ့ပါ")
        return

    user_id, username, reason, reporter_id, reporter_username, status = report_data

    if status != "pending":
        await query.edit_message_text("⚠️ ဒီ report ကို already review လုပ်ပြီးပါပြီ")
        return

    if action == "report_approve":

        cursor.execute(
            "SELECT * FROM scams WHERE user_id=?",
            (user_id,)
        )

        already = cursor.fetchone()

        if not already:
            cursor.execute(
                "INSERT INTO scams VALUES (?, ?, ?, ?)",
                (
                    user_id,
                    username,
                    reason,
                    "Owner Approved"
                )
            )

            cursor.execute(
                """
                INSERT OR REPLACE INTO tracked_users
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    username,
                    username
                )
            )

        cursor.execute(
            "UPDATE reports SET status=? WHERE report_id=?",
            ("approved", report_id)
        )

        conn.commit()

        await query.edit_message_text(
            "╔═══━━━─── • ───━━━═══╗\n"
            "✅ REPORT APPROVED ✅\n"
            "╚═══━━━─── • ───━━━═══╝\n\n"
            f"👤 User » {username}\n"
            f"🆔 ID » {user_id}\n"
            f"📝 Reason » {reason}\n\n"
            "📌 Added to scam database."
        )

        try:
            await context.bot.send_message(
                chat_id=reporter_id,
                text=(
                    "✅ သင့် report ကို Owner က Approved လုပ်ပြီးပါပြီ။\n\n"
                    f"👤 User » {username}\n"
                    f"📝 Reason » {reason}"
                )
            )
        except:
            pass

    elif action == "report_reject":

        cursor.execute(
            "UPDATE reports SET status=? WHERE report_id=?",
            ("rejected", report_id)
        )

        conn.commit()

        await query.edit_message_text(
            "╔═══━━━─── • ───━━━═══╗\n"
            "❌ REPORT REJECTED ❌\n"
            "╚═══━━━─── • ───━━━═══╝\n\n"
            f"👤 User » {username}\n"
            f"📝 Reason » {reason}"
        )

        try:
            await context.bot.send_message(
                chat_id=reporter_id,
                text=(
                    "❌ သင့် report ကို Owner က Reject လုပ်ထားပါတယ်။\n\n"
                    f"👤 User » {username}"
                )
            )
        except:
            pass

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "သုံးနည်း:\n/add @username reason"
        )
        return

    username = context.args[0].strip()
    reason = " ".join(context.args[1:])
    reporter = (
        update.effective_user.username
        or
        str(update.effective_user.id)
    )

    loading = await update.message.reply_text(
        "🔎 Adding scammer..."
    )

    try:

        await client.start()

        user = await client.get_entity(username)

        user_id = user.id

        current_username = (
            f"@{user.username}"
            if user.username
            else username
        )

        cursor.execute(
            """
            SELECT username, reason
            FROM scams
            WHERE user_id=?
            """,
            (user_id,)
        )

        old = cursor.fetchone()

        if old:

            await loading.edit_text(
                f"⚠️ Already Added\n\n"
                f"👤 Saved Username » {old[0]}\n"
                f"🆔 ID » {user_id}\n"
                f"📝 Old Reason » {old[1]}\n\n"
                f"❌ This account already exists."
            )

            return

        cursor.execute(
            """
            INSERT INTO scams
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                current_username,
                reason,
                reporter
            )
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO tracked_users
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                current_username,
                current_username
            )
        )

        conn.commit()

        await loading.edit_text(
            f"🚨 Scam Added\n\n"
            f"👤 Username » {current_username}\n"
            f"🆔 ID » `{user_id}`\n"
            f"📝 Reason » {reason}"
        )

    except Exception as e:

        await loading.edit_text(
            f"❌ Add Failed\n\n{e}"
        )

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:

        await update.message.reply_text(
            "❌ Owner only"
        )

        return

    if not context.args:

        await update.message.reply_text(
            "သုံးနည်း:\n/remove user_id"
        )

        return

    user_id = context.args[0].strip()

    cursor.execute(
        "DELETE FROM scams WHERE user_id=?",
        (user_id,)
    )

    conn.commit()

    if cursor.rowcount == 0:

        await update.message.reply_text(
            "❌ Database ထဲမှာမရှိပါ"
        )

        return

    await update.message.reply_text(
        "✅ Scam Removed\n\n"
        f"🆔 ID » {user_id}"
    )


async def chadd(update: Update, context: ContextTypes.DEFAULT_TYPE):


    # Admin only
    if update.effective_user.id != OWNER_ID:

        await update.message.reply_text(
            "❌ Owner only"
        )

        return
    # Usage
    if not context.args:
        await update.message.reply_text(
            "သုံးနည်း:\n/chadd @channelusername"
        )
        return

    channel = context.args[0].strip()

    # Save channel
    cursor.execute(
        "INSERT OR IGNORE INTO channels VALUES (?)",
        (channel,)
    )

    conn.commit()

    await update.message.reply_text(
        f"✅ {channel} ကို Channel List ထဲထည့်ပြီးပါပြီ။"
    )

async def chlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:

        await update.message.reply_text(
            "❌ Owner only"
        )

        return

    cursor.execute(
        "SELECT username FROM channels"
    )

    channels = cursor.fetchall()

    if not channels:

        await update.message.reply_text(
            "❌ Channel list မရှိသေး"
        )

        return

    text = (
        "╔═══━━━─── • ───━━━═══╗\n"
        "📢 SAVED CHANNEL LIST 📢\n"
        "╚═══━━━─── • ───━━━═══╝\n\n"
    )

    for i, ch in enumerate(channels, start=1):

        text += (
            f"{i}. {ch[0]}\n"
        )

    text += (
        "\n━━━━━━━━━━━━━━━\n"
        f"📊 Total Channels » {len(channels)}"
    )

    await update.message.reply_text(text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("SELECT COUNT(*) FROM scams")
    scam_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM channels")
    channel_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    text = (
        "📊 Bot Stats\n\n"
        f"👥 Total Users: {user_count}\n"
        f"⚠️ Scam Reports: {scam_count}\n"
        f"📢 Saved Channels: {channel_count}\n\n"
        "✅ Bot Status: Online"
    )

    await update.message.reply_text(text)

HELP_TEXT = """
╔═══━━━─── • ───━━━═══╗
🤖 𝗦𝗖𝗔𝗠 𝗦𝗘𝗔𝗥𝗖𝗛 𝗕𝗢𝗧
╚═══━━━─── • ───━━━═══╝

╭━━━〔 🚀 START 〕━━━╮
/start
➥ Bot ကိုစတင်ရန်
╰━━━━━━━━━━━━━━╯

╭━━━〔 📖 HELP 〕━━━╮
/help
➥ Command guide ကြည့်ရန်
╰━━━━━━━━━━━━━━╯

╭━━━〔 🆔 USER ID 〕━━━╮
/id
➥ Telegram ID ကြည့်ရန်
╰━━━━━━━━━━━━━━╯

╭━━━〔 🔎 SEARCH 〕━━━╮
/search @username
➥ Username စစ်ဆေးရန်
➥ ID-based detection
➥ Username changed detect
╰━━━━━━━━━━━━━━╯

╭━━━〔 🚨 REPORT 〕━━━╮
/report @username reason
➥ Scam report တင်ရန်
╰━━━━━━━━━━━━━━╯

╭━━━〔 📜 SCAM LIST 〕━━━╮
/scamlist
➥ Scammer list ကြည့်ရန်
╰━━━━━━━━━━━━━━╯

╭━━━〔 👑 ADMINS 〕━━━╮
/admins
➥ Admin list ကြည့်ရန်
╰━━━━━━━━━━━━━━╯

╭━━━〔 📊 STATS 〕━━━╮
/stats
➥ Bot statistics ကြည့်ရန်
╰━━━━━━━━━━━━━━╯

╭━━━〔 🛡 FEATURES 〕━━━╮
✅ Permanent Scam Database
✅ Username Change Detection
✅ Channel Search
✅ Group Search
✅ ID Tracking System
✅ Fast Scam Alerts
╰━━━━━━━━━━━━━━╯

⚡ Powered By RANDO
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        HELP_TEXT
    )

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:

        await update.message.reply_text(
            "❌ Owner only"
        )

        return

    if not context.args:

        await update.message.reply_text(
            "သုံးနည်း:\n/addadmin user_id"
        )

        return

    admin_id = context.args[0]

    cursor.execute(
        "INSERT OR IGNORE INTO admins VALUES (?)",
        (admin_id,)
    )

    conn.commit()

    await update.message.reply_text(
        f"✅ Admin Added\n\n"
        f"🆔 ID » {admin_id}"
    )

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    text = (
        f"🆔 Your Telegram Info\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🔗 Username: @{user.username}\n"
        f"🆔 ID: {user.id}"
    )

    await update.message.reply_text(text)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Owner only")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "သုံးနည်း:\n"
            "ပို့ချင်တဲ့ message/photo ကို bot ဆီပို့ → reply ပြန်ပြီး /broadcast ရိုက်"
        )
        return

    cursor.execute("SELECT user_id FROM users")
    chats = cursor.fetchall()

    success_count = 0
    fail_count = 0

    status_msg = await update.message.reply_text(
        f"🚀 Broadcasting to {len(chats)} users..."
    )

    source = update.message.reply_to_message

    for chat in chats:
        chat_id = chat[0]

        try:
            await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=source.chat_id,
                message_id=source.message_id
            )

            success_count += 1
            await asyncio.sleep(0.05)

        except Exception as e:
            print("BROADCAST ERROR:", chat_id, e)
            fail_count += 1

    await status_msg.edit_text(
        f"✅ Broadcast ပြီးဆုံးပါပြီ။\n\n"
        f"အောင်မြင်: {success_count}\n"
        f"မအောင်မြင်: {fail_count}"
    )

async def auto_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    text = update.message.text.lower()

    cursor.execute("SELECT * FROM scams")
    rows = cursor.fetchall()

    for row in rows:

        username = str(row[0]).lower().replace("@", "")

        if username in text.replace("@", ""):

            await update.message.reply_text(
                f"⚠️ SCAM ALERT\n\n"
                f"👤 Username: {row[0]}\n"
                f"📝 Reason: {row[1]}\n"
                f"👮 Reporter: {row[2]}"
            )

            break

# ===== START BOT =====
app = ApplicationBuilder().token(BOT_TOKEN).build()

# handlers
app.add_handler(CommandHandler("scam", scam))

app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("remove", remove))
app.add_handler(CommandHandler("chadd", chadd))
app.add_handler(CommandHandler("chlist", chlist))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(
    CommandHandler("addadmin", addadmin)
)
app.add_handler(CommandHandler("id", getid))
app.add_handler(
    CommandHandler("broadcast", broadcast)
)
app.add_handler(
    CommandHandler("backup", backup)
)
app.add_handler(
    CommandHandler("admins", admins)
)

app.add_handler(
    CommandHandler("removeadmin", removeadmin)
)
app.add_handler(
    CommandHandler("scamlist", scamlist)
)
app.add_handler(
    CommandHandler("groupscan", groupscan)
)
app.add_handler(
    CommandHandler("userinfo", userinfo)
)
app.add_handler(CommandHandler("report", report))
app.add_handler(
    CallbackQueryHandler(report_callback, pattern="^report_")
)


print("Bot Running...")

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        auto_scan
    )
)

app.run_polling()
