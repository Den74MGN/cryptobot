import sys, asyncio, logging, hashlib, re, io, aiohttp, pytz
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

# 🛠 Фикс для Python 3.13+
try:
    import cgi
except ImportError:
    import types
    cgi = types.ModuleType("cgi"); cgi.FieldStorage = lambda: None; sys.modules["cgi"] = cgi

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import *
from core.database import DatabaseManager
from core.stats import StatsManager
from core.fetcher import ContentFetcher
from core.formatter import PostFormatter
from core.media import MediaEngine

@dataclass
class NewsItem:
    title: str; description: str; link: str; source: str; published: datetime
    image_url: Optional[str] = None; score: int = 0
    @property
    def unique_id(self) -> str: return hashlib.md5(self.link.encode()).hexdigest()
    @property
    def title_hash(self) -> str: return hashlib.md5(re.sub(r'\W+', '', self.title.lower()).encode()).hexdigest()

class SantaBot:
    def __init__(self):
        self.db = DatabaseManager(DB_FILE, SIMILARITY_THRESHOLD)
        self.stats = StatsManager(STATS_FILE)
        self.formatter = PostFormatter(CHANNEL_NAME, CHANNEL_LINK, TAG_CATEGORIES, DEFAULT_HASHTAGS)
        self.media = MediaEngine()
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))

    async def send_post(self, bot, news):
        try:
            text = self.formatter.format_news(news)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Читать оригинал", url=news.link)]])
            async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as s:
                photo = await self.media.apply_watermark(s, news.image_url, CHANNEL_NAME)
            
            if photo:
                await bot.send_photo(CHANNEL_ID, photo=photo, caption=text, parse_mode='MarkdownV2', reply_markup=kb)
            else:
                await bot.send_message(CHANNEL_ID, text=text, parse_mode='MarkdownV2', reply_markup=kb, disable_web_page_preview=False)
            
            self.db.add_news(news)
            self.stats.log_event("published", news.source)
            logging.info(f"✅ Опубликовано: {news.title[:30]}...")
        except Exception as e:
            logging.error(f"Ошибка публикации: {e}")

    async def republish_last(self, bot):
        data = self.db.get_last_news()
        if data:
            news = NewsItem(title=data['raw_title'], description=data.get('description', ''), 
                            link=data.get('link', CHANNEL_LINK), source=data['source'], 
                            published=datetime.fromisoformat(data['published_at']), image_url=data.get('image_url'))
            await self.send_post(bot, news)

    async def update_and_publish(self, bot, is_startup=False):
        logging.info("⚡️ Сбор новостей (Bits.media)...")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:
            fetcher = ContentFetcher(s, self.stats)
            raw_list = []
            for f in RSS_FEEDS:
                res = await fetcher.fetch_rss(f, HISTORY_START_DATE, pytz.timezone('Europe/Moscow'))
                for r in res:
                    item = NewsItem(**r)
                    if not self.db.is_duplicate(item.unique_id, item.title_hash, item.title):
                        if len(item.description) < MIN_DESCRIPTION_LENGTH or not item.image_url:
                            txt, img = await fetcher.scrape_full_content(item.link)
                            if txt: item.description = txt
                            if not item.image_url: item.image_url = img
                        raw_list.append(item)
            
            raw_list.sort(key=lambda x: x.published, reverse=not is_startup)
            limit = 1 if is_startup else NEWS_PER_PUBLISH
            for news in raw_list[:limit]:
                await self.send_post(bot, news); await asyncio.sleep(12)

    async def run(self):
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("stats", lambda u, c: u.message.reply_text(self.stats.get_report())))
        await app.initialize(); await app.start(); await app.updater.start_polling()
        
        await self.republish_last(app.bot)
        asyncio.create_task(self.update_and_publish(app.bot, is_startup=True))
        
        self.scheduler.add_job(self.update_and_publish, CronTrigger(minute='*/10'), args=[app.bot])
        self.scheduler.start()
        while True: await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    try: asyncio.run(SantaBot().run())
    except (KeyboardInterrupt, SystemExit): pass