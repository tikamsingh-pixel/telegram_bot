import logging
import json
import os
import math
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# =========================
# 📝 LOGGING SETUP
# =========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =========================
# 🔐 CONFIGURATION
# =========================
# Set these in your environment variables, or replace the second argument with your strings for testing
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8270157033:AAERc9UPafWRCBDSk7mw6Uiqhb00WjcB_Qo")
SALES_CHAT_ID = os.environ.get("SALES_CHAT_ID", "-1003615161480")
SUPPORT_CHAT_ID = os.environ.get("SUPPORT_CHAT_ID", "-1003658502551")

WEBSITE_URL = "https://ethal.net/"
PRODUCT_PAGE = "https://ethal.net/products"
EMAIL_ID = "info@ethal.net"

CONTACT_NUMBERS = """
📞 +251715715715
📞 +251716716716
📞 +251717717717
"""

DATA_FILE = "customers.json"
customer_db = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# DEALERS
# =========================

DEALERS = [
    {"name": "Bole Dealer", "lat": 8.9806, "lon": 38.7578, "phone": "+251900000001"},
    {"name": "Piassa Dealer", "lat": 9.0412, "lon": 38.7468, "phone": "+251900000002"},
]

# =========================
# LANGUAGE TEXT
# =========================

TEXT = {
    "EN": {
        "welcome": "Welcome to Ethal 👋",
        "choose_lang": "Please choose your language 👇",
        "mobile": "Please share your mobile number 📱",
        "assist": "How may we assist you today? 😊",
        "thanks": "Thank you 😊",
        "support": "Please describe your issue 🛠",
        "support_done": "✅ Support Request Received\nOur team will contact you shortly 😊",
        "testimonial": "We’d love your feedback 😊",
        "rating": "⭐ Rate your experience (1–5)",
        "invalid_input": "Please choose a valid option from the menu 😊",
        "contact_us": f"{CONTACT_NUMBERS}\n✉️ {EMAIL_ID}"
    },
    "AM": {
        "welcome": "ወደ Ethal እንኳን ደህና መጡ 👋",
        "choose_lang": "ቋንቋ ይምረጡ 👇",
        "mobile": "እባክዎን ስልክ ቁጥር ያጋሩ 📱",
        "assist": "እንዴት ልንረዳዎት? 😊",
        "thanks": "እናመሰግናለን 😊",
        "support": "ችግርዎን ይግለጹ 🛠",
        "support_done": "✅ የድጋፍ ጥያቄ ተቀብሏል 😊",
        "testimonial": "እባክዎን አስተያየት ያጋሩ 😊",
        "rating": "⭐ ደረጃ ይስጡ (1–5)",
        "invalid_input": "እባክዎ ትክክለኛ አማራጭ ይምረጡ 😊",
        "contact_us": f"{CONTACT_NUMBERS}\n✉️ {EMAIL_ID}"
    }
}

# =========================
# STORAGE
# =========================

def load_data():
    global customer_db
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            customer_db.update(json.load(f))

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(customer_db, f, indent=4)

# =========================
# KEYBOARDS
# =========================

def language_menu():
    return ReplyKeyboardMarkup([["🇬🇧 English", "🇪🇹 አማርኛ"]], resize_keyboard=True)

def contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Share Mobile Number", request_contact=True)]],
        resize_keyboard=True
    )

def location_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Share Location", request_location=True)]],
        resize_keyboard=True
    )

def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["🛒 Shop With Us", "🛠 Support"],
            ["📞 Contact Us", "🌐 Visit Website"],
            ["📍 Find Nearest Dealer", "⭐ Share Testimonial"],
            ["🌍 Change Language", "🔚 End Chat"]
        ],
        resize_keyboard=True
    )

def shop_menu():
    return ReplyKeyboardMarkup(
        [
            ["🍲 Household Inquiry", "🍴 Restaurant / Hotel Inquiry"],
            ["💼 Wholesale Inquiry", "🛒 Buy Products Online"],
            ["🔙 Back"]
        ],
        resize_keyboard=True
    )

def testimonial_menu():
    return ReplyKeyboardMarkup(
        [["🎥 Record Video", "📝 Write Testimonial"], ["❌ Cancel"]],
        resize_keyboard=True
    )

def rating_keyboard():
    return ReplyKeyboardMarkup(
        [["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"]],
        resize_keyboard=True
    )

# =========================
# DISTANCE
# =========================

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(d_lon / 2) ** 2
    )
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

