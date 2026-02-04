"""Интеграции: Google Sheets, уведомления менеджерам."""
from pathlib import Path

from config import (
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_SHEET_ID,
    MANAGER_CHAT_ID,
    MANAGER_TELEGRAM_IDS,
    ORDERS_CHANNEL_ID,
)
from database import db
from utils.messages import ORDER_NOTIFY_MANAGER


async def notify_managers_about_order(
    bot,
    order_id: str,
    full_name: str,
    username: str,
    phone: str,
    business_type: str,
    goal: str,
) -> None:
    """Отправить уведомление о новой заявке: в чат команды, в канал, лично менеджерам."""
    text = ORDER_NOTIFY_MANAGER.format(
        order_id=order_id,
        full_name=full_name or "—",
        username=username or "—",
        phone=phone or "—",
        business_type=business_type or "—",
        goal=goal or "—",
    )
    for chat_id in [MANAGER_CHAT_ID, ORDERS_CHANNEL_ID] + (MANAGER_TELEGRAM_IDS or []):
        if not chat_id:
            continue
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
            )
        except Exception:
            pass


def export_orders_to_sheets() -> bool:
    """Экспорт заявок в Google Sheets. Возвращает True при успехе."""
    if not GOOGLE_SHEET_ID or not Path(GOOGLE_CREDENTIALS_PATH).exists():
        return False
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        creds = Credentials.from_service_account_file(
            str(GOOGLE_CREDENTIALS_PATH), scopes=scope
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(GOOGLE_SHEET_ID)
        worksheet = sh.sheet1
        rows = db.get_orders_for_export()
        if not rows:
            return True
        data = [
            [
                str(r.get("created_at", "")),
                str(r.get("order_id", "")),
                str(r.get("full_name", "")),
                str(r.get("phone", "")),
                str(r.get("status", "")),
            ]
            for r in rows
        ]
        worksheet.append_rows(data, value_input_option="USER_ENTERED")
        return True
    except Exception:
        return False


async def remind_managers_new_orders(bot) -> None:
    """Напомнить менеджерам о заявках в статусе new старше 1 часа."""
    from config import REMINDER_AFTER_HOURS
    from utils.messages import REMINDER_NEW_ORDER

    orders = db.get_orders_new_longer_than_hours(REMINDER_AFTER_HOURS)
    if not orders or not (MANAGER_CHAT_ID or MANAGER_TELEGRAM_IDS):
        return
    for o in orders:
        text = REMINDER_NEW_ORDER.format(order_id=o.get("order_id", ""))
        for chat_id in [MANAGER_CHAT_ID] + (MANAGER_TELEGRAM_IDS or []):
            if not chat_id:
                continue
            try:
                await bot.send_message(chat_id=chat_id, text=text)
            except Exception:
                pass
