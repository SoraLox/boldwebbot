"""Основные Reply-клавиатуры."""
from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню."""
    keyboard = [
        [KeyboardButton("🎯 Бесплатный дизайн-макет")],
        [
            KeyboardButton("💰 Цены и услуги"),
            KeyboardButton("📁 Портфолио"),
        ],
        [
            KeyboardButton("📞 Контакты"),
            KeyboardButton("❓ FAQ"),
        ],
        [KeyboardButton("👤 Мой кабинет")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие или введите команду",
    )


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
