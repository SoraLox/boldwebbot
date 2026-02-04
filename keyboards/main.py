"""Основные Reply-клавиатуры."""
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню (Reply-клавиатура)."""
    keyboard = [
        [KeyboardButton("🎯 ЗАКАЗАТЬ САЙТ")],
        [
            KeyboardButton("💰 Цены и услуги"),
            KeyboardButton("❓ FAQ"),
        ],
        [KeyboardButton("👤 Мой кабинет")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие или введите команду",
    )


def get_main_inline_keyboard() -> InlineKeyboardMarkup:
    """Главное меню (Inline-кнопки для лучшей видимости в темной теме)."""
    keyboard = [
        [InlineKeyboardButton("🎯 ЗАКАЗАТЬ САЙТ", callback_data="menu_order")],
        [
            InlineKeyboardButton("💰 Цены и услуги", callback_data="menu_price"),
            InlineKeyboardButton("❓ FAQ", callback_data="menu_faq"),
        ],
        [InlineKeyboardButton("👤 Мой кабинет", callback_data="menu_status")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой «Отправить контакт»."""
    keyboard = [
        [KeyboardButton("📱 Отправить контакт", request_contact=True)],
        [KeyboardButton("❌ Отмена")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
