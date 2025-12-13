import random
import re
import ollama
from .config import OLLAMA_MODEL
from .data import DataCollector
from .market import NoiseTraderAgent, ChaosAgent

class SimulationEngine:
    def __init__(self, user_cash, user_qty, asset_symbol):
        self.collector = DataCollector()
        self.price = self.collector.get_real_start_price(asset_symbol)
        self.noise_env = NoiseTraderAgent()
        self.chaos_agent = ChaosAgent()
        self.symbol = asset_symbol
        self.cash = user_cash
        self.crypto = user_qty
        self.initial_val = self.cash + (self.crypto * self.price)

    def ask_ai_oracle(self, role, context):
        prompt = f"""
        Act as a {role}.
        Context: {context}
        Task: Analyze the situation. Should we BUY or SELL?
        Output ONLY a single integer score from 0 (Strong Sell) to 100 (Strong Buy).
        No text, just the number.
        """
        try:
            res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
            content = res['message']['content']
            nums = re.findall(r'\d+', content)
            if nums: return int(nums[0])
            else: return 50
        except: return 50

    def generate_daily_summary(self, day, headline, action, pnl_day):
        prompt = f"Summarize this trading day in 1 short English sentence: Asset {self.symbol}, News '{headline}', Action {action}, PnL {pnl_day:.2f}%."
        try:
            res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
            return res['message']['content'].strip()
        except: return f"Day {day}: {action} executed."

    def generate_final_report(self, logs):
        try:
            res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': f"Write a short financial report based on these logs: {logs}"}])
            return res['message']['content']
        except: return "Simulation Completed."

    def step(self, day):
        market_mood = random.choice(["Major Crash", "Bad News", "Neutral", "Good News", "Huge Pump"])
        try:
            prompt_news = f"Generate a 1-sentence crypto headline about {self.symbol}. The mood must be: {market_mood}."
            res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt_news}])
            headline = res['message']['content'].strip()
        except: headline = f"Market is unpredictable regarding {self.symbol}."
        
        noise_impact, noise_log = self.noise_env.generate_noise()
        news_bias = 0.0
        if "bull" in headline.lower() or "high" in headline.lower(): news_bias = 0.04
        elif "bear" in headline.lower() or "low" in headline.lower(): news_bias = -0.04
        
        total_move = noise_impact + (news_bias * random.random())
        self.price = self.price * (1 + total_move)

        s_tech = self.ask_ai_oracle("Technical Analyst", f"Price changed by {total_move*100:.2f}%. Volatility is {'High' if abs(total_move)>0.03 else 'Low'}.")
        s_news = self.ask_ai_oracle("News Sentiment Analyst", f"The current headline is: '{headline}'.")
        s_risk = self.ask_ai_oracle("Risk Manager", f"We have ${self.cash:.0f} in cash and {self.crypto:.2f} coins.")
        s_chaos = self.chaos_agent.vote()

        avg_score = (s_tech + s_news + s_risk + s_chaos) / 4
        action = "HOLD"
        reason = "Neutral Consensus"
        prev_val = self.cash + (self.crypto * self.price)
        
        if avg_score >= 60 and self.cash > 0:
            qty = (self.cash * 0.3) / self.price
            self.crypto += qty; self.cash -= (self.cash * 0.3)
            action = "BUY"
            reason = f"Buy ({avg_score:.0f})"
        elif avg_score <= 40 and self.crypto > 0:
            amt = self.crypto * 0.5
            self.crypto -= amt; self.cash += (amt * self.price)
            action = "SELL"
            reason = f"Sell ({avg_score:.0f})"

        current_val = self.cash + (self.crypto * self.price)
        pnl_day = ((current_val - prev_val) / prev_val) * 100 if prev_val > 0 else 0
        explanation = self.generate_daily_summary(day, headline, action, pnl_day)

        return {
            "day": day, "price": self.price, "headline": headline, "noise_log": noise_log,
            "scores": {"tech": s_tech, "news": s_news, "risk": s_risk, "chaos": s_chaos, "avg": avg_score},
            "action": action, "reason": reason, 
            "value": current_val, "cash": self.cash, "crypto_val": self.crypto * self.price,
            "explanation": explanation
        }