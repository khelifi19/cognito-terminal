import random

class NoiseTraderAgent:
    def generate_noise(self):
        sentiment = random.choice([-1, 1, 0, 0, 1]) 
        volatility = random.uniform(0.005, 0.04) 
        impact = sentiment * volatility
        log = "Calm."
        if impact > 0.02: log = "🌊 Noise: FOMO (+)"
        elif impact < -0.02: log = "📉 Noise: Panic (-)"
        return impact, log

class ChaosAgent:
    def vote(self):
        return random.randint(0, 100)