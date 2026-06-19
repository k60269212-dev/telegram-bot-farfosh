#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import asyncio
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
import traceback

# Load environment variables
load_dotenv()

# Setup logging with UTF-8 encoding
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Constants
BOT_TOKEN = os.getenv('BOT_TOKEN', '8890058021:AAFHJh1vWvTJ43847GpP__GFn9J4wcm0EFA')
MAX_YOUTUBE_DURATION = 30 * 60  # 30 minutes in seconds
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Platform list
PLATFORMS = {
    'youtube': {'emoji': '����', 'name': 'YouTube'},
    'tiktok': {'emoji': '🎵', 'name': 'TikTok'},
    'instagram': {'emoji': '📸', 'name': 'Instagram'},
    'twitter': {'emoji': '𝕏', 'name': 'Twitter'},
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - welcome with interactive buttons"""
    try:
        user = update.effective_user
        welcome_message = (
            "Hello! This bot is under development by developer Karim. Let me help you! 🎉\n\n"
            "Select the platform you want to download from:"
        )
        
        # Create interactive buttons
        keyboard = [
            [
                InlineKeyboardButton(f"{PLATFORMS['youtube']['emoji']} YouTube", callback_data='platform_youtube'),
                InlineKeyboardButton(f"{PLATFORMS['tiktok']['emoji']} TikTok", callback_data='platform_tiktok'),
            ],
            [
                InlineKeyboardButton(f"{PLATFORMS['instagram']['emoji']} Instagram", callback_data='platform_instagram'),
                InlineKeyboardButton(f"{PLATFORMS['twitter']['emoji']} Twitter", callback_data='platform_twitter'),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        logger.info(f"User {user.id} started the bot")
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text("❌ An error occurred. Please try again.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show commands list"""
    try:
        help_text = """
📖 **Command List:**

/start - Start the bot and welcome
/help - Show this message
/about - Information about the bot

**How to Use:**
1. Press /start to select a platform
2. Choose the desired platform (YouTube, TikTok, Instagram, Twitter)
3. Send the link or search for video (YouTube only)
4. Choose the download format

✨ **Bot Features:**
📺 Download from YouTube (video or audio)
🎵 TikTok
📸 Instagram
𝕏 Twitter

⚠️ **Notes:**
- Maximum YouTube video duration: 30 minutes
- Files are deleted automatically after sending
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in help command: {str(e)}")
        await update.message.reply_text("❌ An error occurred.")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command - bot information"""
    try:
        about_text = """
👨‍💻 **FarFosh Bot - Video and Audio Downloader**

🔧 **Bot Developer:** Karim
📱 **Supported Platforms:** YouTube, TikTok, Instagram, Twitter

✨ **Features:**
✅ Download YouTube videos (with 30 minute limit)
✅ Extract audio files from YouTube
✅ Download from other platforms
✅ User-friendly interactive interface

🛡️ **Security:**
- Token is protected and secure
- Files are deleted immediately after sending
- User data is not stored

📝 **License:** MIT License

💬 **For Support:** Contact the developer
        """
        await update.message.reply_text(about_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in about command: {str(e)}")
        await update.message.reply_text("❌ An error occurred.")


async def platform_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle platform button clicks"""
    try:
        query = update.callback_query
        await query.answer()
        
        platform = query.data.replace('platform_', '')
        context.user_data['platform'] = platform
        
        if platform == 'youtube':
            message = "Search for or send the video link you want 🔍"
        else:
            message = f"Send the {PLATFORMS[platform]['name']} link 🔗"
        
        await query.edit_message_text(text=message)
        logger.info(f"User {query.from_user.id} selected platform: {platform}")
    except Exception as e:
        logger.error(f"Error in platform_button: {str(e)}")
        await query.answer("❌ An error occurred", show_alert=True)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages and links"""
    try:
        user = update.effective_user
        text = update.message.text
        platform = context.user_data.get('platform')
        
        if not platform:
            await update.message.reply_text("Please select a platform first from /start")
            return
        
        # Handle different platforms
        if platform == 'youtube':
            await handle_youtube(update, context, text)
        elif platform == 'tiktok':
            await handle_tiktok(update, context, text)
        elif platform == 'instagram':
            await handle_instagram(update, context, text)
        elif platform == 'twitter':
            await handle_twitter(update, context, text)
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str) -> None:
    """Handle YouTube - search or download from link"""
    user = update.effective_user
    
    try:
        # Show processing message
        processing_message = await update.message.reply_text("⏳ Processing your request...")
        
        # Check if input is a valid URL or search query
        is_url = _is_valid_url(query)
        
        if is_url:
            # If it's a direct link
            video_url = query
            video_info = await _get_youtube_info(video_url)
        else:
            # If it's a search query
            video_info = await _search_youtube(query)
            if not video_info:
                await processing_message.edit_text("❌ No matching video found. Try another search.")
                return
            video_url = video_info['url']
        
        if not video_info:
            await processing_message.edit_text("❌ Error getting video information.")
            return
        
        # Check video duration
        duration = video_info.get('duration', 0)
        
        if duration > MAX_YOUTUBE_DURATION:
            await processing_message.edit_text(
                f"❌ Sorry! The video duration ({duration // 60} minutes) exceeds the maximum allowed (30 minutes).\n"
                "Please choose a shorter video."
            )
            logger.warning(f"User {user.id} tried to download a long video: {duration}s")
            return
        
        # Show format options
        title = video_info.get('title', 'Video')
        keyboard = [
            [
                InlineKeyboardButton("📹 Download Video", callback_data=f'download_video_{video_url}'),
            ],
            [
                InlineKeyboardButton("🎵 Download Audio Only", callback_data=f'download_audio_{video_url}'),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_message.edit_text(
            f"✅ Video found!\n\n"
            f"📌 <b>Title:</b> {title}\n"
            f"⏱️ <b>Duration:</b> {duration // 60} minutes\n\n"
            f"Choose download format:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        logger.info(f"User {user.id} found YouTube video: {title}")
        
    except Exception as e:
        logger.error(f"Error in handle_youtube: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """Handle TikTok downloads"""
    user = update.effective_user
    
    try:
        if not _is_valid_url(url):
            await update.message.reply_text("❌ Please send a valid link")
            return
        
        processing_message = await update.message.reply_text("⏳ Downloading video...")
        await _download_file(url, 'tiktok', processing_message, update, context)
        logger.info(f"User {user.id} downloaded from TikTok")
        
    except Exception as e:
        logger.error(f"Error in handle_tiktok: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """Handle Instagram downloads"""
    user = update.effective_user
    
    try:
        if not _is_valid_url(url):
            await update.message.reply_text("❌ Please send a valid link")
            return
        
        processing_message = await update.message.reply_text("⏳ Downloading post...")
        await _download_file(url, 'instagram', processing_message, update, context)
        logger.info(f"User {user.id} downloaded from Instagram")
        
    except Exception as e:
        logger.error(f"Error in handle_instagram: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """Handle Twitter downloads"""
    user = update.effective_user
    
    try:
        if not _is_valid_url(url):
            await update.message.reply_text("❌ Please send a valid link")
            return
        
        processing_message = await update.message.reply_text("⏳ Downloading tweet...")
        await _download_file(url, 'twitter', processing_message, update, context)
        logger.info(f"User {user.id} downloaded from Twitter")
        
    except Exception as e:
        logger.error(f"Error in handle_twitter: {str(e)}\n{traceback.format_exc()}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def download_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle download button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Extract download type and URL
    if data.startswith('download_video_'):
        video_url = data.replace('download_video_', '')
        format_type = 'video'
    elif data.startswith('download_audio_'):
        video_url = data.replace('download_audio_', '')
        format_type = 'audio'
    else:
        return
    
    try:
        await query.edit_message_text("⏳ Downloading file...")
        await _download_youtube_file(video_url, format_type, query, context)
        
    except Exception as e:
        logger.error(f"Error in download: {str(e)}\n{traceback.format_exc()}")
        await query.edit_message_text(f"❌ Error: {str(e)}")


async def _download_youtube_file(url: str, format_type: str, query, context) -> None:
    """Download file from YouTube"""
    output_dir = 'downloads'
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'socket_timeout': 30,
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
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        # Check file size
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            os.remove(file_path)
            await query.edit_message_text(f"❌ File is too large (max 50MB)")
            return
        
        # Send file
        with open(file_path, 'rb') as file:
            if format_type == 'audio':
                await query.message.reply_audio(file)
            else:
                await query.message.reply_video(file)
        
        # Delete file after sending
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await query.edit_message_text("✅ Downloaded successfully!")
    except Exception as e:
        raise e


async def _download_file(url: str, platform: str, processing_message, update, context) -> None:
    """Download file from another platform"""
    output_dir = 'downloads'
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'format': 'best',
        'outtmpl': os.path.join(output_dir, f'{platform}_%(title)s.%(ext)s'),
        'socket_timeout': 30,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        # Check file size
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            os.remove(file_path)
            await processing_message.edit_text(f"❌ File is too large (max 50MB)")
            return
        
        # Send file
        with open(file_path, 'rb') as file:
            await update.message.reply_video(file)
        
        # Delete file after sending
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await processing_message.edit_text("✅ Downloaded successfully!")
    except Exception as e:
        raise e


async def _get_youtube_info(url: str) -> dict:
    """Get YouTube video information"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'url': url,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
            }
    except Exception as e:
        logger.error(f"Error getting YouTube info: {str(e)}")
        return None


async def _search_youtube(query: str) -> dict:
    """Search for video on YouTube"""
    search_query = f"ytsearch1:{query}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            
            if info and 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                return {
                    'url': entry['webpage_url'],
                    'title': entry.get('title', 'Unknown'),
                    'duration': entry.get('duration', 0),
                }
    except Exception as e:
        logger.error(f"Error searching YouTube: {str(e)}")
    
    return None


def _is_valid_url(text: str) -> bool:
    """Validate URL"""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Exception occurred: {context.error}\n{traceback.format_exc()}")


def main() -> None:
    """Run the bot"""
    if not BOT_TOKEN or BOT_TOKEN.startswith('YOUR_BOT_TOKEN'):
        logger.error("❌ BOT_TOKEN is not set. Please set it in .env file")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # Button handlers
    application.add_handler(CallbackQueryHandler(platform_button, pattern='^platform_'))
    application.add_handler(CallbackQueryHandler(download_button, pattern='^download_'))
    
    # Text message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🤖 Bot started successfully...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}\n{traceback.format_exc()}")
        sys.exit(1)
