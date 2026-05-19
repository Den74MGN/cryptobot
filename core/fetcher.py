import aiohttp
import feedparser
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

class ContentFetcher:
    def __init__(self, session, stats):
        self.session = session
        self.stats = stats

    def _clean_text(self, text):
        if not text: return ""
        soup = BeautifulSoup(text, 'lxml')
        for s in soup(["script", "style", "nav", "footer", "header", "aside"]): s.decompose()
        clean = soup.get_text(separator=' ', strip=True)
        clean = re.sub(r'(Иллюстрация|Фото|Источник|Автор|Редакция):.*?\.', '', clean)
        return ' '.join(clean.split())

    async def scrape_full_content(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
            async with self.session.get(url, headers=headers, timeout=12) as resp:
                if resp.status != 200: return None, None
                html = await resp.text()
                soup = BeautifulSoup(html, 'lxml')
                
                img_url = None
                og_image = soup.find("meta", property="og:image")
                if og_image: img_url = og_image.get("content")
                
                if img_url: img_url = urljoin(url, img_url)

                article_body = soup.find('div', class_='post-content') or soup.find('article')
                if not article_body: return None, img_url
                
                text = " ".join([p.get_text() for p in article_body.find_all('p') if len(p.get_text()) > 50])
                return self._clean_text(text), img_url
        except:
            return None, None

    async def fetch_rss(self, cfg, history_start, moscow_tz):
        items = []
        try:
            async with self.session.get(cfg['url'], timeout=15) as resp:
                feed = feedparser.parse(await resp.read())
                for entry in feed.entries[:15]:
                    try:
                        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(moscow_tz)
                    except:
                        dt = datetime.now(moscow_tz)
                    if dt.replace(tzinfo=None) < history_start: continue
                    
                    img = None
                    if 'media_content' in entry: img = entry.media_content[0].get('url')
                    elif 'enclosures' in entry and entry.enclosures: img = entry.enclosures[0].get('url')
                    if img: img = urljoin(cfg['url'], img)
                    
                    items.append({
                        'title': self._clean_text(entry.get('title', '')),
                        'description': self._clean_text(entry.get('summary', '') or entry.get('description', '')),
                        'link': entry.get('link', ''),
                        'source': cfg['name'],
                        'published': dt,
                        'image_url': img
                    })
        except: pass
        return items