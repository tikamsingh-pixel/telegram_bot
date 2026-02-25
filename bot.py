import logging
import json
import os
import math
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
    {
        "name": "Wezibon Trading PLC (Addis Ketema)", 
        "lat": 9.0300, "lon": 38.7300, 
        "phone": "+251911213784", 
        "contact": "Mr Tofik Sherif",
        "address": "F4 -40, Wereda 01, Addis Ketema, Addis Abeba"
    },
    {
        "name": "ENDRIS MOHAMMED YEMER (Addis Ketema)", 
        "lat": 9.0310, "lon": 38.7310, 
        "phone": "+251914313256", 
        "contact": "Mr Abdu Mohmmed",
        "address": "G14-B, Wereda 01, Addis Ketema, Addis Abeba"
    },
    {
        "name": "Asrar Sultan (Addis Ketema)", 
        "lat": 9.0295, "lon": 38.7290, 
        "phone": "+251915611186", 
        "contact": "Mr Bilal Lezibo",
        "address": "B25 -06, Wereda 01, Addis Ketema, Addis Abeba"
    },
    {
        "name": "KASSAHUN YEZENGAW MIHIRET (Bahir Dar)", 
        "lat": 11.5900, "lon": 37.3900, 
        "phone": "+251912767641", 
        "contact": "Mr Nega Yezengaw",
        "address": "Kebele Abinet, Bahir Dar, Amhara"
    },
    {
        "name": "ASCHALEW ASRAT TEKLE (Shashemene)", 
        "lat": 7.2000, "lon": 38.6000, 
        "phone": "+251964113754", 
        "contact": "Mr ASCHALEW ASRAT",
        "address": "Kebele Arada, Shashemene, Oromia"
    },
    {
        "name": "WUBEI SEMACHEW TEMSGEN (East Gojam)", 
        "lat": 10.3300, "lon": 37.8500, 
        "phone": "+251000000000", # Phone not provided, using placeholder
        "contact": "Alemayehu Belesty",
        "address": "Kebele 01, East Gojam, Amhara"
    }
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
    return ReplyKeyboardMarkup([["🇬🇧 English", "🇪🇹 አማርኛ"]], 
                               resize_keyboard=True, 
                               one_time_keyboard=True)

def contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Share Mobile Number", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def location_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Share Location", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
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
    # Grouping main actions on one row and Cancel on its own for clarity
    return ReplyKeyboardMarkup(
        [["🎥 Record Video", "📝 Write Testimonial"], ["❌ Cancel"]],
        resize_keyboard=True
    )

