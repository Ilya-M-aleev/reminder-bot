# -*- coding: utf-8 -*-
import asyncio
import os
import logging
import re
import random
from datetime import timedelta

from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
APP_URL   = os.environ["APP_URL"]  # Например: https://your-bot.onrender.com

# Инициализируем Flask
flask_app = Flask(__name__)

# Инициализируем Telegram-бот
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Фразы-напоминания
REMINDER_MESSAGES = [
    "Мне тут птичка напела, что тебе надо",
    "Роднулька, не люблю указывать, но тебе надо",
    "Фух, чуть не проспал! Тебе надо",
    "Твое испытание начинается. Пришло время",
    "Нейрончики, я принес вам лимонад. Вам стоит",
    "Я надеюсь ты не забыл",
]

# Фразы подтверждения
CONFIRM_MESSAGES = [
    "Забились, освежу твои нейрончики спустя {time_str}",
    "Хорошо, напомню через {time_str}",
    "Окей, жди сигнала через {time_str}",
]

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Произошла ошибка: {context.error}")

# Обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    match = re.match(
        r"(\d+)\s*(час|часа|часов|минута|минуты|минут|секунда|секунды|секунд)?\s+(.*)",
        message_text.lower()
    )
    if not match:
        await update.message.reply_text(
            "Извини роднулька, но мне не платят за понимание текста.\n"
            "Пиши вот так:\n3 минуты сделать чай"
        )
        return

    amount = int(match[1])
    unit   = match[2] or "секунд"
    task   = match[3]

    if "час" in unit:
        delta = timedelta(hours=amount)
        word  = get_plural(amount, "час", "часа", "часов")
    elif "минут" in unit:
        delta = timedelta(minutes=amount)
        word  = get_plural(amount, "минута", "минуты", "минут")
    else:
        delta = timedelta(seconds=amount)
        word  = get_plural(amount, "секунда", "секунды", "секунд")

    time_str    = f"{amount} {word}"
    confirm_text = random.choice(CONFIRM_MESSAGES).format(time_str=time_str)
    await update.message.reply_text(confirm_text)

    await asyncio.sleep(delta.total_seconds())

    reminder_text = f"{random.choice(REMINDER_MESSAGES)}\n{task}"
    await update.message.reply_text(reminder_text)

# Функция склонения
def get_plural(n, form1, form2, form5):
    if 11 <= n % 100 <= 14:
        return form5
    if n % 10 == 1:
        return form1
    if 2 <= n % 10 <= 4:
        return form2
    return form5

# Регистрируем хендлеры
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_error_handler(error_handler)

# Flask route для Telegram Webhook
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)  # убираем await, делаем синхронный вызов
    return "ok", 200

# Точка входа
if __name__ == "__main__":
    # Установка вебхука
    @flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
    def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.process_update(update)
    return "ok", 200

    # Запуск Flask-сервера на порту Render
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)


