import os
import asyncio
import feedparser
import hashlib
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# --- Flask Port Fix ---
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is Running!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()
# ----------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_IDS = os.environ.get("CHANNEL_IDS", os.environ.get("CHANNEL_ID", "")).split(",")
CHANNEL_IDS = [c.strip() for c in CHANNEL_IDS if c.strip()]

FEEDS = [
    {"lang": "ENGLISH", "flag": "🇬🇧", "name": "BBC", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"lang": "ENGLISH", "flag": "🇺🇸", "name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"lang": "ENGLISH", "flag": "🇺🇸", "name": "Fox News", "url": "https://moxie.foxnews.com/google-publisher/world.xml"},
    {"lang": "ENGLISH", "flag": "🇶🇦", "name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"lang": "ENGLISH", "flag": "🌍", "name": "Reuters", "url": "https://www.reuters.com/rssFeed/worldNews"},
    {"lang": "SPANISH", "flag": "🇪🇸", "name": "BBC Mundo", "url": "https://feeds.bbci.co.uk/mundo/rss.xml"},
    {"lang": "SPANISH", "flag": "🇪🇸", "name": "DW Espanol", "url": "https://rss.dw.com/rdf/rss-es-all"},
    {"lang": "RUSSIAN", "flag": "🇷🇺", "name": "BBC Russian", "url": "https://feeds.bbci.co.uk/russian/rss.xml"},
    {"lang": "RUSSIAN", "flag": "🇷🇺", "name": "DW Russian", "url": "https://rss.dw.com/rdf/rss-ru-all"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "BBC Burmese", "url": "https://feeds.bbci.co.uk/burmese/rss.xml"},
]

seen = set()

def make_text(feed_info, title, link):
    return f"{feed_info['flag']} <b>[{feed_info['lang']} - {feed_info['name']}]</b>\n\n{title}\n\n🔗 <a href='{link}'>Read Full News</a>\n\n⚡ Powered by <a href='https://t.me/bigolive_asia'>@bigolive_asia</a>"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Bot is running! News will auto post to Channel every 5 min.\n\n⚡ Powered by https://t.me/bigolive_asia"
    )

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Fetching latest news...")
    for feed_info in FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            if not feed.entries: continue
            entry = feed.entries[0]
            link = entry.get("link", "")
            title = entry.get("title", "No Title")
            text = make_text(feed_info, title, link)
            await update.message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Latest fail {feed_info['name']}: {e}")

async def check_news(bot):
    for feed_info in FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:3]:
                link = entry.get("link", "")
                if not link: continue
                h = hashlib.md5(link.encode()).hexdigest()
                if h in seen: continue
                seen.add(h)
                title = entry.get("title", "No Title")
                text = make_text(feed_info, title, link)
                for ch in CHANNEL_IDS:
                    try:
                        await bot.send_message(chat_id=ch, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
                    except Exception as e:
                        print(f"Send fail {ch}: {e}")
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Feed fail {feed_info['name']}: {e}")

async def auto_loop(bot):
    while True:
        await check_news(bot)
        await asyncio.sleep(300)

async def post_init(app):
    asyncio.create_task(auto_loop(app.bot))

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    print("Bot Started - Auto + Commands")
    app.run_polling()

if __name__ == "__main__":
    main()
