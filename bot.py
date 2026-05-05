```python
from flask import Flask, request
import telebot
from telebot import types
import requests
import urllib.parse
import random
import os

TOKEN = "8661126406:AAHII3H0A1LKJsMKC1XvmACRtVqssVerqM0"
OPENROUTER_API_KEY = "sk-or-v1-961d023f850bf5648306d2b99f470296a7902affce2d35d8d155ae7b330bd3c"
WEATHER_API_KEY = "5de971bb2c6b4bb2a5c140851260505"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

count = 0
ai_users = set()

# ---------- КНОПКИ ----------

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("📖 Инструкция")
    btn2 = types.KeyboardButton("ℹ️ Дисклеймер")
    btn3 = types.KeyboardButton("🌦 Погода")
    btn4 = types.KeyboardButton("🤖 Режим ИИ")
    btn5 = types.KeyboardButton("😂 Анекдот")

    markup.add(btn1, btn2)
    markup.add(btn3)
    markup.add(btn4, btn5)

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

# ---------- ПОГОДА ----------

@bot.message_handler(func=lambda m: m.text == "🌦 Погода")
def weather(message):

    msg = bot.send_message(
        message.chat.id,
        "Напиши город:"
    )

    bot.register_next_step_handler(msg, send_weather)

def send_weather(message):

    city = urllib.parse.quote(message.text.strip())

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    )

    try:
        data = requests.get(url).json()

        if str(data.get("cod")) != "200":
            bot.send_message(
                message.chat.id,
                "❌ Город не найден"
            )
            return

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        name = data["name"]

        bot.send_message(
            message.chat.id,
            f"🌦 Погода в {name}\n\n"
            f"🌡 Температура: {temp}°C\n"
            f"☁️ {desc}"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

# ---------- АНЕКДОТЫ ----------

jokes = [

    "— Почему программист не вышел из дома?\n— Потому что был offline.",

    "— Сколько программистов нужно чтобы вкрутить лампочку?\n— Ни одного, это проблема железа.",

    "— Я удалил System32.\n— поздравляю с новым кирпичом.",

    "— Почему Windows думает?\n— обновляется.",

    "— Что делает школьник ночью?\n— ищет ответы в ChatGPT 💀",

    "— Доктор, я буду жить?\n— А смысл?",

    "— Ты сова или жаворонок?\n— Я вообще не это… я устал.",

    "— Почему ты опоздал?\n— Поздно вышел из дома.\n— А раньше выйти?\n— Уже поздно было.",

    "— Мам, можно я не пойду в школу?\n— Нет.\n— Почему?\n— Ты директор.",

    "— Как дела?\n— Как у картошки.\n— Это как?\n— Если зимой не сожрут — весной посадят.",

    "— Ты чего такой грустный?\n— Цены видел?",

    "— Что делаешь?\n— Ничего.\n— А вчера?\n— Не успел закончить.",

    "— У тебя есть хобби?\n— Да, откладывать дела на потом.",

    "— Почему кот смотрит в стену?\n— Он видит твои долги."
]

@bot.message_handler(func=lambda m: m.text == "😂 Анекдот")
def joke(message):

    bot.send_message(
        message.chat.id,
        random.choice(jokes)
    )

# ---------- AI РЕЖИМ ----------

@bot.message_handler(func=lambda m: m.text == "🤖 Режим ИИ")
def toggle_ai(message):

    user_id = message.from_user.id

    if user_id in ai_users:
        ai_users.remove(user_id)

        bot.send_message(
            message.chat.id,
            "❌ AI режим выключен"
        )

    else:
        ai_users.add(user_id)

        bot.send_message(
            message.chat.id,
            "✅ AI режим включен"
        )

# ---------- ОБЫЧНЫЕ СООБЩЕНИЯ ----------

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

    # ---------- AI ----------
    if user_id in ai_users:

        try:

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты рофляный Telegram бот. "
                            "Отвечай коротко, смешно и по-человечески."
                        )
                    },
                    {
                        "role": "user",
                        "content": message.text
                    }
                ]
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )

            result = response.json()

            if "choices" not in result:
                bot.reply_to(message, f"AI ошибка: {result}")
                return

            answer = result["choices"][0]["message"]["content"]

            bot.reply_to(message, answer)

        except Exception as e:
            bot.reply_to(message, f"AI ошибка: {e}")

    # ---------- ОБЫЧНЫЙ РЕЖИМ ----------
    else:

        count += 1

        if count % 3 == 0:
            bot.reply_to(message, "нуу хз, сам решай")
        else:
            bot.reply_to(message, "хз сам решай")

# ---------- WEBHOOK ----------

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():

    update = telebot.types.Update.de_json(
        request.get_data().decode("utf-8")
    )

    bot.process_new_updates([update])

    return "ok", 200

# ---------- ГЛАВНАЯ ----------

@app.route("/")
def index():
    return "Bot is running"

# ---------- ЗАПУСК ----------

if __name__ == "__main__":

    bot.remove_webhook()

    bot.set_webhook(
        url=f"https://tg-bot-c38c.onrender.com/{TOKEN}"
    )

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
```
