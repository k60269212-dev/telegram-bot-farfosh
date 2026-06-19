FROM python:3.11-slim

WORKDIR /app

# تثبيت ffmpeg والمكتبات المطلوبة
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# نسخ requirements
COPY requirements.txt .

# تثبيت مكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# إنشاء مجلد downloads
RUN mkdir -p downloads

# تشغيل البوت
CMD ["python", "bot.py"]
