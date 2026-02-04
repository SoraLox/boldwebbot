"""Команда /start, меню, приветствие, кнопки главного меню."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from database import db
from keyboards import get_main_keyboard
from utils.messages import WELCOME_MESSAGE, PRICE_LIST, HELP_MESSAGE, FAQ_MESSAGE

logger = logging.getLogger("bot")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start: приветствие и главное меню."""
    user = update.effective_user
    if not user:
        return
    db.get_or_create_user(user.id, user.username, user.full_name)
    db.log_event("start", user_id=user.id)
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(),
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /menu: показать главное меню."""
    await update.message.reply_text(
        "Главное меню:",
        reply_markup=get_main_keyboard(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help: контакты и инструкция."""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")


async def cmd_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /portfolio: примеры работ."""
    from config import PORTFOLIO_DIR
    msg = "📁 *Наше портфолио*\n\nПримеры лендингов. Добавьте изображения в папку `assets/portfolio/` для отображения здесь."
    await update.message.reply_text(msg, parse_mode="Markdown")
    if PORTFOLIO_DIR.exists():
        for f in sorted(PORTFOLIO_DIR.iterdir())[:10]:
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                try:
                    with open(f, "rb") as fp:
                        await update.message.reply_photo(photo=fp)
                except Exception:
                    pass


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /price: цены и услуги."""
    await update.message.reply_text(PRICE_LIST, parse_mode="Markdown")


async def handle_main_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопок главного меню."""
    text = (update.message and update.message.text) or ""
    if text == "💰 Цены и услуги":
        await update.message.reply_text(PRICE_LIST, parse_mode="Markdown")
    elif text == "📁 Портфолио":
        await update.message.reply_text(
            "Примеры наших работ: /portfolio\n"
            "Здесь будут фото лендингов. Добавьте изображения в папку assets/portfolio/ и настройте отправку в handlers.",
        )
    elif text == "📞 Контакты":
        await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")
    elif text == "❓ FAQ":
        await update.message.reply_text(FAQ_MESSAGE, parse_mode="Markdown")
    elif text == "👤 Мой кабинет":
        await update.message.reply_text(
            "Проверить статус заявки: /status\nВаши заявки отображаются здесь.",
        )
    else:
        await update.message.reply_text(
            "Используйте кнопки меню или команды: /menu, /order, /portfolio, /price",
            reply_markup=get_main_keyboard(),
        )


def register_start_handlers(application) -> None:
    """Регистрация обработчиков start и меню."""
    from telegram.ext import CommandHandler, MessageHandler, filters

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("menu", cmd_menu))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("portfolio", cmd_portfolio))
    application.add_handler(CommandHandler("price", cmd_price))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_main_menu_buttons,
        )
    )
