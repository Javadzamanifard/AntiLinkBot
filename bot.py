from telebot import TeleBot

from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')

bot = TeleBot(BOT_TOKEN)
ADMIN_ID = env.str('ADMIN_ID')


# ------------------------------------- Start and Help handle ---------------------------------
@bot.message_handler(commands=['start'])
def start_handle(message):
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