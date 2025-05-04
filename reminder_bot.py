import os
import asyncio
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    match = re.match(r'(\d+)\s+(секунд[аы]?|минут[аы]?|час[аов]?)\s+(.+)', msg)
    if not match:
        await update.message.reply_text("Пример: '3 минуты сделать чай'")
        return

    amount = int(match.group(1))
    unit = match.group(2)
    task = match.group(3)

    # Приводим к ключам словаря
    if unit.startswith('секунд'):
        delay = amount
        unit = 'секунд'
    elif unit.startswith('минут'):
        delay = amount * 60
        unit = 'минут'
    elif unit.startswith('час'):
        delay = amount * 3600
        unit = 'часов'
    else:
        await update.message.reply_text("Я так не работаю. Пиши вот так: '3 минуты сделать чай'")
        return

    await update.message.reply_text(f"Забились, освежу твои нейрончики спустя {amount} {unit}: {task}")
    await asyncio.sleep(delay)
    await update.message.reply_text(f"Мне тут птичка напела, что тебе надо: {task}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
