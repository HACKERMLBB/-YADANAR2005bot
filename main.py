import os
import asyncio
import feedparser
import hashlib
from flask import Flask
import threading
from telegram import Bot
from telegram.constants import ParseMode

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Running!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_flask, daemon=True).start()

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
    {"lang": "RUSSIAN", "flag": "🇷🇺", "name": "BBC Russian", "url": "https://feeds.bbci.co.uk/russian/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "BBC Burmese", "url": "https://feeds.bbci.co.uk/burmese/rss.xml"},
]

seen = set()
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
                text = f"{feed_info['flag']} <b>[{feed_info['lang']} - {feed_info['name']}]</b>\n\n{title}\n\n🔗 <a href='{link}'>Read Full News</a>\n\n⚡ Powered by <a href='https://t.me/bigolive_asia'>@bigolive_asia</a>"
                for ch in CHANNEL_IDS:
                    try:
                        await bot.send_message(chat_id=ch, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
                    except Exception as e:
                        print(f"Send fail {ch}: {e}")
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Feed fail {feed_info['name']}: {e}")

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Bot Started")
    while True:
        await check_news(bot)
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