def rating_keyboard():
    # A single row of stars is very standard for UX
    return ReplyKeyboardMarkup(
        [["⭐ 1", "⭐ 2", "⭐ 3", "⭐ 4", "⭐ 5"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def cancel_keyboard():
    return ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)

# =========================
# DISTANCE
# =========================

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points 
    on the Earth using the Haversine formula.
    """
    R = 6371  # Earth radius in km
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (math.sin(d_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(d_lambda / 2) ** 2)
    
    # Calculate the central angle
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = update.effective_user

    # 1. Initialize New User
    if user_id not in customer_db:
        customer_db[user_id] = {
            "name": user.first_name,
            "mobile": None,
            "language": None,
            "state": "lang"
        }
        save_data()
        # Friendly first impression
        await update.message.reply_text(TEXT["EN"]["welcome"])

    customer = customer_db[user_id]

    # 2. Check for missing language (Onboarding)
    if not customer.get("language"):
        customer["state"] = "lang"
        save_data()
        await update.message.reply_text(TEXT["EN"]["choose_lang"], reply_markup=language_menu())
        return

    # 3. Welcome Back Returning User
    # Reset state to ensure they aren't stuck in an old flow
    customer["state"] = None
    save_data()

    lang = customer["language"]
    welcome_msg = f"{TEXT[lang]['welcome']} {customer['name']} 😊"
    
    await update.message.reply_text(welcome_msg)
    await update.message.reply_text(
        TEXT[lang]["assist"],
        reply_markup=main_menu()
    )

# =========================
# HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Safely handle non-text messages (like images or stickers)
    text = update.message.text if update.message.text else ""

    # Ensure user exists in database
    if user_id not in customer_db:
        await start(update, context)
        return

    customer = customer_db[user_id]
    
    # Determine the current language dictionary
    # We default to "EN" if the user hasn't picked one yet
    lang = customer.get("language") or "EN"
    t = TEXT.get(lang, TEXT["EN"])

    # Log the interaction (useful for debugging)
    # print(f"User {user_id} ({customer['name']}) sent: {text}")



    # =========================
    # 🌍 LANGUAGE SELECTION
    # =========================
    if customer["state"] == "lang":
        if "English" in text:
            customer["language"] = "EN"
        elif "አማርኛ" in text:
            customer["language"] = "AM"
        else:
            # If they type something else, gently nudge them to use the buttons
            await update.message.reply_text("Please choose a language / እባክዎን ቋንቋ ይምረጡ", reply_markup=language_menu())
            return

        # Crucial: Update the local translation reference immediately
        lang = customer["language"]
        t = TEXT[lang] 

        customer["state"] = "mobile"
        save_data()

        # Now t["mobile"] will be in the correct language!
        await update.message.reply_text(t["mobile"], reply_markup=contact_keyboard())
        return
    
    # =========================
    # 📱 CONTACT / LEAD CAPTURE
    # =========================
    
    # 1. Handle the incoming contact object
    if update.message.contact:
        customer["mobile"] = update.message.contact.phone_number
        customer["state"] = None  # Clear state now that we have the info
        save_data()
        
        await update.message.reply_text(t["thanks"])
        # Give them the main menu immediately to start exploring
        await update.message.reply_text(t["assist"], reply_markup=main_menu())
        return

    # 2. Gatekeeper: If mobile is missing, don't let them do anything else
    if customer["mobile"] is None:
        # If they haven't sent a contact yet, keep asking
        await update.message.reply_text(
            t["mobile"], 
            reply_markup=contact_keyboard()
        )
        return

    # =========================
    # 🛒 SHOP & SALES INQUIRIES
    # =========================
    if "Shop With Us" in text:
        await update.message.reply_text("Please choose a category 😊", reply_markup=shop_menu())
        return

    if "Back" in text:
        await update.message.reply_text(t["assist"], reply_markup=main_menu())
        return

    if "Inquiry" in text:
        # This catches Household, Wholesale, and Restaurant inquiries
        await context.bot.send_message(
            SALES_CHAT_ID,
            f"🛒 **NEW SALES INQUIRY**\n\n"
            f"👤 **Name:** {customer['name']}\n"
            f"📱 **Mobile:** {customer['mobile']}\n"
            f"🏷️ **Category:** {text}"
        )
        await update.message.reply_text(
            "✅ Inquiry received! Our sales team will call you shortly to discuss your needs. 😊", 
            reply_markup=main_menu()
        )
        return

    if "Buy Products Online" in text:
        # Professional link presentation
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Browse Online Store", url=PRODUCT_PAGE)]
        ])
        await update.message.reply_text(
            "You can browse and buy our products directly from our website:",
            reply_markup=keyboard
        )
        return

    # =========================
    # 🛠️ SUPPORT SYSTEM
    # =========================
    if text == "🛠 Support":
        customer["state"] = "support"
        save_data()
        # Using t["support"] from your dictionary (e.g., "Please describe your issue")
        # Added cancel_keyboard so they aren't trapped in the 'support' state
        await update.message.reply_text(
            t["support"], 
            reply_markup=cancel_keyboard()
        )
        return

    if customer["state"] == "support":
        # Check if the user sent text. If they sent a photo/file, you can still forward it!
        content = text if text else "[User sent media/non-text message]"
        
        # Forward the detailed request to your Support Group
        await context.bot.send_message(
            SUPPORT_CHAT_ID,
            f"⚠️ **NEW SUPPORT TICKET**\n\n"
            f"👤 **User:** {customer['name']}\n"
            f"📱 **Mobile:** {customer['mobile']}\n"
            f"🆔 **User ID:** `{user_id}`\n\n"
            f"📝 **Issue:**\n{content}"
        )
        
        # Reset the state so they can use the Main Menu again
        customer["state"] = None
        save_data()
        
        # Confirm to the user
        await update.message.reply_text(
            t["support_done"], 
            reply_markup=main_menu()
        )
        return

    # =========================
    # 📍 DEALER LOCATOR
    # =========================
    if text == "📍 Find Nearest Dealer":
        # We use a specialized keyboard that asks for GPS coordinates
        await update.message.reply_text(
            "To find the nearest dealer, please share your location 📍", 
            reply_markup=location_keyboard()
        )
        return

    if update.message.location:
        lat, lon = update.message.location.latitude, update.message.location.longitude
        
        # Find nearest dealer
        nearest = min(DEALERS, key=lambda d: calculate_distance(lat, lon, d["lat"], d["lon"]))
        dist = calculate_distance(lat, lon, nearest["lat"], nearest["lon"])
        
        # Build a detailed response message
        response = (
            f"✅ **Nearest Dealer Found!**\n\n"
            f"🏪 **Name:** {nearest['name']}\n"
            f"📍 **Address:** {nearest['address']}\n"
            f"👤 **Contact Person:** {nearest['contact']}\n"
            f"📏 **Distance:** {dist:.1f} km away\n"
            f"📞 **Phone:** {nearest['phone']}"
        )
        
        await update.message.reply_text(response, parse_mode="Markdown", reply_markup=main_menu())
        return await context.bot.send_location(
            chat_id=update.effective_chat.id, 
            latitude=nearest["lat"], 
            longitude=nearest["lon"]
        )
        return

    # =========================
    # ⭐ TESTIMONIAL HANDLING
    # =========================
    if text == "⭐ Share Testimonial":
        customer["state"] = "testimonial_menu"
        save_data()
        await update.message.reply_text(t["testimonial"], reply_markup=testimonial_menu())
        return

    # --- VIDEO TESTIMONIAL ---
    if text == "🎥 Record Video":
        customer["state"] = "video_waiting"
        save_data()
        await update.message.reply_text("🎥 Please record or upload your video testimonial 😊", reply_markup=cancel_keyboard())
        return

    if customer["state"] == "video_waiting":
        # Check if the user actually sent a video
        if update.message.video:
            customer["video_id"] = update.message.video.file_id
            customer["state"] = "video_rating"
            save_data()

            await update.message.reply_text(t["rating"], reply_markup=rating_keyboard())
            return
        
        else: 
            # This 'else' is correctly aligned now to catch non-video messages during this state
            await update.message.reply_text("Please upload a valid video file 🎥, or press ❌ Cancel.") 
            return
    
    if customer.get ("state") == "video_rating": 
        # Safely extract rating, default to 0 if text is somehow empty
        rating = "".join(filter(str.isdigit, text))

        if rating not in ["1", "2", "3", "4", "5"]:
            await update.message.reply_text(
            "Please select a rating from 1–5 ⭐",
            reply_markup=rating_keyboard()
        )
        return
    
        # Forward the video to the sales team
    try:
        await context.bot.send_message(
            SALES_CHAT_ID,
            f"⭐ TESTIMONIAL\n\n"
            f"Name: {customer['name']}\n"
            f"Mobile: {customer['mobile']}\n"
            f"Rating: {rating}/5 ⭐\n\n"
            f"Feedback:\n{customer['testimonial']}"
        )
    except Exception as e:
        print("Sales forward error:", e)

        
        # Reset state
        customer["state"] = None
        customer.pop("video_id", None) 
        save_data() 
        
        await update.message.reply_text("✨ Thank you for your feedback 😊" , reply_markup=main_menu()) 
        return
    
    # --- TEXT TESTIMONIAL ---
    if text == "📝 Write Testimonial":
        customer["state"] = "text_waiting"
        save_data()
        await update.message.reply_text("📝 Please write your testimonial 😊", reply_markup=cancel_keyboard())
        return

    if customer["state"] == "text_waiting":
        customer["testimonial"] = text
        customer["state"] = "text_rating"
        save_data()

        await update.message.reply_text(t["rating"], reply_markup=rating_keyboard())
        return

    if customer.get("state") == "text_rating":
        rating = "".join(filter(str.isdigit, text))
        
        if rating not in ["1", "2", "3", "4", "5"]:
            await update.message.reply_text(
            "Please select a rating from 1–5 ⭐",
            reply_markup=rating_keyboard()
        )
        return
        
        # Forward the text to the sales team
    try:
        await context.bot.send_message(
            SALES_CHAT_ID,
            f"⭐ TESTIMONIAL\n\n"
            f"Name: {customer['name']}\n"
            f"Mobile: {customer['mobile']}\n"
            f"Rating: {rating}/5 ⭐\n\n"
            f"Feedback:\n{customer['testimonial']}"
        )

    except Exception as e:
        print("Sales forward error:", e)
        
        # Reset state
        customer["state"] = None
        customer.pop("testimonial", None)
        save_data()
        
        await update.message.reply_text("✨ Thank you for your feedback 😊", reply_markup=main_menu()
        )
        return

    # ℹ️ UTILITY & NAVIGATION

    if "Contact Us" in text:
        await update.message.reply_text(t["contact_us"], reply_markup=main_menu())
        return

    if "Visit Website" in text:
        # It's often better to send a message WITH the link rather than just the URL
        await update.message.reply_text(f"🌐 Visit our official website: {WEBSITE_URL}", reply_markup=main_menu())
        return

    if "Change Language" in text:
        customer["language"] = None
        customer["state"] = "lang"
        save_data()
        await update.message.reply_text(TEXT["EN"]["choose_lang"], reply_markup=language_menu())
        return

    if "End Chat" in text:
        # Clear the user's state so they can start fresh next time
        customer["state"] = None
        save_data()
        await update.message.reply_text("Thank you for choosing Ethal! Have a great day 😊", reply_markup=ReplyKeyboardRemove())
        return

    # FINAL FALLBACK (Only if no other conditions were met)
    else:
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

