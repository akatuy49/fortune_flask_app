from flask import Flask, render_template, request, redirect, url_for, session
import openai
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # セッション用の秘密鍵

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 日本時間を取得する関数
def get_japan_time():
    return datetime.utcnow() + timedelta(hours=9)

lucky_items = ["🔮 水晶玉", "🌙 月のペンダント", "✨ 星型チャーム", "🧿 お守り", "📿 パワーストーン", "🌟 光る羽根", "💫 魔法の本"]

destiny_quotes = [
    "運命はあなたの味方です。",
    "今日の選択が未来を変えるでしょう。",
    "信じる心が幸運を引き寄せます。",
    "すべてはタイミング。焦らずゆっくり。",
    "目の前のチャンスを逃さないで。"
]

def get_fortune(name, birthdate, genre):
    today = get_japan_time().strftime("%Y年%m月%d日")
    prompt = f"""
あなたはプロの占い師です。
対象者は「{name}さん」、生年月日は「{birthdate}」です。
今日は{today}です。

ジャンル「{genre}」に関して、今日1日の運勢を300〜400文字で占ってください。
・文章の構成にメリハリをつけ、段落ごとにわかりやすく改行してください。
・前向きで自然な鑑定文にしてください。
・数秘術や星占いの要素を取り入れて構いません。
・読みやすさと占いらしい語り口を重視してください。
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=800
        )
        return response.choices[0].message.content.replace("。", "。\n\n")
    except Exception as e:
        return f"⚠️ エラーが発生しました：{str(e)}"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        code = request.form.get("code")
        if code == "1234":
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error="パスコードが間違っています")
    return render_template("login.html")

@app.route("/index")
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("fortune.html", result=None, name=None)

@app.route("/fortune", methods=["POST"])
def fortune():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    name = request.form.get("name")
    birthdate = request.form.get("birthdate")
    genre = request.form.get("genre")
    result = get_fortune(name, birthdate, genre)
    item = random.choice(lucky_items)
    quote = random.choice(destiny_quotes)

    today = get_japan_time().strftime("%Y年%m月%d日")
    formatted = f"<div style='text-align: center;'>"
    formatted += f"<strong>{name}さんの結果はこちら👇</strong><br><br>"
    formatted += f"【🔮{today}の{genre}🔮】<br><br>"
    formatted += f"─ 鑑定結果 ─<br><br>"
    formatted += f"{result.strip().replace(chr(10), '<br>')}<br><br>"
    formatted += f"💡ラッキーアイテム：{item}<br>"
    formatted += f"🔮 運命のひとこと：{quote}"
    formatted += f"</div>"

    return render_template("fortune.html", result=formatted, name=name)

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
