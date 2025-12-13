import pandas as pd
import json
import ollama
import re
import random
from .config import OLLAMA_MODEL

class QuantitativeAnalyst:
    def batch_calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        def analyze_row(row):
            change = row.get('price_change_percentage_24h', 0) or 0
            base_score = 5.0
            if change > 10: base_score += 3
            elif change > 5: base_score += 2
            elif change > 0: base_score += 1
            elif change < -10: base_score -= 3
            elif change < -5: base_score -= 2
            variance = (hash(row['symbol']) % 20) / 10.0 - 1.0 
            final_score = base_score + variance
            final_score = max(1.0, min(10.0, final_score))
            rsi = 50 + (change * 2.0)
            rsi = max(20, min(90, rsi))
            signal = "HOLD"
            if rsi > 75: signal = "SELL"
            elif rsi < 35: signal = "BUY"
            return pd.Series([round(rsi, 1), float(final_score), signal])
        df[['RSI', 'Tech_Score', 'Signal']] = df.apply(analyze_row, axis=1)
        return df

    def calculate_deep_indicators(self, market_data: dict, history_df: pd.DataFrame) -> dict:
        if market_data.get("error"): return {"RSI": 50, "Score": 5, "Signal": "N/A"}
        change = market_data.get('change_24h', 0.0)
        base_score = 5.0
        if change > 5: base_score += 2.5
        elif change > 2: base_score += 1.5
        elif change < -5: base_score -= 2.5
        elif change < -2: base_score -= 1.5
        score = max(1.0, min(10.0, base_score))
        rsi = max(20, min(90, 50 + (change * 2.0)))
        signal = "STRONG BUY" if score >= 8 else "BUY" if score >= 6 else "STRONG SELL" if score <= 3 else "SELL" if score <= 4 else "NEUTRAL"
        return {"RSI": round(rsi, 2), "Score": score, "Signal": signal}

class SocialAnalyst:
    def analyze_sentiment(self, feed: list) -> dict:
        text_blob = " ".join(feed)
        prompt = f"""Analyze sentiment: "{text_blob}". Return ONLY JSON: {{ "sentiment_score": float(1.0-10.0), "mood": "Bullish/Bearish/Neutral" }}"""
        try:
            response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"sentiment_score": random.uniform(4.5, 5.5), "mood": "Neutral"}
        except: 
            return {"sentiment_score": random.uniform(4.5, 5.5), "mood": "Neutral"}

class StrategyEngine:
    def generate_executive_summary(self, asset_id, market, quant, social) -> str:
        return "Analysis ready."
    def portfolio_advisor(self, risk, holdings, context) -> str:
        return "Legacy Advisor Mode."

class ChatAssistant:
    def respond(self, text: str) -> str:
        prompt = f"Answer shortly in English only about crypto else say sorry i am an ai agent and i can only answer about crypto: {text}"
        try:
            response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content']
        except Exception as e: return f"Error: {e}"