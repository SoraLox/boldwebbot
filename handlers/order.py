"""Статус заявки и прочее по заявкам."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from database import db
from keyboards import get_main_keyboard

logger = logging.getLogger("bot")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /status — проверить статус последней заявки."""
    user = update.effective_user
    if not user:
        return
    row = db.get_last_order_by_telegram_user(user.id)
    if not row:
        await update.message.reply_text(
            "У вас пока нет заявок. Оформить заявку: /order",
            reply_markup=get_main_keyboard(),
        )
        return
    status_text = {"new": "🆕 Новая", "in_progress": "🔄 В работе", "done": "✅ Выполнена", "cancelled": "❌ Отменена"}.get(
        row["status"], row["status"]
    )
    await update.message.reply_text(
        f"📋 *Ваша последняя заявка:* {row['order_id']}\n"
        f"Статус: {status_text}\n"
        f"Дата: {row['created_at']}",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(),
    )


def register_order_handlers(application) -> None:
    """Регистрация обработчиков заказов."""
    from telegram.ext import CommandHandler
    application.add_handler(CommandHandler("status", cmd_status))
