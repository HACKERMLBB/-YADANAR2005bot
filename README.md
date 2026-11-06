# 🌍 YADANAR - World News Bot

Auto World News Bot for Telegram Channel. Posts breaking news automatically in 4 languages.

⚡ Powered by [@bigolive_asia](https://t.me/bigolive_asia)

## ✨ Features

- 📰 Auto Post News Every 5 Minutes
- 🌐 4 Languages - English, Spanish, Russian, Myanmar
- 📡 10+ Trusted Sources - BBC, CNN, Fox News, Al Jazeera, Reuters, DW
- 🤖 Commands - `/start` & `/latest`
- 🚫 No Duplicate News

## 📰 News Sources

| Language | Sources |
| :--- | :--- |
| 🇬🇧 ENGLISH | BBC, CNN, Fox News, Al Jazeera, Reuters |
| 🇪🇸 SPANISH | BBC Mundo, DW Espanol |
| 🇷🇺 RUSSIAN | BBC Russian, DW Russian |
| 🇲🇲 MYANMAR | BBC Burmese |

## 🤖 Bot Commands

- `/start` - Check if bot is running
- `/latest` - Get latest news instantly

## 🚀 Deploy on Render

1. Fork this repo
2. Go to [Render.com](https://render.com) > New Web Service
3. Connect this repo
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `python main.py`

### 🔑 Environment Variables

Add these in Render > Environment:

| Variable | Example |
| :--- | :--- |
| `BOT_TOKEN` | `123456:ABC-YourBotToken` |
| `CHANNEL_IDS` | `-1001234567890` |

> Get `BOT_TOKEN` from [@BotFather](https://t.me/BotFather)
> Get `CHANNEL_IDS` - Add bot as Admin to your Channel

## 📦 Requirements

- `python-telegram-bot`
- `feedparser`
- `Flask`

## 📝 License

Free to use. Credit to [@bigolive_asia](https://t.me/bigolive_asia)
