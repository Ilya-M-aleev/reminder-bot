import os
import asyncio
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]

# Возможные фразы для напоминания
REMINDER_PHRASES = [
    "Мне тут птичка напела, что тебе надо", "Роднулька, не люблю указывать, но тебе надо", "Фух, чуть не проспал! Тебе надо", "Твое испытание начинается. Пришло время", "Нейрончики я принес вам лимонад. Вам стоит", "Я надеюсь ты не забыл"
]

def pluralize(value, forms):
    if 11 <= value % 100 <= 14:
        return forms[2]
    last_digit = value % 10
    if last_digit == 1:
        return forms[0]
    elif 2 <= last_digit <= 4:
        return forms[1]
    else:
        return forms[2]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    match = re.match(r'(\d+)\s+(секунд[аы]?|минут[аы]?|час[аов]?)\s+(.+)', msg)
    if not match:
        await update.message.reply_text("Извини роднулька, но мне не платят за понимание текста.\nПиши вот так: 3 минуты сделать чай")
        return

    amount = int(match.group(1))
    unit_raw = match.group(2)
    task = match.group(3)

    if unit_raw.startswith('секунд'):
        delay = amount
        unit_forms = ('секунду', 'секунды', 'секунд')
    elif unit_raw.startswith('минут'):
        delay = amount * 60
        unit_forms = ('минуту', 'минуты', 'минут')
    elif unit_raw.startswith('час'):
        delay = amount * 3600
        unit_forms = ('час', 'часа', 'часов')
    else:
        await update.message.reply_text("Извини роднулька, но мне не платят за понимание текста.\nПиши вот так: '3 минуты сделать чай'")
        return

    unit_correct = pluralize(amount, unit_forms)
    await update.message.reply_text(f"Забились, освежу твои нейрончики спустя {amount} {unit_correct}")
    await asyncio.sleep(delay)

    reminder = random.choice(REMINDER_PHRASES)
    await update.message.reply_text(f"{reminder}\n{task.strip()}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
