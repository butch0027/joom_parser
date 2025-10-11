import asyncio
import logging
import os
import signal
from typing import Final

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ----- конфиг -----
TOKEN: Final[str | None] = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("tg-bot")

# ----- хендлеры -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я в Docker 🐳  Команды: /help /ping /id")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступно:\n"
        "/start — приветствие\n"
        "/help — помощь\n"
        "/ping — проверка ответа\n"
        "/id — показать твой chat_id\n"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")

async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id if update.effective_chat else "unknown"
    await update.message.reply_text(f"chat_id: {cid}")

async def echo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # простой эхо на обычный текст
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.exception("Ошибка в обработчике: %s", context.error)

# ----- запуск -----
async def run() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не задан (env).")

    app = Application.builder().token(TOKEN).build()

    # команды для меню бота
    await app.bot.set_my_commands([
        BotCommand("start", "Запуск"),
        BotCommand("help", "Помощь"),
        BotCommand("ping", "Проверка ответа"),
        BotCommand("id", "Показать chat_id"),
    ])

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("id", show_id))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))
    app.add_error_handler(on_error)

    # аккуратное завершение по сигналам (Docker stop)
    stop_event = asyncio.Event()

    def _graceful_shutdown(*_):
        log.info("Получен сигнал, останавливаюсь…")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _graceful_shutdown)

    # long polling
    log.info("Стартую polling…")
    runner = app.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None, close_loop=False, poll_interval=1.5)
    # app.run_polling синхронно блокирует; оборачиваем в таска
    task = asyncio.create_task(asyncio.to_thread(runner))
    await stop_event.wait()
    log.info("Остановка…")
    app.stop()
    await app.shutdown()
    await app.bot.close()
    task.cancel()

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
