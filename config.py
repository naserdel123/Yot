import os
from dotenv import load_dotenv

load_dotenv()

# توكن البوت من @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', 'ضع_توكن_البوت_هنا')

# API اليوتيوب من Google Cloud Console
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'ضع_مفتاح_API_هنا')

# قائمة الكلمات الممنوعة (يمكن توسيعها)
BANNED_WORDS = {
    'سب', 'قذف', 'حرام', 'كفر', 
    'stupid', 'idiot', 'bad_word',
    # أضف المزيد حسب احتياجك
}

# معرفات المشرفين (اختياري)
ADMIN_IDS = set()
