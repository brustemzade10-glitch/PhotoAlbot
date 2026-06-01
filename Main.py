import os
from threading import Thread
from flask import Flask
import telebot
import requests
import urllib.parse
import io
from telebot import types

# 1. RENDER ÜÇÜN VEB SERVER (PORT) AYARI
app = Flask('')

@app.route('/')
def home():
    return "Bot aktivdir!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

Thread(target=run).start()

# 2. BOTUN AYARLARI VƏ TOKENİ
API_TOKEN = '8648490903:AAF8hFJfZwXvevgqapeMKmdUT8aA8Ynic8g'
bot = telebot.TeleBot(API_TOKEN)

# 3. ÇOXDİLLİ MESAJ LÜĞƏTİ
MESSAGES = {
    'az': {
        'welcome': "Salam! Şəkil yaratmaq üçün ingiliscə təsvir (prompt) göndərin. 🎨",
        'generating': "Şəkliniz hazırlanır, zəhmət olmasa gözləyin... 🎨",
        'error_api': "AI serverindən cavab alınmadı. Bir az sonra yenidən yoxlayın.",
        'error_gen': "Xəta baş verdi. Yenidən cəhd edin."
    },
    'tr': {
        'welcome': "Merhaba! Görsel oluşturmak için İngilizce bir açıklama (prompt) gönderin. 🎨",
        'generating': "Görseliniz hazırlanıyor, lütfen bekleyin... 🎨",
        'error_api': "AI sunucusundan yanıt alınamadı. Lütfen biraz sonra tekrar deneyin.",
        'error_gen': "Bir hata oluştu. Lütfen tekrar deneyin."
    },
    'en': {
        'welcome': "Hello! Send an English description (prompt) to generate an image. 🎨",
        'generating': "Your image is being generated, please wait... 🎨",
        'error_api': "No response from AI server. Please try again later.",
        'error_gen': "An error occurred. Please try again."
    },
    'ru': {
        'welcome': "Привет! Отправьте описание на английском языке для генерации изображения. 🎨",
        'generating': "Ваше изображение генерируется, пожалуйста, подождите... 🎨",
        'error_api': "Нет ответа от AI сервера. Пожалуйста, попробуйте позже.",
        'error_gen': "Произошла ошибка. Пожалуйста, попробуйте еще раз."
    }
}

# İstifadəçilərin dil seçimlərini müvəqqəti saxlamaq üçün lüğət
user_languages = {}

# 4. /START VƏ /HELP ƏMRLƏRİ (DİL SEÇİM DÜYMƏLƏRİ)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_az = types.InlineKeyboardButton("🇦🇿 Azərbaycan", callback_data="lang_az")
    btn_tr = types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
    btn_en = types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    btn_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    
    markup.add(btn_az, btn_tr, btn_en, btn_ru)
    
    bot.send_message(
        chat_id, 
        "Zəhmət olmasa dil seçin / Lütfen dil seçin / Please choose a language / Пожалуйста, выберите язык:", 
        reply_markup=markup
    )

# 5. SEÇİLƏN DİLİN YADDAŞA YAZILMASI
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_choice(call):
    chat_id = call.message.chat.id
    selected_lang = call.data.split('_')[1]  # az, tr, en, ru
    
    user_languages[chat_id] = selected_lang
    welcome_text = MESSAGES[selected_lang]['welcome']
    
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=welcome_text)

# 6. SURƏT YARATMA (POLLINATIONS AI INTEGRATION)
@bot.message_handler(func=lambda message: True)
def generate_image(message):
    chat_id = message.chat.id
    prompt = message.text
    
    # İstifadəçi dil seçməyibsə standart olaraq 'en' qəbul edilir
    lang = user_languages.get(chat_id, 'en')
    
    # İstifadəçinin öz dilində "Gözləyin" mesajı verilir
    waiting_msg = bot.reply_to(message, MESSAGES[lang]['generating'])
    
    try:
        # Mətni təmizləyirik və URL formatına salırıq
        encoded_prompt = urllib.parse.quote(prompt.strip())
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        # Şəkli internetdən Python yaddaşına yükləyirik
        response = requests.get(image_url, timeout=30)
        
        if response.status_code == 200:
            # Şəkli bayt (byte) formatında Telegram-a fayl kimi göndəririk
            photo = io.BytesIO(response.content)
            photo.name = 'ai_image.jpg'
            
            bot.send_photo(chat_id, photo, caption=f"🎬 Prompt: {prompt}")
            bot.delete_message(chat_id, waiting_msg.message_id)
        else:
            bot.edit_message_text(MESSAGES[lang]['error_api'], chat_id, waiting_msg.message_id)
            
    except Exception as e:
        print(f"XƏTA: {e}")
        bot.edit_message_text(f"{MESSAGES[lang]['error_gen']} ({str(e)[:20]})", chat_id, waiting_msg.message_id)

# Botu işə salırıq
bot.infinity_polling()
                                  
