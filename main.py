import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config.config import TELEGRAM_BOT_TOKEN, missing_config
from handlers.commands import start, ask, handle_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch-all so no handler exception is ever swallowed silently."""
    logger.error("Unhandled exception while processing update", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Sorry, something went wrong. Please try again later."
            )
        except Exception:
            logger.exception("Failed to send error reply")


def main() -> None:
    missing = missing_config()
    if missing:
        logger.error(
            "Missing required environment variables: %s. Check your .env file.",
            ", ".join(missing),
        )
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info("Starting bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
