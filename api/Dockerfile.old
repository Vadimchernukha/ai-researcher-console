FROM python:3.11-slim

# Cache bust - updated 2024-01-15
# Установка только базовых зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Проверка установки uvicorn
RUN which uvicorn || echo "uvicorn not found in PATH"
RUN python -c "import uvicorn; print('uvicorn imported successfully')"

# Установка Playwright браузеров и зависимостей
RUN playwright install chromium
RUN playwright install-deps chromium

# Копирование исходного кода
COPY . .

# Создание пользователя для безопасности (но не переключаемся на него)
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Переменные окружения
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/home/app/.cache/ms-playwright

# Экспорт порта
EXPOSE 8000

# Команда запуска
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]