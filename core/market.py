import logging

logger = logging.getLogger("SantaBot.Market")

class MarketManager:
    def __init__(self, fear_greed_url, coingecko_url, ticker_coins):
        self.fear_greed_url = fear_greed_url
        self.coingecko_url = coingecko_url
        self.ticker_coins = ticker_coins

    async def get_fear_greed(self, session):
        try:
            async with session.get(self.fear_greed_url, timeout=10) as resp:
                data = await resp.json()
                return data['data'][0]
        except Exception as e:
            logger.error(f"Ошибка Fear&Greed: {e}")
            return None

    async def get_prices(self, session):
        params = {
            "ids": ",".join(self.ticker_coins),
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        try:
            async with session.get(self.coingecko_url, params=params, timeout=10) as resp:
                return await resp.json()
        except Exception as e:
            logger.error(f"Ошибка CoinGecko: {e}")
            return None