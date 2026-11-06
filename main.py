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
    # --- ENGLISH WORLD ---
    {"lang": "ENGLISH", "flag": "🇬🇧", "name": "BBC", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"lang": "ENGLISH", "flag": "🇺🇸", "name": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"lang": "ENGLISH", "flag": "🇺🇸", "name": "Fox News", "url": "https://moxie.foxnews.com/google-publisher/world.xml"},
    {"lang": "ENGLISH", "flag": "🇶🇦", "name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"lang": "ENGLISH", "flag": "🌍", "name": "Reuters", "url": "https://www.reuters.com/rssFeed/worldNews"},

    # --- SPANISH WORLD ---
    {"lang": "SPANISH", "flag": "🇪🇸", "name": "BBC Mundo", "url": "https://feeds.bbci.co.uk/mundo/rss.xml"},
    {"lang": "SPANISH", "flag": "🇪🇸", "name": "DW Espanol", "url": "https://rss.dw.com/rdf/rss-es-all"},

    # --- RUSSIAN ---
    {"lang": "RUSSIAN", "flag": "🇷🇺", "name": "BBC Russian", "url": "https://feeds.bbci.co.uk/russian/rss.xml"},
    {"lang": "RUSSIAN", "flag": "🇷🇺", "name": "DW Russian", "url": "https://rss.dw.com/rdf/rss-ru-all"},

    # --- HINDI ---
    {"lang": "HINDI", "flag": "🇮🇳", "name": "BBC Hindi", "url": "https://feeds.bbci.co.uk/hindi/rss.xml"},
    {"lang": "HINDI", "flag": "🇮🇳", "name": "DW Hindi", "url": "https://rss.dw.com/rdf/rss-hi-all"},

    # --- TAMIL ---
    {"lang": "TAMIL", "flag": "🇱🇰", "name": "BBC Tamil", "url": "https://feeds.bbci.co.uk/tamil/rss.xml"},
    {"lang": "TAMIL", "flag": "🇱🇰", "name": "DW Tamil", "url": "https://rss.dw.com/rdf/rss-ta-all"},

    # --- SINHALA ---
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "Hiru News", "url": "https://www.hirunews.lk/rss/sinhala.xml"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "Ada Derana", "url": "https://sinhala.adaderana.lk/rss.php"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "BBC Sinhala", "url": "https://feeds.bbci.co.uk/sinhala/rss.xml"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "NewsFirst Sinhala", "url": "https://sinhala.newsfirst.lk/feed"},

    # --- MYANMAR LOCAL ---
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "BBC Burmese", "url": "https://feeds.bbci.co.uk/burmese/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "VOA Burmese", "url": "https://burmese.voanews.com/api/epiqq"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Irrawaddy Burmese", "url": "https://burma.irrawaddy.com/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Irrawaddy English", "url": "https://www.irrawaddy.com/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "DVB Myanmar", "url": "https://www.dvb.no/feed"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Mizzima", "url": "https://www.mizzima.com/feed"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Myanmar Now", "url": "https://www.myanmar-now.org/en/rss.xml"},

    # --- PHILIPPINES ---
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "GMA News", "url": "https://www.gmanetwork.com/news/rss/"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "Inquirer", "url": "https://www.inquirer.net/fullfeed"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "Rappler", "url": "https://www.rappler.com/feed/"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "ABS-CBN News", "url": "https://news.abs-cbn.com/rss"},

    # --- INDONESIA ---
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "BBC Indonesia", "url": "https://feeds.bbci.co.uk/indonesia/rss.xml"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "DW Indonesia", "url": "https://rss.dw.com/rdf/rss-id-all"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Kompas", "url": "https://www.kompas.com/rss"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Detik", "url": "https://rss.detik.com/"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Tempo", "url": "https://rss.tempo.co/"},

    # --- COLOMBIA ---
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "El Tiempo Colombia", "url": "https://www.eltiempo.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "El Espectador", "url": "https://www.elespectador.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "Semana Colombia", "url": "https://www.semana.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "Caracol Noticias", "url": "https://noticias.caracoltv.com/rss.xml"},

    # --- MEXICO / BRAZIL / ARGENTINA / LATIN ---
    {"lang": "MEXICO", "flag": "🇲🇽", "name": "El Universal Mexico", "url": "https://www.eluniversal.com.mx/rss.xml"},
    {"lang": "MEXICO", "flag": "🇲🇽", "name": "Milenio Mexico", "url": "https://www.milenio.com/rss.xml"},
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "G1 Brazil", "url": "https://g1.globo.com/rss/g1/"},
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "BBC Brasil", "url": "https://feeds.bbci.co.uk/portuguese/rss.xml"},
    {"lang": "ARGENTINA", "flag": "🇦🇷", "name": "Clarin Argentina", "url": "https://www.clarin.com/rss.xml"},
    {"lang": "ARGENTINA", "flag": "🇦🇷", "name": "Infobae Argentina", "url": "https://www.infobae.com/america/rss/"},
    {"lang": "CHILE", "flag": "🇨🇱", "name": "Emol Chile", "url": "https://www.emol.com/rss.xml"},
    {"lang": "PERU", "flag": "🇵🇪", "name": "El Comercio Peru", "url": "https://elcomercio.pe/rss/"},
    {"lang": "LATIN", "flag": "🌎", "name": "CNN Espanol", "url": "https://cnnespanol.cnn.com/feed/"},

    # --- CHINA - NEW ---
    {"lang": "CHINA", "flag": "🇨🇳", "name": "BBC Chinese", "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "BBC Chinese Trad", "url": "https://feeds.bbci.co.uk/zhongwen/trad/rss.xml"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "DW Chinese", "url": "https://rss.dw.com/rdf/rss-zh-cn-all"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "China Daily", "url": "https://www.chinadaily.com.cn/rss/world_rss.xml"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "China Daily China", "url": "https://www.chinadaily.com.cn/rss/china_rss.xml"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "Xinhua News", "url": "http://www.xinhuanet.com/english/rss/worldrss.xml"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "CGTN", "url": "https://www.cgtn.com/subscribe/rss/section/news.xml"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "SCMP Hong Kong", "url": "https://www.scmp.com/rss/91/feed"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "VOA Chinese", "url": "https://www.voachinese.com/api/epiqq"},
    {"lang": "CHINA", "flag": "🇨🇳", "name": "RFA Chinese", "url": "https://www.rfa.org/mandarin/rss2.xml"},

    # --- EUROPE - UK ---
    {"lang": "UK", "flag": "🇬🇧", "name": "BBC UK", "url": "https://feeds.bbci.co.uk/news/uk/rss.xml"},
    {"lang": "UK", "flag": "🇬🇧", "name": "The Guardian UK", "url": "https://www.theguardian.com/uk/rss"},
    {"lang": "UK", "flag": "🇬🇧", "name": "Sky News UK", "url": "https://feeds.skynews.com/feeds/rss/home.xml"},
    {"lang": "UK", "flag": "🇬🇧", "name": "Daily Mail UK", "url": "https://www.dailymail.co.uk/home/index.rss"},

    # --- EUROPE - FRANCE ---
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "France 24 English", "url": "https://www.france24.com/en/rss"},
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "France 24 French", "url": "https://www.france24.com/fr/rss"},
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "Le Monde French", "url": "https://www.lemonde.fr/rss/une.xml"},
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "BBC French", "url": "https://feeds.bbci.co.uk/french/rss.xml"},

    # --- EUROPE - GERMANY ---
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "DW English", "url": "https://rss.dw.com/rdf/rss-en-all"},
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "DW German", "url": "https://rss.dw.com/rdf/rss-de-all"},
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "Tagesschau Germany", "url": "https://www.tagesschau.de/xml/rss2/"},
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "Spiegel Germany", "url": "https://www.spiegel.de/schlagzeilen/index.rss"},

    # --- EUROPE - ITALY / SPAIN / OTHERS ---
    {"lang": "ITALY", "flag": "🇮🇹", "name": "ANSA Italy", "url": "https://www.ansa.it/sito/ansait_rss.xml"},
    {"lang": "ITALY", "flag": "🇮🇹", "name": "BBC Italian", "url": "https://feeds.bbci.co.uk/italian/rss.xml"},
    {"lang": "SPAIN", "flag": "🇪🇸", "name": "El Pais Spain", "url": "https://feeds.elpais.com/meridian/rss"},
    {"lang": "SPAIN", "flag": "🇪🇸", "name": "El Mundo Spain", "url": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml"},
    {"lang": "NETHERLANDS", "flag": "🇳🇱", "name": "NOS Netherlands", "url": "https://feeds.nos.nl/nosnieuwsalgemeen"},
    {"lang": "NETHERLANDS", "flag": "🇳🇱", "name": "DW Dutch", "url": "https://rss.dw.com/rdf/rss-nl-all"},
    {"lang": "POLAND", "flag": "🇵🇱", "name": "TVN Poland", "url": "https://tvn24.pl/rss"},
    {"lang": "UKRAINE", "flag": "🇺🇦", "name": "Kyiv Independent", "url": "https://kyivindependent.com/feed/"},
    {"lang": "UKRAINE", "flag": "🇺🇦", "name": "BBC Ukrainian", "url": "https://feeds.bbci.co.uk/ukrainian/rss.xml"},
    {"lang": "TURKEY", "flag": "🇹🇷", "name": "Daily Sabah Turkey", "url": "https://www.dailysabah.com/rss"},
    {"lang": "TURKEY", "flag": "🇹🇷", "name": "BBC Turkish", "url": "https://feeds.bbci.co.uk/turkish/rss.xml"},
    {"lang": "EUROPE", "flag": "🇪🇺", "name": "Euronews", "url": "https://www.euronews.com/rss?format=mrss&level=theme&name=news"},
    {"lang": "EUROPE", "flag": "🇪🇺", "name": "Politico Europe", "url": "https://www.politico.eu/feed/"},
]

seen = set()

def make_text(feed_info, title, link):
    return f"{feed_info['flag']} <b>[{feed_info['lang']} - {feed_info['name']}]</b>\n\n{title}\n\n🔗 <a href='{link}'>Read Full News</a>\n\n⚡ Powered by <a href='https://t.me/bigolive_asia'>@bigolive_asia</a>"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Bot is running! News every 5 min.\n\nRegions: World, China, Europe (UK, France, Germany, Italy, Spain, Netherlands, Poland, Ukraine, Turkey), Latin, Asia\n\n⚡ Powered by https://t.me/bigolive_asia"
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
