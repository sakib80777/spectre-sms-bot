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
GENEX_API_KEY = "ZNX_Q4JF0FKQIDHBTUOL36JU3EKI"

# 🌍 ফেসবুকের জন্য রানিং কান্ট্রি লিস্ট (পতাকাসহ)
FACEBOOK_COUNTRIES = {
    "fb_italy": {"name": "🇮🇹 Italy (Facebook)", "service_code": "facebook_italy", "traffic": "98% (High Speed)"},
    "fb_usa": {"name": "🇺🇸 USA (Facebook)", "service_code": "facebook_usa", "traffic": "95% (Stable)"},
    "fb_uk": {"name": "🇬🇧 UK (Facebook)", "service_code": "facebook_uk", "traffic": "92% (Good)"},
    "fb_canada": {"name": "🇨🇦 Canada (Facebook)", "service_code": "facebook_canada", "traffic": "96% (Fast)"}
}

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

# ইউজারের সফল ওটিপি কাউন্ট বাড়ানোর ফাংশন
def increment_user_otp(user_id):
    conn = sqlite3.connect('spectre_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET total_otps = total_otps + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# 📱 জেনেক্স এপিআই থেকে ফেসবুকের নির্দিষ্ট কান্ট্রি অনুযায়ী লাইভ নাম্বার আনার ফাংশন
def fetch_number_from_genex(service_code):
    try:
        headers = {
            "mapikey": GENEX_API_KEY,
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
        f"⚡ **WELCOME TO SPECTRE FACEBOOK SMS PANEL** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Hello, **{user.first_name}**!\n\n"
        f"🚀 Exclusive automated platform for **Facebook OTP & Number verification**. Get instant numbers securely.\n\n"
        f"👇 Select an option from the control panel below:"
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# 🎛️ মেনু বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    text = message.text
    user = message.from_user
    balance, total_otps = get_or_create_user(user.id, user.first_name)
    
    if text == "📱 GET NUMBER":
        markup = types.InlineKeyboardMarkup(row_width=1)
        # ফেসবুকের কান্ট্রিগুলো পতাকাসহ ইনলাইন বাটনে যোগ করা
        for key, data in FACEBOOK_COUNTRIES.items():
            markup.add(types.InlineKeyboardButton(f"{data['name']} (Traffic: {data['traffic']})", callback_data=f"fb_country_{key}"))
        
        bot.send_message(message.chat.id, "📘 **FACEBOOK TARGET COUNTRY SELECTION:**\nSelect your desired country below to fetch a live Facebook verification number:", parse_mode="Markdown", reply_markup=markup)
        
    elif text == "📊 LIVE TRAFFIC":
        traffic_msg = "📊 **FACEBOOK LIVE TRAFFIC MONITOR** 📊\n\n"
        for key, data in FACEBOOK_COUNTRIES.items():
            traffic_msg += f"• {data['name']}: `Success Rate {data['traffic']}`\n"
        traffic_msg += "\n⚡ *Genex Facebook gates are running at high velocity.*"
        bot.send_message(message.chat.id, traffic_msg, parse_mode="Markdown")
        
    elif text == "👤 STATUS":
        status_msg = (
            f"👤 **USER ACCOUNT STATUS**\n\n"
            f"• Full Name: {user.first_name}\n"
            f"• Telegram ID: `{user.id}`\n"
            f"• Total Received OTPs: `{total_otps}` 📥\n"
            f"• Account Tier: `VIP Facebook Panel` 🌟"
        )
        bot.send_message(message.chat.id, status_msg, parse_mode="Markdown")
        
    elif text == "💰 BALANCE":
        balance_msg = (
            f"💰 **WALLET & BALANCE**\n\n"
            f"• Current Balance: `{balance} BDT`\n"
            f"• Total OTPs Processed: `{total_otps}`\n\n"
            f"💳 *To add balance or top-up, contact administration.*"
        )
        bot.send_message(message.chat.id, balance_msg, parse_mode="Markdown")
        
    elif text == "💳 WITHDRAW (Min 50৳)":
        if balance >= 50:
            withdraw_markup = types.InlineKeyboardMarkup(row_width=2)
            withdraw_markup.add(
                types.InlineKeyboardButton("💸 Bkash", callback_data="withdraw_bkash"),
                types.InlineKeyboardButton("💸 Nagad", callback_data="withdraw_nagad"),
                types.InlineKeyboardButton("💸 Rocket", callback_data="withdraw_rocket"),
                types.InlineKeyboardButton("💎 Binance", callback_data="withdraw_binance")
            )
            withdraw_msg = (
                f"✅ **WITHDRAWAL GATEWAY**\n\n"
                f"• Available Balance: `{balance} BDT`\n"
                f"• Minimum Limit: `50 BDT`\n\n"
                f"👇 **Select your preferred payout method:**"
            )
            bot.send_message(message.chat.id, withdraw_msg, parse_mode="Markdown", reply_markup=withdraw_markup)
        else:
            withdraw_msg = (
                f"⚠️ **INSUFFICIENT BALANCE**\n\n"
                f"• Current Balance: `{balance} BDT`\n"
                f"• Required Minimum: `50 BDT`\n\n"
                f"❌ *Your balance is below 50 BDT.*"
            )
            bot.send_message(message.chat.id, withdraw_msg, parse_mode="Markdown")
        
    elif text == "🏆 TODAY TOP":
        top_msg = (
            "🏆 **TODAY'S TOP FACEBOOK COUNTRIES** 🏆\n\n"
            "1. 🇮🇹 **Italy (Facebook)** -> `98% Success (High Traffic)`\n"
            "2. 🇨🇦 **Canada (Facebook)** -> `96% Success (Fast Gateway)`\n\n"
            "🔥 *Optimized for seamless Facebook verifications.*"
        )
        bot.send_message(message.chat.id, top_msg, parse_mode="Markdown")
        
    elif text == "💬 SUPPORT":
        support_markup = types.InlineKeyboardMarkup()
        support_markup.add(types.InlineKeyboardButton("💬 Contact Admin / Support", url=f"https://t.me/{ADMIN_CONTACT.replace('@', '')}"))
        
        support_msg = (
            f"💬 **24/7 CUSTOMER SUPPORT DESK**\n\n"
            f"Need help, top-up, or facing any issues?\n"
            f"Directly message our official admin: `{ADMIN_CONTACT}`"
        )
        bot.send_message(message.chat.id, support_msg, parse_mode="Markdown", reply_markup=support_markup)
        
    else:
        bot.send_message(message.chat.id, "⚠️ Please use the official control panel buttons below.")

# 📱 ইনলাইন বাটন হ্যান্ডলার (ফেসবুক কান্ট্রি ও উইথড্র)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data.startswith("fb_country_"):
        c_key = call.data.replace("fb_country_", "")
        if c_key in FACEBOOK_COUNTRIES:
            c_info = FACEBOOK_COUNTRIES[c_key]
            bot.answer_callback_query(call.id, f"Fetching {c_info['name']} number...")
            
            # জেনেক্স এপিআই থেকে ফেসবুকের নির্দিষ্ট কান্ট্রি কোড দিয়ে নাম্বার আনা
            assigned_number = fetch_number_from_genex(c_info["service_code"])
            
            if assigned_number:
                response_msg = (
                    f"⏳ **WAITING FOR FACEBOOK OTP...**\n\n"
                    f"🌍 **Gateway:** {c_info['name']}\n"
                    f"📱 **Assigned Number:** `{assigned_number}`\n\n"
                    f"📌 *Status:* Ready. Send Facebook verification code to this number. OTP will appear here automatically."
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Get Another Number", callback_data=f"fb_country_{c_key}"))
                markup.add(types.InlineKeyboardButton("🔙 Back to Country List", callback_data="back_fb_menu"))
                
                bot.edit_message_text(response_msg, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
                
                # ইউজারের সফল ওটিপি কাউন্ট এবং চ্যানেলে লগ পাঠানোর ফাংশন কল
                increment_user_otp(user_id)
                trigger_otp_listener(assigned_number, c_info['name'], user_id)
            else:
                no_num_msg = (
                    f"⚠️ **NO NUMBER AVAILABLE**\n\n"
                    f"❌ Currently, no stock is available for `{c_info['name']}` right now.\n"
                    f"🔄 *Please try another country or check back soon.*"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔙 Back to Country List", callback_data="back_fb_menu"))
                bot.edit_message_text(no_num_msg, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "back_fb_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, data in FACEBOOK_COUNTRIES.items():
            markup.add(types.InlineKeyboardButton(f"{data['name']} (Traffic: {data['traffic']})", callback_data=f"fb_country_{key}"))
        bot.edit_message_text("📘 **FACEBOOK TARGET COUNTRY SELECTION:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("withdraw_"):
        method = call.data.replace("withdraw_", "").upper()
        bot.answer_callback_query(call.id, f"Selected {method} for payout!")
        
        payout_text = (
            f"📥 **{method} WITHDRAWAL PENDING**\n\n"
            f"• Payout Method: `{method}`\n"
            f"• Minimum Limit: `50 BDT`\n\n"
            f"📌 *To complete your payout, please message admin {ADMIN_CONTACT} with your Telegram ID (`{user_id}`) and your {method} Account Number.*"
        )
        bot.send_message(call.message.chat.id, payout_text, parse_mode="Markdown")

def trigger_otp_listener(phone, service, user_id):
    log_text = (
        f"🔔 **NEW FACEBOOK NUMBER ASSIGNED & LISTENING**\n\n"
        f"📱 **Number:** `{phone}`\n"
        f"🌍 **Service:** {service}\n"
        f"👤 **Target User ID:** `{user_id}`\n\n"
        f"⏳ *Waiting for incoming Facebook SMS/OTP...*"
    )
    try:
        bot.send_message(OTP_CHANNEL_ID, log_text, parse_mode="Markdown")
    except Exception as e:
        print(f"OTP Forwarding Error: {e}")

# বট রান করার লুপ
if __name__ == "__main__":
    print("SPECTRE_FACEBOOK_SMS_BOT is running smoothly...")
    bot.infinity_polling()
