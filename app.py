PANEL = """
<h2>Собранные email</h2>
<table border=1 cellpadding=6>
<tr><th>ID</th><th>Telegram</th><th>Email</th><th>Время</th></tr>
{% for v in rows %}
<tr><td>{{v[0]}}</td><td>{{v[1]}}</td><td>{{v[2]}}</td><td>{{v[3]}}</td></tr>
{% endfor %}
</table>
<p>Всего: {{rows|length}}</p>
"""
