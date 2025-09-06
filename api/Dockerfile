FROM python:3.11-slim

# Установка системных зависимостей для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя app
RUN useradd --create-home --shell /bin/bash app

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей как root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Playwright и браузеров как root
RUN playwright install chromium
RUN playwright install-deps chromium

# Копирование исходного кода
COPY . .

# Изменение владельца файлов
RUN chown -R app:app /app

# Переменные окружения
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Переключение на пользователя app
USER app

# Экспорт порта
EXPOSE 8000

# Команда запуска с поддержкой переменной PORT от Railway
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
