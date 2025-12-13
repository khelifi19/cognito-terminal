import requests
import time
import pandas as pd
import random

class DataCollector:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {"User-Agent": "Mozilla/5.0"}
    
    def resolve_coin_id(self, query: str) -> str:
        query = str(query).lower().strip()
        if "(" in query and ")" in query:
            return query.split("(")[1].replace(")", "").strip()
        return query

    def get_market_scanner_data(self, limit=50):
        url = f"{self.base_url}/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": limit, "page": 1, "sparkline": "true", "price_change_percentage": "24h"}
        try:
            time.sleep(1.0)
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                formatted_data = []
                for coin in data:
                    raw_spark = coin.get('sparkline_in_7d', {}).get('price', [])
                    coin['sparkline_processed'] = raw_spark[::4] if raw_spark else []
                    formatted_data.append(coin)
                return pd.DataFrame(formatted_data)
            return pd.DataFrame()
        except: return pd.DataFrame()

    def get_real_time_data(self, asset_input: str) -> dict:
        asset_id = self.resolve_coin_id(asset_input)
        try:
            time.sleep(0.5)
            response = requests.get(f"{self.base_url}/simple/price", params={"ids": asset_id, "vs_currencies": "usd", "include_24hr_vol": "true", "include_24hr_change": "true", "include_market_cap": "true"}, headers=self.headers, timeout=5)
            data = response.json()
            if asset_id not in data: return {"error": f"Asset '{asset_id}' not found."}
            d = data[asset_id]
            return {"id": asset_id, "price": d.get('usd', 0), "volume_24h": d.get('usd_24h_vol', 0), "change_24h": d.get('usd_24h_change', 0), "market_cap": d.get('usd_market_cap', 0)}
        except Exception as e: return {"error": str(e)}

    def get_history(self, asset_id: str, days: int = 30) -> pd.DataFrame:
        try:
            time.sleep(0.5)
            r = requests.get(f"{self.base_url}/coins/{asset_id}/market_chart", params={"vs_currency": "usd", "days": days}, headers=self.headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                prices = data.get('prices', [])
                volumes = data.get('total_volumes', [])
                if not prices: return pd.DataFrame()
                df = pd.DataFrame(prices, columns=['timestamp', 'price'])
                vol_clean = [v[1] for v in volumes]
                df['volume'] = vol_clean[:len(df)]
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df.set_index('timestamp')
            return pd.DataFrame()
        except: return pd.DataFrame()

    def generate_social_feed(self, asset_name: str, change_24h: float) -> list:
        return random.sample([f"{asset_name} is hot!", f"Hold {asset_name}."], 2)

    def get_real_start_price(self, symbol):
        ids = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "AVAX": "avalanche-2", "XRP": "ripple", "DOGE": "dogecoin"}
        asset_id = ids.get(symbol.upper(), "bitcoin")
        try:
            r = requests.get(f"{self.base_url}/simple/price?ids={asset_id}&vs_currencies=usd", headers=self.headers, timeout=5)
            return float(r.json()[asset_id]['usd'])
        except: return 50000.0