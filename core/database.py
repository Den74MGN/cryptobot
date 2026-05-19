import sqlite3
import re
from difflib import SequenceMatcher

class DatabaseManager:
    def __init__(self, db_path, similarity_threshold):
        self.db_path = db_path
        self.threshold = similarity_threshold
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute('PRAGMA journal_mode=WAL')
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                           (id TEXT PRIMARY KEY, title_hash TEXT, raw_title TEXT, source TEXT, 
                            description TEXT, image_url TEXT, published_at TEXT, link TEXT)''')
            conn.commit()

    def is_duplicate(self, news_id, title_hash, raw_title) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if cursor.execute('SELECT 1 FROM news WHERE id = ?', (news_id,)).fetchone(): return True
            if cursor.execute('SELECT 1 FROM news WHERE title_hash = ?', (title_hash,)).fetchone(): return True
            
            cursor.execute('SELECT raw_title FROM news ORDER BY published_at DESC LIMIT 150')
            recent = [row[0] for row in cursor.fetchall()]
            new_clean = re.sub(r'\W+', ' ', raw_title.lower()).strip()
            for old in recent:
                if SequenceMatcher(None, new_clean, old.lower()).ratio() > self.threshold: return True
            return False

    def add_news(self, item):
        with self._get_connection() as conn:
            p_date = item.published.isoformat()
            conn.execute('''INSERT OR IGNORE INTO news VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                (item.unique_id, item.title_hash, item.title, item.source, item.description, item.image_url, p_date, item.link))
            conn.commit()

    def get_last_news(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            res = conn.execute('SELECT * FROM news ORDER BY published_at DESC LIMIT 1').fetchone()
            return dict(res) if res else None