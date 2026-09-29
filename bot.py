import os
import tempfile
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط فيديو TikTok")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("⏳ جاري التحميل...")

    try:
        with tempfile.TemporaryDirectory() as folder:
            out = folder + "/video.%(ext)s"
            opts = {
                "outtmpl": out,
                "format": "best[ext=mp4]/best",
                "noplaylist": True
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            files = os.listdir(folder)
            file = folder + "/" + files[0]

            with open(file, "rb") as f:
                await update.message.reply_video(f)

    except Exception:
        await update.message.reply_text("❌ تعذر تحميل الفيديو")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, video))
app.run_polling()
