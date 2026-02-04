"""Обработчики команд и сообщений."""
from handlers.start import register_start_handlers
from handlers.quiz import get_quiz_conversation_handler
from handlers.order import register_order_handlers
from handlers.admin import register_admin_handlers

__all__ = [
    "register_start_handlers",
    "get_quiz_conversation_handler",
    "register_order_handlers",
    "register_admin_handlers",
]
