import telebot
from telebot import types
import sqlite3
import requests

# 🔑 আপনার মেইন বটের টোকেন এখানে বসান
TOKEN = "9150625768:AAEacN3GgqQQ1XG1oAZ7D_aFF6503Kob_ug"
bot = telebot.TeleBot(TOKEN)

# 📢 ওটিপি আসার পর যে চ্যানেল বা গ্রুপে অটোমেটিক ট্রান্সফার হবে তার আইডি
OTP_CHANNEL_ID = 1004381508455 
ADMIN_CONTACT = "@sakib43900"

# 🌐 জেনেক্স (Genex) এপিআই কনফিগারেশন
GENEX_API_URL = "https://api.zenexnetwork.com/v1/getnum"
ZENEX_API_KEY = "ZNX_Q4JF0FKQIDHBTUOL36JU3EKI"

# উইথড্র ও পেমেন্ট রিকোয়েস্ট টেম্পোরারি সেভ করার ডিকশনারি
USER_WITHDRAW_STATE = {}

# 🗄️ ডাটাবেজ ইনিশিয়ালাইজেশন (SQLite)
def init_db():
    conn = sqlite3.connect('spectre_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            balance REAL DEFAULT 0.0,
            total_otps INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_or_create_user(user_id, full_name):
    conn = sqlite3.connect('spectre_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance, total_otps FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('INSERT INTO users (user_id, full_name, balance, total_otps) VALUES (?, ?, ?, ?)', (user_id, full_name, 0.0, 0))
        conn.commit()
        balance, total_otps = 0.0, 0
    else:
        balance, total_otps = user
        
    conn.close()
    return balance, total_otps

def increment_user_otp(user_id):
    conn = sqlite3.connect('spectre_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET total_otps = total_otps + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# 📱 জেনেক্স এপিআই থেকে লাইভ নাম্বার আনার ফাংশন
def fetch_number_from_genex(service_code):
    try:
        headers = {
            "mapikey": ZENEX_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "service": service_code
        }
        
        response = requests.post(GENEX_API_URL, headers=headers, json=payload, timeout=10)
        data = response.json()
        
        if "number" in data:
            return data.get("number")
        elif "data" in data and "number" in data["data"]:
            return data["data"]["number"]
        else:
            return None 
    except Exception as e:
        print(f"Genex API Error: {e}")
        return None

# 🚀 /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    get_or_create_user(user.id, user.first_name)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📱 GET NUMBER"),
        types.KeyboardButton("📊 LIVE TRAFFIC"),
        types.KeyboardButton("👤 STATUS"),
        types.KeyboardButton("💰 BALANCE"),
        types.KeyboardButton("💳 WITHDRAW (Min 50৳)"),
        types.KeyboardButton("🏆 TODAY TOP"),
        types.KeyboardButton("💬 SUPPORT")
    )
    
    welcome_text = (
        f"⚡ **WELCOME TO SPECTRE AUTOMATED SMS PANEL** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Hello, **{user.first_name}**!\n\n"
        f"🚀 Fully automated real-time OTP verification solution. Select an option from the panel below:"
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# 🎛️ মেনু ও টেক্সট মেসেজ হ্যান্ডলার (উইথড্র অ্যাকাউন্ট নাম্বার ইনপুট রিসিভ করার জন্য)
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user = message.from_user
    user_id = user.id
    text = message.text
    
    # যদি ইউজার উইথড্র করার জন্য অ্যাকাউন্ট নাম্বার লিখে পাঠায়
    if user_id in USER_WITHDRAW_STATE:
        state_info = USER_WITHDRAW_STATE[user_id]
        method = state_info["method"]
        acc_number = text.strip()
        
        # ডাটাবেজ থেকে ব্যালেন্স চেক
        balance, _ = get_or_create_user(user_id, user.first_name)
        
        if balance < 50:
            bot.send_message(message.chat.id, "❌ **Error:** Your balance dropped below 50 BDT. Withdrawal cancelled.", parse_mode="Markdown")
            del USER_WITHDRAW_STATE[user_id]
            return
            
        # এডমিন বা চ্যানেল নোটিফিকেশন মেসেজ তৈরি
        withdrawal_log = (
            f"📥 **NEW WITHDRAWAL REQUEST** 📥\n\n"
            f"• User Name: {user.first_name}\n"
            f"• Telegram ID: `{user_id}`\n"
            f"• Method: `{method}`\n"
            f"• Account Number: `{acc_number}`\n"
            f"• Amount: `{balance} BDT`\n\n"
            f"📌 *Action Required: Please send payment and clear balance.*"
        )
        
        # ওটিপি চ্যানেলে রিকোয়েস্ট পাঠিয়ে দেওয়া
        try:
            bot.send_message(OTP_CHANNEL_ID, withdrawal_log, parse_mode="Markdown")
        except Exception as e:
            print(f"Withdrawal Log Error: {e}")
            
        bot.send_message(
            message.chat.id, 
            f"✅ **Withdrawal Request Submitted Successfully!**\n\nYour request for `{balance} BDT` via `{method}` (`{acc_number}`) has been sent to the admin. Payment will be sent soon.", 
            parse_mode="Markdown"
        )
        
        del USER_WITHDRAW_STATE[user_id]
        return

    balance, total_otps = get_or_create_user(user_id, user.first_name)
    
    if text == "📱 GET NUMBER":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📘 Facebook Verification", callback_data="menu_facebook"))
        
        bot.send_message(
            message.chat.id, 
            "🌐 **SERVICE CATEGORIES:**\nSelect a platform below to proceed with real-time numbers:", 
            parse_mode="Markdown", 
            reply_markup=markup
        )
        
    elif text == "📊 LIVE TRAFFIC":
        traffic_msg = (
            "📊 **GENEX REAL-TIME LIVE TRAFFIC** 📊\n\n"
            "• Facebook Gateway: `High Speed & Active`\n"
            "• Stock Range Sync: `Real-time Connected`\n\n"
            "⚡ *Server traffic is optimal for verifications.*"
        )
        bot.send_message(message.chat.id, traffic_msg, parse_mode="Markdown")
        
    elif text == "👤 STATUS":
        status_msg = (
            f"👤 **USER ACCOUNT STATUS**\n\n"
            f"• Full Name: {user.first_name}\n"
            f"• Telegram ID: `{user_id}`\n"
            f"• Total Processed OTPs: `{total_otps}` 📥\n"
            f"• Status: `Active VIP` 🌟"
        )
        bot.send_message(message.chat.id, status_msg, parse_mode="Markdown")
        
    elif text == "💰 BALANCE":
        balance_msg = (
            f"💰 **WALLET & BALANCE**\n\n"
            f"• Current Balance: `{balance} BDT`\n"
            f"• Total OTPs Used: `{total_otps}`\n\n"
            f"💳 *To top-up your balance, contact administration.*"
        )
        bot.send_message(message.chat.id, balance_msg, parse_mode="Markdown")
        
    elif text == "💳 WITHDRAW (Min 50৳)":
        if balance >= 50:
            withdraw_markup = types.InlineKeyboardMarkup(row_width=2)
            withdraw_markup.add(
                types.InlineKeyboardButton("💸 Bkash", callback_data="withdraw_Bkash"),
                types.InlineKeyboardButton("💸 Nagad", callback_data="withdraw_Nagad"),
                types.InlineKeyboardButton("💸 Rocket", callback_data="withdraw_Rocket"),
                types.InlineKeyboardButton("💎 Binance", callback_data="withdraw_Binance")
            )
            withdraw_msg = (
                f"✅ **WITHDRAWAL GATEWAY**\n\n"
                f"• Available Balance: `{balance} BDT`\n"
                f"• Minimum Limit: `50 BDT`\n\n"
                f"👇 **Select your payout method:**"
            )
            bot.send_message(message.chat.id, withdraw_msg, parse_mode="Markdown", reply_markup=withdraw_markup)
        else:
            error_msg = (
                f"⚠️ **INSUFFICIENT BALANCE ERROR** ⚠️\n\n"
                f"• Current Balance: `{balance} BDT`\n"
                f"• Required Minimum: `50 BDT`\n\n"
                f"❌ *Your balance is below 50 BDT. You cannot request a withdrawal right now.*"
            )
            bot.send_message(message.chat.id, error_msg, parse_mode="Markdown")
        
    elif text == "🏆 TODAY TOP":
        top_msg = (
            "🏆 **TODAY'S TOP SERVICES** 🏆\n\n"
            "1. 📘 **Facebook Real-Time Gateway** -> `Active Stock`\n\n"
            "🔥 *Highest success rate for automated verifications.*"
        )
        bot.send_message(message.chat.id, top_msg, parse_mode="Markdown")
        
    elif text == "💬 SUPPORT":
        support_markup = types.InlineKeyboardMarkup()
        support_markup.add(types.InlineKeyboardButton("💬 Contact Admin / Support", url=f"https://t.me/{ADMIN_CONTACT.replace('@', '')}"))
        
        support_msg = (
            f"💬 **24/7 CUSTOMER SUPPORT DESK**\n\n"
            f"Need help or facing any issues?\n"
            f"Directly message our official admin: `{ADMIN_CONTACT}`"
        )
        bot.send_message(message.chat.id, support_msg, parse_mode="Markdown", reply_markup=support_markup)
        
    else:
        bot.send_message(message.chat.id, "⚠️ Please use the official control panel buttons below.")

# 📱 ইনলাইন বাটন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "menu_facebook":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🇮🇹 Italy (Facebook Range)", callback_data="get_fb_italy"))
        markup.add(types.InlineKeyboardButton("🇺🇸 USA (Facebook Range)", callback_data="get_fb_usa"))
        markup.add(types.InlineKeyboardButton("🌐 Auto-Detect Best Range", callback_data="get_fb_auto"))
        markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
        
        bot.edit_message_text(
            "📘 **FACEBOOK REAL-TIME NUMBER RANGES:**\nSelect an active range from Genex gateway below:", 
            call.message.chat.id, 
            call.message.message_id, 
            parse_mode="Markdown", 
            reply_markup=markup
        )
        
    elif call.data.startswith("get_fb_"):
        range_type = call.data.replace("get_fb_", "")
        bot.answer_callback_query(call.id, "Fetching real-time number from Genex...")
        
        service_code = f"facebook_{range_type}" if range_type != "auto" else "facebook"
        assigned_number = fetch_number_from_genex(service_code)
        
        if assigned_number:
            response_msg = (
                f"⏳ **WAITING FOR FACEBOOK OTP...**\n\n"
                f"📱 **Assigned Number:** `{assigned_number}`\n\n"
                f"📌 *Status:* Ready. Send Facebook verification code. OTP will appear here automatically."
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Get Another Number", callback_data="menu_facebook"))
            markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
            
            bot.edit_message_text(response_msg, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
            
            increment_user_otp(user_id)
            trigger_otp_listener(assigned_number, f"Facebook ({range_type.upper()})", user_id)
        else:
            no_num_msg = (
                f"⚠️ **NO NUMBER AVAILABLE IN THIS RANGE**\n\n"
                f"❌ Currently, no active stock is available for this range in Genex.\n"
                f"🔄 *Please try another range or try again shortly.*"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back to Ranges", callback_data="menu_facebook"))
            bot.edit_message_text(no_num_msg, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("withdraw_"):
        method = call.data.replace("withdraw_", "")
        bot.answer_callback_query(call.id, f"Selected {method}!")
        
        USER_WITHDRAW_STATE[user_id] = {"method": method}
        
        prompt_msg = (
            f"📥 **{method.upper()} WITHDRAWAL SETUP**\n\n"
            f"✍️ *Please type and send your {method} Account Number (e.g., 017xxxxxxxx) in the chat now:*"
        )
        bot.send_message(call.message.chat.id, prompt_msg, parse_mode="Markdown")

    elif call.data == "back_menu":
        bot.edit_message_text("🌐 **MAIN CONTROL PANEL:**\nSelect an option from your main keyboard below.", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

def trigger_otp_listener(phone, service, user_id):
    log_text = (
        f"🔔 **NEW NUMBER ASSIGNED & LISTENING**\n\n"
        f"📱 **Number:** `{phone}`\n"
        f"🌍 **Service:** {service}\n"
        f"👤 **Target User ID:** `{user_id}`\n\n"
        f"⏳ *Waiting for incoming SMS/OTP...*"
    )
    try:
        bot.send_message(OTP_CHANNEL_ID, log_text, parse_mode="Markdown")
    except Exception as e:
        print(f"OTP Forwarding Error: {e}")

# বট রান করার লুপ
if __name__ == "__main__":
    print("SPECTRE_ULTIMATE_SMS_BOT is running smoothly...")
    bot.infinity_polling()
