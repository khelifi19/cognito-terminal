import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import random
import json
import os
from datetime import datetime

from backend.data import DataCollector
from backend.analysts import QuantitativeAnalyst, SocialAnalyst, StrategyEngine, ChatAssistant
from backend.engine import SimulationEngine

# --- 1. PAGE CONFIG ---
st.set_page_config(
    layout="wide", 
    page_title="COGNITO TERMINAL", 
    page_icon="💸", 
    initial_sidebar_state="collapsed"
)

# --- 2. GESTION HISTORIQUE & NAVIGATION ---
HISTORY_FILE = "cognito_history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    except: return []

def save_to_history(asset, days, start_val, end_val, pnl_percent, ai_summary):
    history = load_history()
    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Asset": asset.upper(),
        "Duration": f"{days} Days",
        "Initial ($)": start_val,
        "Final ($)": end_val,
        "PnL (%)": pnl_percent,
        "Summary": ai_summary
    }
    history.insert(0, new_entry)
    with open(HISTORY_FILE, "w") as f: json.dump(history, f, indent=4)

if 'page' not in st.session_state: st.session_state.page = 'landing'

def go_to_app(): st.session_state.page = 'app'; st.rerun()
def go_to_home(): st.session_state.page = 'landing'; st.rerun()

# --- 3. CSS ULTRA PRO (FOND D'ÉCRAN + GLASSMORPHISM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    
    /* FOND D'ECRAN GLOBAL */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.9)), 
                          url("https://images.unsplash.com/photo-1639322537228-ad7117a76437?q=80&w=2832&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    /* TYPOGRAPHIE */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #E0E0E0;
    }
    
    h1, h2, h3 { color: #00FFA3 !important; font-weight: 700; text-transform: uppercase; }
    
    /* TITRE LANDING */
    .landing-title {
        font-size: 90px; font-weight: 800;
        background: -webkit-linear-gradient(#fff, #00FFA3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0px; letter-spacing: -2px;
        filter: drop-shadow(0 0 15px rgba(0, 255, 163, 0.4));
    }
    .landing-subtitle {
        font-size: 22px; color: #aaa; text-align: center; margin-top: -10px; margin-bottom: 50px; font-weight: 300;
    }
    
    /* CARTES EFFET VERRE (GLASSMORPHISM) */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease;
        height: 100%;
    }
    .glass-card:hover {
        transform: translateY(-10px);
        border-color: #00FFA3;
        box-shadow: 0 10px 30px rgba(0, 255, 163, 0.1);
    }
    .card-icon { font-size: 40px; margin-bottom: 15px; }
    .card-title { color: #fff; font-size: 20px; font-weight: 700; margin-bottom: 10px; }
    .card-text { color: #bbb; font-size: 14px; line-height: 1.6; }

    /* BOUTON D'ENTRÉE */
    .enter-btn button {
        font-size: 20px !important;
        padding: 15px 40px !important;
        background: linear-gradient(45deg, #00FFA3, #008F7A) !important;
        color: black !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(0, 255, 163, 0.4);
        transition: all 0.3s ease;
    }
    .enter-btn button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 40px rgba(0, 255, 163, 0.7);
    }

    /* STYLES INTERNES APP */
    div[data-testid="stMetric"] {
        background: rgba(0, 20, 10, 0.6);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(0, 255, 163, 0.2);
        border-radius: 15px; padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# PARTIE A : LANDING PAGE (MODERNISÉE)
# ==========================================
if st.session_state.page == 'landing':
    
    # Espaceur pour centrer verticalement
    st.write("")
    st.write("")
    
    # 1. HEADER & LOGO
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        st.markdown('<p class="landing-title">COGNITO</p>', unsafe_allow_html=True)
        st.markdown('<p class="landing-subtitle">The Autonomous Multi-Agent Trading System • Powered by Llama 3</p>', unsafe_allow_html=True)
        
        # BOUTON CENTRAL
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            st.markdown('<div class="enter-btn">', unsafe_allow_html=True)
            if st.button("🚀 ENTER TERMINAL", use_container_width=True):
                go_to_app()
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.write("")

    # 2. CARTES FONCTIONNALITÉS (GRID)
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🧠</div>
            <div class="card-title">LLM Core Intelligence</div>
            <div class="card-text">
                Powered by a local <b>Llama 3</b> engine. It reads news, interprets volatility, and generates human-like financial reports in real-time.
            </div>
            <br>
            <img src="https://plus.unsplash.com/premium_photo-1683121710572-7723bd2e235d?q=80&w=2832&auto=format&fit=crop" style="width:100%; border-radius:10px; opacity:0.8;">
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🧬</div>
            <div class="card-title">Multi-Agent Simulation</div>
            <div class="card-text">
                Watch 4 autonomous agents (Tech, News, Risk, Chaos) debate and vote on trade execution. <b>Emergent behavior</b> at its finest.
            </div>
            <br>
            <img src="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2832&auto=format&fit=crop" style="width:100%; border-radius:10px; opacity:0.8;">
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🔍</div>
            <div class="card-title">Deep Crypto Audit</div>
            <div class="card-text">
                Connects to CoinGecko API for live data. Visualizes RSI, MACD, and Sentiment Scores via professional dynamic gauges.
            </div>
            <br>
            <img src="https://images.unsplash.com/photo-1642543492481-44e81e3914a7?q=80&w=2940&auto=format&fit=crop" style="width:100%; border-radius:10px; opacity:0.8;">
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.divider()
    st.markdown("<div style='text-align:center; color:#555;'>v2.0.4 • Powered by Streamlit & Ollama • Local Privacy First</div>", unsafe_allow_html=True)


# ==========================================
# PARTIE B : APPLICATION PRINCIPALE
# ==========================================
elif st.session_state.page == 'app':

    if 'sim_running' not in st.session_state: st.session_state.sim_running = False
    if 'sim_config' not in st.session_state: st.session_state.sim_config = {}

    @st.cache_resource
    def load_system():
        return {
            "Data": DataCollector(), "Quant": QuantitativeAnalyst(),
            "Social": SocialAnalyst(), "Strategy": StrategyEngine(), "Chat": ChatAssistant()
        }
    sys = load_system()

    @st.cache_data(ttl=300)
    def get_cached_market_data(): return sys["Data"].get_market_scanner_data(50)

    # --- HELPERS ---
    def create_gauge(value, color_scale="Green"):
        color = "#00FFA3" if color_scale == "Green" else "#00C4CC"
        if value < 4: color = "#FF4B4B"
        elif value < 6.5: color = "#FFA500"
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'axis': {'range': [0, 10], 'tickcolor': "#333"}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 2, 'bordercolor': "#333", 'steps': [{'range': [0, 4], 'color': 'rgba(255, 75, 75, 0.1)'}, {'range': [4, 6.5], 'color': 'rgba(255, 165, 0, 0.1)'}]},
            number = {'font': {'color': 'white'}}
        ))
        fig.update_layout(height=160, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        return fig

    def create_clean_chart(df, asset_name, change_24h):
        color = '#00FFA3' if change_24h >= 0 else '#FF4B4B'
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
        fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', line=dict(color=color, width=2), fill='tozeroy'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], marker_color='rgba(255, 255, 255, 0.3)'), row=2, col=1)
        fig.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False, color='#666'), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#666'))
        return fig

    # --- SIDEBAR ---
    with st.sidebar:
        if st.button("🏠 EXIT TERMINAL"): go_to_home()
        st.divider()
        st.header("💬 AI Assistant")
        if "msgs" not in st.session_state: st.session_state["msgs"] = []
        for m in st.session_state["msgs"]: st.chat_message(m["role"]).write(m["content"])
        if p := st.chat_input("Ask about crypto..."):
            st.session_state["msgs"].append({"role":"user", "content":p})
            st.chat_message("user").write(p)
            st.chat_message("assistant").write(sys["Chat"].respond(p))

    # --- HEADER ---
    c_logo, c_title = st.columns([1, 6])
    with c_logo: st.markdown("## 💸")
    with c_title:
        st.title("COGNITO TERMINAL")
        st.caption("INSTITUTIONAL GRADE AI TRADING SYSTEM")

    # --- GLOBAL SCANNER ---
    st.markdown("### 🌍 Global Market Overview")
    with st.container(border=True):
        df_market = get_cached_market_data()
        assets_list = []
        if not df_market.empty:
            df_market = sys["Quant"].batch_calculate(df_market)
            assets_list = [f"{row['symbol'].upper()} ({row['id']})" for _, row in df_market.iterrows()]
            st.dataframe(
                df_market[['image', 'symbol', 'sparkline_processed', 'current_price', 'price_change_percentage_24h', 'Tech_Score']], 
                column_config={
                    "image": st.column_config.ImageColumn("", width="small"), 
                    "symbol": st.column_config.TextColumn("Ticker", width="small"),
                    "sparkline_processed": st.column_config.LineChartColumn("7d Trend", width="medium"),
                    "current_price": st.column_config.NumberColumn("Price ($)", format="$%.4f"),
                    "price_change_percentage_24h": st.column_config.NumberColumn("24h %", format="%.2f %%"),
                    "Tech_Score": st.column_config.ProgressColumn("Cognito Score", min_value=0, max_value=10, format="%.1f/10"),
                },
                use_container_width=True, hide_index=True, height=400
            )
        else:
            st.warning("⚠️ API Rate Limit. Using basic fallback data.")
            assets_list = ["BTC (bitcoin)", "ETH (ethereum)", "SOL (solana)", "AVAX (avalanche-2)", "XRP (ripple)"]

    st.write("") 

    # --- TABS ---
    tab_audit, tab_duel, tab_strat, tab_history = st.tabs(["🔍 DEEP AUDIT", "⚔️ ASSET DUEL", "🧬 MULTI-AGENT SIM", "📜 HISTORY"])

    # --- TAB 1: AUDIT ---
    with tab_audit:
        st.markdown("#### Real-Time Asset Analysis")
        c1, c2 = st.columns([3, 1])
        with c1: sel_asset = st.selectbox("Select Asset to Audit", assets_list, label_visibility="collapsed")
        with c2: btn_analyze = st.button("RUN ANALYSIS", type="primary", use_container_width=True)

        if btn_analyze:
            target = sel_asset
            with st.status(f"🚀 Initializing Deep Audit for **{target}**...", expanded=True) as status:
                st.write("📡 Establishing secure connection to Market API...")
                market = sys["Data"].get_real_time_data(target)
                if "error" not in market:
                    st.write("🧮 Computing RSI, MACD & Volatility...")
                    hist = sys["Data"].get_history(market['id'])
                    q = sys["Quant"].calculate_deep_indicators(market, hist)
                    st.write("🧠 Engaging LLM for Sentiment Analysis...")
                    feed = sys["Data"].generate_social_feed(market['id'], market['change_24h'])
                    social_res = sys["Social"].analyze_sentiment(feed)
                    status.update(label="✅ Analysis Completed", state="complete", expanded=False)

                    st.divider()
                    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
                    c_kpi1.metric("Current Price", f"${market['price']}", f"{market['change_24h']:.2f}%")
                    c_kpi2.metric("24h Volume", f"${market['volume_24h']:,.0f}")
                    c_kpi3.metric("Market Cap", f"${market['market_cap']:,.0f}")
                    c_kpi4.metric("RSI (14)", f"{q['RSI']}", delta_color="off")

                    st.write("")
                    with st.container(border=True):
                        st.markdown("#### 🧠 Intelligence Consensus")
                        col_gauges, col_summary = st.columns([2, 1])
                        with col_gauges:
                            g1, g2 = st.columns(2)
                            with g1:
                                st.plotly_chart(create_gauge(q['Score'], "Green"), use_container_width=True)
                                st.caption("Technical Score")
                            with g2:
                                dynamic_social = social_res.get('sentiment_score', 5.0)
                                st.plotly_chart(create_gauge(dynamic_social, "Blue"), use_container_width=True)
                                st.caption("Sentiment Score")
                        with col_summary:
                            st.info(f"**SIGNAL: {q['Signal']}**")
                            st.markdown(f"Outlook: **{social_res.get('mood', 'Neutral')}**")

                    if not hist.empty:
                        st.write("")
                        st.markdown("#### 📉 Price Action (30D)")
                        with st.container(border=True):
                            st.plotly_chart(create_clean_chart(hist, market['id'], market['change_24h']), use_container_width=True)
                else: st.error(f"Error: {market['error']}")

    # --- TAB 2: DUEL ---
    with tab_duel:
        st.markdown("#### Head-to-Head Comparison")
        c1, c2, c3 = st.columns([2, 2, 1])
        a = c1.selectbox("Asset A", assets_list, index=0)
        b = c2.selectbox("Asset B", assets_list, index=1)
        if c3.button("VS", use_container_width=True):
            col_a, col_b = st.columns(2)
            def show_mini(col, name):
                with col:
                    d = sys["Data"].get_real_time_data(name)
                    if "error" not in d:
                        with st.container(border=True):
                            st.metric(name, f"${d['price']}", f"{d['change_24h']}%")
            show_mini(col_a, a); show_mini(col_b, b)

    # --- TAB 3: SIMULATION ---
    with tab_strat:
        st.markdown("#### 🧬 Multi-Agent Market Simulation")
        with st.container():
            ag1, ag2, ag3, ag4 = st.columns(4)
            with ag1: st.info("**🤖 Tech Agent**\n\nQuant")
            with ag2: st.success("**📰 News Agent**\n\nSentiment")
            with ag3: st.warning("**🛡️ Risk Agent**\n\nGuard")
            with ag4: st.error("**🃏 Chaos Agent**\n\nEntropy")

        with st.container(border=True):
            with st.form("simulation_form_ui"):
                c1, c2, c3, c4 = st.columns(4)
                raw_asset = c1.selectbox("Target Asset", assets_list, index=0)
                sim_asset = raw_asset.split(" ")[0] if " " in raw_asset else raw_asset
                sim_cash = c2.number_input("Initial Cash ($)", min_value=500, max_value=100000, value=10000, step=500)
                sim_qty = c3.number_input(f"Starting {sim_asset}", 0.5, step=0.1)
                sim_days = c4.slider("Days", 5, 60, 10)
                submitted = st.form_submit_button("🔴 INITIALIZE SIMULATION", type="primary", use_container_width=True)

        if submitted:
            st.session_state.sim_running = True
            st.session_state.sim_config = {"cash": sim_cash, "qty": sim_qty, "asset": sim_asset, "days": sim_days}

        if st.session_state.sim_running:
            cfg = st.session_state.sim_config
            engine = SimulationEngine(cfg["cash"], cfg["qty"], cfg["asset"])
            
            st.write("")
            with st.status("🚀 Booting Agents...", expanded=True) as status:
                time.sleep(0.5); st.write("🌍 Connecting..."); time.sleep(0.5); st.write("🤖 Agents deliberating...")
                status.update(label="Simulation Live", state="complete", expanded=False)
            
            live_display = st.empty()
            chart_display = st.empty()
            full_table_data = []
            history_vals = []
            full_logs = ""

            for day in range(1, cfg['days'] + 1):
                s = engine.step(day)
                history_vals.append({"Day": day, "Total Value": s['value'], "Baseline": engine.initial_val})
                full_table_data.append({"Day": day, "Price": f"${s['price']:,.2f}", "Action": s['action'], "Reason": s['reason'], "Cash": f"${s['cash']:,.0f}", "Total Value": f"${s['value']:,.0f}", "AI Summary": s['explanation']})
                full_logs += f"{s['explanation']}\n"
                
                with live_display.container():
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1: st.markdown(f"##### 📅 Day {day} / {cfg['days']}"); st.caption(f"NEWS: {s['headline']}")
                        with c2: st.metric("Asset Price", f"${s['price']:,.2f}")
                        cols = st.columns(5)
                        cols[0].metric("Tech", s['scores']['tech']); cols[1].metric("News", s['scores']['news'])
                        cols[2].metric("Risk", s['scores']['risk']); cols[3].metric("Chaos", s['scores']['chaos'])
                        cols[4].metric("AVG", f"{s['scores']['avg']:.0f}")
                        if s['action'] == "BUY": st.success(f"✅ BUY ({s['reason']})")
                        elif s['action'] == "SELL": st.error(f"🔻 SELL ({s['reason']})")
                        else: st.info(f"⏸️ HOLD ({s['reason']})")

                df_chart = pd.DataFrame(history_vals)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_chart['Day'], y=df_chart['Baseline'], mode='lines', name='Start', line=dict(color='gray', dash='dash')))
                fig.add_trace(go.Scatter(x=df_chart['Day'], y=df_chart['Total Value'], mode='lines+markers', name='Portfolio', line=dict(color='#00FFA3', width=3)))
                fig.update_layout(title="📈 Live Performance", height=350, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), hovermode="x unified")
                chart_display.plotly_chart(fig, use_container_width=True)
                time.sleep(0.1)

            st.divider()
            st.subheader("🏁 Mission Report")
            with st.spinner("Compiling Final Analysis..."):
                final_report = engine.generate_final_report(full_logs)
                st.success(final_report)
            
            # SAUVEGARDE HISTORIQUE
            pnl_final = ((history_vals[-1]['Total Value'] - engine.initial_val) / engine.initial_val) * 100
            save_to_history(cfg['asset'], cfg['days'], engine.initial_val, history_vals[-1]['Total Value'], pnl_final, final_report)
            st.toast("Simulation saved to History!", icon="💾")

            st.write("### 📋 Transaction Log")
            st.dataframe(pd.DataFrame(full_table_data), column_config={"AI Summary": st.column_config.TextColumn("AI Logic", width="large")}, use_container_width=True, hide_index=True)
            st.session_state.sim_running = False

    # --- TAB 4: HISTORY ---
    with tab_history:
        st.markdown("#### 📜 Past Simulations Archive")
        history_data = load_history()
        
        if not history_data:
            st.info("No simulations recorded yet.")
        else:
            df_history = pd.DataFrame(history_data)
            st.dataframe(
                df_history,
                column_config={
                    "Date": st.column_config.TextColumn("Date", width="medium"),
                    "Asset": st.column_config.TextColumn("Asset", width="small"),
                    "Duration": st.column_config.TextColumn("Duration", width="small"),
                    "Initial ($)": st.column_config.NumberColumn("Initial", format="$%.0f"),
                    "Final ($)": st.column_config.NumberColumn("Final", format="$%.0f"),
                    "PnL (%)": st.column_config.ProgressColumn("Profit/Loss", min_value=-50, max_value=50, format="%.2f%%"),
                    "Summary": st.column_config.TextColumn("AI Summary", width="large"),
                },
                use_container_width=True,
                hide_index=True
            )
            if st.button("🗑️ Clear History"):
                if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE); st.rerun()