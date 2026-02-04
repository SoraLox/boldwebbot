# Telegram-бот студии лендингов

Продающий бот для студии по созданию лендингов: воронка продаж, квиз из 5 вопросов, сбор заявок, уведомления менеджерам, экспорт в Google Sheets.

## Требования

- Python 3.10+
- Токен бота от [@BotFather](https://t.me/BotFather)

## Установка

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env: BOT_TOKEN, ADMIN_IDS, при необходимости MANAGER_CHAT_ID и др.
```

## Запуск

```bash
python bot.py
```

## Команды пользователя

| Команда | Описание |
|--------|----------|
| /start | Приветствие и главное меню |
| /menu | Показать меню |
| /help | Контакты и инструкция |
| /portfolio | Примеры работ |
| /price | Цены и услуги |
| /order | Начать заявку (квиз) |
| /status | Статус последней заявки |
| /cancel | Отменить текущее действие |

## Админ-команды

Укажите свой Telegram ID в `ADMIN_IDS` в `.env`.

| Команда | Описание |
|--------|----------|
| /admin_stats | Статистика бота |
| /admin_broadcast \<текст\> | Рассылка всем пользователям |
| /admin_export | Экспорт заявок за сегодня (CSV) |
| /admin_user \<id\> | Информация о пользователе |
| /admin_order \<order_id\> \<статус\> | Изменить статус заявки |

## Структура проекта

```
telegram_bot/
├── bot.py                 # Точка входа
├── config.py              # Конфигурация
├── requirements.txt
├── .env.example
├── database/
│   ├── db.py              # Работа с SQLite
│   └── models.py          # Схема таблиц
├── handlers/
│   ├── start.py           # /start, меню, /help, /portfolio, /price
│   ├── quiz.py            # Квиз и оформление заявки
│   ├── order.py           # /status
│   └── admin.py           # Админ-команды
├── keyboards/
│   ├── main.py            # Reply-клавиатуры
│   └── inline.py          # Inline-кнопки квиза
├── utils/
│   ├── messages.py        # Тексты сообщений
│   ├── logger.py          # Логирование
│   └── integrations.py   # Уведомления менеджерам, Google Sheets
├── assets/
│   └── portfolio/         # Изображения для /portfolio
└── data/                  # SQLite БД (создаётся при первом запуске)
```

## Интеграции

- **Уведомления менеджерам**: при новой заявке сообщение уходит в `MANAGER_CHAT_ID`, `ORDERS_CHANNEL_ID` и лично каждому из `MANAGER_TELEGRAM_IDS`.
- **Google Sheets**: задайте `GOOGLE_SHEET_ID` и положите `credentials.json` (Service Account). Ежедневно в 23:00 новые заявки экспортируются в первый лист.
- **Напоминания**: каждые 30 минут проверяются заявки в статусе «новая» старше 1 часа — менеджерам отправляется напоминание.

## Защита

- Лимит заявок: 5 в час на пользователя.
- Валидация телефона при вводе.
- Админ-команды доступны только пользователям из `ADMIN_IDS`.
