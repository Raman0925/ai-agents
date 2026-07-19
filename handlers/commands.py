from telegram import Update
from telegram.ext import ContextTypes
from agents.researcher import run_researcher


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive!")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)

    if not topic:
        await update.message.reply_text("Usage: /ask <topic>")
        return

    await update.message.reply_text(f"Researching: {topic}...")

    answer = run_researcher(topic)

    await update.message.reply_text(answer)
