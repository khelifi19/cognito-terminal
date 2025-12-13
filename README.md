# 💸 COGNITO TERMINAL

> **Institutional Grade AI Financial Intelligence**
> *Autonomous Multi-Agent Crypto Trading System powered by Local Llama 3 & Real-Time Analytics.*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Ollama](https://img.shields.io/badge/AI-Llama3-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

**Cognito Terminal** is not just a dashboard. It is a **Multi-Agent System (MAS)** where 4 distinct Artificial Intelligences (Tech, News, Risk, Chaos) debate and vote to make trading decisions in real-time.

Everything runs **locally** on your machine using **Ollama**, ensuring complete privacy for your strategies and zero latency.

### ✨ Key Features
- **🌍 Global Scanner:** Live market overview with auto-zooming Sparklines (7d trends).
- **🔍 Deep Audit:** Hybrid asset analysis (Math + AI) with dynamic sentiment gauges.
- **🧬 Multi-Agent Simulation:** Watch agents buy/sell based on AI-generated news and market physics.
- **📜 Persistent History:** Automatically saves your simulation results to a local JSON database.

---

## 🛠️ Installation Guide

### 1. Prerequisites
* **Python 3.10+** installed.
* **[Ollama](https://ollama.com/)** installed (to run the AI brain).

### 2. Clone the Repository
Open your terminal and run:
```bash
git clone [https://github.com/YOUR_USERNAME/cognito-terminal.git](https://github.com/YOUR_USERNAME/cognito-terminal.git)
cd cognito-terminal

************

3. Install Dependencies
Install the required Python libraries:
```bash
pip install -r requirements.txt

************* 

4. Setup the AI Model (Crucial)
Download the specific Llama 3 model used by the agents:

Bash

ollama pull llama3:8b

*************

🚀 How to Run
You will need two terminal windows open to run the system.

Terminal 1: Start the AI Brain

Bash

ollama serve
(Keep this window open in the background)

Terminal 2: Launch the App Navigate to your project folder and run:

Bash

streamlit run app.py
A browser tab will automatically open at http://localhost:8501. Click "ENTER TERMINAL" to start.


***********************

📂 Project Architecture
The codebase follows a clean Separation of Concerns architecture:

Plaintext

COGNITO/
├── app.py                  # Frontend (Streamlit UI, Navigation, Visuals)
├── backend/                # Logic Core
│   ├── __init__.py         # Package initializer
│   ├── config.py           # Configuration constants
│   ├── data.py             # CoinGecko API Connection
│   ├── analysts.py         # Analysis Agents (Tech, Social, Chat)
│   ├── market.py           # Simulation Agents (Noise, Chaos)
│   └── engine.py           # Simulation Orchestrator
├── cognito_history.json    # Local database (Simulation logs)
└── requirements.txt        # Dependencies list