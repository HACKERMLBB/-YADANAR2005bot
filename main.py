# File Name: Main.py
import os
import asyncio
import feedparser
import hashlib
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# --- මේ ටික අනිවාර්යයි, නැත්නම් Render එකේ Crash වෙනවා ---
try:
    asyncio.set_event_loop(asyncio.new_event_loop())
except RuntimeError:
    pass

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is Running!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port, use_reloader=False)
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_IDS = [c.strip() for c in os.environ.get("CHANNEL_IDS", "").split(",") if c.strip()]
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

FEEDS = [
    {"lang": "WORLD", "flag": "🌍", "name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"lang": "SRI LANKA", "flag": "🇱🇰", "name": "Sri Lanka", "url": "https://news.google.com/rss/search?q=Sri+Lanka&hl=en&gl=LK&ceid=LK:en"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "BBC Sinhala", "url": "https://feeds.bbci.co.uk/sinhala/rss.xml"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "Lanka Sinhala", "url": "https://news.google.com/rss/search?q=Sri+Lanka&hl=si&gl=LK&ceid=LK:si"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "BBC Burmese", "url": "https://feeds.bbci.co.uk/burmese/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Myanmar News", "url": "https://news.google.com/rss/search?q=Myanmar&hl=en&gl=MM&ceid=MM:en"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "India News", "url": "https://news.google.com/rss/search?q=India&hl=en&gl=IN&ceid=IN:en"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "BBC Hindi", "url": "https://feeds.bbci.co.uk/hindi/rss.xml"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Thailand News", "url": "https://news.google.com/rss/search?q=Thailand&hl=en&gl=TH&ceid=TH:en"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "BBC Thai", "url": "https://feeds.bbci.co.uk/thai/rss.xml"},
    {"lang": "JAPAN", "flag": "🇯🇵", "name": "Japan News", "url": "https://news.google.com/rss/search?q=Japan&hl=en&gl=JP&ceid=JP:en"},
    {"lang": "KOREA", "flag": "🇰🇷", "name": "Korea News", "url": "https://news.google.com/rss/search?q=Korea&hl=en&gl=KR&ceid=KR:en"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "China News", "url": "https://news.google.com/rss/search?q=China&hl=en&gl=CN&ceid=CN:en"},
    {"lang": "UK", "flag": "🇬🇧", "name": "BBC UK", "url": "https://feeds.bbci.co.uk/news/uk/rss.xml"},
    {"lang": "USA", "flag": "🇺🇸", "name": "USA News", "url": "https://news.google.com/rss/search?q=USA&hl=en&gl=US&ceid=US:en"},
    {"lang": "UKRAINE", "flag": "🇺🇦", "name": "Ukraine News", "url": "https://news.google.com/rss/search?q=Ukraine&hl=en&gl=UA&ceid=UA:en"},
    {"lang": "ISRAEL", "flag": "🇮🇱", "name": "Israel News", "url": "https://news.google.com/rss/search?q=Israel&hl=en&gl=IL&ceid=IL:en"},
    {"lang": "IRAN", "flag": "🇮🇷", "name": "Iran News", "url": "https://news.google.com/rss/search?q=Iran&hl=en&gl=IR&ceid=IR:en"},
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "Brazil News", "url": "https://news.google.com/rss/search?q=Brazil&hl=en&gl=BR&ceid=BR:en"},
    {"lang": "PAKISTAN", "flag": "🇵🇰", "name": "Pakistan News", "url": "https://news.google.com/rss/search?q=Pakistan&hl=en&gl=PK&ceid=PK:en"},
    {"lang": "BANGLADESH", "flag": "🇧🇩", "name": "Bangladesh News", "url": "https://news.google.com/rss/search?q=Bangladesh&hl=en&gl=BD&ceid=BD:en"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "Philippines News", "url": "https://news.google.com/rss/search?q=Philippines&hl=en&gl=PH&ceid=PH:en"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Indonesia News", "url": "https://news.google.com/rss/search?q=Indonesia&hl=en&gl=ID&ceid=ID:en"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "Vietnam News", "url": "https://news.google.com/rss/search?q=Vietnam&hl=en&gl=VN&ceid=VN:en"},
]

seen = set()

def make_text(f, title, link):
    return f"{f['flag']} <b>[{f['lang']} - {f['name']}]</b>\n\n{title}\n\n🔗 <a href='{link}'>Read Full News</a>\n\n⚡ Powered by @bigolive_asia"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 News Bot Running!\n\n👉 /news Sri Lanka\n👉 /news Myanmar\n👉 /news India\n👉 /countries - All Countries\n👉 /latest - Latest News"
    )

async def news_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("✍️ Ex: /news Sri Lanka\n/news Myanmar\n/news India")
        return
    query = " ".join(context.args).strip().upper()
    if "LANKA" in query or "SINHALA" in query:
        query = "SRI LANKA"
    matched = [f for f in FEEDS if query == f["lang"] or query in f["name"].upper()]
    if query == "SRI LANKA":
        matched += [f for f in FEEDS if f["lang"] == "SINHALA" and f not in matched]
    if not matched:
        await update.message.reply_text("❌ Not found. Try /countries")
        return
    await update.message.reply_text(f"📰 {query} - Latest News...")
    count = 0
    for f in matched:
        try:
            feed = feedparser.parse(f["url"])
            if not feed.entries: continue
            e = feed.entries[0]
            await update.message.reply_text(make_text(f, e.get("title","No Title"), e.get("link","")), parse_mode=ParseMode.HTML)
            count += 1
            await asyncio.sleep(0.7)
            if count >= 10: break
        except: pass
    if count == 0:
        await update.message.reply_text("😔 News not found now.")

async def countries_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    langs = sorted(set([f"{f['flag']} {f['lang']}" for f in FEEDS]))
    await update.message.reply_text("🌍 All Countries:\n\n" + "\n".join(langs) + "\n\nUse: /news Country")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Fetching...")
    for f in FEEDS[:10]:
        try:
            feed = feedparser.parse(f["url"])
            if not feed.entries: continue
            e = feed.entries[0]
            await update.message.reply_text(make_text(f, e.get("title",""), e.get("link","")), parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.7)
        except: pass

async def check_news(bot):
    for f in FEEDS:
        try:
            feed = feedparser.parse(f["url"])
            for e in feed.entries[:2]:
                link = e.get("link","")
                if not link: continue
                h = hashlib.md5(link.encode()).hexdigest()
                if h in seen: continue
                seen.add(h)
                text = make_text(f, e.get("title",""), link)
                targets = list(CHANNEL_IDS)
                if OWNER_ID: targets.append(OWNER_ID)
                for ch in targets:
                    try:
                        await bot.send_message(chat_id=ch, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
                    except Exception as ex:
                        print(f"Send fail {ch}: {ex}")
                await asyncio.sleep(0.5)
        except Exception as ex:
            print(f"Feed fail {f['name']}: {ex}")

async def auto_loop(bot):
    while True:
        await check_news(bot)
        await asyncio.sleep(180)

async def post_init(app):
    asyncio.create_task(auto_loop(app.bot))

def main():
    # --- main එක ඇතුලෙත් Loop එක හදනවා, 100% Crash වෙන්නේ නෑ ---
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news_country))
    app.add_handler(CommandHandler("countries", countries_list))
    app.add_handler(CommandHandler("latest", latest))
    print("Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
