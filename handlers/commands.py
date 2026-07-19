import asyncio
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from agents.crew import run_ceo_crew

logger = logging.getLogger(__name__)

CREW_TIMEOUT_SECONDS = 600  # hard cap so a hung crew never fails silently
TELEGRAM_MAX_LEN = 4096

ERROR_REPLY = "Sorry, an error occurred while processing your request. Please try again later."
TIMEOUT_REPLY = "This is taking too long and was cancelled. Please try again with a simpler request."


def _chunk(text: str, size: int = TELEGRAM_MAX_LEN):
    return [text[i : i + size] for i in range(0, len(text), size)] or [""]


async def _run_crew_and_reply(update: Update, prompt: str) -> None:
    """Run the crew off the event loop, with a timeout, and reply in chunks."""
    try:
        # to_thread keeps the bot responsive; wait_for guarantees we always answer.
        answer = await asyncio.wait_for(
            asyncio.to_thread(run_ceo_crew, prompt),
            timeout=CREW_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Crew run timed out for prompt: %r", prompt)
        await update.message.reply_text(TIMEOUT_REPLY)
        return
    except Exception:
        logger.exception("Crew run failed for prompt: %r", prompt)
        await update.message.reply_text(ERROR_REPLY)
        return

    if not answer or not answer.strip():
        logger.warning("Crew returned empty answer for prompt: %r", prompt)
        await update.message.reply_text("I couldn't produce an answer for that. Please rephrase and try again.")
        return

    for chunk in _chunk(answer):
        await update.message.reply_text(chunk)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bot is alive!")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("Usage: /ask <topic>")
        return

    await update.message.reply_text(f"Jarvis (CEO) is thinking about: {topic}...")
    await update.message.chat.send_action(ChatAction.TYPING)
    await _run_crew_and_reply(update, topic)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not update.message.text:
        return
    prompt = update.message.text

    await update.message.reply_text("Jarvis (CEO) is processing your request...")
    await update.message.chat.send_action(ChatAction.TYPING)
    await _run_crew_and_reply(update, prompt)
