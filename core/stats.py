import json
from pathlib import Path

class StatsManager:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.data = self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f: return json.load(f)
            except: pass
        return {"published": 0, "duplicates": 0, "errors": 0, "sources": {}}

    def log_event(self, event_type, source=None):
        if event_type in self.data: self.data[event_type] += 1
        if source:
            if "sources" not in self.data: self.data["sources"] = {}
            self.data["sources"][source] = self.data["sources"].get(source, 0) + 1
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False)

    def get_report(self):
        s = self.data
        top = sorted(s.get("sources", {}).items(), key=lambda x: x[1], reverse=True)
        src_str = "\n".join([f"• {n}: {c}" for n, c in top[:10]]) or "Нет данных"
        return f"📊 Статистика SantaCryptoNews\n\n✅ Постов: {s['published']}\n🚫 Дублей: {s['duplicates']}\n❌ Ошибок: {s['errors']}\n\n🏆 Источники:\n{src_str}"