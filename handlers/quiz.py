"""Квиз-опрос из 2 вопросов, контакт, подтверждение заявки."""
import logging
import re
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import (
    QUIZ_BUSINESS,
    QUIZ_GOAL,
    QUIZ_CONTACT,
    QUIZ_CONFIRM,
    MAX_ORDERS_PER_HOUR,
)
from database import db
from keyboards import (
    get_main_keyboard,
    get_contact_keyboard,
    get_quiz_keyboard_business,
    get_quiz_keyboard_goal,
    get_confirm_order_keyboard,
)
from keyboards.inline import QUIZ_LABELS
from utils.messages import (
    QUIZ_INTRO,
    QUIZ_Q1,
    QUIZ_Q2,
    QUIZ_CONTACT as MSG_QUIZ_CONTACT,
    QUIZ_CONFIRM as MSG_QUIZ_CONFIRM,
    ORDER_CONFIRM_TEMPLATE,
)
from utils.integrations import notify_managers_about_order

logger = logging.getLogger("bot")

PHONE_REGEX = re.compile(r"^[\d\s\+\-\(\)]{10,20}$")


def _get_quiz_data(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if "quiz_data" not in context.user_data:
        context.user_data["quiz_data"] = {}
    return context.user_data["quiz_data"]


# --- Вход в квиз (/order) ---
async def cmd_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /order — начало квиза."""
    user = update.effective_user
    if not user:
        return ConversationHandler.END
    if db.count_orders_last_hour(user.id) >= MAX_ORDERS_PER_HOUR:
        await update.message.reply_text(
            "Вы уже отправили несколько заявок за последний час. Пожалуйста, подождите.",
            reply_markup=get_main_keyboard(),
        )
        return ConversationHandler.END
    context.user_data["quiz_data"] = {}
    await update.message.reply_text(QUIZ_INTRO, parse_mode="Markdown")
    await update.message.reply_text(QUIZ_Q1, parse_mode="Markdown", reply_markup=get_quiz_keyboard_business())
    return QUIZ_BUSINESS


# --- Ответы квиза (inline) ---
async def quiz_answer_business(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = _get_quiz_data(context)
    data["business_type"] = QUIZ_LABELS.get(q.data, q.data)
    await q.edit_message_text(text=f"{QUIZ_Q1}\n✔ {data['business_type']}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=QUIZ_Q2,
        parse_mode="Markdown",
        reply_markup=get_quiz_keyboard_goal(),
    )
    return QUIZ_GOAL


async def quiz_answer_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = _get_quiz_data(context)
    data["goal"] = QUIZ_LABELS.get(q.data, q.data)
    await q.edit_message_text(text=f"{QUIZ_Q2}\n✔ {data['goal']}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MSG_QUIZ_CONTACT,
        parse_mode="Markdown",
        reply_markup=get_contact_keyboard(),
    )
    return QUIZ_CONTACT


# --- Контакт (текст или request_contact) ---
async def quiz_contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number or ""
    elif update.message.text:
        text = update.message.text.strip()
        if text == "❌ Отмена":
            await update.message.reply_text("Заявка отменена.", reply_markup=get_main_keyboard())
            return ConversationHandler.END
        if PHONE_REGEX.match(text):
            phone = text
    if not phone or len(phone) < 10:
        await update.message.reply_text(
            "Введите корректный номер телефона (например +7 999 123-45-67) или нажмите «Отправить контакт».",
            reply_markup=get_contact_keyboard(),
        )
        return QUIZ_CONTACT
    data = _get_quiz_data(context)
    data["phone"] = phone
    data["contact_preference"] = "phone"
    summary = (
        f"*Проверьте данные:*\n\n"
        f"Сфера: {data.get('business_type', '—')}\n"
        f"Цель: {data.get('goal', '—')}\n"
        f"Телефон: {phone}\n\n"
        f"{MSG_QUIZ_CONFIRM}"
    )
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=get_confirm_order_keyboard(),
    )
    return QUIZ_CONFIRM


# --- Подтверждение заявки (inline) ---
async def quiz_confirm_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.data != "order_confirm_submit":
        return QUIZ_CONFIRM
    await q.answer()
    user = update.effective_user
    data = _get_quiz_data(context)
    order_id = db.create_order(
        telegram_user_id=user.id,
        business_type=data.get("business_type", ""),
        goal=data.get("goal", ""),
        budget="5000",
        timeline="",
        materials="",
        contact_preference=data.get("contact_preference", "phone"),
        phone=data.get("phone", ""),
    )
    db.get_or_create_user(user.id, user.username, user.full_name)
    db.update_user_phone(user.id, data.get("phone", ""))
    db.log_event("order_created", user_id=user.id, order_id=order_id)
    await q.edit_message_text(
        ORDER_CONFIRM_TEMPLATE.format(order_id=order_id),
        parse_mode="Markdown",
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Меню:",
        reply_markup=get_main_keyboard(),
    )
    await notify_managers_about_order(
        context.bot,
        order_id=order_id,
        full_name=user.full_name or "",
        username=user.username or "",
        phone=data.get("phone", ""),
        business_type=data.get("business_type", ""),
        goal=data.get("goal", ""),
    )
    context.user_data.pop("quiz_data", None)
    return ConversationHandler.END


async def quiz_confirm_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("Заявка отменена.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Меню:",
        reply_markup=get_main_keyboard(),
    )
    context.user_data.pop("quiz_data", None)
    return ConversationHandler.END


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /cancel — выход из любого состояния."""
    await update.message.reply_text("Действие отменено.", reply_markup=get_main_keyboard())
    context.user_data.pop("quiz_data", None)
    return ConversationHandler.END


def get_quiz_conversation_handler() -> ConversationHandler:
    """Собрать ConversationHandler для квиза и заявки."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("order", cmd_order),
            MessageHandler(filters.Regex("^🎯 ЗАКАЗАТЬ САЙТ$"), cmd_order),
        ],
        states={
            QUIZ_BUSINESS: [CallbackQueryHandler(quiz_answer_business, pattern="^quiz_business_")],
            QUIZ_GOAL: [CallbackQueryHandler(quiz_answer_goal, pattern="^quiz_goal_")],
            QUIZ_CONTACT: [
                MessageHandler(filters.CONTACT, quiz_contact_received),
                MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_contact_received),
            ],
            QUIZ_CONFIRM: [
                CallbackQueryHandler(quiz_confirm_submit, pattern="^order_confirm_submit$"),
                CallbackQueryHandler(quiz_confirm_cancel, pattern="^order_confirm_cancel$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
    )
