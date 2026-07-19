import asyncio
import logging
import os
import time

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from agents.crew import run_ceo_crew

logger = logging.getLogger(__name__)

# Hard cap so a hung crew never fails silently. Code reviews on large PRs
# can take 15-20 min, so default is 30 min; override with CREW_TIMEOUT_SECONDS in .env
CREW_TIMEOUT_SECONDS = int(os.getenv("CREW_TIMEOUT_SECONDS", "1800"))
PROGRESS_INTERVAL_SECONDS = 60  # progress message every minute
TELEGRAM_MAX_LEN = 4096

ERROR_REPLY = "Sorry, an error occurred while processing your request. Please try again later."
TIMEOUT_REPLY = (
    "I stopped waiting -- this ran past the time limit. The work may still "
    "finish in the background (for code reviews, check the PR for comments). "
    "Check the console logs to see which step it was on."
)


def _chunk(text: str, size: int = TELEGRAM_MAX_LEN):
    return [text[i : i + size] for i in range(0, len(text), size)] or [""]


async def _run_crew_and_reply(update: Update, prompt: str) -> None:
    """Run the crew off the event loop, sending a progress update every
    minute until it finishes, times out, or fails."""
    # Shared status the crew thread writes to and the ticker reads from.
    status = {"last_step": "delegating to the right specialist..."}

    def on_step(info: str) -> None:
        status["last_step"] = info

    crew_future = asyncio.create_task(
        asyncio.to_thread(run_ceo_crew, prompt, on_step)
    )
    started = time.monotonic()

    try:
        while True:
            done, _ = await asyncio.wait(
                {crew_future}, timeout=PROGRESS_INTERVAL_SECONDS
            )
            if done:
                answer = crew_future.result()  # re-raises crew exceptions
                break

            elapsed = time.monotonic() - started
            if elapsed >= CREW_TIMEOUT_SECONDS:
                # Threads can't be force-killed; we stop waiting and tell
                # the user. The stray thread finishes in the background.
                logger.error("Crew run timed out for prompt: %r", prompt)
                await update.message.reply_text(TIMEOUT_REPLY)
                return

            minutes = int(elapsed // 60)
            await update.message.reply_text(
                f"⏳ Still working ({minutes} min): {status['last_step']}"
            )
            await update.message.chat.send_action(ChatAction.TYPING)
    except Exception:
        logger.exception("Crew run failed for prompt: %r", prompt)
        await update.message.reply_text(ERROR_REPLY)
        return

    if not answer or not answer.strip():
        logger.warning("Crew returned empty answer for prompt: %r", prompt)
        await update.message.reply_text(
            "I couldn't produce an answer for that. Please rephrase and try again."
        )
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
