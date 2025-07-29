from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from flask import Flask
from threading import Thread
import time
import requests
import os
from dotenv import load_dotenv

# === LOAD TOKEN & ADMIN ID DARI .env ===
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# === FLASK SERVER ===
app = Flask('')

@app.route('/')
def home():
    return "Bot juragan aktif!", 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

def keep_loop():
    while True:
        time.sleep(60)

def self_ping():
    while True:
        try:
            requests.get("https://replit.com/@bellatasya171/terakir")  # Ganti jika perlu
        except:
            pass
        time.sleep(300)

# === MESSAGE ===
main_message = (
    "🎉 *Selamat datang juragan di BAHASENAK* 🎉\n\n"
    "Mau beli *VIP JURAGAN*? Langsung pilih paket VIP di bawah ini ya juragan 👇"
)

main_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("💎 VIP INDO (50k)", callback_data="vip_indo")],
    [InlineKeyboardButton("💎 VIP JILBAB (50k)", callback_data="vip_jilbab")],
    [InlineKeyboardButton("💎 VIP EROPA (50k)", callback_data="vip_eropa")],
    [InlineKeyboardButton("💎 VIP JAPAN (50k)", callback_data="vip_japan")],
    [InlineKeyboardButton("💎 ALL VIP (100k)", callback_data="vip_all")],
])

transfer_message = (
    "💳 *Oke juragan!*\n\n"
    "Silahkan transfer ke nomor ini ya juragan:\n"
    "DANA: 081311361110\n"
    "Atas Nama: JAXX TEGXX HARXX\n\n"
    "Jika sudah, bot akan *otomatis mengundang kamu kedalam groupnya!* 🧙‍♂️ Admin : @Jancuk168\n\n"
    "_Untuk kembali ke menu utama, cukup ketik /start ya juragan_ 🔄")

waiting_message = (
    "📸 Bukti transfer sudah diterima ya juragan!\n"
    "Tunggu *1-3 menit* yaa, LINK undangan akan dikirim ✉️\n\n"
    "Kalau belum muncul juga, boleh kontak admin: @Jancuk168 ☎️")

user_transfer_state = set()

# === HANDLER ===
def start(update, context):
    user_id = update.message.from_user.id
    name = update.message.from_user.full_name
    update.message.reply_text(main_message, reply_markup=main_keyboard, parse_mode="Markdown")
    
    # Kirim info ke admin saat ada user baru
    if ADMIN_ID:
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"👤 *User baru:* [{name}](tg://user?id={user_id})\nID: `{user_id}`",
            parse_mode="Markdown"
        )

def handle_message(update, context):
    user_id = update.message.from_user.id
    text = update.message.text or ''
    
    # Forward ke admin
    if ADMIN_ID:
        user_name = update.message.from_user.full_name
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 Pesan dari [{user_name}](tg://user?id={user_id}):\n{text}",
            parse_mode="Markdown"
        )
    
    # Respon ke user
    if user_id in user_transfer_state:
        if update.message.photo:
            update.message.reply_text(waiting_message, parse_mode="Markdown")
        else:
            update.message.reply_text(transfer_message, parse_mode="Markdown")
    else:
        update.message.reply_text(main_message, reply_markup=main_keyboard, parse_mode="Markdown")

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    vip_options = {
        "vip_indo": "🔥 *VIP INDO (50k)*\n\nVIP indo khusus INDONESIA...",
        "vip_jilbab": "🧕 *VIP JILBAB (50k)*\n\nSudah dipastikan durasinya panjang...",
        "vip_eropa": "👸 *VIP EROPA (50k)*\n\nCocok yang suka cari drama...",
        "vip_japan": "🎌 *VIP JAPAN (50k)*\n\nDurasi panjang minimal 10 menit...",
        "vip_all": "💎 *ALL VIP (100k)*\n\nSemua paket langsung dikasih juragan...",
    }

    vip_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali", callback_data="back")],
        [InlineKeyboardButton("✅ Lanjutkan", callback_data="lanjut_transfer")]
    ])

    if query.data == "back":
        user_transfer_state.discard(user_id)
        query.edit_message_text(main_message, reply_markup=main_keyboard, parse_mode="Markdown")
    elif query.data in vip_options:
        query.edit_message_text(vip_options[query.data], reply_markup=vip_keyboard, parse_mode="Markdown")
    elif query.data == "lanjut_transfer":
        user_transfer_state.add(user_id)
        query.edit_message_text(transfer_message, parse_mode="Markdown")

# === JALANKAN BOT DAN KEEP ALIVE ===
keep_alive()
Thread(target=keep_loop, daemon=True).start()
Thread(target=self_ping, daemon=True).start()

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.all, handle_message))
dp.add_handler(CallbackQueryHandler(button_handler))

print("🤖 Bot juragan aktif dan berjalan...")
updater.start_polling()
updater.idle()
