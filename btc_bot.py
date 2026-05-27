from telegram.ext import Application
from config import BOT_TOKEN

print("BOT STARTED")

app = Application.builder().token(BOT_TOKEN).build()

print("BOT RUNNING")

app.run_polling()
