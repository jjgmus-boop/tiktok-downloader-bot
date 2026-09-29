import os
import tempfile
import threading
import requests
import yt_dlp
from flask import Flask, request

TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)


def send_message(chat_id, text):
    requests.post(
        f"{API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=30
    )


def download_and_send(chat_id, url):
    send_message(chat_id, "⏳ جاري تحميل الفيديو...")

    try:
        with tempfile.TemporaryDirectory() as folder:
            output = os.path.join(folder, "video.%(ext)s")

            options = {
                "outtmpl": output,
                "format": "best[ext=mp4]/best",
                "noplaylist": True
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])

            files = os.listdir(folder)

            if not files:
                raise Exception("لم يتم العثور على الفيديو")

            file_path = os.path.join(folder, files[0])

            with open(file_path, "rb") as video:
                response = requests.post(
                    f"{API}/sendVideo",
                    data={"chat_id": chat_id},
                    files={"video": video},
                    timeout=180
                )

            if not response.ok:
                send_message(
                    chat_id,
                    "❌ تعذر إرسال الفيديو. ربما حجم الفيديو كبير."
                )

    except Exception:
        send_message(chat_id, "❌ تعذر تحميل الفيديو")


@app.get("/")
def home():
    return "TikTok bot is running", 200


@app.post("/webhook")
def webhook():
    data = request.get_json(silent=True) or {}

    message = data.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id:
        return "ok", 200

    if text == "/start":
        send_message(
            chat_id,
            "👋 أهلاً بك!\n\nأرسل رابط فيديو TikTok"
        )

    elif text:
        threading.Thread(
            target=download_and_send,
            args=(chat_id, text),
            daemon=True
        ).start()

    return "ok", 200


def set_webhook():
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if render_url:
        requests.post(
            f"{API}/setWebhook",
            json={"url": render_url + "/webhook"},
            timeout=30
        )


set_webhook()
