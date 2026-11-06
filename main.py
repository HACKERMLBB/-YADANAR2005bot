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

    # --- SPANISH / RUSSIAN ---
    {"lang": "SPANISH", "flag": "🇪🇸", "name": "BBC Mundo", "url": "https://feeds.bbci.co.uk/mundo/rss.xml"},
    {"lang": "SPANISH", "flag": "🇪🇸", "name": "DW Espanol", "url": "https://rss.dw.com/rdf/rss-es-all"},
    {"lang": "RUSSIAN", "flag": "🇷🇺", "name": "BBC Russian", "url": "https://feeds.bbci.co.uk/russian/rss.xml"},
    {"lang": "RUSSIAN", "flag": "🇷🇺", "name": "DW Russian", "url": "https://rss.dw.com/rdf/rss-ru-all"},

    # --- INDIA ---
    {"lang": "INDIA", "flag": "🇮🇳", "name": "NDTV India", "url": "https://feeds.feedburner.com/ndtvnews-top-stories"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Indian Express", "url": "https://indianexpress.com/feed/"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Hindustan Times", "url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "India Today", "url": "https://www.indiatoday.in/rss/home"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Republic India", "url": "https://www.republicworld.com/rss"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "DD News India", "url": "https://ddnews.gov.in/feed"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Deccan Herald", "url": "https://www.deccanherald.com/rss/national.rss"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Zee News India", "url": "https://zeenews.india.com/rss/india-national-news.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Economic Times India", "url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "BBC Hindi", "url": "https://feeds.bbci.co.uk/hindi/rss.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "DW Hindi", "url": "https://rss.dw.com/rdf/rss-hi-all"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "BBC Tamil", "url": "https://feeds.bbci.co.uk/tamil/rss.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "DW Tamil", "url": "https://rss.dw.com/rdf/rss-ta-all"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Aaj Tak Hindi", "url": "https://www.aajtak.in/rss"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "ABP News Hindi", "url": "https://www.abplive.com/feed"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Manorama Malayalam", "url": "https://www.onmanorama.com/rss.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Mathrubhumi Malayalam", "url": "https://www.mathrubhumi.com/rss.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Eenadu Telugu", "url": "https://www.eenadu.net/rss"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Sakshi Telugu", "url": "https://www.sakshi.com/rss"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Dinamalar Tamil", "url": "https://www.dinamalar.com/rss.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Anandabazar Bengali", "url": "https://www.anandabazar.com/rss.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Dainik Bhaskar Hindi", "url": "https://www.bhaskar.com/rss-v1--category-0.xml"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "WION India Global", "url": "https://www.wionews.com/rss"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "Firstpost India", "url": "https://www.firstpost.com/feed"},

    # --- SINHALA ---
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "Hiru News", "url": "https://www.hirunews.lk/rss/sinhala.xml"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "Ada Derana", "url": "https://sinhala.adaderana.lk/rss.php"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "BBC Sinhala", "url": "https://feeds.bbci.co.uk/sinhala/rss.xml"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "NewsFirst Sinhala", "url": "https://sinhala.newsfirst.lk/feed"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "Lankadeepa", "url": "https://www.lankadeepa.lk/rss/sinhala.xml"},

    # --- MYANMAR ---
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "BBC Burmese", "url": "https://feeds.bbci.co.uk/burmese/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "VOA Burmese", "url": "https://burmese.voanews.com/api/epiqq"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Irrawaddy Burmese", "url": "https://burma.irrawaddy.com/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Irrawaddy English", "url": "https://www.irrawaddy.com/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "DVB Myanmar", "url": "https://www.dvb.no/feed"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Mizzima", "url": "https://www.mizzima.com/feed"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Myanmar Now", "url": "https://www.myanmar-now.org/en/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "RFA Burmese", "url": "https://www.rfa.org/burmese/rss2.xml"},

    # --- PHILIPPINES ---
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "GMA News", "url": "https://www.gmanetwork.com/news/rss/"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "Inquirer", "url": "https://www.inquirer.net/fullfeed"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "Rappler", "url": "https://www.rappler.com/feed/"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "ABS-CBN News", "url": "https://news.abs-cbn.com/rss"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "PhilStar", "url": "https://www.philstar.com/rss/headlines"},

    # --- INDONESIA ---
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "BBC Indonesia", "url": "https://feeds.bbci.co.uk/indonesia/rss.xml"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "DW Indonesia", "url": "https://rss.dw.com/rdf/rss-id-all"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Kompas", "url": "https://www.kompas.com/rss"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Detik", "url": "https://rss.detik.com/"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Tempo", "url": "https://rss.tempo.co/"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Antara News", "url": "https://en.antaranews.com/rss"},

    # --- CHINA ---
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

    # --- ENGLISH GLOBAL ---
    {"lang": "WORLD", "flag": "🌍", "name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "Reuters World", "url": "https://www.reuters.com/rssfeed/worldNews"},
    {"lang": "WORLD", "flag": "🌍", "name": "AP News", "url": "https://apnews.com/rss"},
    {"lang": "WORLD", "flag": "🌍", "name": "France 24 English", "url": "https://www.france24.com/en/rss"},
    {"lang": "WORLD", "flag": "🌍", "name": "DW English", "url": "https://rss.dw.com/rdf/rss-en-all"},
    {"lang": "WORLD", "flag": "🌍", "name": "Euronews English", "url": "https://www.euronews.com/rss"},
    {"lang": "WORLD", "flag": "🌍", "name": "NPR World", "url": "https://feeds.npr.org/1004/rss.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "NY Times World", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "Washington Post World", "url": "https://feeds.washingtonpost.com/rss/world"},

    # --- ENGLISH LOCAL ---
    {"lang": "SRI LANKA", "flag": "🇱🇰", "name": "Daily Mirror", "url": "https://www.dailymirror.lk/rss"},
    {"lang": "SRI LANKA", "flag": "🇱🇰", "name": "Daily FT", "url": "https://www.ft.lk/rss"},
    {"lang": "SRI LANKA", "flag": "🇱🇰", "name": "Daily News", "url": "https://www.dailynews.lk/rss"},
    {"lang": "SRI LANKA", "flag": "🇱🇰", "name": "The Island", "url": "https://www.island.lk/rss"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "VnExpress English", "url": "https://e.vnexpress.net/rss/news.rss"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "VietnamNet English", "url": "https://vietnamnet.vn/en/rss"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "Hanoi Times", "url": "https://hanoitimes.vn/rss"},
    {"lang": "CAMBODIA", "flag": "🇰🇭", "name": "Khmer Times English", "url": "https://www.khmertimeskh.com/feed/"},
    {"lang": "CAMBODIA", "flag": "🇰🇭", "name": "Cambodianess", "url": "https://cambodianess.com/feed/"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "The Star English", "url": "https://www.thestar.com.my/rss/News/Nation"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "Malaysiakini", "url": "https://www.malaysiakini.com/rss/en/news.rss"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "Sinar Daily", "url": "https://www.sinardaily.my/feed/"},
    {"lang": "NEPAL", "flag": "🇳🇵", "name": "My Republica", "url": "https://myrepublica.nagariknetwork.com/feed/"},
    {"lang": "NEPAL", "flag": "🇳🇵", "name": "Himalayan Times", "url": "https://thehimalayantimes.com/rss"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Jakarta Post", "url": "https://www.thejakartapost.com/rss"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Antara English", "url": "https://en.antaranews.com/rss/top-story"},

    # --- EUROPE ---
    {"lang": "UK", "flag": "🇬🇧", "name": "BBC UK", "url": "https://feeds.bbci.co.uk/news/uk/rss.xml"},
    {"lang": "UK", "flag": "🇬🇧", "name": "The Guardian UK", "url": "https://www.theguardian.com/uk/rss"},
    {"lang": "UK", "flag": "🇬🇧", "name": "Sky News UK", "url": "https://feeds.skynews.com/feeds/rss/home.xml"},
    {"lang": "UK", "flag": "🇬🇧", "name": "Daily Mail UK", "url": "https://www.dailymail.co.uk/home/index.rss"},
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "France 24 French", "url": "https://www.france24.com/fr/rss"},
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "Le Monde French", "url": "https://www.lemonde.fr/rss/une.xml"},
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "BBC French", "url": "https://feeds.bbci.co.uk/french/rss.xml"},
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "DW German", "url": "https://rss.dw.com/rdf/rss-de-all"},
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "Tagesschau Germany", "url": "https://www.tagesschau.de/xml/rss2/"},
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "Spiegel Germany", "url": "https://www.spiegel.de/schlagzeilen/index.rss"},
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

    # --- WEST ASIA / MIDDLE EAST ---
    {"lang": "WEST ASIA", "flag": "🌍", "name": "BBC Arabic", "url": "https://feeds.bbci.co.uk/arabic/rss.xml"},
    {"lang": "WEST ASIA", "flag": "🌍", "name": "DW Arabic", "url": "https://rss.dw.com/rdf/rss-ar-all"},
    {"lang": "WEST ASIA", "flag": "🌍", "name": "Al Jazeera Arabic", "url": "https://www.aljazeera.net/aljazeera/rss"},
    {"lang": "WEST ASIA", "flag": "🌍", "name": "Al Arabiya English", "url": "https://english.alarabiya.net/feed/rss2.xml"},
    {"lang": "WEST ASIA", "flag": "🌍", "name": "Al Arabiya Arabic", "url": "https://www.alarabiya.net/feed/rss2.xml"},
    {"lang": "WEST ASIA", "flag": "🌍", "name": "Middle East Eye", "url": "https://www.middleeasteye.net/rss"},
    {"lang": "SAUDI", "flag": "🇸🇦", "name": "Arab News Saudi", "url": "https://www.arabnews.com/rss.xml"},
    {"lang": "SAUDI", "flag": "🇸🇦", "name": "Saudi Gazette", "url": "https://saudigazette.com.sa/rss.xml"},
    {"lang": "SAUDI", "flag": "🇸🇦", "name": "Saudi Press Agency", "url": "https://www.spa.gov.sa/rss.xml"},
    {"lang": "UAE", "flag": "🇦🇪", "name": "Gulf News UAE", "url": "https://gulfnews.com/rss"},
    {"lang": "UAE", "flag": "🇦🇪", "name": "Khaleej Times UAE", "url": "https://www.khaleejtimes.com/rss"},
    {"lang": "UAE", "flag": "🇦🇪", "name": "The National UAE", "url": "https://www.thenationalnews.com/rss"},
    {"lang": "QATAR", "flag": "🇶🇦", "name": "Gulf Times Qatar", "url": "https://www.gulf-times.com/rss.xml"},
    {"lang": "QATAR", "flag": "🇶🇦", "name": "The Peninsula Qatar", "url": "https://www.thepeninsulaqatar.com/rss"},
    {"lang": "ISRAEL", "flag": "🇮🇱", "name": "Times of Israel", "url": "https://www.timesofisrael.com/feed/"},
    {"lang": "ISRAEL", "flag": "🇮🇱", "name": "Jerusalem Post", "url": "https://www.jpost.com/rss/rssfeedsfrontpage.aspx"},
    {"lang": "ISRAEL", "flag": "🇮🇱", "name": "Haaretz Israel", "url": "https://www.haaretz.com/feed"},
    {"lang": "ISRAEL", "flag": "🇮🇱", "name": "Ynet Israel", "url": "https://www.ynetnews.com/category/3082/rss2.xml"},
    {"lang": "IRAN", "flag": "🇮🇷", "name": "Tehran Times Iran", "url": "https://www.tehrantimes.com/rss"},
    {"lang": "IRAN", "flag": "🇮🇷", "name": "Press TV Iran", "url": "https://www.presstv.ir/RSS"},
    {"lang": "IRAN", "flag": "🇮🇷", "name": "BBC Persian", "url": "https://feeds.bbci.co.uk/persian/rss.xml"},
    {"lang": "IRAN", "flag": "🇮🇷", "name": "Iran International", "url": "https://www.iranintl.com/en/feed"},
    {"lang": "IRAQ", "flag": "🇮🇶", "name": "Iraq News", "url": "https://www.iraqinews.com/feed/"},
    {"lang": "JORDAN", "flag": "🇯🇴", "name": "Jordan Times", "url": "https://www.jordantimes.com/rss"},
    {"lang": "LEBANON", "flag": "🇱🇧", "name": "Daily Star Lebanon", "url": "https://www.dailystar.com.lb/rss"},
    {"lang": "LEBANON", "flag": "🇱🇧", "name": "LBC Lebanon", "url": "https://www.lbcgroup.tv/rss"},
    {"lang": "SYRIA", "flag": "🇸🇾", "name": "SANA Syria", "url": "https://sana.sy/en/rss.xml"},
    {"lang": "KUWAIT", "flag": "🇰🇼", "name": "Arab Times Kuwait", "url": "https://www.arabtimesonline.com/feed/"},
    {"lang": "KUWAIT", "flag": "🇰🇼", "name": "Kuwait Times", "url": "https://www.kuwaittimes.com/feed/"},
    {"lang": "BAHRAIN", "flag": "🇧🇭", "name": "GDN Bahrain", "url": "https://www.gdnonline.com/rss.xml"},
    {"lang": "OMAN", "flag": "🇴🇲", "name": "Times of Oman", "url": "https://timesofoman.com/rss"},
    {"lang": "OMAN", "flag": "🇴🇲", "name": "Muscat Daily Oman", "url": "https://www.muscatdaily.com/rss"},
    {"lang": "YEMEN", "flag": "🇾🇪", "name": "Yemen Online", "url": "https://www.yemenonline.info/feed/"},
    {"lang": "PALESTINE", "flag": "🇵🇸", "name": "WAFA Palestine", "url": "https://english.wafa.ps/rss"},

    # --- EAST ASIA ---
    {"lang": "JAPAN", "flag": "🇯🇵", "name": "NHK Japan", "url": "https://www3.nhk.or.jp/nhkworld/en/news/rss.xml"},
    {"lang": "JAPAN", "flag": "🇯🇵", "name": "Japan Times", "url": "https://www.japantimes.co.jp/feed/"},
    {"lang": "JAPAN", "flag": "🇯🇵", "name": "BBC Japanese", "url": "https://feeds.bbci.co.uk/japanese/rss.xml"},
    {"lang": "JAPAN", "flag": "🇯🇵", "name": "Kyodo News Japan", "url": "https://english.kyodonews.net/rss"},
    {"lang": "JAPAN", "flag": "🇯🇵", "name": "Asahi Shimbun Japan", "url": "https://www.asahi.com/rss/asahi/newsheadlines.xml"},
    {"lang": "KOREA", "flag": "🇰🇷", "name": "Korea Herald", "url": "http://www.koreaherald.com/rss/index.xml"},
    {"lang": "KOREA", "flag": "🇰🇷", "name": "Korea Times", "url": "https://www.koreatimes.co.kr/www/rss/nation.xml"},
    {"lang": "KOREA", "flag": "🇰🇷", "name": "Yonhap News Korea", "url": "https://en.yna.co.kr/rss/all"},
    {"lang": "KOREA", "flag": "🇰🇷", "name": "BBC Korean", "url": "https://feeds.bbci.co.uk/korean/rss.xml"},
    {"lang": "KOREA", "flag": "🇰🇷", "name": "DW Korean", "url": "https://rss.dw.com/rdf/rss-ko-all"},
    {"lang": "TAIWAN", "flag": "🇹🇼", "name": "Focus Taiwan", "url": "https://focustaiwan.tw/rss"},
    {"lang": "TAIWAN", "flag": "🇹🇼", "name": "Taipei Times Taiwan", "url": "https://www.taipeitimes.com/xml/index.rss"},
    {"lang": "TAIWAN", "flag": "🇹🇼", "name": "Taiwan News", "url": "https://www.taiwannews.com.tw/rss"},
    {"lang": "HONG KONG", "flag": "🇭🇰", "name": "Hong Kong Free Press", "url": "https://hongkongfp.com/feed/"},
    {"lang": "MONGOLIA", "flag": "🇲🇳", "name": "Montsame Mongolia", "url": "https://montsame.mn/en/rss"},
    {"lang": "EAST ASIA", "flag": "🌏", "name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar"},

    # --- MEXICO / LATIN ---
    {"lang": "MEXICO", "flag": "🇲🇽", "name": "El Universal Mexico", "url": "https://www.eluniversal.com.mx/rss.xml"},
    {"lang": "MEXICO", "flag": "🇲🇽", "name": "Milenio Mexico", "url": "https://www.milenio.com/rss.xml"},
    {"lang": "MEXICO", "flag": "🇲🇽", "name": "DW Mexico / Latam", "url": "https://rss.dw.com/rdf/rss-es-latam"},
    {"lang": "LATIN", "flag": "🌎", "name": "CNN Espanol", "url": "https://cnnespanol.cnn.com/feed/"},
    {"lang": "LATIN", "flag": "🌎", "name": "Telemundo", "url": "https://www.telemundo.com/rss.xml"},

    # --- SOUTH AMERICA ---
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "G1 Brazil", "url": "https://g1.globo.com/rss/g1/"},
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "Folha Brazil", "url": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml"},
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "BBC Brasil", "url": "https://feeds.bbci.co.uk/portuguese/rss.xml"},
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "Estadao Brazil", "url": "https://www.estadao.com.br/rss.xml"},
    {"lang": "ARGENTINA", "flag": "🇦🇷", "name": "Clarin Argentina", "url": "https://www.clarin.com/rss.xml"},
    {"lang": "ARGENTINA", "flag": "🇦🇷", "name": "La Nacion Argentina", "url": "https://www.lanacion.com.ar/arc/outboundfeeds/rss/"},
    {"lang": "ARGENTINA", "flag": "🇦🇷", "name": "Infobae Argentina", "url": "https://www.infobae.com/america/rss/"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "El Tiempo Colombia", "url": "https://www.eltiempo.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "El Espectador", "url": "https://www.elespectador.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "Semana Colombia", "url": "https://www.semana.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "Caracol Noticias", "url": "https://noticias.caracoltv.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "RCN Noticias", "url": "https://www.noticiasrcn.com/rss.xml"},
    {"lang": "COLOMBIA", "flag": "🇨🇴", "name": "Blu Radio Colombia", "url": "https://www.bluradio.com/rss.xml"},
    {"lang": "CHILE", "flag": "🇨🇱", "name": "Emol Chile", "url": "https://www.emol.com/rss.xml"},
    {"lang": "CHILE", "flag": "🇨🇱", "name": "La Tercera Chile", "url": "https://www.latercera.com/rss.xml"},
    {"lang": "CHILE", "flag": "🇨🇱", "name": "BioBio Chile", "url": "https://www.biobiochile.cl/rss.xml"},
    {"lang": "CHILE", "flag": "🇨🇱", "name": "Cooperativa Chile", "url": "https://www.cooperativa.cl/rss.xml"},
    {"lang": "PERU", "flag": "🇵🇪", "name": "El Comercio Peru", "url": "https://elcomercio.pe/rss/"},
    {"lang": "PERU", "flag": "🇵🇪", "name": "RPP Peru", "url": "https://rpp.pe/rss.xml"},
    {"lang": "PERU", "flag": "🇵🇪", "name": "La Republica Peru", "url": "https://larepublica.pe/rss.xml"},
    {"lang": "PERU", "flag": "🇵🇪", "name": "Gestion Peru", "url": "https://gestion.pe/rss.xml"},
    {"lang": "VENEZUELA", "flag": "🇻🇪", "name": "El Nacional Venezuela", "url": "https://www.elnacional.com/rss/"},
    {"lang": "VENEZUELA", "flag": "🇻🇪", "name": "El Universal Venezuela", "url": "https://www.eluniversal.com/rss.xml"},
    {"lang": "VENEZUELA", "flag": "🇻🇪", "name": "Telesur Venezuela", "url": "https://www.telesurtv.net/rss.xml"},
    {"lang": "VENEZUELA", "flag": "🇻🇪", "name": "Efecto Cocuyo Venezuela", "url": "https://efectococuyo.com/feed/"},
    {"lang": "ECUADOR", "flag": "🇪🇨", "name": "El Comercio Ecuador", "url": "https://www.elcomercio.com/rss.xml"},
    {"lang": "ECUADOR", "flag": "🇪🇨", "name": "El Universo Ecuador", "url": "https://www.eluniverso.com/rss.xml"},
    {"lang": "ECUADOR", "flag": "🇪🇨", "name": "Primicias Ecuador", "url": "https://www.primicias.ec/rss.xml"},
    {"lang": "BOLIVIA", "flag": "🇧🇴", "name": "El Deber Bolivia", "url": "https://eldeber.com.bo/rss.xml"},
    {"lang": "BOLIVIA", "flag": "🇧🇴", "name": "Los Tiempos Bolivia", "url": "https://www.lostiempos.com/rss.xml"},
    {"lang": "BOLIVIA", "flag": "🇧🇴", "name": "Pagina Siete Bolivia", "url": "https://www.paginasiete.bo/rss.xml"},
    {"lang": "PARAGUAY", "flag": "🇵🇾", "name": "ABC Paraguay", "url": "https://www.abc.com.py/rss.xml"},
    {"lang": "PARAGUAY", "flag": "🇵🇾", "name": "Ultima Hora Paraguay", "url": "https://www.ultimahora.com/rss.xml"},
    {"lang": "PARAGUAY", "flag": "🇵🇾", "name": "La Nacion Paraguay", "url": "https://www.lanacion.com.py/rss.xml"},
    {"lang": "URUGUAY", "flag": "🇺🇾", "name": "El Pais Uruguay", "url": "https://www.elpais.com.uy/rss.xml"},
    {"lang": "URUGUAY", "flag": "🇺🇾", "name": "El Observador Uruguay", "url": "https://www.elobservador.com.uy/rss.xml"},
    {"lang": "URUGUAY", "flag": "🇺🇾", "name": "Montevideo Portal", "url": "https://www.montevideo.com.uy/rss.xml"},
    {"lang": "GUYANA", "flag": "🇬🇾", "name": "Stabroek News Guyana", "url": "https://www.stabroeknews.com/feed/"},
    {"lang": "GUYANA", "flag": "🇬🇾", "name": "Guyana Chronicle", "url": "https://guyanachronicle.com/feed/"},
    {"lang": "SURINAME", "flag": "🇸🇷", "name": "Suriname Herald", "url": "https://www.surinameherald.com/feed/"},
    {"lang": "SURINAME", "flag": "🇸🇷", "name": "Starnieuws Suriname", "url": "https://www.starnieuws.com/rss.xml"},
    {"lang": "FRENCH GUIANA", "flag": "🇬🇫", "name": "France Guyane", "url": "https://www.franceguyane.fr/rss.xml"},
    {"lang": "SOUTH AMERICA", "flag": "🌎", "name": "DW Espanol Latam", "url": "https://rss.dw.com/rdf/rss-es-latam"},

    # --- THAILAND ---
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Bangkok Post", "url": "https://www.bangkokpost.com/rss/data/news.xml"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "The Nation", "url": "https://www.nationthailand.com/rss"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Thai PBS World", "url": "https://www.thaipbsworld.com/rss"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Khaosod English", "url": "https://www.khaosodenglish.com/feed/"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Pattaya Mail", "url": "https://www.pattayamail.com/feed"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Phuket News", "url": "https://www.thephuketnews.com/feed/"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Thairath", "url": "https://www.thairath.co.th/rss/news"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Daily News Thai", "url": "https://www.dailynews.co.th/rss"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Matichon", "url": "https://www.matichon.co.th/feed"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Khaosod Thai", "url": "https://www.khaosod.co.th/feed"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Sanook News", "url": "https://www.sanook.com/news/rss/"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Manager Online", "url": "https://mgronline.com/rss"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "PPTV HD", "url": "https://www.pptvhd36.com/rss"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Thai PBS Thai", "url": "https://www.thaipbs.or.th/rss"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "BBC Thai", "url": "https://feeds.bbci.co.uk/thai/rss.xml"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "VOA Thai", "url": "https://www.voathai.com/api/zmio-ep_yr"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "RFA Thai", "url": "https://www.rfa.org/thai/RSS"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "DW Thai", "url": "https://rss.dw.com/rdf/rss-th-all"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Reuters Thailand", "url": "https://www.reuters.com/rssfeed/thailandNews"},

    # --- VIETNAM ---
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "VnExpress", "url": "https://vnexpress.net/rss/tin-moi-nhat.rss"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "Tuoi Tre News", "url": "https://tuoitrenews.vn/rss/feed.rss"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "VietnamNet", "url": "https://vietnamnet.vn/rss/tin-moi-nhat.rss"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "VietnamPlus", "url": "https://en.vietnamplus.vn/rss/home.rss"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "BBC Vietnamese", "url": "https://feeds.bbci.co.uk/vietnamese/rss.xml"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "VOA Vietnamese", "url": "https://www.voatiengviet.com/api/zrqo-qem$-vvr"},

    # --- CAMBODIA ---
    {"lang": "CAMBODIA", "flag": "🇰🇭", "name": "Khmer Times", "url": "https://www.khmertimeskh.com/feed/"},
    {"lang": "CAMBODIA", "flag": "🇰🇭", "name": "Phnom Penh Post", "url": "https://www.phnompenhpost.com/rss.xml"},
    {"lang": "CAMBODIA", "flag": "🇰🇭", "name": "BBC Khmer", "url": "https://feeds.bbci.co.uk/khmer/rss.xml"},

    # --- MALAYSIA ---
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "The Star", "url": "https://www.thestar.com.my/rss/News/Nation"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "New Straits Times", "url": "https://www.nst.com.my/rss/feed/news"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "Malay Mail", "url": "https://www.malaymail.com/feed/rss"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "Free Malaysia Today", "url": "https://www.freemalaysiatoday.com/feed/"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "Bernama", "url": "https://www.bernama.com/en/rss/rss.php"},

    # --- BHUTAN ---
    {"lang": "BHUTAN", "flag": "🇧🇹", "name": "Kuensel", "url": "https://kuenselonline.com/feed/"},
    {"lang": "BHUTAN", "flag": "🇧🇹", "name": "Bhutan Times", "url": "https://bhutantimes.bt/feed/"},
    {"lang": "BHUTAN", "flag": "🇧🇹", "name": "BBS", "url": "https://www.bbs.bt/feed/"},

    # --- NEPAL ---
    {"lang": "NEPAL", "flag": "🇳🇵", "name": "Kathmandu Post", "url": "https://kathmandupost.com/rss"},
    {"lang": "NEPAL", "flag": "🇳🇵", "name": "Online Khabar", "url": "https://english.onlinekhabar.com/feed/"},
    {"lang": "NEPAL", "flag": "🇳🇵", "name": "BBC Nepali", "url": "https://feeds.bbci.co.uk/nepali/rss.xml"},
    {"lang": "NEPAL", "flag": "🇳🇵", "name": "Setopati", "url": "https://en.setopati.com/feed/"},

    # --- LAOS ---
    {"lang": "LAOS", "flag": "🇱🇦", "name": "Vientiane Times", "url": "https://www.vientianetimes.org.la/feed/"},
    {"lang": "LAOS", "flag": "🇱🇦", "name": "BBC Lao", "url": "https://feeds.bbci.co.uk/lao/rss.xml"},
    {"lang": "LAOS", "flag": "🇱🇦", "name": "Laotian Times", "url": "https://laotiantimes.com/feed/"},
    {"lang": "LAOS", "flag": "🇱🇦", "name": "VOA Lao", "url": "https://www.voalaos.com/api/zqio-qem$-vvr"},
    {"lang": "LAOS", "flag": "🇱🇦", "name": "RFA Lao", "url": "https://www.rfa.org/lao/rss2.xml"},

    # --- SINGAPORE ---
    {"lang": "SINGAPORE", "flag": "🇸🇬", "name": "Straits Times", "url": "https://www.straitstimes.com/news/singapore/rss.xml"},
    {"lang": "SINGAPORE", "flag": "🇸🇬", "name": "CNA Singapore", "url": "https://www.channelnewsasia.com/rssfeeds/8395986"},
    {"lang": "SINGAPORE", "flag": "🇸🇬", "name": "CNA Asia", "url": "https://www.channelnewsasia.com/rssfeeds/8395884"},
    {"lang": "SINGAPORE", "flag": "🇸🇬", "name": "Mothership", "url": "https://mothership.sg/feed/"},
    {"lang": "SINGAPORE", "flag": "🇸🇬", "name": "Today Online", "url": "https://www.todayonline.com/rss.xml"},
    {"lang": "SINGAPORE", "flag": "🇸🇬", "name": "Business Times", "url": "https://www.businesstimes.com.sg/rss.xml"},

    # --- BRUNEI ---
    {"lang": "BRUNEI", "flag": "🇧🇳", "name": "Borneo Bulletin", "url": "https://borneobulletin.com.bn/feed/"},
    {"lang": "BRUNEI", "flag": "🇧🇳", "name": "The Scoop Brunei", "url": "https://thescoop.co/feed/"},

    # --- TIMOR-LESTE ---
    {"lang": "TIMOR-LESTE", "flag": "🇹🇱", "name": "Tatoli Timor", "url": "https://en.tatoli.tl/feed/"},
    {"lang": "TIMOR-LESTE", "flag": "🇹🇱", "name": "Timor Post", "url": "https://www.timorpost.com/feed/"},
    {"lang": "TIMOR-LESTE", "flag": "🇹🇱", "name": "Tempo Timor", "url": "https://www.tempotimor.com/feed/"},

    # --- NORTH KOREA ---
    {"lang": "NORTH KOREA", "flag": "🇰🇵", "name": "KCNA Watch", "url": "https://kcnawatch.org/feed/"},
    {"lang": "NORTH KOREA", "flag": "🇰🇵", "name": "NK News", "url": "https://www.nknews.org/feed/"},
    {"lang": "NORTH KOREA", "flag": "🇰🇵", "name": "Daily NK", "url": "https://www.dailynk.com/english/feed/"},
    {"lang": "NORTH KOREA", "flag": "🇰🇵", "name": "38 North", "url": "https://www.38north.org/feed/"},
    {"lang": "NORTH KOREA", "flag": "🇰🇵", "name": "Yonhap NK", "url": "https://en.yna.co.kr/rss/nk"},

    # --- TIBET ---
    {"lang": "TIBET", "flag": "🏔️", "name": "RFA Tibetan", "url": "https://www.rfa.org/tibetan/rss2.xml"},
    {"lang": "TIBET", "flag": "🏔️", "name": "VOA Tibetan", "url": "https://www.voatibetan.com/api/zqio-qem$-vvr"},
    {"lang": "TIBET", "flag": "🏔️", "name": "Phayul Tibet", "url": "https://www.phayul.com/feed/"},
    {"lang": "TIBET", "flag": "🏔️", "name": "Tibet Post", "url": "https://www.thetibetpost.com/feed/"},
    {"lang": "TIBET", "flag": "🏔️", "name": "Tibet Times", "url": "https://www.tibettimes.net/feed/"},
    {"lang": "TIBET", "flag": "🏔️", "name": "Tibet Watch", "url": "https://www.tibetwatch.org/feed/"},
    {"lang": "TIBET", "flag": "🏔️", "name": "Central Tibetan Admin", "url": "https://tibet.net/feed/"},
]

seen = set()

def make_text(feed_info, title, link):
    return f"{feed_info['flag']} <b>[{feed_info['lang']} - {feed_info['name']}]</b>\n\n{title}\n\n🔗 <a href='{link}'>Read Full News</a>\n\n⚡ Powered by <a href='https://t.me/bigolive_asia'>@bigolive_asia</a>"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Bot is running! News every 5 min.\n\nAll Regions: India, World, Sinhala, Myanmar, Philippines, Indonesia, China, Europe, West Asia, East Asia, Latin, South America, Thailand, Vietnam, Cambodia, Malaysia, Bhutan, Nepal, Laos, Singapore, Brunei, Timor-Leste, North Korea, Tibet\n\n⚡ Powered by https://t.me/bigolive_asia"
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
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest))
    print("Bot Started - Auto + Commands")
    app.run_polling()

if __name__ == "__main__":
    main()
