from telebot import TeleBot

from environs import Env

import re

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

env = Env()
env.read_env()


#--------------Constants------------------
BOT_TOKEN = env.str('BOT_TOKEN')

bot = TeleBot(BOT_TOKEN)
SUPER_ADMIN_ID = env.str('ADMIN_ID')

whitelist = []
LINK_REG = re.compile(r"(?i)(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)")

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
            bot.delete_message(message.chat.id, message.message_id)
            bot.reply_to(message, f"⚠️ {message.from_user.first_name}، ارسال لینک در گروه ممنوع است!")
    except Exception as e:
        print(f'Errors:{e}')