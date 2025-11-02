from telebot import TeleBot, types

from environs import Env

import re

import json
import os
import query

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

env = Env()
env.read_env()


#--------------Constants------------------
BOT_TOKEN = env.str('BOT_TOKEN')
MAX_WARN = 3

bot = TeleBot(BOT_TOKEN)
SUPER_ADMIN_ID = env.str('ADMIN_ID')
LINK_REG = re.compile(r"(?i)(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)")

# ------------------------------------- Admin panel ---------------------------------
def is_super_admin(user_id):
    return user_id == int(SUPER_ADMIN_ID)


def show_admin_panel(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🟢 مدیریت لیست سفید", callback_data="whitelist_menu"),
        InlineKeyboardButton("⚙️ تنظیمات بات", callback_data="settings_menu"),
        InlineKeyboardButton("📊 وضعیت ربات", callback_data="status")
    )
    bot.send_message(message.chat.id, "🎛️ *پنل مدیریت ادمین*", reply_markup=markup, parse_mode='Markdown')



# ------------------------------------- White list and Bot settings in panel ---------------------------------
def show_whitelist_menu(call):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("➕ اضافه کردن کاربر", callback_data="add_whitelist"),
        InlineKeyboardButton("➖ حذف کاربر", callback_data="remove_whitelist"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
    )
    bot.edit_message_text("📝 مدیریت لیست سفید", call.message.chat.id, call.message.message_id,
                        reply_markup=markup)


def show_settings_menu(call):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🗑 حذف پیام‌ها", callback_data="mode_delete"),
        InlineKeyboardButton("⚠️ هشدار", callback_data="mode_warn"),
        InlineKeyboardButton("⛔ بن", callback_data="mode_ban"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
    )
    bot.edit_message_text("⚙️ تنظیمات ربات", call.message.chat.id, call.message.message_id,
                        reply_markup=markup)


# ------------------------------------- Callback handle ---------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global link_mode
    if not is_super_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ شما اجازه دسترسی به این بخش را ندارید!")
        return
    
    if call.data == "admin_panel":
        show_admin_panel(call.message)
    elif call.data == "whitelist_menu":
        show_whitelist_menu(call)
    elif call.data == "settings_menu":
        show_settings_menu(call)
    elif call.data == "status":
        link_mode = query.get_current_link_mode()  # Get current link mode from the database
        number_of_whitelisted = query.get_number_of_all_whitelists_user()  # Get number of whitelisted users from the database
        number_of_warned = query.get_number_of_warned_users()  # Get number of warned users from the database
        status_text = (
            f"📊 وضعیت ربات:\n"
            f"• حالت برخورد با لینک: {link_mode}\n"
            f"• تعداد کاربران لیست سفید: {number_of_whitelisted}\n"
            f"• کاربران با هشدار: {number_of_warned}\n"
        )
        bot.send_message(call.message.chat.id, status_text)
    elif call.data.startswith("mode_"):
        link_mode = call.data.split("_")[1]
        query.update_link_mode(link_mode)  # Update link mode in the database
        bot.answer_callback_query(call.id, f"✅ حالت لینک‌ها به '{link_mode}' تغییر کرد!")
        show_settings_menu(call)
    elif call.data == "add_whitelist":
        msg = bot.send_message(call.message.chat.id, "➕ لطفاً *user_id* کاربر را برای اضافه کردن وارد کنید:", parse_mode='Markdown', reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, add_whitelist)
    elif call.data == "remove_whitelist":
        msg = bot.send_message(call.message.chat.id, "➖ لطفاً *user_id* کاربر را برای حذف وارد کنید:", parse_mode='Markdown', reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, remove_whitelist)


def add_whitelist(message):
    try:
        user_id = int(message.text.strip())
        result = query.get_user_id(user_id)  # Ensure user exists in the database
        white = query.get_whitelist(user_id)  # Get whitelist status from the database
        if result and white == 'False':
            query.update_white_by_user_id(user_id)  # Update whitelist status in the database
            bot.reply_to(message, f"✅ کاربر {user_id} در لیست سفید به‌روزرسانی شد.")
        else:
            query.insert_user(user_id, white='True')  # Insert user if not exists
            bot.reply_to(message, f"✅ کاربر {user_id} به لیست سفید اضافه شد.")
    except:
        bot.reply_to(message, "❌ مقدار وارد شده معتبر نیست. لطفاً فقط user_id عددی ارسال کنید.")

