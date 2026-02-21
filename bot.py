from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

import json
import os
import math

# =========================
# 🔐 CONFIGURATION
# =========================

BOT_TOKEN = "8270157033:AAERc9UPafWRCBDSk7mw6Uiqhb00WjcB_Qo"
SALES_CHAT_ID = "-1003615161480"
SUPPORT_CHAT_ID = "-1003658502551"

WEBSITE_URL = "https://ethal.net/"
PRODUCT_PAGE = "https://ethal.net/products"

EMAIL_ID = "info@ethal.net"

CONTACT_NUMBERS = """
+251715715715
+251716716716
+251717717717
"""

DATA_FILE = "customers.json"

customer_db = {}

# =========================
# 🌍 LANGUAGE TEXT
# =========================

TEXT = {
    "EN": {
        "welcome": "Welcome to Ethal 👋",
        "choose_lang": "Please choose your language 👇",
        "mobile": "Please share your mobile number 📱",
        "assist": "How may we assist you today? 😊",
        "thanks": "Thank you 😊",
        "testimonial": "We’d love your feedback 😊",
        "rating": "⭐ Rate your experience (1–5)"
    },
    "AM": {
        "welcome": "ወደ Ethal እንኳን ደህና መጡ 👋",
        "choose_lang": "ቋንቋ ይምረጡ 👇",
        "mobile": "እባክዎን ስልክ ቁጥር ያጋሩ 📱",
        "assist": "እንዴት ልንረዳዎት? 😊",
        "thanks": "እናመሰግናለን 😊",
        "testimonial": "እባክዎን አስተያየት ያጋሩ 😊",
        "rating": "⭐ ደረጃ ይስጡ (1–5)"
    }
}

# =========================
# 💾 STORAGE
# =========================

def load_data():
    global customer_db
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            customer_db = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(customer_db, f)

# =========================
# 📋 KEYBOARDS
# =========================

def language_menu():
    return ReplyKeyboardMarkup(
        [["🇬🇧 English", "🇪🇹 አማርኛ"]],
        resize_keyboard=True
    )

def contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Share Mobile Number", request_contact=True)]],
        resize_keyboard=True
    )

def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["🛒 Shop With Us"],
            ["⭐ Share Testimonial"],
            ["🌍 Change Language"],
            ["🔚 End Chat"]
        ],
        resize_keyboard=True
    )

def shop_menu():
    return ReplyKeyboardMarkup(
        [
            ["🍲 Household Inquiry"],
            ["🍴 Restaurant / Hotel Inquiry"],
            ["💼 Wholesale Inquiry"],
            ["🔙 Back to Main Menu"]
        ],
        resize_keyboard=True
    )

def testimonial_menu():
    return ReplyKeyboardMarkup(
        [
            ["🎥 Record Video"],
            ["📝 Write Testimonial"],
            ["❌ Cancel"]
        ],
        resize_keyboard=True
    )

def rating_keyboard():
    return ReplyKeyboardMarkup(
        [["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"]],
        resize_keyboard=True
    )

def cancel_keyboard():
    return ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)

# =========================
# 🚀 START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)
    user = update.effective_user

    if user_id not in customer_db:

        customer_db[user_id] = {
            "name": user.first_name,
            "mobile": None,
            "language": None,
            "state": "lang"
        }

        save_data()

        await update.message.reply_text(TEXT["EN"]["welcome"])
        await update.message.reply_text(TEXT["EN"]["choose_lang"], reply_markup=language_menu())
        return

    customer = customer_db[user_id]

    if customer["language"] is None:
        customer["state"] = "lang"
        save_data()
        await update.message.reply_text(TEXT["EN"]["choose_lang"], reply_markup=language_menu())
        return

    await update.message.reply_text(
        f"{TEXT[customer['language']]['welcome']} {customer['name']} 😊"
    )

    await update.message.reply_text(
        TEXT[customer["language"]]["assist"],
        reply_markup=main_menu()
    )

