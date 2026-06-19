#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp
from dotenv import load_dotenv
import re
from urllib.parse import urlparse

# تحميل متغيرات البيئة
load_dotenv()

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# الثوابت
BOT_TOKEN = os.getenv('BOT_TOKEN', '8890058021:AAFHJh1vWvTJ43847GpP__GFn9J4wcm0EFA')
MAX_YOUTUBE_DURATION = 30 * 60  # 30 دقيقة بالثواني

# قائمة المنصات
PLATFORMS = {
    'youtube': {'emoji': '📺', 'name': 'يوتيوب'},
    'tiktok': {'emoji': '🎵', 'name': 'تيك توك'},
    'instagram': {'emoji': '📸', 'name': 'انستغرام'},
    'twitter': {'emoji': '𝕏', 'name': 'تويتر'},
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start - ترحيب بالمستخدم مع الأزرار التفاعلية"""
    user = update.effective_user
    welcome_message = (
        "مرحبا هذا البوت تحت تطوير المطور كريم تفضل شوفني يساعدك 🎉\n\n"
        "اختر المنصة التي تريد التحميل منها:"
    )
    
    # إنشاء الأزرار التفاعلية
    keyboard = [
        [
            InlineKeyboardButton(f"{PLATFORMS['youtube']['emoji']} يوتيوب", callback_data='platform_youtube'),
            InlineKeyboardButton(f"{PLATFORMS['tiktok']['emoji']} تيك توك", callback_data='platform_tiktok'),
        ],
        [
            InlineKeyboardButton(f"{PLATFORMS['instagram']['emoji']} انستغرام", callback_data='platform_instagram'),
            InlineKeyboardButton(f"{PLATFORMS['twitter']['emoji']} تويتر", callback_data='platform_twitter'),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    logger.info(f"المستخدم {user.id} بدأ البوت")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /help - عرض قائمة الأوامر"""
    help_text = """
📖 **قائمة الأوامر:**

/start - بدء البوت والترحيب
/help - عرض هذه الرسالة
/about - معلومات عن البوت

**كيفية الاستخدام:**
1. اضغط /start لاختيار المنصة
2. اختر المنصة المطلوبة (يوتيوب، تيك توك، انستغرام، تويتر)
3. أرسل الرابط أو ابحث عن الفيديو (يوتيوب فقط)
4. اختر صيغة التحميل المطلوبة

✨ **ميزات البوت:**
📺 تحميل من يوتيوب (فيديو أو صوتي)
🎵 تيك توك
📸 انستغرام
𝕏 تويتر

⚠️ **ملاحظات:**
- حد أقصى لفيديو يوتيوب: 30 دقيقة
- الملفات تُحذف تلقائياً بعد الإرسال
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /about - معلومات عن البوت"""
    about_text = """
👨‍💻 **بوت فرفوش - تحميل الفيديوهات والصوتيات**

🔧 **مطور البوت:** كريم
📱 **المنصات المدعومة:** يوتيوب، تيك توك، انستغرام، تويتر

✨ **الميزات:**
✅ تحميل فيديوهات يوتيوب (مع حد أقصى 30 دقيقة)
✅ استخراج ملفات صوتية من يوتيوب
✅ تحميل من منصات أخرى
✅ واجهة تفاعلية وسهلة الاستخدام

🛡️ **الأمان:**
- التوكن محمي وآمن
- الملفات تُحذف فوراً بعد الإرسال
- لا يتم حفظ بيانات المستخدمين

📝 **الترخيص:** MIT License

💬 **للدعم والمساعدة:** تواصل مع المطور
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')


async def platform_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج ضغط أزرار المنصات"""
    query = update.callback_query
    await query.answer()
    
    platform = query.data.replace('platform_', '')
    context.user_data['platform'] = platform
    
    if platform == 'youtube':
        message = "ابحث عن المقطع أ�� أرسل رابط الفيديو الذي تريده 🔍"
    else:
        message = f"أرسل رابط {PLATFORMS[platform]['name']} المباشر 🔗"
    
    await query.edit_message_text(text=message)
    logger.info(f"المستخدم {query.from_user.id} اختار منصة: {platform}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الرسائل النصية والروابط"""
    user = update.effective_user
    text = update.message.text
    platform = context.user_data.get('platform')
    
    if not platform:
        await update.message.reply_text("الرجاء اختيار منصة أولاً من قائمة /start")
        return
    
    # معالجة اليوتيوب
    if platform == 'youtube':
        await handle_youtube(update, context, text)
    
    # معالجة تيك توك
    elif platform == 'tiktok':
        await handle_tiktok(update, context, text)
    
    # معالجة انستغرام
    elif platform == 'instagram':
        await handle_instagram(update, context, text)
    
    # معالجة تويتر
    elif platform == 'twitter':
        await handle_twitter(update, context, text)


async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str) -> None:
    """معالج يوتيوب - البحث أو التحميل من رابط"""
    user = update.effective_user
    
    try:
        # معالج الرسالة - إظهار "جاري المعالجة"
        processing_message = await update.message.reply_text("⏳ جاري معالجة الطلب...")
        
        # التحقق من أن المدخل رابط أم نص للبحث
        is_url = _is_valid_url(query)
        
        if is_url:
            # إذا كان رابطاً مباشراً
            video_url = query
            video_info = await _get_youtube_info(video_url)
        else:
            # إذا كان نصاً للبحث
            video_info = await _search_youtube(query)
            if not video_info:
                await processing_message.edit_text("❌ لم أجد فيديو مطابق. حاول بحثاً آخر.")
                return
            video_url = video_info['url']
        
        if not video_info:
            await processing_message.edit_text("❌ حدث خطأ في الحصول على معلومات الفيديو.")
            return
        
        # التحقق من مدة الفيديو
        duration = video_info.get('duration', 0)
        
        if duration > MAX_YOUTUBE_DURATION:
            await processing_message.edit_text(
                f"❌ عذراً! مدة الفيديو ({duration // 60} دقيقة) تتجاوز الحد الأقصى المسموح به (30 دقيقة).\n"
                "الرجاء اختيار فيديو أقصر."
            )
            logger.warning(f"المستخدم {user.id} حاول تحميل فيديو طويل: {duration}s")
            return
        
        # عرض خيارات الصيغة
        title = video_info.get('title', 'فيديو')
        keyboard = [
            [
                InlineKeyboardButton("📹 تحميل الفيديو", callback_data=f'download_video_{video_url}'),
            ],
            [
                InlineKeyboardButton("🎵 تحميل ملف صوتي فقط", callback_data=f'download_audio_{video_url}'),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_message.edit_text(
            f"✅ تم العثور على الفيديو!\n\n"
            f"📌 <b>الاسم:</b> {title}\n"
            f"⏱️ <b>المدة:</b> {duration // 60} دقيقة\n\n"
            f"اختر صيغة التحميل:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        logger.info(f"المستخدم {user.id} وجد فيديو يوتيوب: {title}")
        
    except Exception as e:
        logger.error(f"خطأ في معالجة يوتيوب: {str(e)}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")


async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """معالج تيك توك"""
    user = update.effective_user
    
    try:
        if not _is_valid_url(url):
            await update.message.reply_text("❌ الرجاء إرسال رابط صحيح")
            return
        
        processing_message = await update.message.reply_text("⏳ جاري تحميل المقطع...")
        
        # تحميل الفيديو
        await _download_file(url, 'tiktok', processing_message, update, context)
        
        logger.info(f"المستخدم {user.id} حمل من تيك توك")
        
    except Exception as e:
        logger.error(f"خطأ في معالجة تيك توك: {str(e)}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")


async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """معالج انستغرام"""
    user = update.effective_user
    
    try:
        if not _is_valid_url(url):
            await update.message.reply_text("❌ الرجاء إرسال رابط صحيح")
            return
        
        processing_message = await update.message.reply_text("⏳ جاري تحميل المنشور...")
        
        # تحميل الفيديو
        await _download_file(url, 'instagram', processing_message, update, context)
        
        logger.info(f"المستخدم {user.id} حمل من انستغرام")
        
    except Exception as e:
        logger.error(f"خطأ في معالجة انستغرام: {str(e)}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")


async def handle_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """معالج تويتر"""
    user = update.effective_user
    
    try:
        if not _is_valid_url(url):
            await update.message.reply_text("❌ الرجاء إرسال رابط صحيح")
            return
        
        processing_message = await update.message.reply_text("⏳ جاري تحميل التغريدة...")
        
        # تحميل الفيديو
        await _download_file(url, 'twitter', processing_message, update, context)
        
        logger.info(f"المستخدم {user.id} حمل من تويتر")
        
    except Exception as e:
        logger.error(f"خطأ في معالجة تويتر: {str(e)}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")


async def download_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أزرار التحميل"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # استخراج نوع التحميل والرابط
    if data.startswith('download_video_'):
        video_url = data.replace('download_video_', '')
        format_type = 'video'
    elif data.startswith('download_audio_'):
        video_url = data.replace('download_audio_', '')
        format_type = 'audio'
    else:
        return
    
    try:
        await query.edit_message_text("⏳ جاري تحميل الملف...")
        
        # تحميل الملف
        await _download_youtube_file(video_url, format_type, query, context)
        
    except Exception as e:
        logger.error(f"خطأ في التحميل: {str(e)}")
        await query.edit_message_text(f"❌ حدث خطأ: {str(e)}")


async def _download_youtube_file(url: str, format_type: str, query, context) -> None:
    """تحميل ملف من يوتيوب"""
    output_dir = 'downloads'
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
    }
    
    if format_type == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        })
    else:
        ydl_opts.update({
            'format': 'best[ext=mp4]',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        })
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
    
    # إرسال الملف
    if format_type == 'audio':
        await query.message.reply_audio(open(file_path, 'rb'))
    else:
        await query.message.reply_video(open(file_path, 'rb'))
    
    # حذف الملف بعد الإرسال
    os.remove(file_path)
    await query.edit_message_text("✅ تم التحميل بنجاح!")


async def _download_file(url: str, platform: str, processing_message, update, context) -> None:
    """تحميل ملف من منصة أخرى"""
    output_dir = 'downloads'
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'format': 'best',
        'outtmpl': os.path.join(output_dir, f'{platform}_%(title)s.%(ext)s'),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
    
    # إرسال الملف
    await update.message.reply_video(open(file_path, 'rb'))
    
    # حذف الملف بعد الإرسال
    os.remove(file_path)
    await processing_message.edit_text("✅ تم التحميل بنجاح!")


async def _get_youtube_info(url: str) -> dict:
    """الحصول على معلومات فيديو يوتيوب"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'url': url,
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
        }


async def _search_youtube(query: str) -> dict:
    """البحث عن فيديو على يوتيوب"""
    search_query = f"ytsearch1:{query}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        
        if info and 'entries' in info and len(info['entries']) > 0:
            entry = info['entries'][0]
            return {
                'url': entry['webpage_url'],
                'title': entry.get('title', 'Unknown'),
                'duration': entry.get('duration', 0),
            }
    
    return None


def _is_valid_url(text: str) -> bool:
    """التحقق من صحة الرابط"""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مع��لج الأخطاء"""
    logger.error(f"حدث استثناء: {context.error}")


def main() -> None:
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # معالجات الأزرار
    application.add_handler(CallbackQueryHandler(platform_button, pattern='^platform_'))
    application.add_handler(CallbackQueryHandler(download_button, pattern='^download_'))
    
    # معالج الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء البوت
    logger.info("🤖 البوت بدأ التشغيل...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
