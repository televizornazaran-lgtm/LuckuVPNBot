import json, random, threading
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from flask import Flask, request, jsonify

TOKEN = "8381559075:AAE2zuxEzrJfn0W_Cy-BNbiIQj2jw1_M0AM"
KEYS_FILE = "keys.txt"
USERS_FILE = "users.json"

app_bot = ApplicationBuilder().token(TOKEN).build()
flask_app = Flask(__name__)

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_new_key(user_id):
    users = load_users()
    with open(KEYS_FILE, "r") as f:
        keys = f.read().splitlines()
    if user_id not in users:
        users[user_id] = {"keys": [], "free_until": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")}
    remaining_keys = list(set(keys) - set(users[user_id]["keys"]))
    if remaining_keys:
        key = random.choice(remaining_keys)
        users[user_id]["keys"].append(key)
        save_users(users)
    return users[user_id]

@flask_app.route("/get_user_data")
def get_user_data():
    user_id = request.args.get("user_id")
    user_data = get_new_key(user_id)
    return jsonify(user_data)

@flask_app.route("/get_key")
def api_get_key():
    user_id = request.args.get("user_id")
    user_data = get_new_key(user_id)
    return jsonify(user_data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 Lucky VPN – быстрый и стабильный сервис\n"
        "Откройте мини-приложение через кнопку и получите ключи!\n"
        "📞 Поддержка: @lucky_vpn_support"
    )

app_bot.add_handler(CommandHandler("start", start))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используйте мини-приложение или /start")

app_bot.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

def run_flask():
    flask_app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_flask).start()
print("🚀 Lucky VPN Bot + WebApp запущен...")
app_bot.run_polling()