# =========================
# START
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

    customer = customer_db[user_id]

    if customer["language"] is None:
        customer["state"] = "lang"
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
# HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)
    text = update.message.text or ""

    if user_id not in customer_db:
        await start(update, context)
        return

    customer = customer_db[user_id]
    lang = customer.get("language") or "EN"
    t = TEXT[lang]

    # LANGUAGE
    if customer["state"] == "lang":
        if "English" in text:
            customer["language"] = "EN"
        elif "አማርኛ" in text:
            customer["language"] = "AM"
        else:
            return

        customer["state"] = "mobile"
        save_data()
        await update.message.reply_text(t["mobile"], reply_markup=contact_keyboard())
        return

    # CONTACT
    if update.message.contact:
        customer["mobile"] = update.message.contact.phone_number
        customer["state"] = None
        save_data()
        await update.message.reply_text(t["thanks"])
        await update.message.reply_text(t["assist"], reply_markup=main_menu())
        return

    if customer["mobile"] is None:
        await update.message.reply_text(t["mobile"], reply_markup=contact_keyboard())
        return

    # SHOP
    if "Shop With Us" in text:
        await update.message.reply_text("Choose category 😊", reply_markup=shop_menu())
        return

    if text == "🔙 Back":
        await update.message.reply_text(t["assist"], reply_markup=main_menu())
        return

    if "Inquiry" in text:
        await context.bot.send_message(
            SALES_CHAT_ID,
            f"🛒 NEW INQUIRY\n\nName: {customer['name']}\nMobile: {customer['mobile']}\nCategory: {text}"
        )
        await update.message.reply_text("✅ Inquiry received. Our team will contact you shortly 😊", reply_markup=main_menu())
        return

    if "Buy Products Online" in text:
        await update.message.reply_text(f"{PRODUCT_PAGE}", reply_markup=main_menu())
        return

    # SUPPORT
    if "Support" in text:
        customer["state"] = "support"
        save_data()
        await update.message.reply_text(t["support"])
        return

    if customer["state"] == "support":
        await context.bot.send_message(
            SUPPORT_CHAT_ID,
            f"🛠 Support Request\n\nName: {customer['name']}\nMobile: {customer['mobile']}\nIssue:\n{text}"
        )
        customer["state"] = None
        save_data()
        await update.message.reply_text(t["support_done"], reply_markup=main_menu())
        return

    # DEALER
    if "Find Nearest Dealer" in text:
        await update.message.reply_text("Share your location 📍", reply_markup=location_keyboard())
        return

    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        nearest = min(DEALERS, key=lambda d: calculate_distance(lat, lon, d["lat"], d["lon"]))
        await update.message.reply_text(
            f"📍 {nearest['name']}\n📞 {nearest['phone']}",
            reply_markup=main_menu()
        )
        return

    # TESTIMONIAL
    if "Share Testimonial" in text:
        customer["state"] = "testimonial"
        save_data()
        await update.message.reply_text(t["testimonial"], reply_markup=testimonial_menu())
        return

    if text == "📝 Write Testimonial":
        customer["state"] = "text_testimonial"
        save_data()
        await update.message.reply_text("Write your feedback 😊")
        return

    if customer["state"] == "text_testimonial":
        customer["testimonial"] = text
        customer["state"] = "rating"
        save_data()
        await update.message.reply_text(t["rating"], reply_markup=rating_keyboard())
        return

    if customer["state"] == "rating":
        rating = text.replace("⭐", "").strip()
        await context.bot.send_message(
            SALES_CHAT_ID,
            f"⭐ TESTIMONIAL\n\nName: {customer['name']}\nMobile: {customer['mobile']}\nRating: {rating}/5\n\n{customer['testimonial']}"
        )
        customer["state"] = None
        save_data()
        await update.message.reply_text("Thank you 😊", reply_markup=main_menu())
        return

    if "Contact Us" in text:
        await update.message.reply_text(t["contact_us"], reply_markup=main_menu())
        return

    if "Visit Website" in text:
        await update.message.reply_text(WEBSITE_URL, reply_markup=main_menu())
        return

    if "Change Language" in text:
        customer["language"] = None
        customer["state"] = "lang"
        save_data()
        await update.message.reply_text(TEXT["EN"]["choose_lang"], reply_markup=language_menu())
        return

    if "End Chat" in text:
        await update.message.reply_text("Thank you 😊", reply_markup=ReplyKeyboardRemove())
        return

    await update.message.reply_text(t["invalid_input"], reply_markup=main_menu())


# =========================
# RUN
# =========================

if __name__ == "__main__":
    load_data()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    logger.info("Bot is running...")
    app.run_polling()