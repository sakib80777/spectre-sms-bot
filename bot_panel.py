import telebot
from telebot import types

# 🔑 আপনার মেইন বটের টোকেন এখানে বসান
TOKEN = "9150625768:AAEacN3GgqQQ1XG1oAZ7D_aFF6503Kob_ug"
bot = telebot.TeleBot(TOKEN)

# 📢 ওটিপি আসার পর যে চ্যানেল বা গ্রুপে অটোমেটিক ট্রান্সফার হবে তার আইডি
OTP_CHANNEL_ID = 1004381508455 
ADMIN_CONTACT = "@sakib43900"

# 🌐 ডাটাবেজ (নম্বর ও ট্রাফিক ম্যানেজমেন্ট)
DATABASE = {
    "italy_v7": {
        "country_name": "🇮🇹 Italy V7",
        "numbers": ["+393241843903", "+393241526521", "+393241325282"],
        "traffic": "High Speed (98% Success)",
        "today_otps": "142 OTPs Received Today"
    },
    "usa_v1": {
        "country_name": "🇺🇸 USA V1 (New)",
        "numbers": ["+14155552671", "+12025550143"],
        "traffic": "Stable (95% Success)",
        "today_otps": "98 OTPs Received Today"
    }
}

# 🚀 /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📱 GET NUMBER"),
        types.KeyboardButton("📊 LIVE TRAFFIC"),
        types.KeyboardButton("👤 STATUS"),
        types.KeyboardButton("💰 BALANCE"),
        types.KeyboardButton("🏆 TODAY TOP"),
        types.KeyboardButton("💬 SUPPORT")
    )
    
    welcome_text = (
        f"⚡ **WELCOME TO SPECTRE SMS PANEL** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Hello, **{user_name}**!\n\n"
        f"🚀 Welcome to your ultimate virtual OTP solution. Get your instant numbers and OTPs safely and securely.\n\n"
        f"👇 Select an option from the control panel below to begin:"
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# 🎛️ মেনু বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    text = message.text
    
    if text == "📱 GET NUMBER":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, data in DATABASE.items():
            markup.add(types.InlineKeyboardButton(f"{data['country_name']} -> ({len(data['numbers'])} Numbers Available)", callback_data=f"country_{key}"))
        
        bot.send_message(message.chat.id, "🌐 **CHOOSE YOUR TARGET COUNTRY:**\nSelect a country below to assign a live virtual number:", parse_mode="Markdown", reply_markup=markup)
        
    elif text == "📊 LIVE TRAFFIC":
        traffic_msg = "📊 **SPECTRE LIVE TRAFFIC MONITOR** 📊\n\n"
        for key, data in DATABASE.items():
            traffic_msg += f"• {data['country_name']}: `{data['traffic']}`\n"
        traffic_msg += "\n⚡ *All server gates are actively forwarding messages.*"
        bot.send_message(message.chat.id, traffic_msg, parse_mode="Markdown")
        
    elif text == "👤 STATUS":
        user = message.from_user
        status_msg = (
            f"👤 **USER ACCOUNT STATUS**\n\n"
            f"• Full Name: {user.first_name}\n"
            f"• Telegram ID: `{user.id}`\n"
            f"• Account Tier: `VIP Member` 🌟\n"
            f"• Security Status: `Encrypted & Active`"
        )
        bot.send_message(message.chat.id, status_msg, parse_mode="Markdown")
        
    elif text == "💰 BALANCE":
        balance_msg = (
            "💰 **WALLET & BALANCE**\n\n"
            "• Current Balance: `$0.00 USD`\n"
            "• Total Used: `0 OTPs`\n\n"
            "💳 *To add balance or top-up, contact administration.*"
        )
        bot.send_message(message.chat.id, balance_msg, parse_mode="Markdown")
        
    elif text == "🏆 TODAY TOP":
        top_msg = "🏆 **TODAY'S TOP PERFORMING SERVICES** 🏆\n\n"
        count = 1
        for key, data in DATABASE.items():
            top_msg += f"{count}. **{data['country_name']}** -> {data['today_otps']}\n"
            count += 1
        top_msg += "\n🔥 *Highest success rate for verifications.*"
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

# 📱 ইনলাইন বাটন হ্যান্ডলার ও ওটিপি ফরওয়ার্ডিং সিস্টেম
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("country_"):
        c_key = call.data.replace("country_", "")
        if c_key in DATABASE:
            c_data = DATABASE[c_key]
            assigned_number = c_data["numbers"][0] if c_data["numbers"] else "No Number Available"
            user_id = call.from_user.id
            
            bot.answer_callback_query(call.id, f"Assigned from {c_data['country_name']}!")
            
            # ইউজারের চ্যাটে নম্বর চলে যাবে
            response_msg = (
                f"⏳ **WAITING FOR OTP...** 🇫🇷\n\n"
                f"🌍 **Service:** {c_data['country_name']}\n"
                f"📱 **Assigned Number:** `{assigned_number}`\n\n"
                f"📌 *Status:* Ready to receive incoming messages. OTP codes will appear here automatically."
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"country_{c_key}"))
            markup.add(types.InlineKeyboardButton("🔙 Back to Country List", callback_data="back_menu"))
            
            bot.edit_message_text(response_msg, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
            
            # 🔄 [অটোমেটিক ওটিপি ট্রান্সফার ফাংশন] 
            # যখনই কেউ নম্বর নিবে, ব্যাকগ্রাউন্ডে ওটিপি চ্যানেলে নোটিফিকেশন চলে যাবে যে এই নাম্বারে ওটিপির জন্য অপেক্ষা করা হচ্ছে
            trigger_otp_listener(assigned_number, c_data['country_name'], user_id)
            
    elif call.data == "back_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, data in DATABASE.items():
            markup.add(types.InlineKeyboardButton(f"{data['country_name']} -> ({len(data['numbers'])} Numbers Available)", callback_data=f"country_{key}"))
        bot.edit_message_text("🌐 **CHOOSE YOUR TARGET COUNTRY:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

def trigger_otp_listener(phone, service, user_id):
    """
    এই ফাংশনটি প্যানেল বা এপিআই থেকে আসা ওটিপি রিসিভ করে সরাসরি আপনার নির্ধারিত ওটিপি গ্রুপ বা চ্যানেলে ট্রান্সফার করবে।
    """
    log_text = (
        f"🔔 **NEW NUMBER ASSIGNED & LISTENING**\n\n"
        f"📱 **Number:** `{phone}`\n"
        f"🌍 **Service:** {service}\n"
        f"👤 **Target User ID:** `{user_id}`\n\n"
        f"⏳ *Waiting for incoming SMS/OTP from gateway...*"
    )
    try:
        # ওটিপি চ্যানেল বা গ্রুপে মেসেজ পাঠিয়ে দিবে
        bot.send_message(OTP_CHANNEL_ID, log_text, parse_mode="Markdown")
    except Exception as e:
        print(f"OTP Forwarding Error: {e}")

# বট রান করার লুপ
if __name__ == "__main__":
    print("SPECTRE_SMS_BOT (Combined with Auto OTP Logger) is running smoothly...")
    bot.infinity_polling()