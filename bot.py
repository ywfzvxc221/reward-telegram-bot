import telebot
from telebot import types
from config import BOT_TOKEN, ADMIN_ID, PROOF_CHANNEL, FORCE_SUB_CHANNEL

bot = telebot.TeleBot(BOT_TOKEN)

# إعدادات قابلة للتعديل من لوحة التحكم
settings = {
    "daily_bonus": 100,  # مكافأة يومية
    "referral_bonus": 150,  # مكافأة الإحالة
    "tasks": []  # قائمة المهام
}

# تحقق من الاشتراك الإجباري
def check_subscription(user_id):
    try:
        status = bot.get_chat_member(FORCE_SUB_CHANNEL, user_id).status
        return status in ["member", "creator", "administrator"]
    except:
        return False

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك الآن", url=f"https://t.me/{FORCE_SUB_CHANNEL[1:]}"))
        bot.send_message(message.chat.id, "الرجاء الاشتراك في القناة أولاً للاستمرار.", reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("حسابي", "المكافأة اليومية")
    markup.row("سحب", "تنفيذ المهام")
    markup.row("نشر إعلان", "الدعم الفني")
    markup.row("شروط الاستخدام", "لوحة التحكم")

    bot.send_message(message.chat.id, f"مرحباً {first_name}! اختر من القائمة:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def main_menu(message):
    user_id = message.from_user.id
    text = message.text

    if text == "حسابي":
        bot.send_message(user_id, "رصيدك الحالي: 0 BTC")
    elif text == "المكافأة اليومية":
        bot.send_message(user_id, f"تم إضافة {settings['daily_bonus']} ساتوشي إلى حسابك!")
    elif text == "سحب":
        bot.send_message(user_id, "للسحب، أرسل عنوان محفظتك على FaucetPay أو Binance.")
    elif text == "تنفيذ المهام":
        if not settings["tasks"]:
            bot.send_message(user_id, "لا توجد مهام حالياً.")
        else:
            for task in settings["tasks"]:
                bot.send_message(user_id, f"مهمة: {task['desc']} — المكافأة: {task['reward']} ساتوشي")
    elif text == "نشر إعلان":
        bot.send_message(user_id, f"لنشر إعلانك راسل الإدارة: @{ADMIN_ID}")
    elif text == "الدعم الفني":
        bot.send_message(user_id, "للدعم الفني، تواصل معنا عبر: @support")
    elif text == "شروط الاستخدام":
        bot.send_message(user_id, "باستخدامك للبوت فإنك توافق على جميع الشروط والأحكام.")
    elif text == "لوحة التحكم" and user_id == ADMIN_ID:
        admin_panel(user_id)
    else:
        bot.send_message(user_id, "يرجى اختيار خيار من القائمة.")

def admin_panel(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("تغيير مكافأة الدخول", "تغيير مكافأة الإحالة")
    markup.row("إضافة مهمة", "عرض المهام", "حذف المهام")
    markup.add("رجوع")
    bot.send_message(user_id, "أهلاً بك في لوحة التحكم.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "تغيير مكافأة الدخول" and m.from_user.id == ADMIN_ID)
def set_daily_bonus(message):
    msg = bot.send_message(message.chat.id, "أدخل قيمة المكافأة اليومية:")
    bot.register_next_step_handler(msg, save_daily_bonus)

def save_daily_bonus(message):
    try:
        value = int(message.text)
        settings["daily_bonus"] = value
        bot.send_message(message.chat.id, f"تم تحديث المكافأة اليومية إلى {value} ساتوشي.")
    except:
        bot.send_message(message.chat.id, "قيمة غير صالحة.")

@bot.message_handler(func=lambda m: m.text == "تغيير مكافأة الإحالة" and m.from_user.id == ADMIN_ID)
def set_ref_bonus(message):
    msg = bot.send_message(message.chat.id, "أدخل قيمة مكافأة الإحالة:")
    bot.register_next_step_handler(msg, save_ref_bonus)

def save_ref_bonus(message):
    try:
        value = int(message.text)
        settings["referral_bonus"] = value
        bot.send_message(message.chat.id, f"تم تحديث مكافأة الإحالة إلى {value} ساتوشي.")
    except:
        bot.send_message(message.chat.id, "قيمة غير صالحة.")

@bot.message_handler(func=lambda m: m.text == "إضافة مهمة" and m.from_user.id == ADMIN_ID)
def add_task(message):
    msg = bot.send_message(message.chat.id, "أرسل وصف المهمة والمكافأة (مثال: اشترك بقناة @channel = 100):")
    bot.register_next_step_handler(msg, save_task)

def save_task(message):
    try:
        parts = message.text.split("=")
        desc = parts[0].strip()
        reward = int(parts[1].strip())
        settings["tasks"].append({"desc": desc, "reward": reward})
        bot.send_message(message.chat.id, "تمت إضافة المهمة.")
    except:
        bot.send_message(message.chat.id, "صيغة غير صحيحة.")

@bot.message_handler(func=lambda m: m.text == "عرض المهام" and m.from_user.id == ADMIN_ID)
def list_tasks(message):
    if not settings["tasks"]:
        bot.send_message(message.chat.id, "لا توجد مهام.")
    else:
        for i, task in enumerate(settings["tasks"], 1):
            bot.send_message(message.chat.id, f"{i}. {task['desc']} — {task['reward']} ساتوشي")

@bot.message_handler(func=lambda m: m.text == "حذف المهام" and m.from_user.id == ADMIN_ID)
def clear_tasks(message):
    settings["tasks"] = []
    bot.send_message(message.chat.id, "تم حذف جميع المهام.")

bot.polling()
