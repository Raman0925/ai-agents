import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.config import TELEGRAM_BOT_TOKEN
from handlers.commands import start, ask, handle_message

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN provided. Please check your .env file.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot...")
    # Start the Telegram bot polling loop
    app.run_polling()


if __name__ == "__main__":
    main()
