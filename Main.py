import telebot
import requests
import urllib.parse
import io

# BotFather-dan aldığın tokeni bura yaz
API_TOKEN = '8648490903:AAFdxx_iYYNXWw5qQsjgD1iQfCvu8jAeQEU'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salam! Mən şəkil yaradan süni intellekt botuyam. Mənə ingiliscə bir təsvir yaz və mən onun şəklini çəkim.")

@bot.message_handler(func=lambda message: True)
def generate_image(message):
    prompt = message.text
    waiting_msg = bot.reply_to(message, "Şəkil hazırlanır, lütfən gözləyin... 🎨")
    
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
            
            bot.send_photo(message.chat.id, photo, caption=f"🎬 Sizin prompt: {prompt}")
            bot.delete_message(message.chat.id, waiting_msg.message_id)
        else:
            bot.edit_message_text("AI serverindən cavab alınmadı. Bir az sonra yenidən yoxlayın.", message.chat.id, waiting_msg.message_id)
            
    except Exception as e:
        # Konsolda dəqiq xətanın nə olduğunu görmək üçün:
        print(f"XƏTA: {e}")
        bot.edit_message_text(f"Xəta baş verdi: {str(e)[:50]}", message.chat.id, waiting_msg.message_id)

# Botu işə salırıq
bot.infinity_polling()
      
