"""Конфигурация бота."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Пути
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "bot.db"
LOG_PATH = BASE_DIR / "bot.log"
ASSETS_DIR = BASE_DIR / "assets"
PORTFOLIO_DIR = ASSETS_DIR / "portfolio"

# Бот
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STUDIO_NAME = os.getenv("STUDIO_NAME", "Лендинг Студия")

# Админ и уведомления
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID", "")  # Чат команды
ORDERS_CHANNEL_ID = os.getenv("ORDERS_CHANNEL_ID", "")  # Канал заявок
MANAGER_TELEGRAM_IDS = [int(x) for x in os.getenv("MANAGER_TELEGRAM_IDS", "").split(",") if x.strip()]

# Лимиты
MAX_ORDERS_PER_HOUR = 5
REMINDER_AFTER_HOURS = 1
FOLLOWUP_AFTER_HOURS = 24
SHEETS_EXPORT_HOUR = 23
SHEETS_EXPORT_MINUTE = 0

# Google Sheets
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", BASE_DIR / "credentials.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")

# Состояния ConversationHandler
(
    QUIZ_BUSINESS,
    QUIZ_GOAL,
    QUIZ_TIMELINE,
    QUIZ_MATERIALS,
    QUIZ_CONTACT,
    QUIZ_CONFIRM,
) = range(6)
