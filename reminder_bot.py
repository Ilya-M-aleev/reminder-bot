import os
import logging
import re
import random
from datetime import timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.environ["BOT_TOKEN"]

# Возможные фразы для напоминания
REMINDER_MESSAGES = [
    "Мне тут птичка напела, что тебе надо", 
    "Роднулька, не люблю указывать, но тебе надо", 
    "Фух, чуть не проспал! Тебе надо", 
    "Твое испытание начинается. Пришло время", 
    "Нейрончики я принес вам лимонад. Вам стоит", 
    "Я надеюсь ты не забыл",
]

# Варианты подтверждений установки
CONFIRM_MESSAGES = [
    "Забились, освежу твои нейрончики спустя {time_str}",
]

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Произошла ошибка: {context.error}")

# Обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    match = re.match(r"(\d+)\s*(минута|минуты|минут|секунда|секунды|секунд)?\s+(.*)", message_text.lower())
    if not match:
        await update.message.reply_text("Извини роднулька, но мне не платят за понимание текста.\nПиши вот так: 3 минуты сделать чай")
        return

    amount = int(match[1])
    unit = match[2] or "секунд"
    task = match[3]

    if "минут" in unit:
        delta = timedelta(minutes=amount)
        word = get_plural(amount, "минута", "минуты", "минут")
    else:
        delta = timedelta(seconds=amount)
        word = get_plural(amount, "секунда", "секунды", "секунд")

    time_str = f"{amount} {word}"
    confirm_text = random.choice(CONFIRM_MESSAGES).format(time_str=time_str)
    await update.message.reply_text(confirm_text)

    await asyncio.sleep(delta.total_seconds())

    reminder_text = f"{random.choice(REMINDER_MESSAGES)}\n{task}"
    await update.message.reply_text(reminder_text)

# Функция склонения слов
def get_plural(n, form1, form2, form5):
    if 11 <= n % 100 <= 14:
        return form5
    if n % 10 == 1:
        return form1
    if 2 <= n % 10 <= 4:
        return form2
    return form5

# Запуск приложения
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    application.run_polling()
