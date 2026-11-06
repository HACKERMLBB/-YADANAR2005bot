import os
import asyncio
import threading
import feedparser
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# --- Render එකට ඕනේ Port එක ---
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
# --- මෙතනින් ඉවරයි ---

FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

sent_links = set()

def get_war_news():
    keywords = ["war", "attack", "missile", "airstrike", "military", "iran", "israel", "ukraine", "russia", "gaza", "bomb", "troops", "conflict", "army", "killed"]
    news = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                if entry.link in sent_links:
                    continue
                if any(k in entry.title.lower() for k in keywords):
                    news.append(entry)
                    sent_links.add(entry.link)
                if len(news) >= 3:
                    break
        except:
            continue
    return news[:3]

async def send_auto_news(context: ContextTypes.DEFAULT_TYPE):
    news = get_war_news()
    if not news:
        return
    for item in news:
        # --- මෙන්න Powered By එක දැම්මේ ---
        text = f"🚨 **BREAKING WAR NEWS** 🚨\n\n📰 {item.title}\n\n🔗 [Read Full News]({item.link})\n\n#War #WorldNews #Breaking\n\n⚡ Powered by [yadanar2005bot](https://t.me/yadanar2005bot)"
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌍 Bot is running! News will auto post to Channel every 5 min.\n\n⚡ Powered by https://t.me/yadanar2005bot")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_war_news()
    if not news:
        await update.message.reply_text("No new war news right now.")
        return
    for item in news:
        await update.message.reply_text(f"📰 {item.title}\n🔗 {item.link}\n\n⚡ Powered by https://t.me/yadanar2005bot")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    job_queue = app.job_queue
    job_queue.run_repeating(send_auto_news, interval=300, first=10)
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Bot Started...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
