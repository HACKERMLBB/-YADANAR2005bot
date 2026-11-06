import os
import feedparser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # -100xxxxxxxxxx

FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.reuters.com/rssfeed/worldNews",
]

sent_links = set()

def get_war_news():
    keywords = ["war", "attack", "missile", "airstrike", "military", "iran", "israel", "ukraine", "russia", "gaza", "bomb", "troops", "conflict", "invasion", "army", "killed"]
    news = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                if entry.link in sent_links:
                    continue
                title = entry.title.lower()
                if any(k in title for k in keywords):
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
        text = f"🚨 **BREAKING WAR NEWS** 🚨\n\n📰 {item.title}\n\n🔗 [Read Full News]({item.link})\n\n#War #WorldNews #Breaking"
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌍 Bot is running! News will auto post to Channel every 30 min.")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_war_news()
    if not news:
        await update.message.reply_text("No new war news right now.")
        return
    for item in news:
        text = f"📰 {item.title}\n🔗 {item.link}"
        await update.message.reply_text(text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))

    # හැම විනාඩි 30කටම Channel එකට Auto News යනවා
    job_queue = app.job_queue
    job_queue.run_repeating(send_auto_news, interval=1800, first=10)

    print("Bot Started...")
    app.run_polling()
