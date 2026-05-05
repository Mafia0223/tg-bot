from flask import Flask, request
import telebot
from telebot import types

TOKEN = "8661126406:AAHII3H0A1LKJsMKC1XvmACRtVqssVerqM0"

URL = "https://tg-bot-c38c.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

count = 0

# ---------- КНОПКИ ----------

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("📖 Инструкция")
    btn2 = types.KeyboardButton("ℹ️ Дисклеймер")

    markup.add(btn1)
    markup.add(btn2)

    return markup

# ---------- START ----------

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Бот запущен.",
        reply_markup=main_keyboard()
    )

# ---------- ИНСТРУКЦИЯ ----------

@bot.message_handler(func=lambda m: m.text == "📖 Инструкция")
def instruction(message):
    bot.reply_to(message, "я хз")

# ---------- ДИСКЛЕЙМЕР ----------

@bot.message_handler(func=lambda m: m.text == "ℹ️ Дисклеймер")
def disclaimer(message):
    bot.reply_to(
        message,
        "Этот бот отвечает в шуточной форме и создан для развлечения. "
        "Его сообщения не отражают реальность и не должны восприниматься всерьёз. "
        "Всё, что он пишет — это юмор, а не факты."
    )

# ---------- ОБЫЧНЫЕ СООБЩЕНИЯ ----------

@bot.message_handler(func=lambda m: True)
def reply(message):
    global count

    if message.text in ["📖 Инструкция", "ℹ️ Дисклеймер"]:
        return

    count += 1

    if count % 3 == 0:
        bot.reply_to(message, "нуу хз, сам решай")
    else:
        bot.reply_to(message, "хз сам решай")

    try:
        bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[{"type": "emoji", "emoji": "👍"}]
        )
    except:
        pass

# ---------- WEBHOOK ----------

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

# ---------- ЗАПУСК ----------

if __name__ == "__main__":

    bot.remove_webhook()

    bot.set_webhook(
        url=f"{URL}/{TOKEN}"
    )

    app.run(host="0.0.0.0", port=5000)