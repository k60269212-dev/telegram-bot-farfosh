# FarFosh Bot - Video Downloader 🎬

A powerful Telegram bot for downloading videos and audio from multiple platforms.

## Features ✨

- 📺 **YouTube**: Download videos or extract audio (MP3)
- 🎵 **TikTok**: Download TikTok videos
- 📸 **Instagram**: Download Instagram posts and reels
- 𝕏 **Twitter**: Download Twitter videos
- 🎯 Smart search for YouTube videos
- ⚡ Fast and efficient downloads
- 🛡️ Secure token handling
- 🗑️ Automatic file cleanup

## Requirements 📋

- Python 3.11+
- FFmpeg
- Docker (optional)
- Valid Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## Installation 🚀

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/k60269212-dev/telegram-bot-farfosh.git
cd telegram-bot-farfosh
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN
```

5. Run the bot:
```bash
python bot.py
```

### Option 2: Docker Installation

1. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f telegram-bot
```

4. Stop the bot:
```bash
docker-compose down
```

## Configuration ⚙️

Edit `.env` file to configure:

```bash
# Required: Your bot token from BotFather
BOT_TOKEN=YOUR_TOKEN_HERE

# Optional: Maximum YouTube video duration in minutes
MAX_YOUTUBE_MINUTES=30

# Optional: Logging level
LOG_LEVEL=INFO
```

## Usage 💡

1. Start the bot: `/start`
2. Select your platform
3. Send video link or search query (YouTube only)
4. Choose download format
5. Wait for the download to complete

## Bot Commands 🎮

- `/start` - Start bot and select platform
- `/help` - Show help message
- `/about` - Show bot information

## Troubleshooting 🔧

### Bot won't start
- Check if BOT_TOKEN is correct in `.env`
- Ensure BOT_TOKEN has no extra spaces
- Verify internet connection

### Download fails
- Check if the link is valid
- Ensure FFmpeg is installed
- For YouTube: video should be less than 30 minutes
- Check file size (max 50MB)

### Docker issues
- Rebuild image: `docker-compose build --no-cache`
- Check logs: `docker-compose logs telegram-bot`
- Ensure Docker and Docker Compose are installed

## Supported Platforms 🌐

| Platform | Status | Notes |
|----------|--------|-------|
| YouTube | ✅ | Supports search and direct links |
| TikTok | ✅ | Requires valid link |
| Instagram | ✅ | Supports posts and reels |
| Twitter | ✅ | Requires valid link |

## Limitations ⚠️

- YouTube videos limited to 30 minutes
- Maximum file size: 50MB
- Automatic file deletion after sending
- Requires stable internet connection

## Performance 📊

- Memory limit: 512MB
- CPU limit: 1 core
- Average download time: 10-30 seconds

## Security 🔒

- Bot token is kept secure in `.env` file
- User data is not stored
- Files are deleted automatically
- No logging of user information

## Developer 👨‍💻

**Karim** - [@k60269212-dev](https://github.com/k60269212-dev)

## License 📝

MIT License - Feel free to use and modify

## Support 💬

For issues or questions:
1. Check existing [GitHub Issues](https://github.com/k60269212-dev/telegram-bot-farfosh/issues)
2. Create a new issue if needed
3. Contact the developer

## Changelog 📜

### v1.1 (Latest)
- ✅ Fixed Docker build errors
- ✅ Updated dependencies
- ✅ Improved error handling
- ✅ Added health checks
- ✅ Better logging
- ✅ Code cleanup and optimization

### v1.0
- Initial release

---

**Made with ❤️ by Karim**
