"""Inline-клавиатуры для квиза и подтверждения."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Квиз: сфера бизнеса
BUSINESS_OPTIONS = [
    ("👔 Услуги", "quiz_business_services"),
    ("🛍️ Товары", "quiz_business_goods"),
    ("🎓 Инфобизнес", "quiz_business_infobiz"),
    ("📱 Другое", "quiz_business_other"),
]

# Цель сайта
GOAL_OPTIONS = [
    ("📋 Заявки", "quiz_goal_leads"),
    ("🛒 Продажи", "quiz_goal_sales"),
    ("📢 Информирование", "quiz_goal_info"),
    ("👤 Резюме", "quiz_goal_resume"),
]

# Сроки
TIMELINE_OPTIONS = [
    ("Срочно (1-3 дня)", "quiz_timeline_urgent"),
    ("Неделя", "quiz_timeline_week"),
    ("Месяц", "quiz_timeline_month"),
    ("Не важно", "quiz_timeline_any"),
]

# Материалы
MATERIALS_OPTIONS = [
    ("Текст + фото", "quiz_materials_full"),
    ("Только текст", "quiz_materials_text"),
    ("Нет", "quiz_materials_none"),
    ("Нужна помощь", "quiz_materials_help"),
]


def _make_inline(rows: list[tuple[str, str]], cols: int = 2) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, (label, data) in enumerate(rows):
        row.append(InlineKeyboardButton(label, callback_data=data))
        if len(row) == cols or i == len(rows) - 1:
            buttons.append(row)
            row = []
    return InlineKeyboardMarkup(buttons)


def get_quiz_keyboard_business() -> InlineKeyboardMarkup:
    return _make_inline(BUSINESS_OPTIONS)


def get_quiz_keyboard_goal() -> InlineKeyboardMarkup:
    return _make_inline(GOAL_OPTIONS)


def get_quiz_keyboard_timeline() -> InlineKeyboardMarkup:
    return _make_inline(TIMELINE_OPTIONS)


def get_quiz_keyboard_materials() -> InlineKeyboardMarkup:
    return _make_inline(MATERIALS_OPTIONS)


def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Отправить заявку", callback_data="order_confirm_submit")],
        [InlineKeyboardButton("❌ Отмена", callback_data="order_confirm_cancel")],
    ])


# Маппинг callback_data -> человекочитаемый текст для заявки
QUIZ_LABELS = {
    "quiz_business_services": "Услуги",
    "quiz_business_goods": "Товары",
    "quiz_business_infobiz": "Инфобизнес",
    "quiz_business_other": "Другое",
    "quiz_goal_leads": "Заявки",
    "quiz_goal_sales": "Продажи",
    "quiz_goal_info": "Информирование",
    "quiz_goal_resume": "Резюме",
    "quiz_timeline_urgent": "Срочно (1-3 дня)",
    "quiz_timeline_week": "Неделя",
    "quiz_timeline_month": "Месяц",
    "quiz_timeline_any": "Не важно",
    "quiz_materials_full": "Текст + фото",
    "quiz_materials_text": "Только текст",
    "quiz_materials_none": "Нет",
    "quiz_materials_help": "Нужна помощь",
}
