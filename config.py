# config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

base_dir = Path(__file__).resolve().parent
env_path = base_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def clean_env(key: str):
    val = os.getenv(key)
    return val.strip().replace('"', '').replace("'", "") if val else None

# 🔐 СЕКРЕТЫ (из .env)
BOT_TOKEN = clean_env("BOT_TOKEN")
CHANNEL_ID = clean_env("CHANNEL_ID")
ADMIN_ID = clean_env("ADMIN_ID")

# 🔗 БРЕНДИНГ
CHANNEL_LINK = "https://t.me/SantaCryptoNews" 
CHANNEL_NAME = "SantaCryptoNews"

# 📡 ЕДИНСТВЕННЫЙ ИСТОЧНИК
RSS_FEEDS = [
    {"name": "Bits.media", "url": "https://bits.media/rss2/", "lang": "ru"}
]

# 📈 СКОРИНГ И ПАРАМЕТРЫ ТЕКСТА
SCORE_RUSSIA = 100
SCORE_FULL_CONTENT = 80
MIN_DESCRIPTION_LENGTH = 180 

# 🔍 ТРИГГЕРЫ
RUSSIA_KEYWORDS = ["россия", "рф", "цб рф", "госдума", "минфин", "рубль", "набиуллина", "путин"]
BULL_KEYWORDS = ["рост", "взлет", "памп", "pump", "bull", "ath", "вырос", "позитив"]
BEAR_KEYWORDS = ["падение", "обвал", "дамп", "dump", "bear", "упал", "негатив"]

# 🏷️ ТЕГИ (Категории)
TAG_CATEGORIES = {
    "COINS": {"bitcoin": "#BTC", "биткоин": "#BTC", "ethereum": "#ETH", "ton": "#TON"},
    "THEMES": {"defi": "#DeFi", "nft": "#NFT", "майнинг": "#Mining"},
    "MARKET": {"листинг": "#Listing", "аирдроп": "#Airdrop", "инвестиции": "#Invest"}
}
DEFAULT_HASHTAGS = ["#Crypto", "#Blockchain", "#News", "#CryptoMarket"]

# 📁 ТЕХНИЧЕСКИЕ ФАЙЛЫ
DB_FILE = "santa_news.db"
STATS_FILE = "bot_stats.json"
MAX_HISTORY = 5000
CHECK_INTERVAL = 10
NEWS_PER_PUBLISH = 3
HISTORY_START_DATE = datetime(2026, 1, 1)
SIMILARITY_THRESHOLD = 0.75 
BLACKLIST_WORDS = ["реклама", "партнерский материал", "p2p связка", "сигналы"]