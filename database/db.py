"""Работа с SQLite базой данных."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import DB_PATH
from database.models import ALL_TABLES


def init_db() -> None:
    """Создание таблиц и директории для БД."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        for table_sql in ALL_TABLES:
            conn.execute(table_sql)
        conn.commit()


@contextmanager
def get_connection():
    """Контекстный менеджер подключения к БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """Возвращает контекстный менеджер для использования в with."""
    return get_connection()


# --- Пользователи ---

def get_or_create_user(user_id: int, username: Optional[str], full_name: Optional[str]) -> int:
    """Получить или создать пользователя. Возвращает id в таблице users."""
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id FROM users WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        if row:
            return row["id"]
        conn.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username or "", full_name or ""),
        )
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def update_user_phone(user_id: int, phone: str) -> None:
    """Обновить телефон пользователя по Telegram user_id."""
    with get_connection() as conn:
        conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        conn.commit()


def get_all_active_user_ids() -> list[int]:
    """Список Telegram user_id всех активных пользователей (для рассылки)."""
    with get_connection() as conn:
        cur = conn.execute("SELECT user_id FROM users WHERE status = 'active'")
        return [row["user_id"] for row in cur.fetchall()]


def get_user_by_telegram_id(telegram_user_id: int) -> Optional[dict]:
    """Получить пользователя по Telegram user_id."""
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (telegram_user_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


# --- Заявки ---

def count_orders_last_hour(telegram_user_id: int) -> int:
    """Количество заявок пользователя за последний час."""
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT COUNT(*) as cnt FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE u.user_id = ? AND o.created_at >= datetime('now', '-1 hour')
            """,
            (telegram_user_id,),
        )
        return cur.fetchone()["cnt"]


def create_order(
    telegram_user_id: int,
    business_type: str,
    goal: str,
    budget: str,
    timeline: str,
    materials: str,
    contact_preference: str,
    phone: str,
) -> str:
    """Создать заявку. Возвращает order_id (например #2024-001)."""
    user_pk = get_or_create_user(telegram_user_id, None, None)
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) as cnt FROM orders WHERE date(created_at) = date('now')"
        )
        daily_count = cur.fetchone()["cnt"]
    order_id = f"#{datetime.now().strftime('%Y')}-{daily_count + 1:03d}"
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO orders (
                order_id, user_id, business_type, goal, budget, timeline,
                materials, contact_preference, phone, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
            """,
            (order_id, user_pk, business_type, goal, budget, timeline, materials, contact_preference, phone),
        )
        conn.commit()
        return order_id


def get_last_order_by_telegram_user(telegram_user_id: int) -> Optional[dict]:
    """Последняя заявка пользователя по Telegram user_id."""
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT o.order_id, o.status, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE u.user_id = ?
            ORDER BY o.created_at DESC LIMIT 1
            """,
            (telegram_user_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_order_by_id(order_id: str) -> Optional[dict]:
    """Получить заявку по order_id (например #2024-001)."""
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT o.*, u.user_id as telegram_user_id, u.username, u.full_name, u.phone as user_phone
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.order_id = ?
            """,
            (order_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_orders_new_longer_than_hours(hours: float) -> list[dict]:
    """Заявки в статусе 'new' старше N часов (для напоминаний)."""
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT o.*, u.user_id as telegram_user_id, u.full_name
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.status = 'new' AND o.created_at <= datetime('now', ?)
            """,
            (f"-{hours} hours",),
        )
        return [dict(r) for r in cur.fetchall()]


def update_order_status(order_id: str, status: str, manager_id: Optional[int] = None, notes: Optional[str] = None) -> None:
    """Обновить статус заявки."""
    with get_connection() as conn:
        if manager_id is not None and notes is not None:
            conn.execute(
                "UPDATE orders SET status = ?, manager_id = ?, notes = ? WHERE order_id = ?",
                (status, manager_id, notes, order_id),
            )
        elif manager_id is not None:
            conn.execute(
                "UPDATE orders SET status = ?, manager_id = ? WHERE order_id = ?",
                (status, manager_id, order_id),
            )
        elif notes is not None:
            conn.execute(
                "UPDATE orders SET status = ?, notes = ? WHERE order_id = ?",
                (status, notes, order_id),
            )
        else:
            conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        conn.commit()


def get_orders_for_export(since: Optional[datetime] = None) -> list[dict]:
    """Заявки для экспорта (например за день). Если since не указан — все новые за сегодня."""
    with get_connection() as conn:
        if since:
            cur = conn.execute(
                """
                SELECT o.order_id, o.created_at, o.status, o.phone, u.full_name
                FROM orders o JOIN users u ON o.user_id = u.id
                WHERE o.created_at >= ?
                ORDER BY o.created_at
                """,
                (since.isoformat(),),
            )
        else:
            cur = conn.execute(
                """
                SELECT o.order_id, o.created_at, o.status, o.phone, u.full_name
                FROM orders o JOIN users u ON o.user_id = u.id
                WHERE date(o.created_at) = date('now')
                ORDER BY o.created_at
                """,
            )
        return [dict(r) for r in cur.fetchall()]


# --- Аналитика ---

def log_event(event_type: str, user_id: Optional[int] = None, order_id: Optional[str] = None, payload: Optional[str] = None) -> None:
    """Записать событие для аналитики."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO analytics (event_type, user_id, order_id, payload) VALUES (?, ?, ?, ?)",
            (event_type, user_id, order_id, payload or ""),
        )
        conn.commit()


# --- Админ / статистика ---

def get_stats() -> dict[str, Any]:
    """Базовая статистика для админки."""
    with get_connection() as conn:
        users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
        orders = conn.execute("SELECT COUNT(*) as c FROM orders").fetchone()["c"]
        new_orders = conn.execute("SELECT COUNT(*) as c FROM orders WHERE status = 'new'").fetchone()["c"]
        today_start = conn.execute("SELECT COUNT(*) as c FROM analytics WHERE event_type = 'start' AND date(created_at) = date('now')").fetchone()["c"]
        return {
            "users_total": users,
            "orders_total": orders,
            "orders_new": new_orders,
            "starts_today": today_start,
        }
