"""Админ-команды: статистика, рассылка, экспорт, пользователь, заявка."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from config import ADMIN_IDS
from database import db

logger = logging.getLogger("bot")


def _is_admin(user_id: int) -> bool:
    return user_id in (ADMIN_IDS or [])


async def cmd_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /admin_stats — статистика бота."""
    if not update.effective_user or not _is_admin(update.effective_user.id):
        await update.message.reply_text("Доступ запрещён.")
        return
    stats = db.get_stats()
    text = (
        "📊 *Статистика бота*\n\n"
        f"👥 Пользователей: {stats['users_total']}\n"
        f"📋 Всего заявок: {stats['orders_total']}\n"
        f"🆕 Новых заявок: {stats['orders_new']}\n"
        f"🚀 Запусков /start сегодня: {stats['starts_today']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /admin_broadcast <текст> — рассылка всем пользователям."""
    if not update.effective_user or not _is_admin(update.effective_user.id):
        await update.message.reply_text("Доступ запрещён.")
        return
    text = (context.args or [])
    if not text:
        await update.message.reply_text("Использование: /admin_broadcast Текст рассылки")
        return
    msg = " ".join(text)
    user_ids = db.get_all_active_user_ids()
    sent = 0
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=msg)
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"Рассылка отправлена: {sent} из {len(user_ids)}")


async def cmd_admin_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /admin_export — экспорт заявок (отправка файла)."""
    if not update.effective_user or not _is_admin(update.effective_user.id):
        await update.message.reply_text("Доступ запрещён.")
        return
    rows = db.get_orders_for_export()
    if not rows:
        await update.message.reply_text("Нет заявок за сегодня для экспорта.")
        return
    import csv
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Дата", "ID заявки", "Имя", "Телефон", "Статус"])
    for r in rows:
        w.writerow([
            str(r.get("created_at", "")),
            str(r.get("order_id", "")),
            str(r.get("full_name", "")),
            str(r.get("phone", "")),
            str(r.get("status", "")),
        ])
    buf.seek(0)
    from telegram import InputFile
    doc = InputFile(io.BytesIO(buf.getvalue().encode("utf-8-sig")), filename="orders_export.csv")
    await update.message.reply_document(document=doc)


async def cmd_admin_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /admin_user <user_id> — информация о пользователе."""
    if not update.effective_user or not _is_admin(update.effective_user.id):
        await update.message.reply_text("Доступ запрещён.")
        return
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("Использование: /admin_user <telegram_user_id>")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Укажите числовой user_id.")
        return
    u = db.get_user_by_telegram_id(uid)
    if not u:
        await update.message.reply_text("Пользователь не найден.")
        return
    text = (
        f"👤 *Пользователь*\n\n"
        f"ID: {u['user_id']}\n"
        f"Username: @{u.get('username') or '—'}\n"
        f"Имя: {u.get('full_name') or '—'}\n"
        f"Телефон: {u.get('phone') or '—'}\n"
        f"Регистрация: {u.get('registration_date')}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_admin_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /admin_order <order_id> <статус> — изменить статус заявки."""
    if not update.effective_user or not _is_admin(update.effective_user.id):
        await update.message.reply_text("Доступ запрещён.")
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Использование: /admin_order <order_id> <new|in_progress|done|cancelled>")
        return
    order_id = context.args[0].strip()
    if not order_id.startswith("#"):
        order_id = "#" + order_id
    status = context.args[1].strip().lower()
    if status not in ("new", "in_progress", "done", "cancelled"):
        await update.message.reply_text("Статус: new, in_progress, done или cancelled.")
        return
    o = db.get_order_by_id(order_id)
    if not o:
        await update.message.reply_text("Заявка не найдена.")
        return
    db.update_order_status(order_id, status)
    await update.message.reply_text(f"Статус заявки {order_id} изменён на: {status}")


def register_admin_handlers(application) -> None:
    """Регистрация админ-обработчиков."""
    application.add_handler(CommandHandler("admin_stats", cmd_admin_stats))
    application.add_handler(CommandHandler("admin_broadcast", cmd_admin_broadcast))
    application.add_handler(CommandHandler("admin_export", cmd_admin_export))
    application.add_handler(CommandHandler("admin_user", cmd_admin_user))
    application.add_handler(CommandHandler("admin_order", cmd_admin_order))
