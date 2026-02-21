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
        "support": "Please describe your issue 🛠",
        "support_done": "✅ Support Request Received\nOur team will contact you shortly 😊",
        "testimonial": "We’d love your feedback 😊",
        "rating": "⭐ Rate your experience (1–5)",
        "invalid_input": "Please choose a valid option from the menu 😊",
        "contact_us": f"Here is how you can reach us:\n{CONTACT_NUMBERS}\n✉️ {EMAIL_ID}"
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
        "contact_us": f"በነዚህ አድራሻዎች ሊያገኙን ይችላሉ:\n{CONTACT_NUMBERS}\n✉️ {EMAIL_ID}"
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
        json.dump(customer_db, f, indent=4)

# =========================
# 📋 KEYBOARDS
# =========================
def language_menu():
    return ReplyKeyboardMarkup([["🇬🇧 English", "🇪🇹 አማርኛ"]], resize_keyboard=True)

def contact_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("📱 Share Mobile Number", request_contact=True)]], resize_keyboard=True)

def location_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("📍 Share Location", request_location=True)]], resize_keyboard=True)

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
            ["🔙 Back to Main Menu"]
        ],
        resize_keyboard=True
    )

def testimonial_menu():
    return ReplyKeyboardMarkup([["🎥 Record Video", "📝 Write Testimonial"], ["❌ Cancel"]], resize_keyboard=True)

def rating_keyboard():
    return ReplyKeyboardMarkup([["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"]], resize_keyboard=True)

def location_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("📍 Share Location", request_location=True)]], resize_keyboard=True)


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

    await update.message.reply_text(f"{TEXT[customer['language']]['welcome']} {customer['name']} 😊")
    await update.message.reply_text(TEXT[customer["language"]]["assist"], reply_markup=main_menu())

# =========================
# 💬 HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text if update.message.text else ""

    if user_id not in customer_db:
        await start(update, context)
        return

    customer = customer_db[user_id]
    lang = customer.get("language", "EN") # Default to EN if missing to prevent errors
    t = TEXT[lang] if lang else TEXT["EN"]

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
        else:
            await update.message.reply_text("Please select a language from the menu.")
            return

        customer["state"] = "mobile"
        save_data()
        await update.message.reply_text(TEXT[customer["language"]]["mobile"], reply_markup=contact_keyboard())
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

    # MAIN MENU ACTIONS
    if text == "🛒 Shop With Us":
        await update.message.reply_text("🛒 Shop With Us 😊", reply_markup=shop_menu())
        return

    elif text == "📞 Contact Us":
        await update.message.reply_text(t["contact_us"], reply_markup=main_menu())
        return

    elif text == "🌐 Visit Website":
        await update.message.reply_text(f"Visit us here: {WEBSITE_URL}", reply_markup=main_menu())
        return

    elif text == "🛠 Support":
        customer["state"] = "support_request"
        save_data()
        await update.message.reply_text(t["support"], reply_markup=cancel_keyboard())
        return

      
    elif customer["state"] == "support_request":
        # Forward support request to support chat
        await context.bot.send_message(
            SUPPORT_CHAT_ID,
            f"🛠 Support Request\n\nName: {customer['name']}\nMobile: {customer['mobile']}\nIssue: {text}"
        )
        customer["state"] = None
        save_data()
        await update.message.reply_text(t["support_done"], reply_markup=main_menu())
        return

    elif "Buy Products Online" in text:

        await update.message.reply_text(
            f"Browse products here 👇\n{PRODUCT_PAGE}",
            reply_markup=main_menu()
        )
    return

    elif text == "🔙 Back to Main Menu":
        await update.message.reply_text(t["assist"], reply_markup=main_menu())
        return


    # DEALER
    elif text == "📍 Find Nearest Dealer":
        await update.message.reply_text("Share your location 📍", reply_markup=location_keyboard())
        return

    elif update.message.location:
        user_lat = update.message.location.latitude
        user_lon = update.message.location.longitude

        nearest = min(DEALERS, key=lambda d: calculate_distance(user_lat, user_lon, d["lat"], d["lon"]))

        await update.message.reply_text(
            f"""📍 Nearest Dealer

        {nearest['name']}
        Phone: {nearest['phone']}
        """
        )
        await update.message.reply_text(TEXT[lang]["assist"], reply_markup=main_menu())
        return

    # TESTIMONIAL ENTRY
    elif text == "⭐ Share Testimonial":
        customer["state"] = None
        save_data()
        await update.message.reply_text(t["testimonial"], reply_markup=testimonial_menu())
        return

    # VIDEO TESTIMONIAL
    elif text == "🎥 Record Video":
        customer["state"] = "video"
        save_data()
        await update.message.reply_text("🎥 Please upload your video testimonial 😊", reply_markup=cancel_keyboard())
        return

    elif customer["state"] == "video":
        if update.message.video:
            customer["video_id"] = update.message.video.file_id
            customer["state"] = "video_rating"
            save_data()
            await update.message.reply_text(t["rating"], reply_markup=rating_keyboard())
        else:
            await update.message.reply_text("Please upload a valid video file, or press Cancel. 🎥")
        return

    elif customer["state"] == "video_rating":
        rating = text.replace("⭐", "").strip()
        await context.bot.send_video(
            SALES_CHAT_ID,
            customer["video_id"],
            caption=f"🎥 Video Testimonial\n\nName: {customer['name']}\nMobile: {customer['mobile']}\nRating: {rating}/5 ⭐"
        )
        customer["state"] = None
        save_data()
        await update.message.reply_text("✨ Thank you for your feedback 😊")
        await update.message.reply_text(t["assist"], reply_markup=main_menu())
        return

    # TEXT TESTIMONIAL
    elif text == "📝 Write Testimonial":
        customer["state"] = "text_testimonial"
        save_data()
        await update.message.reply_text("📝 Please write your testimonial 😊", reply_markup=cancel_keyboard())
        return

    elif customer["state"] == "text_testimonial":
        customer["testimonial"] = text
        customer["state"] = "text_rating"
        save_data()
        await update.message.reply_text(t["rating"], reply_markup=rating_keyboard())
        return

    elif customer["state"] == "text_rating":
        rating = text.replace("⭐", "").strip()
        await context.bot.send_message(
            SALES_CHAT_ID,
            f"⭐ Testimonial\n\nName: {customer['name']}\nMobile: {customer['mobile']}\nRating: {rating}/5 ⭐\n\nFeedback:\n{customer['testimonial']}"
        )
        customer["state"] = None
        save_data()
        await update.message.reply_text("✨ Thank you for your feedback 😊")
        await update.message.reply_text(t["assist"], reply_markup=main_menu())
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
        await update.message.reply_text("Thank you for visiting Ethal 😊", reply_markup=ReplyKeyboardRemove())
        return

    # UNKNOWN INPUT
    else:
        await update.message.reply_text(t["invalid_input"], reply_markup=main_menu())

# =========================
# 🤖 BOT SETUP
# =========================
if __name__ == "__main__":
    load_data()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is running...")
    app.run_polling()

