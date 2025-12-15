# 🤖 AI Collaboration & Prompts Documentation

**Project:** Cognito Terminal
**Context:** Institutional-Grade AI Trading System

This document traces the iterative development process with AI assistants. It highlights not just the successful prompts, but the **edge cases, logic bugs, API crashes, and LLM hallucinations** encountered during development and how they were resolved through specific prompting strategies.

---

## 1. UI/UX: The "Invisible Text" & Dark Mode Bug

**Goal:** Implement a "Cyberpunk/Institutional" interface without breaking Streamlit's native accessibility.

> **Initial Prompt:**
> "Generate a CSS block to turn the Streamlit app background to dark hex #0E1117 and make the buttons neon green."

**❌ The Issue:** The code worked for the background, but Streamlit's default font color remained dark grey, making all sidebar text and input labels invisible/unreadable against the black background.

> **Correction Prompt:**
> "The previous CSS made the text unreadable because the font color didn't update.
> Please analyze the DOM structure of Streamlit widgets (specifically `.stTextInput` and `.css-1d391kg`) and provide a specific CSS override to force all label fonts to white (`#FAFAFA`) and bold them."

**✅ Outcome:** A robust `markdown(unsafe_allow_html=True)` block that targets specific Streamlit classes to ensure contrast compliance and readability.

---

## 2. Logic Architecture: Fixing the "Passive" Agents

**Goal:** Create a Multi-Agent Simulation (MAS) where agents actually disagree based on distinct personalities.

> **Initial Prompt:**
> "Write a Python class for a 'Multi-Agent Simulation'. I want a Tech Agent, a News Agent, and a Chaos Agent. They should return a score between 0 and 100."

**❌ The Issue:** The AI generated a script where agents simply returned random numbers using `random.randint()`. This felt meaningless; there was no logic behind the "debate," and the consensus was just a flat average.

> **Refinement Prompt:**
> "This logic is too simple. The agents need 'personalities' based on input data.
> 1. Refactor the **Tech Agent** to weigh the input 'RSI' value heavily (if RSI > 70, score should drop).
> 2. The **Chaos Agent** should introduce drift based on a 'volatility' parameter, not just random noise.
> 3. Implement a **Weighted Average** calculation where the 'Risk Agent' has a 2x veto power if the market is crashing."

**✅ Outcome:** A nuanced `SimulationEngine` class where agents react differently to the same data input, creating realistic "debates" in the logs.

---

## 3. Data Visualization: The "White Box" Glitch

**Goal:** Integrate Plotly gauge charts seamlessly into the dark theme for the "Deep Audit" section.

> **Initial Prompt:**
> "Create a Plotly gauge chart for the Sentiment Score."

**❌ The Issue:** Plotly generated the chart with a large white square background and standard margins, ruining the dark UI integration.

> **Debugging Prompt:**
> "The chart looks bad. It has a white background and huge padding.
> Update the Plotly `update_layout` parameters to:
> 1. Set `paper_bgcolor` and `plot_bgcolor` to 'rgba(0,0,0,0)' (transparent).
> 2. Set margins to zero (`l=0, r=0, t=0, b=0`).
> 3. Change the font color to white."

**✅ Outcome:** Professional, transparent widgets that float perfectly on the dark background.

---

## 4. API Handling: The "Rate Limit" Crash

**Goal:** Fetch real data from CoinGecko without crashing the app during demos.

> **Initial Prompt:**
> "Write a function to fetch Ethereum price data from CoinGecko API for the last 30 days."

**❌ The Issue:** The app crashed immediately upon testing with a `429 Too Many Requests` error because the AI placed the API call inside the main Streamlit loop, fetching data on every single interaction (button click/hover).

> **Architectural Fix Prompt:**
> "I'm getting a 429 error. The API is being called too often.
> Please refactor this function to use Streamlit's caching decorator (`@st.cache_data`). Also, add a `try/except` block to return mock data if the API fails, so the app doesn't break during the demo."

**✅ Outcome:** A resilient `get_market_data` function that caches results for 5 minutes and degrades gracefully if the API is down.

---

## 5. Streamlit State Management: The "Amnesia" Bug

**Goal:** Keep the AI Assistant chat history alive while the user interacts with other tabs (Market Overview, Simulation).

> **Initial Prompt:**
> "Create a chatbot sidebar in Streamlit. It should append user messages and AI responses to a list `messages = []` and display them."

**❌ The Issue:** Streamlit acts as a loop. Every time the user clicked "Run Analysis" or changed a filter in the main dashboard, the script re-ran from top to bottom, resetting `messages = []` to empty. The chat history vanished instantly.

> **Fix Prompt:**
> "The chat history is deleted every time I interact with a button. The variable `messages` keeps resetting.
> Refactor this to use `st.session_state`. Check if 'chat_history' exists in session_state; if not, initialize it. Only append new messages to this persistent state."

**✅ Outcome:** A persistent chat interface that remembers context even while the user navigates between different trading tools.

---

## 6. Financial Accuracy: The "RSI Mismatch" Bug

**Goal:** Calculate the Relative Strength Index (RSI) for the Deep Audit section.

> **Initial Prompt:**
> "Write a Python function to calculate RSI based on a list of closing prices."

**❌ The Issue:** The AI provided a "Simple Moving Average" version of RSI. When compared to TradingView or CoinGecko, the values were off by 5-10 points (e.g., showing 45 instead of 53). It wasn't using the industry-standard smoothing method.

> **Correction Prompt:**
> "The RSI values are inaccurate compared to trading platforms. You are using a simple average for gains/losses.
> Rewrite the function to use **Wilder's Smoothing method** (Exponential Moving Average) for the RS calculation. The lookback period must be exactly 14 periods."

**✅ Outcome:** A mathematically rigorous `calculate_rsi` function that matches institutional data sources.

---

## 7. LLM Output Control: The "Markdown Hallucination"

**Goal:** Generate a structured "Mission Report" at the end of the simulation that Streamlit can render cleanly.

> **Initial Prompt:**
> "Analyze the simulation log and summarize the performance. Give me a title, the PnL, and a summary."

**❌ The Issue:** The local Llama 3 model would sometimes output raw text, sometimes JSON, or sometimes add conversational filler like "Here is your report:", breaking the UI layout which expected specific dictionary keys.

> **Structuring Prompt:**
> "You are a JSON-only API. Do not output conversational text.
> Analyze the data and return a strictly valid JSON object with these exact keys:
> `{
>   'title': 'string',
>   'pnl_percentage': 'float',
>   'summary_text': 'string (max 50 words)',
>   'key_decision': 'string'
> }`
> If the PnL is negative, the tone of the summary must be 'Cautionary'. If positive, 'Analytical'."

**✅ Outcome:** A robust parsing system where the UI extracts clean data from the LLM to display the green "Mission Report" card reliably every time.

---

## 8. Content Generation: Video Script Timing

**Goal:** Squeeze technical explanations into a short video format.

> **Initial Prompt:**
> "Write a script explaining the Multi-Agent Simulation."

**❌ The Issue:** The generated script was 4 minutes long, too verbose, and used generic words like "innovative features" repeatedly.

> **Editing Prompt:**
> "This is too long. I have exactly 90 seconds for this section (1:30 to 3:00).
> Cut the fluff. Focus only on:
> 1. Initialization (Input form).
> 2. The voting process (Agents debating).
> 3. The Mission Report.
> Use 'Institutional' tone. Sync the text with specific visual cues like 'clicking the button'."

**✅ Outcome:** A punchy, time-coded script used for the final project voiceover.