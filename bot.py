"""Telegram-бот студии лендингов. Точка входа."""
import logging
from datetime import time

from telegram.ext import Application, Defaults

from config import (
    BOT_TOKEN,
    SHEETS_EXPORT_HOUR,
    SHEETS_EXPORT_MINUTE,
    REMINDER_AFTER_HOURS,
)
from database import init_db
from handlers import (
    register_start_handlers,
    get_quiz_conversation_handler,
    register_order_handlers,
    register_admin_handlers,
)
from utils.logger import setup_logging
from utils.integrations import export_orders_to_sheets, remind_managers_new_orders


def main() -> None:
    setup_logging(logging.INFO)
    logger = logging.getLogger("bot")

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан. Укажите в .env")
        return

    init_db()
    defaults = Defaults(parse_mode="Markdown")
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .defaults(defaults)
        .build()
    )

    # Обработчики: сначала ConversationHandler (квиз), потом остальные
    application.add_handler(get_quiz_conversation_handler())
    register_start_handlers(application)
    register_order_handlers(application)
    register_admin_handlers(application)

    # Ежедневный экспорт в Google Sheets в 23:00
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(
            lambda ctx: export_orders_to_sheets(),
            time=time(hour=SHEETS_EXPORT_HOUR, minute=SHEETS_EXPORT_MINUTE),
        )

        async def job_remind(ctx):
            await remind_managers_new_orders(ctx.application.bot)

        job_queue.run_repeating(
            job_remind,
            interval=1800,
            first=1800,
        )

    logger.info("Бот запущен (polling)")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