# =========================
# 💬 HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in customer_db:
        await start(update, context)
        return

    customer = customer_db[user_id]
    lang = customer["language"]

    # CANCEL
    if text == "❌ Cancel":

        customer["state"] = None
        save_data()

        await update.message.reply_text("No problem 😊", reply_markup=main_menu())
        return

    # LANGUAGE
    if customer["state"] == "lang":

        if "English" in text:
            customer["language"] = "EN"

        elif "አማርኛ" in text:
            customer["language"] = "AM"

        customer["state"] = "mobile"
        save_data()

        await update.message.reply_text(
            TEXT[customer["language"]]["mobile"],
            reply_markup=contact_keyboard()
        )
        return

    # CONTACT
    if update.message.contact:

        customer["mobile"] = update.message.contact.phone_number
        customer["state"] = None
        save_data()

        await update.message.reply_text(TEXT[customer["language"]]["thanks"])
        await update.message.reply_text(TEXT[customer["language"]]["assist"], reply_markup=main_menu())
        return

    # FORCE MOBILE
    if customer["mobile"] is None:

        await update.message.reply_text(TEXT[customer["language"]]["mobile"], reply_markup=contact_keyboard())
        return

    # SHOP MENU
    if text == "🛒 Shop With Us":

        await update.message.reply_text("🛒 Shop With Us 😊", reply_markup=shop_menu())
        return

    elif text == "🔙 Back to Main Menu":

        await update.message.reply_text(TEXT[customer["language"]]["assist"], reply_markup=main_menu())
        return

    # TESTIMONIAL ENTRY
    elif text == "⭐ Share Testimonial":

        customer["state"] = None
        save_data()

        await update.message.reply_text(
            TEXT[customer["language"]]["testimonial"],
            reply_markup=testimonial_menu()
        )
        return

    # VIDEO TESTIMONIAL
    elif text == "🎥 Record Video":

        customer["state"] = "video"
        save_data()

        await update.message.reply_text(
            "🎥 Please upload your video testimonial 😊",
            reply_markup=cancel_keyboard()
        )
        return

    elif customer["state"] == "video" and update.message.video:

        customer["video_id"] = update.message.video.file_id
        customer["state"] = "video_rating"
        save_data()

        await update.message.reply_text(
            TEXT[customer["language"]]["rating"],
            reply_markup=rating_keyboard()
        )
        return

    elif customer["state"] == "video_rating":

        rating = text.replace("⭐", "").strip()

        await context.bot.send_video(
            SALES_CHAT_ID,
            customer["video_id"],
            caption=f"""🎥 Video Testimonial

Name: {customer['name']}
Mobile: {customer['mobile']}

Rating: {rating}/5 ⭐
"""
        )

        customer["state"] = None
        save_data()

        await update.message.reply_text("✨ Thank you for your feedback 😊")
        await update.message.reply_text(TEXT[customer["language"]]["assist"], reply_markup=main_menu())
        return

    # TEXT TESTIMONIAL
    elif text == "📝 Write Testimonial":

        customer["state"] = "text_testimonial"
        save_data()

        await update.message.reply_text(
            "📝 Please write your testimonial 😊",
            reply_markup=cancel_keyboard()
        )
        return

    elif customer["state"] == "text_testimonial":

        customer["testimonial"] = text
        customer["state"] = "text_rating"
        save_data()

        await update.message.reply_text(
            TEXT[customer["language"]]["rating"],
            reply_markup=rating_keyboard()
        )
        return

    elif customer["state"] == "text_rating":

        rating = text.replace("⭐", "").strip()

        await context.bot.send_message(
            SALES_CHAT_ID,
            f"""⭐ Testimonial

Name: {customer['name']}
Mobile: {customer['mobile']}

Rating: {rating}/5 ⭐

Feedback:
{customer['testimonial']}
"""
        )

        customer["state"] = None
        save_data()

        await update.message.reply_text("✨ Thank you for your feedback 😊")
        await update.message.reply_text(TEXT[customer["language"]]["assist"], reply_markup=main_menu())
        return

    # LANGUAGE SWITCH
    elif text == "🌍 Change Language":

        customer["language"] = None
        customer["state"] = "lang"
        save_data()

        await update.message.reply_text(TEXT["EN"]["choose_lang"], reply_markup=language_menu())
        return

    # END CHAT
    elif text == "🔚 End Chat":

        customer["state"] = None
        save_data()

        await update.message.reply_text(
            "Thank you for visiting Ethal 😊",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    else:

        await update.message.reply_text("Please choose an option 😊", reply_markup=main_menu())

# =========================
# 🤖 BOT SETUP
# =========================

load_data()

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

print("Bot Running...")
app.run_polling()