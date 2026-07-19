import logging
from telegram import Update
from telegram.ext import ContextTypes
from agents.crew import run_ceo_crew

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive!")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)

    if not topic:
        await update.message.reply_text("Usage: /ask <topic>")
        return

    await update.message.reply_text(f"Jarvis (CEO) is thinking about: {topic}...")

    try:
        answer = run_ceo_crew(topic)
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error("Error researching topic '%s': %s", topic, e, exc_info=True)
        await update.message.reply_text(
            "Sorry, an error occurred while researching. Please try again later."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    if not prompt:
        return

    await update.message.reply_text("Jarvis (CEO) is processing your request...")

    try:
        answer = run_ceo_crew(prompt)
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error("Error processing message '%s': %s", prompt, e, exc_info=True)
        await update.message.reply_text(
            "Sorry, an error occurred while processing your request. Please try again later."
        )
