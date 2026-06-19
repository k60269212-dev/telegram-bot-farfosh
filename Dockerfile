FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg and required libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install Python libraries with error handling
RUN pip install --no-cache-dir -r requirements.txt --retries 3 || \
    (pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt)

# Copy project files
COPY . .

# Create downloads directory with proper permissions
RUN mkdir -p downloads && chmod 755 downloads

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('bot.py') else 1)" || exit 1

# Run the bot
CMD ["python", "bot.py"]
