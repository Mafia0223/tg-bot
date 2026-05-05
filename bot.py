from flask import Flask, request
import telebot
from telebot import types
import requests

TOKEN = "8661126406:AAHII3H0A1LKJsMKC1XvmACRtVqssVerqM0"
OPENROUTER_API_KEY = "sk-or-v1-961d023f850bf5648306d2b99f470296a7902affce2d35d8d155ae7b330bd3c"
WEATHER_API_KEY = "5de971bb2c6b4bb2a5c140851260505"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

count = 0
ai_users = set()


def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("📖 Инструкция")
    btn2 = types.KeyboardButton("ℹ️ Дисклеймер")
    btn3 = types.KeyboardButton("🌦 Погода")
    btn4 = types.KeyboardButton("🤖 Режим ИИ")
    btn5 = types.KeyboardButton(" Анекдот")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4, btn5)

    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Бот запущен.",
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "📖 Инструкция")
def instruction(message):
    bot.reply_to(message, "я хз")


@bot.message_handler(func=lambda m: m.text == "ℹ️ Дисклеймер")
def disclaimer(message):
    bot.reply_to(
        message,
        "Этот бот отвечает в шуточной форме и создан для развлечения. "
        "Его сообщения не отражают реальность и не должны восприниматься всерьёз. "
        "Всё, что он пишет — это юмор, а не факты."
    )


@bot.message_handler(func=lambda m: m.text == "🌦 Погода")
def weather(message):
    msg = bot.send_message(message.chat.id, "Напиши город:")
    bot.register_next_step_handler(msg, send_weather)

def send_weather(message):
    city = message.text

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    try:
        data = requests.get(url).json()

        if data.get("cod") != 200:
            bot.send_message(message.chat.id, "❌ Город не найден")
            return

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]

        bot.send_message(
            message.chat.id,
            f"🌦 Погода в {city}\n\n🌡 {temp}°C\n☁️ {desc}"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


@bot.message_handler(func=lambda m: m.text == " Анекдот")
def joke(message):
    try:
        url = (
            "https://v2.jokeapi.dev/joke/Any"
            "?type=twopart"
        )

        r = requests.get(url).json()

        if r.get("error"):
            bot.send_message(message.chat.id, "❌ не получилось получить анекдот")
            return

        setup = r.get("setup")
        punchline = r.get("delivery")

        bot.send_message(
            message.chat.id,
            f" {setup}\n\n{punchline}"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == "🤖 Режим ИИ")
def toggle_ai(message):
    user_id = message.from_user.id

    if user_id in ai_users:
        ai_users.remove(user_id)
        bot.send_message(message.chat.id, "❌ AI выключен")
    else:
        ai_users.add(user_id)
        bot.send_message(message.chat.id, "✅ AI включен")


@bot.message_handler(func=lambda m: True)
def reply(message):

    global count

    if message.text in [
        "📖 Инструкция",
        "ℹ️ Дисклеймер",
        "🌦 Погода",
        "🤖 Режим ИИ",
        "😂 Анекдот"
    ]:
        return

    user_id = message.from_user.id

    if user_id in ai_users:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты рофляный Telegram бот. Отвечай коротко и смешно."
                    },
                    {
                        "role": "user",
                        "content": message.text
                    }
                ]
            }

            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )

            result = res.json()

            answer = result["choices"][0]["message"]["content"]
            bot.reply_to(message, answer)

        except Exception as e:
            bot.reply_to(message, f"AI ошибка: {e}")

    else:
        count += 1
        bot.reply_to(message, "нуу хз, сам решай" if count % 3 else "хз сам решай")


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def index():
    return "Bot is running"


if __name__ == "__main__":
    bot.remove_webhook()

    bot.set_webhook(
        url=f"https://tg-bot-c38c.onrender.com/{TOKEN}"
    )

    app.run(host="0.0.0.0", port=5000)