import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from config import BOT_TOKEN, BANNED_WORDS
from utils.youtube import search_youtube
from utils.filters import contains_banned_words, get_warning_message

# تفعيل التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
SEARCHING = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب مع زر الإضافة للمجموعة"""
    user = update.effective_user
    
    welcome_text = f"""
🎵 **أهلاً وسهلاً {user.first_name}!** 🎵

أنا بوت موسيقى متكامل! 🤖

**مميزاتي:**
• 🔍 البحث عن الأغاني في يوتيوب
• 🛡️ حذف الرسائل المخالفة تلقائياً
• 👤 معرفة معلومات المستخدمين
• ⚡️ سرعة في الاستجابة

**للاستخدام:** أضفني إلى مجموعتك واجعلني مشرفاً!
    """
    
    # زر إضافة البوت للمجموعة
    keyboard = [
        [InlineKeyboardButton(
            "➕ أضفني إلى مجموعتك", 
            url=f"https://t.me/{context.bot.username}?startgroup=true"
        )],
        [InlineKeyboardButton(
            "📢 قناة البوت", 
            url="https://t.me/your_channel"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البحث عن أغنية"""
    if not context.args:
        await update.message.reply_text(
            "❌ **طريقة الاستخدام:**\n"
            "`/بحث اسم الأغنية`\n\n"
            "مثال: `/بحث محمد عبده يا غايب`",
            parse_mode='Markdown'
        )
        return
    
    query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 جاري البحث عن: *{query}*...", parse_mode='Markdown')
    
    try:
        results = await search_youtube(query)
        
        if not results:
            await update.message.reply_text("❌ لم أجد نتائج للبحث")
            return
        
        # عرض أول 5 نتائج
        for i, video in enumerate(results[:5], 1):
            keyboard = [[InlineKeyboardButton(
                "▶️ تشغيل في يوتيوب", 
                url=f"https://youtube.com/watch?v={video['id']}"
            )]]
            
            message = (
                f"*{i}. {video['title']}*\n"
                f"👤 {video['channel']}\n"
                f"⏱ {video['duration']}\n"
                f"👁 {video['views']:,} مشاهدة"
            )
            
            await update.message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error searching: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء البحث")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الحصول على معرف المستخدم"""
    # إذا كان الرد على رسالة
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_chat = update.message.reply_to_message.chat
        
        info_text = f"""
🆔 **معلومات المستخدم:**

👤 **الاسم:** `{target_user.first_name}`
📝 **اليوزر:** @{target_user.username if target_user.username else 'لا يوجد'}
🆔 **الآيدي:** `{target_user.id}`
🤖 **بوت؟** {'نعم' if target_user.is_bot else 'لا'}

💬 **في المجموعة:**
📛 **اسم المجموعة:** {target_chat.title}
🆔 **آيدي المجموعة:** `{target_chat.id}`
        """
    else:
        # معلومات المرسل
        user = update.effective_user
        chat = update.effective_chat
        
        info_text = f"""
🆔 **معلوماتك:**

👤 **الاسم:** `{user.first_name}`
📝 **اليوزر:** @{user.username if user.username else 'لا يوجد'}
🆔 **آيديك:** `{user.id}`
🤖 **بوت؟** {'نعم' if user.is_bot else 'لا'}

💬 **المحادثة الحالية:**
📛 **النوع:** {chat.type}
🆔 **الآيدي:** `{chat.id}`
        """
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def moderate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الإشراف التلقائي على الرسائل"""
    message = update.message
    user = message.from_user
    chat = message.chat
    
    # التحقق من الكلمات الممنوعة
    if message.text and contains_banned_words(message.text):
        try:
            # حذف الرسالة
            await message.delete()
            
            # طرد المستخدم (اختياري - يمكن تغييره إلى تحذير فقط)
            # await chat.ban_member(user.id)  # للحظر الدائم
            # await chat.restrict_member(user.id, until_date=int(time.time() + 3600))  # لتقييد لساعة
            
            warning = get_warning_message(user.first_name)
            warn_msg = await context.bot.send_message(
                chat.id,
                warning,
                parse_mode='Markdown'
            )
            
            # حذف رسالة التحذير بعد 10 ثواني
            await asyncio.sleep(10)
            await warn_msg.delete()
            
            logger.info(f"Deleted banned message from {user.id} in {chat.id}")
            
        except Exception as e:
            logger.error(f"Moderation error: {e}")
    
    # التحقق من الروابط المشبوهة (اختياري)
    elif message.entities:
        for entity in message.entities:
            if entity.type in ['url', 'text_link']:
                # يمكن إضافة فحص الروابط هنا
                pass

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_to_group':
        await query.edit_message_text(
            "✅ اضغط على الرابط أعلاه لإضافتي إلى مجموعتك!"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأخطاء"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("بحث", search_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("id", get_id))
    application.add_handler(CommandHandler("ايدي", get_id))
    
    # معالجة الأزرار
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # الإشراف على الرسائل في المجموعات
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            moderate_message
        )
    )
    
    # معالجة الأخطاء
    application.add_error_handler(error_handler)
    
    # تشغيل البوت
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
    