def remove_whitelist(message):
    try:
        user_id = int(message.text.strip())
        result = query.get_user_id(user_id)  # Ensure user exists in the database
        white = query.get_whitelist(user_id)  # Get whitelist status from the database 
        if result and white == 'True':
            query.remove_user_from_whitlist(user_id)  # Remove user from whitelist in the database
            bot.reply_to(message, f"✅ کاربر {user_id} از لیست سفید حذف شد.")
        else:
            bot.reply_to(message, "❌ کاربر در لیست سفید نیست یا وجود ندارد.")
    except:
        bot.reply_to(message, "❌ مقدار وارد شده معتبر نیست. لطفاً فقط user_id عددی ارسال کنید.")

# ------------------------------------- Start and Help handle ---------------------------------
@bot.message_handler(commands=['start'])
def start_handle(message):
    user_id = message.from_user.id
    # Register user in the database
    query.insert_user(user_id)
    if is_super_admin(user_id):
        show_admin_panel(message)
    else:
        welcome_text = (
            "🌟 *سلام و خوش آمدید!*\n\n"
            "من ربات ضد لینک شما هستم 🤖\n"
            "هدفم: محافظت از گروه‌ها و کانال شما در برابر لینک‌های ناخواسته 🔒\n\n"
            "✨ *ویژگی‌های من:*"
            "\n• شناسایی و حذف خودکار لینک‌ها"
            "\n• هشدار به کاربران خاطی"
            "\n• مدیریت لیست سفید کاربران و دامنه‌ها"
            "\n• مناسب برای گروه‌ها و کانال‌های شما\n\n"
            "📌 برای دیدن دستورها و راهنمای استفاده، /help را ارسال کنید.\n"
            "با من گروهت امن و مرتب خواهد بود! 🚀"
        )
        bot.reply_to(message, welcome_text, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def help_handle(message):
    help_text = (
        "📖 *راهنمای کامل ربات ضد لینک*\n\n"
        "✅ *وظیفه من:* حذف خودکار لینک‌ها و مدیریت کاربران خاطی\n\n"
        "💡 *دستورات اصلی:*\n"
        "• /start - شروع ربات و خوش‌آمدگویی\n"
        "• /help - نمایش این راهنما\n"
        "• اضافه کردن کاربر به لیست سفید\n"
        "• حذف کاربر از لیست سفید\n"
        "• تنظیم نحوه برخورد با لینک‌ها\n"
        "• مشاهده وضعیت فعلی ربات\n\n"
        "⚡ نکته: تنها ادمین‌ها می‌توانند دستورات مدیریتی را اجرا کنند.\n\n"
        "با استفاده از من، گروه و کانال شما همیشه امن و مرتب باقی می‌ماند! 🛡️"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')


# ------------------------------------- Checking text ---------------------------------
@bot.message_handler(func= lambda message:True)
def check_link(message):
    admin_user_id = SUPER_ADMIN_ID
    white = query.get_whitelist(message.from_user.id)
    link_mode = query.get_current_link_mode()
    if message.chat.type not in ["group", "supergroup"]:
        return
    try:
        if message.from_user.id == admin_user_id or white == 'True':
            return
        if message.text and LINK_REG.search(message.text):
            if link_mode == "delete":
                bot.delete_message(message.chat.id, message.message_id)
            elif link_mode == "warn":
                query.update_warns_by_user_id(message.from_user.id)
                warns_count = query.get_warns_by_user_id(message.from_user.id)
                bot.reply_to(message, f"⚠️ {message.from_user.first_name}، ارسال لینک ممنوع است! ({warns_count} هشدار)")
                if warns_count >= MAX_WARN:
                    bot.kick_chat_member(message.chat.id, message.from_user.id)
                    bot.send_message(message.chat.id, f"⛔ {message.from_user.first_name} به دلیل دریافت {MAX_WARN} هشدار، از گروه اخراج شد!")
            elif link_mode == "ban":
                bot.kick_chat_member(message.chat.id, message.from_user.id)
    except Exception as e:
        print(f"Error: {e}")


print("ربات در حال اجراست...")
bot.infinity_polling()