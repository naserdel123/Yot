import re
from config import BANNED_WORDS

def contains_banned_words(text: str) -> bool:
    """التحقق من وجود كلمات ممنوعة"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # التحقق من الكلمات الممنوعة
    for word in BANNED_WORDS:
        # استخدام regex للبحث عن الكلمة ككلمة منفصلة
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    # التحقق من الروابط المشبوهة (اختياري)
    suspicious_patterns = [
        r't\.me/\w+',  # روابط تلجرام
        r'bit\.ly/\w+',  # روابط مختصرة
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            # يمكن إضافة منطق إضافي هنا
            pass
    
    return False

def get_warning_message(user_name: str) -> str:
    """رسالة التحذير"""
    return f"""
⚠️ **تم حذف رسالة مخالفة**

عذراً {user_name}، 
تم حذف رسالتك لاحتوائها على محتوى مخالف.

📜 **يرجى الالتزام بقوانين المجموعة**
    """
    