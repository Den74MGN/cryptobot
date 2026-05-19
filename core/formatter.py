import re
import random

class PostFormatter:
    def __init__(self, channel_name, channel_link, tag_categories, default_hashtags):
        self.channel_name, self.channel_link = channel_name, channel_link
        self.tag_categories, self.default_hashtags = tag_categories, default_hashtags

    def escape_md(self, text: str) -> str:
        if not text: return ""
        special = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(special)}])', r'\\\1', str(text))

    def format_market_report(self, fng, prices):
        val = int(fng['value'])
        emoji = "😨" if val < 40 else "🤩" if val > 60 else "😐"
        bar = "▰" * (val // 10) + "▱" * (10 - (val // 10))
        text = f"📊 *ОБЗОР РЫНКА (МСК)*\n\n{emoji} *Индекс страха:* {val}/100\nСтатус: _{self.escape_md(fng['value_classification'])}_\n`{bar}`\n\n💰 *Курсы активов:*\n"
        for coin, data in prices.items():
            change = data.get('usd_24h_change', 0)
            price = data.get('usd', 0)
            c_emoji = "📈" if change > 0 else "📉"
            p_form = f"{price:,.0f}$".replace(',', ' ')
            text += f"• {coin.capitalize()}: *{self.escape_md(p_form)}* ({c_emoji} {change:.1f}%)\n"
        brand = self.escape_md(f"📢 Подпишись на {self.channel_name}")
        return f"{text}\n[{brand}]({self.channel_link})\n\n#MarketUpdate #FearAndGreed"

    def generate_tags(self, title, desc):
        text = (title + " " + (desc if desc else "")).lower()
        tags = {f"#{self.channel_name}"}
        for category, mapping in self.tag_categories.items():
            found = [t for k, t in mapping.items() if k in text]
            if found:
                random.shuffle(found)
                tags.update(found[:2])
        target = random.randint(5, 7)
        avail = [t for t in self.default_hashtags if t not in tags]
        random.shuffle(avail)
        while len(tags) < target and avail: tags.add(avail.pop())
        return " ".join([self.escape_md(t) for t in tags])

    def format_news(self, news):
        title = self.escape_md(news.title.upper())
        raw_body = news.description if news.description else ""
        sentences = [s.strip() for s in raw_body.split(". ") if len(s.strip()) > 5]
        if sentences:
            body = f"◈ _{self.escape_md(sentences[0])}\\._\n\n"
            rem = sentences[1:]
            for i in range(0, len(rem), 2):
                chunk = ". ".join(rem[i:i+2])
                if chunk: body += self.escape_md(chunk) + "\\.\n\n"
        else: body = self.escape_md(raw_body)
        tags = self.generate_tags(news.title, news.description)
        brand = self.escape_md(f"📢 Подпишись на {self.channel_name}")
        safe_l = str(self.channel_link).replace(')', '\\)').replace('\\', '\\\\')
        return f"⚡️ *{title}*\n\n{body}📍 Источник: \\#{self.escape_md(news.source)}\n[{brand}]({safe_l})\n\n{tags}"