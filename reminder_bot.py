import os
import asyncio
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ' '.join(context.args)
    match = re.search(r'через (\d+) (секунд|минут|часов?) (.+)', msg)
    if not match:
        await update.message.reply_text("Пример: /remind через 5 минут позвонить маме")
        return

    amount = int(match.group(1))
    unit = match.group(2)
    task = match.group(3)

    delay = {
        'секунд': amount,
        'минут': amount * 60,
        'часов': amount * 3600
    }[unit]

    await update.message.reply_text(f"Напомню через {amount} {unit}: {task}")
    await asyncio.sleep(delay)
    await update.message.reply_text(f"Напоминаю: {task}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("remind", remind_command))
app.run_polling()
