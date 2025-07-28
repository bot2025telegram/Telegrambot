import telebot
from flask import Flask, request

API_TOKEN = '8476968349:AAEq-_TOTqa2nZUhy06cRArRMf7P9Nhb_IA'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# إعدادات البوت
CHANNEL_USERNAME = "@hackeralgeria17"
GROUP_LOG_ID = -1002875578542
user_data = {}

# التحقق من الانضمام للقناة
def is_user_joined_channel(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# /start مع ربط الإحالة
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    ref_id = message.text.split()[1] if len(message.text.split()) > 1 else None

    if user_id not in user_data:
        user_data[user_id] = {'joined': False, 'referred': False, 'ref_by': None}

    if ref_id and str(user_id) != ref_id:
        user_data[user_id]['ref_by'] = ref_id
        user_data[int(ref_id)] = user_data.get(int(ref_id), {'joined': False, 'referred': False, 'ref_by': None})
        user_data[int(ref_id)]['referred'] = True

    bot.send_message(user_id, "👋 مرحبًا بك! استخدم الأزرار للبدء.")

# زر "تحقق من المهام 🔁"
@bot.message_handler(func=lambda m: m.text == "تحقق من المهام 🔁")
def check_tasks(message):
    user_id = message.from_user.id
    joined = is_user_joined_channel(user_id)
    referred = user_data.get(user_id, {}).get("ref_by") is not None

    if joined:
        user_data[user_id]['joined'] = True

    if joined and referred:
        bot.send_message(user_id, "✅ لقد أكملت المهام! يمكنك الآن استخدام الخدمات المجانية.")
    else:
        bot.send_message(user_id, "❌ لم تكمل المهام بعد.\n\n🔸 الانضمام إلى القناة: @hackeralgeria17\n🔸 نسخ رابط البوت ومشاركته مع شخص واحد فقط.")

# تحويل الرسائل التي تحتوي على "رابط" أو "خدمة"
@bot.message_handler(func=lambda m: any(word in m.text.lower() for word in ["رابط", "خدمة"]))
def forward_message(message):
    bot.forward_message(GROUP_LOG_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "📨 تم إرسال طلبك إلى الدعم للمراجعة. شكراً لك!")

# Webhook من Telegram → إلى السيرفر
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# تعيين Webhook
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://your-render-url.onrender.com")  # ← غيّر هذا الرابط لرابط Render الخاص بك
    return "Webhook set!", 200

if __name__ == "__main__":
    app.run(debug=True)
