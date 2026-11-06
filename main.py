import asyncio
import feedparser
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

# War News RSS Feeds - ලෝකේ ඔක්කොම
FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.reuters.com/reuters/worldNews",
]

def get_war_news():
    keywords = ["war", "attack", "missile", "airstrike", "military", "iran", "israel", "ukraine", "russia", "gaza", "bomb", "troops", "conflict"]
    news = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.title.lower()
                if any(k in title for k in keywords):
                    news.append(f"📰 **{entry.title}**\n🔗 {entry.link}\n")
                if len(news) >= 5:
                    break
        except:
            continue
    return news[:5]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 **World War News Bot**\n\n"
        "Commands:\n"
        "/latest - Latest War News\n"
        "/start - Start Bot\n\n"
        "Auto news every 1 hour! 🚨",
        parse_mode="Markdown"
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Fetching latest war news...")
    news = get_war_news()
    if not news:
        await update.message.reply_text("No new war news right now.")
        return
    text = "🚨 **LATEST WAR NEWS** 🚨\n\n" + "\n\n".join(news)
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=False)

async def auto_news(context: ContextTypes.DEFAULT_TYPE):
    # ඔයාගේ Channel ID / Group ID එක දාන්න මෙතන
    pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    app.run_polling()
