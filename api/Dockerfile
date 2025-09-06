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
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Playwright и браузеров как root
# Пропускаем playwright install-deps, так как на Debian trixie пакеты недоступны в fallback
RUN playwright install chromium || true

# Копирование исходного кода из папки api
COPY api/ .

# Копирование дополнительных папок проекта
COPY src/ /app/src/
COPY config/ /app/config/

# Изменение владельца файлов
RUN chown -R app:app /app

# Проверка что main.py доступен и синтаксически корректен
RUN ls -la /app && echo "Files in /app:"
RUN python -c "import sys; print('Python path:', sys.path)"
RUN test -f main.py && echo "✅ main.py found" || echo "❌ main.py not found"
RUN python -m py_compile main.py
RUN python -c "import main; print('✅ main.py imported successfully')"

# Переменные окружения
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Остаемся как root для Railway (некоторые платформы требуют root)
# USER app

# Экспорт порта
EXPOSE 8000

# Команда запуска с поддержкой переменной PORT от Railway  
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
