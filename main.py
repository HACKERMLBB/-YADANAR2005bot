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
    # --- ENGLISH GLOBAL ---
    {"lang": "WORLD", "flag": "🌍", "name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss"},
    {"lang": "WORLD", "flag": "🌍", "name": "Sky News", "url": "https://feeds.skynews.com/feeds/rss/world.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "Reuters", "url": "https://feeds.reuters.com/reuters/worldNews"},
    {"lang": "WORLD", "flag": "🌍", "name": "AP News", "url": "https://apnews.com/rss"},
    {"lang": "WORLD", "flag": "🌍", "name": "France 24", "url": "https://www.france24.com/en/rss"},
    {"lang": "WORLD", "flag": "🌍", "name": "DW News", "url": "https://rss.dw.com/rdf/rss-en-all"},
    {"lang": "WORLD", "flag": "🌍", "name": "Euronews", "url": "https://www.euronews.com/rss?format=mrss&level=theme&name=news"},
    {"lang": "WORLD", "flag": "🌍", "name": "NBC News", "url": "https://feeds.nbcnews.com/nbcnews/public/news"},
    {"lang": "WORLD", "flag": "🌍", "name": "ABC News", "url": "https://abcnews.go.com/abcnews/topstories"},
    {"lang": "WORLD", "flag": "🌍", "name": "CBS News", "url": "https://www.cbsnews.com/latest/rss/main"},
    {"lang": "WORLD", "flag": "🌍", "name": "Fox News", "url": "https://moxie.foxnews.com/google-publisher/latest.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"lang": "WORLD", "flag": "🌍", "name": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "CGTN", "url": "https://www.cgtn.com/subscribe/rss/section/world.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "WION", "url": "https://www.wionews.com/rss/world.xml"},
    {"lang": "WORLD", "flag": "🌍", "name": "ABC Australia", "url": "https://www.abc.net.au/news/feed/51120/rss.xml"},

    # --- SRI LANKA ---
    {"lang": "SRI LANKA", "flag": "🇱🇰", "name": "Sri Lanka", "url": "https://news.google.com/rss/search?q=Sri+Lanka&hl=en&gl=LK&ceid=LK:en"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "BBC Sinhala", "url": "https://feeds.bbci.co.uk/sinhala/rss.xml"},
    {"lang": "SINHALA", "flag": "🇱🇰", "name": "Lanka Sinhala", "url": "https://news.google.com/rss/search?q=Sri+Lanka&hl=si&gl=LK&ceid=LK:si"},

    # --- EAST ASIA ---
    {"lang": "CHINA", "flag": "🇨🇳", "name": "China News", "url": "https://news.google.com/rss/search?q=China&hl=en&gl=CN&ceid=CN:en"},
    {"lang": "JAPAN", "flag": "🇯🇵", "name": "Japan News", "url": "https://news.google.com/rss/search?q=Japan&hl=en&gl=JP&ceid=JP:en"},
    {"lang": "KOREA", "flag": "🇰🇷", "name": "Korea News", "url": "https://news.google.com/rss/search?q=Korea&hl=en&gl=KR&ceid=KR:en"},
    {"lang": "NORTH KOREA", "flag": "🇰🇵", "name": "North Korea News", "url": "https://news.google.com/rss/search?q=North+Korea&hl=en&gl=KP&ceid=KP:en"},
    {"lang": "TAIWAN", "flag": "🇹🇼", "name": "Taiwan News", "url": "https://news.google.com/rss/search?q=Taiwan&hl=en&gl=TW&ceid=TW:en"},
    {"lang": "MONGOLIA", "flag": "🇲🇳", "name": "Mongolia News", "url": "https://news.google.com/rss/search?q=Mongolia&hl=en&gl=MN&ceid=MN:en"},

    # --- SOUTHEAST ASIA ---
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "Thailand News", "url": "https://news.google.com/rss/search?q=Thailand&hl=en&gl=TH&ceid=TH:en"},
    {"lang": "THAILAND", "flag": "🇹🇭", "name": "BBC Thai", "url": "https://feeds.bbci.co.uk/thai/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "BBC Burmese", "url": "https://feeds.bbci.co.uk/burmese/rss.xml"},
    {"lang": "MYANMAR", "flag": "🇲🇲", "name": "Myanmar News", "url": "https://news.google.com/rss/search?q=Myanmar&hl=en&gl=MM&ceid=MM:en"},
    {"lang": "VIETNAM", "flag": "🇻🇳", "name": "Vietnam News", "url": "https://news.google.com/rss/search?q=Vietnam&hl=en&gl=VN&ceid=VN:en"},
    {"lang": "PHILIPPINES", "flag": "🇵🇭", "name": "Philippines News", "url": "https://news.google.com/rss/search?q=Philippines&hl=en&gl=PH&ceid=PH:en"},
    {"lang": "INDONESIA", "flag": "🇮🇩", "name": "Indonesia News", "url": "https://news.google.com/rss/search?q=Indonesia&hl=en&gl=ID&ceid=ID:en"},
    {"lang": "MALAYSIA", "flag": "🇲🇾", "name": "Malaysia News", "url": "https://news.google.com/rss/search?q=Malaysia&hl=en&gl=MY&ceid=MY:en"},
    {"lang": "SINGAPORE", "flag": "🇸🇬", "name": "Singapore News", "url": "https://news.google.com/rss/search?q=Singapore&hl=en&gl=SG&ceid=SG:en"},
    {"lang": "CAMBODIA", "flag": "🇰🇭", "name": "Cambodia News", "url": "https://news.google.com/rss/search?q=Cambodia&hl=en&gl=KH&ceid=KH:en"},
    {"lang": "LAOS", "flag": "🇱🇦", "name": "Laos News", "url": "https://news.google.com/rss/search?q=Laos&hl=en&gl=LA&ceid=LA:en"},
    {"lang": "BRUNEI", "flag": "🇧🇳", "name": "Brunei News", "url": "https://news.google.com/rss/search?q=Brunei&hl=en&gl=BN&ceid=BN:en"},
    {"lang": "TIMOR-LESTE", "flag": "🇹🇱", "name": "Timor-Leste News", "url": "https://news.google.com/rss/search?q=Timor+Leste&hl=en&gl=TL&ceid=TL:en"},

    # --- SOUTH ASIA ---
    {"lang": "INDIA", "flag": "🇮🇳", "name": "India News", "url": "https://news.google.com/rss/search?q=India&hl=en&gl=IN&ceid=IN:en"},
    {"lang": "INDIA", "flag": "🇮🇳", "name": "BBC Hindi", "url": "https://feeds.bbci.co.uk/hindi/rss.xml"},
    {"lang": "PAKISTAN", "flag": "🇵🇰", "name": "Pakistan News", "url": "https://news.google.com/rss/search?q=Pakistan&hl=en&gl=PK&ceid=PK:en"},
    {"lang": "BANGLADESH", "flag": "🇧🇩", "name": "Bangladesh News", "url": "https://news.google.com/rss/search?q=Bangladesh&hl=en&gl=BD&ceid=BD:en"},
    {"lang": "NEPAL", "flag": "🇳🇵", "name": "Nepal News", "url": "https://news.google.com/rss/search?q=Nepal&hl=en&gl=NP&ceid=NP:en"},
    {"lang": "BHUTAN", "flag": "🇧🇹", "name": "Bhutan News", "url": "https://news.google.com/rss/search?q=Bhutan&hl=en&gl=BT&ceid=BT:en"},
    {"lang": "MALDIVES", "flag": "🇲🇻", "name": "Maldives News", "url": "https://news.google.com/rss/search?q=Maldives&hl=en&gl=MV&ceid=MV:en"},
    {"lang": "AFGHANISTAN", "flag": "🇦🇫", "name": "Afghanistan News", "url": "https://news.google.com/rss/search?q=Afghanistan&hl=en&gl=AF&ceid=AF:en"},

    # --- CENTRAL ASIA ---
    {"lang": "KAZAKHSTAN", "flag": "🇰🇿", "name": "Kazakhstan News", "url": "https://news.google.com/rss/search?q=Kazakhstan&hl=en&gl=KZ&ceid=KZ:en"},
    {"lang": "UZBEKISTAN", "flag": "🇺🇿", "name": "Uzbekistan News", "url": "https://news.google.com/rss/search?q=Uzbekistan&hl=en&gl=UZ&ceid=UZ:en"},
    {"lang": "KYRGYZSTAN", "flag": "🇰🇬", "name": "Kyrgyzstan News", "url": "https://news.google.com/rss/search?q=Kyrgyzstan&hl=en&gl=KG&ceid=KG:en"},
    {"lang": "TAJIKISTAN", "flag": "🇹🇯", "name": "Tajikistan News", "url": "https://news.google.com/rss/search?q=Tajikistan&hl=en&gl=TJ&ceid=TJ:en"},
    {"lang": "TURKMENISTAN", "flag": "🇹🇲", "name": "Turkmenistan News", "url": "https://news.google.com/rss/search?q=Turkmenistan&hl=en&gl=TM&ceid=TM:en"},

    # --- WEST ASIA ---
    {"lang": "SAUDI", "flag": "🇸🇦", "name": "Saudi News", "url": "https://news.google.com/rss/search?q=Saudi+Arabia&hl=en&gl=SA&ceid=SA:en"},
    {"lang": "UAE", "flag": "🇦🇪", "name": "UAE News", "url": "https://news.google.com/rss/search?q=UAE&hl=en&gl=AE&ceid=AE:en"},
    {"lang": "QATAR", "flag": "🇶🇦", "name": "Qatar News", "url": "https://news.google.com/rss/search?q=Qatar&hl=en&gl=QA&ceid=QA:en"},
    {"lang": "ISRAEL", "flag": "🇮🇱", "name": "Israel News", "url": "https://news.google.com/rss/search?q=Israel&hl=en&gl=IL&ceid=IL:en"},
    {"lang": "IRAN", "flag": "🇮🇷", "name": "Iran News", "url": "https://news.google.com/rss/search?q=Iran&hl=en&gl=IR&ceid=IR:en"},
    {"lang": "IRAQ", "flag": "🇮🇶", "name": "Iraq News", "url": "https://news.google.com/rss/search?q=Iraq&hl=en&gl=IQ&ceid=IQ:en"},
    {"lang": "TURKEY", "flag": "🇹🇷", "name": "Turkey News", "url": "https://news.google.com/rss/search?q=Turkey&hl=en&gl=TR&ceid=TR:en"},
    {"lang": "JORDAN", "flag": "🇯🇴", "name": "Jordan News", "url": "https://news.google.com/rss/search?q=Jordan&hl=en&gl=JO&ceid=JO:en"},
    {"lang": "LEBANON", "flag": "🇱🇧", "name": "Lebanon News", "url": "https://news.google.com/rss/search?q=Lebanon&hl=en&gl=LB&ceid=LB:en"},
    {"lang": "SYRIA", "flag": "🇸🇾", "name": "Syria News", "url": "https://news.google.com/rss/search?q=Syria&hl=en&gl=SY&ceid=SY:en"},
    {"lang": "KUWAIT", "flag": "🇰🇼", "name": "Kuwait News", "url": "https://news.google.com/rss/search?q=Kuwait&hl=en&gl=KW&ceid=KW:en"},
    {"lang": "BAHRAIN", "flag": "🇧🇭", "name": "Bahrain News", "url": "https://news.google.com/rss/search?q=Bahrain&hl=en&gl=BH&ceid=BH:en"},
    {"lang": "OMAN", "flag": "🇴🇲", "name": "Oman News", "url": "https://news.google.com/rss/search?q=Oman&hl=en&gl=OM&ceid=OM:en"},
    {"lang": "YEMEN", "flag": "🇾🇪", "name": "Yemen News", "url": "https://news.google.com/rss/search?q=Yemen&hl=en&gl=YE&ceid=YE:en"},
    {"lang": "PALESTINE", "flag": "🇵🇸", "name": "Palestine News", "url": "https://news.google.com/rss/search?q=Palestine&hl=en&gl=PS&ceid=PS:en"},
    {"lang": "CYPRUS", "flag": "🇨🇾", "name": "Cyprus News", "url": "https://news.google.com/rss/search?q=Cyprus&hl=en&gl=CY&ceid=CY:en"},
    {"lang": "ARMENIA", "flag": "🇦🇲", "name": "Armenia News", "url": "https://news.google.com/rss/search?q=Armenia&hl=en&gl=AM&ceid=AM:en"},
    {"lang": "GEORGIA", "flag": "🇬🇪", "name": "Georgia News", "url": "https://news.google.com/rss/search?q=Georgia&hl=en&gl=GE&ceid=GE:en"},
    {"lang": "AZERBAIJAN", "flag": "🇦🇿", "name": "Azerbaijan News", "url": "https://news.google.com/rss/search?q=Azerbaijan&hl=en&gl=AZ&ceid=AZ:en"},

    # --- EUROPE 44 ---
    {"lang": "UK", "flag": "🇬🇧", "name": "BBC UK", "url": "https://feeds.bbci.co.uk/news/uk/rss.xml"},
    {"lang": "UKRAINE", "flag": "🇺🇦", "name": "Ukraine News", "url": "https://news.google.com/rss/search?q=Ukraine&hl=en&gl=UA&ceid=UA:en"},
    {"lang": "FRANCE", "flag": "🇫🇷", "name": "France News", "url": "https://news.google.com/rss/search?q=France&hl=en&gl=FR&ceid=FR:en"},
    {"lang": "GERMANY", "flag": "🇩🇪", "name": "Germany News", "url": "https://news.google.com/rss/search?q=Germany&hl=en&gl=DE&ceid=DE:en"},
    {"lang": "ITALY", "flag": "🇮🇹", "name": "Italy News", "url": "https://news.google.com/rss/search?q=Italy&hl=en&gl=IT&ceid=IT:en"},
    {"lang": "SPAIN", "flag": "🇪🇸", "name": "Spain News", "url": "https://news.google.com/rss/search?q=Spain&hl=en&gl=ES&ceid=ES:en"},
    {"lang": "NETHERLANDS", "flag": "🇳🇱", "name": "Netherlands News", "url": "https://news.google.com/rss/search?q=Netherlands&hl=en&gl=NL&ceid=NL:en"},
    {"lang": "POLAND", "flag": "🇵🇱", "name": "Poland News", "url": "https://news.google.com/rss/search?q=Poland&hl=en&gl=PL&ceid=PL:en"},
    {"lang": "PORTUGAL", "flag": "🇵🇹", "name": "Portugal News", "url": "https://news.google.com/rss/search?q=Portugal&hl=en&gl=PT&ceid=PT:en"},
    {"lang": "BELGIUM", "flag": "🇧🇪", "name": "Belgium News", "url": "https://news.google.com/rss/search?q=Belgium&hl=en&gl=BE&ceid=BE:en"},
    {"lang": "SWITZERLAND", "flag": "🇨🇭", "name": "Switzerland News", "url": "https://news.google.com/rss/search?q=Switzerland&hl=en&gl=CH&ceid=CH:en"},
    {"lang": "AUSTRIA", "flag": "🇦🇹", "name": "Austria News", "url": "https://news.google.com/rss/search?q=Austria&hl=en&gl=AT&ceid=AT:en"},
    {"lang": "SWEDEN", "flag": "🇸🇪", "name": "Sweden News", "url": "https://news.google.com/rss/search?q=Sweden&hl=en&gl=SE&ceid=SE:en"},
    {"lang": "NORWAY", "flag": "🇳🇴", "name": "Norway News", "url": "https://news.google.com/rss/search?q=Norway&hl=en&gl=NO&ceid=NO:en"},
    {"lang": "DENMARK", "flag": "🇩🇰", "name": "Denmark News", "url": "https://news.google.com/rss/search?q=Denmark&hl=en&gl=DK&ceid=DK:en"},
    {"lang": "FINLAND", "flag": "🇫🇮", "name": "Finland News", "url": "https://news.google.com/rss/search?q=Finland&hl=en&gl=FI&ceid=FI:en"},
    {"lang": "GREECE", "flag": "🇬🇷", "name": "Greece News", "url": "https://news.google.com/rss/search?q=Greece&hl=en&gl=GR&ceid=GR:en"},
    {"lang": "IRELAND", "flag": "🇮🇪", "name": "Ireland News", "url": "https://news.google.com/rss/search?q=Ireland&hl=en&gl=IE&ceid=IE:en"},
    {"lang": "CZECH", "flag": "🇨🇿", "name": "Czech News", "url": "https://news.google.com/rss/search?q=Czech&hl=en&gl=CZ&ceid=CZ:en"},
    {"lang": "HUNGARY", "flag": "🇭🇺", "name": "Hungary News", "url": "https://news.google.com/rss/search?q=Hungary&hl=en&gl=HU&ceid=HU:en"},
    {"lang": "ROMANIA", "flag": "🇷🇴", "name": "Romania News", "url": "https://news.google.com/rss/search?q=Romania&hl=en&gl=RO&ceid=RO:en"},
    {"lang": "BULGARIA", "flag": "🇧🇬", "name": "Bulgaria News", "url": "https://news.google.com/rss/search?q=Bulgaria&hl=en&gl=BG&ceid=BG:en"},
    {"lang": "CROATIA", "flag": "🇭🇷", "name": "Croatia News", "url": "https://news.google.com/rss/search?q=Croatia&hl=en&gl=HR&ceid=HR:en"},
    {"lang": "SERBIA", "flag": "🇷🇸", "name": "Serbia News", "url": "https://news.google.com/rss/search?q=Serbia&hl=en&gl=RS&ceid=RS:en"},
    {"lang": "BELARUS", "flag": "🇧🇾", "name": "Belarus News", "url": "https://news.google.com/rss/search?q=Belarus&hl=en&gl=BY&ceid=BY:en"},
    {"lang": "SLOVENIA", "flag": "🇸🇮", "name": "Slovenia News", "url": "https://news.google.com/rss/search?q=Slovenia&hl=en&gl=SI&ceid=SI:en"},
    {"lang": "SLOVAKIA", "flag": "🇸🇰", "name": "Slovakia News", "url": "https://news.google.com/rss/search?q=Slovakia&hl=en&gl=SK&ceid=SK:en"},
    {"lang": "LITHUANIA", "flag": "🇱🇹", "name": "Lithuania News", "url": "https://news.google.com/rss/search?q=Lithuania&hl=en&gl=LT&ceid=LT:en"},
    {"lang": "LATVIA", "flag": "🇱🇻", "name": "Latvia News", "url": "https://news.google.com/rss/search?q=Latvia&hl=en&gl=LV&ceid=LV:en"},
    {"lang": "ESTONIA", "flag": "🇪🇪", "name": "Estonia News", "url": "https://news.google.com/rss/search?q=Estonia&hl=en&gl=EE&ceid=EE:en"},
    {"lang": "ICELAND", "flag": "🇮🇸", "name": "Iceland News", "url": "https://news.google.com/rss/search?q=Iceland&hl=en&gl=IS&ceid=IS:en"},
    {"lang": "LUXEMBOURG", "flag": "🇱🇺", "name": "Luxembourg News", "url": "https://news.google.com/rss/search?q=Luxembourg&hl=en&gl=LU&ceid=LU:en"},
    {"lang": "MALTA", "flag": "🇲🇹", "name": "Malta News", "url": "https://news.google.com/rss/search?q=Malta&hl=en&gl=MT&ceid=MT:en"},
    {"lang": "ALBANIA", "flag": "🇦🇱", "name": "Albania News", "url": "https://news.google.com/rss/search?q=Albania&hl=en&gl=AL&ceid=AL:en"},
    {"lang": "BOSNIA", "flag": "🇧🇦", "name": "Bosnia News", "url": "https://news.google.com/rss/search?q=Bosnia&hl=en&gl=BA&ceid=BA:en"},
    {"lang": "MONTENEGRO", "flag": "🇲🇪", "name": "Montenegro News", "url": "https://news.google.com/rss/search?q=Montenegro&hl=en&gl=ME&ceid=ME:en"},
    {"lang": "NORTH MACEDONIA", "flag": "🇲🇰", "name": "North Macedonia News", "url": "https://news.google.com/rss/search?q=North+Macedonia&hl=en&gl=MK&ceid=MK:en"},
    {"lang": "MOLDOVA", "flag": "🇲🇩", "name": "Moldova News", "url": "https://news.google.com/rss/search?q=Moldova&hl=en&gl=MD&ceid=MD:en"},
    {"lang": "RUSSIA", "flag": "🇷🇺", "name": "Russia News", "url": "https://news.google.com/rss/search?q=Russia&hl=en&gl=RU&ceid=RU:en"},
    {"lang": "ANDORRA", "flag": "🇦🇩", "name": "Andorra News", "url": "https://news.google.com/rss/search?q=Andorra&hl=en&gl=AD&ceid=AD:en"},
    {"lang": "MONACO", "flag": "🇲🇨", "name": "Monaco News", "url": "https://news.google.com/rss/search?q=Monaco&hl=en&gl=MC&ceid=MC:en"},
    {"lang": "SAN MARINO", "flag": "🇸🇲", "name": "San Marino News", "url": "https://news.google.com/rss/search?q=San+Marino&hl=en&gl=SM&ceid=SM:en"},
    {"lang": "VATICAN", "flag": "🇻🇦", "name": "Vatican News", "url": "https://news.google.com/rss/search?q=Vatican&hl=en&gl=VA&ceid=VA:en"},
    {"lang": "LIECHTENSTEIN", "flag": "🇱🇮", "name": "Liechtenstein News", "url": "https://news.google.com/rss/search?q=Liechtenstein&hl=en&gl=LI&ceid=LI:en"},
    {"lang": "KOSOVO", "flag": "🇽🇰", "name": "Kosovo News", "url": "https://news.google.com/rss/search?q=Kosovo&hl=en&gl=XK&ceid=XK:en"},

    # --- TERRITORIES / SPECIAL REGIONS ---
    {"lang": "TIBET", "flag": "🏔️", "name": "Tibet News", "url": "https://news.google.com/rss/search?q=Tibet&hl=en&gl=CN&ceid=CN:en"},
    {"lang": "HONG KONG", "flag": "🇭🇰", "name": "Hong Kong News", "url": "https://news.google.com/rss/search?q=Hong+Kong&hl=en&gl=HK&ceid=HK:en"},
    {"lang": "MACAU", "flag": "🇲🇴", "name": "Macau News", "url": "https://news.google.com/rss/search?q=Macau&hl=en&gl=MO&ceid=MO:en"},
    {"lang": "KASHMIR", "flag": "🏔️", "name": "Kashmir News", "url": "https://news.google.com/rss/search?q=Kashmir&hl=en&gl=IN&ceid=IN:en"},
    {"lang": "KURDISTAN", "flag": "☀️", "name": "Kurdistan News", "url": "https://news.google.com/rss/search?q=Kurdistan&hl=en&gl=IQ&ceid=IQ:en"},
    {"lang": "SCOTLAND", "flag": "🏴󐁧󐁢󐁳󐁣󐁴󐁿", "name": "Scotland News", "url": "https://news.google.com/rss/search?q=Scotland&hl=en&gl=GB&ceid=GB:en"},
    {"lang": "WALES", "flag": "🏴󐁧󐁢󐁷󐁬󐁳󐁿", "name": "Wales News", "url": "https://news.google.com/rss/search?q=Wales&hl=en&gl=GB&ceid=GB:en"},
    {"lang": "NORTHERN IRELAND", "flag": "🇬🇧", "name": "Northern Ireland News", "url": "https://news.google.com/rss/search?q=Northern+Ireland&hl=en&gl=GB&ceid=GB:en"},
    {"lang": "GIBRALTAR", "flag": "🇬🇮", "name": "Gibraltar News", "url": "https://news.google.com/rss/search?q=Gibraltar&hl=en&gl=GI&ceid=GI:en"},
    {"lang": "CATALONIA", "flag": "🏴", "name": "Catalonia News", "url": "https://news.google.com/rss/search?q=Catalonia&hl=en&gl=ES&ceid=ES:en"},
    {"lang": "BASQUE", "flag": "🏴", "name": "Basque News", "url": "https://news.google.com/rss/search?q=Basque&hl=en&gl=ES&ceid=ES:en"},
    {"lang": "CORSICA", "flag": "🇫🇷", "name": "Corsica News", "url": "https://news.google.com/rss/search?q=Corsica&hl=en&gl=FR&ceid=FR:en"},
    {"lang": "GREENLAND", "flag": "🇬🇱", "name": "Greenland News", "url": "https://news.google.com/rss/search?q=Greenland&hl=en&gl=GL&ceid=GL:en"},
    {"lang": "FAROE", "flag": "🇫🇴", "name": "Faroe Islands News", "url": "https://news.google.com/rss/search?q=Faroe+Islands&hl=en&gl=FO&ceid=FO:en"},
    {"lang": "CRIMEA", "flag": "🏴", "name": "Crimea News", "url": "https://news.google.com/rss/search?q=Crimea&hl=en&gl=UA&ceid=UA:en"},
    {"lang": "TRANSNISTRIA", "flag": "🏴", "name": "Transnistria News", "url": "https://news.google.com/rss/search?q=Transnistria&hl=en&gl=MD&ceid=MD:en"},
    {"lang": "SICILY", "flag": "🇮🇹", "name": "Sicily News", "url": "https://news.google.com/rss/search?q=Sicily&hl=en&gl=IT&ceid=IT:en"},
    {"lang": "SARDINIA", "flag": "🇮🇹", "name": "Sardinia News", "url": "https://news.google.com/rss/search?q=Sardinia&hl=en&gl=IT&ceid=IT:en"},

    # --- OTHER ---
    {"lang": "USA", "flag": "🇺🇸", "name": "USA News", "url": "https://news.google.com/rss/search?q=USA&hl=en&gl=US&ceid=US:en"},
    {"lang": "BRAZIL", "flag": "🇧🇷", "name": "Brazil News", "url": "https://news.google.com/rss/search?q=Brazil&hl=en&gl=BR&ceid=BR:en"},
]

seen = set()

def make_text(f, title, link):
    return f"{f['flag']} <b>[{f['lang']} - {f['name']}]</b>\n\n{title}\n\n🔗 <a href='{link}'>Read Full News</a>\n\n⚡ Powered by @bigolive_asia"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to ŸᗅĐᗅŇᗅᏒ💗 news bot\n\n"
        "🌍 News Bot Running!\n\n"
        "👉 /news Myanmar\n"
        "👉 /news India\n"
        "👉 /countries - All Countries\n"
        "👉 /latest - Latest News\n\n"
        "⚡ Update channel every 3 minutes\n"
        "🔥 Powered by t.me/bigolive_asia"
    )

async def news_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("✍️ Ex: /news Myanmar\n/news India")
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
