"""Клавиатуры бота."""
from keyboards.main import get_main_keyboard, get_contact_keyboard
from keyboards.inline import (
    get_quiz_keyboard_business,
    get_quiz_keyboard_goal,
    get_quiz_keyboard_timeline,
    get_quiz_keyboard_materials,
    get_confirm_order_keyboard,
)

__all__ = [
    "get_main_keyboard",
    "get_quiz_keyboard_business",
    "get_quiz_keyboard_goal",
    "get_quiz_keyboard_timeline",
    "get_quiz_keyboard_materials",
    "get_contact_keyboard",
    "get_confirm_order_keyboard",
]
