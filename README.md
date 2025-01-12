# Emotion Statistics Bot

Telegram bot for sending daily emotion statistics reports from institutions.

## Features

- Daily automated reports at 9:00 AM (Almaty time)
- Admin control for managing report recipients
- Support for multiple institutions and emotion types
- Secure environment variable configuration

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-repo/emotion-statistics-bot.git
cd emotion-statistics-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:

```
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

4. Run the bot:

```bash
python bot.py
```

## Example Daily Report

```
📊 Ежедневный отчет по эмоциям

🏢 В учреждении ТРЦ "Mega" за 25.03.2024:
📌 Всего зафиксировано: 1500 эмоций
👥 Из них в базе: 1200 эмоций

😊 happy: 450
😐 neutral: 380
😠 angry: 220
😢 sad: 150

──────────────────────────────

🏢 В учреждении ТРЦ "Asia Park" за 25.03.2024:
📌 Всего зафиксировано: 2000 эмоций
👥 Из них в базе: 1800 эмоций

😊 happy: 800
😐 neutral: 600
😠 angry: 250
😢 sad: 150

──────────────────────────────
```
