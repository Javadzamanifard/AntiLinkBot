from telebot import TeleBot

from environs import Env

import re

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

env = Env()
env.read_env()


#--------------Constants------------------
BOT_TOKEN = env.str('BOT_TOKEN')
link_mode = 'delete'
warns = {}

bot = TeleBot(BOT_TOKEN)
SUPER_ADMIN_ID = env.str('ADMIN_ID')

whitelist = []
LINK_REG = re.compile(r"(?i)(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)")


# ------------------------------------- Admin panel ---------------------------------
def is_super_admin(user_id):
    return user_id == SUPER_ADMIN_ID


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
        status_text = (
            f"📊 وضعیت ربات:\n"
            f"• حالت برخورد با لینک: {link_mode}\n"
            f"• تعداد کاربران لیست سفید: {len(whitelist)}\n"
            f"• کاربران با هشدار: {len(warns)}"
        )
        bot.send_message(call.message.chat.id, status_text)
    elif call.data.startswith("mode_"):
        global link_mode
        link_mode = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"✅ حالت لینک‌ها به '{link_mode}' تغییر کرد!")
        show_settings_menu(call)
    elif call.data == "add_whitelist":
        msg = bot.send_message(call.message.chat.id, "➕ لطفاً *user_id* کاربر را برای اضافه کردن وارد کنید:", parse_mode='Markdown', reply_markup=telebot.types.ForceReply())
        bot.register_next_step_handler(msg, add_whitelist)
    elif call.data == "remove_whitelist":
        msg = bot.send_message(call.message.chat.id, "➖ لطفاً *user_id* کاربر را برای حذف وارد کنید:", parse_mode='Markdown', reply_markup=telebot.types.ForceReply())
        bot.register_next_step_handler(msg, remove_whitelist)


def add_whitelist(message):
    try:
        user_id = int(message.text.strip())
        if user_id not in whitelist:
            whitelist.append(user_id)
            bot.reply_to(message, f"✅ کاربر {user_id} به لیست سفید اضافه شد.")
        else:
            bot.reply_to(message, "کاربر از قبل در لیست سفید است.")
    except:
        bot.reply_to(message, "❌ مقدار وارد شده معتبر نیست. لطفاً فقط user_id عددی ارسال کنید.")

def remove_whitelist(message):
    try:
        user_id = int(message.text.strip())
        if user_id in whitelist:
            whitelist.remove(user_id)
            bot.reply_to(message, f"✅ کاربر {user_id} از لیست سفید حذف شد.")
        else:
            bot.reply_to(message, "کاربر در لیست سفید نیست.")
    except:
        bot.reply_to(message, "❌ مقدار وارد شده معتبر نیست. لطفاً فقط user_id عددی ارسال کنید.")

# ------------------------------------- Start and Help handle ---------------------------------
@bot.message_handler(commands=['start'])
def start_handle(message):
    user_id = message.from_user.id
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
        "• /whitelist add <user> - اضافه کردن کاربر به لیست سفید\n"
        "• /whitelist remove <user> - حذف کاربر از لیست سفید\n"
        "• /setmode <delete|warn|ban> - تنظیم نحوه برخورد با لینک‌ها\n"
        "• /status - مشاهده وضعیت فعلی ربات\n\n"
        "⚡ نکته: تنها ادمین‌ها می‌توانند دستورات مدیریتی را اجرا کنند.\n\n"
        "با استفاده از من، گروه و کانال شما همیشه امن و مرتب باقی می‌ماند! 🛡️"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')


# ------------------------------------- Checking text ---------------------------------
@bot.message_handler(func= lambda message:True)
def check_link(message):
    admin_user_id = SUPER_ADMIN_ID
    try:
        if message.from_user.id == admin_user_id or message.from_user.id in whitelist:
            return
        if message.text and LINK_REG.search(message.text):
            if link_mode == "delete":
                bot.delete_message(message.chat.id, message.message_id)
            elif link_mode == "warn":
                warns[message.from_user.id] = warns.get(message.from_user.id, 0) + 1
                bot.reply_to(message, f"⚠️ {message.from_user.first_name}، ارسال لینک ممنوع است! ({warns[message.from_user.id]} هشدار)")
            elif link_mode == "ban":
                bot.kick_chat_member(message.chat.id, message.from_user.id)
    except Exception as e:
        print(f'Errors:{e}')