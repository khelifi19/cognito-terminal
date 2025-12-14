import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import random
import json
import os
from datetime import datetime

# IMPORTS BACKEND
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

# --- 3. CSS FINAL (CORRIGÉ : SIDEBAR NOIRE + TEXTE BLANC) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* --- 1. FOND GÉNÉRAL & POLICE --- */
    /* Fond de l'application principale */
    [data-testid="stAppViewContainer"] {
        background-color: #0E1117;
    }
    /* Fond du Header (transparent) */
    [data-testid="stHeader"] {
        background: transparent;
    }
    /* Police globale et couleur par défaut (Blanc cassé) */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E6E6E6; 
    }

    /* --- 2. SIDEBAR NOIRE (CORRECTION ICI) --- */
    /* Force le fond de la sidebar en noir pour correspondre au thème */
    [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
        border-right: 1px solid #30363D;
    }
    /* Corrige les titres dans la sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #00FFA3 !important; /* Vert fluo */
    }
    /* Corrige les textes normaux dans la sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div, [data-testid="stSidebar"] span {
        color: #FFFFFF !important; /* Blanc pur */
    }

    /* --- 3. TITRES VERTS FLUO --- */
    h1, h2, h3, h4, h5 {
        color: #00FFA3 !important;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    /* --- 4. TEXTE DES PARAGRAPHES (MAIN APP) --- */
    [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-size: 16px;
    }

    /* --- 5. INPUTS & SELECTBOX --- */
    /* Fond des menus déroulants et champs texte */
    div[data-baseweb="select"] > div, [data-testid="stTextInput"] input {
        background-color: #161B22 !important;
        color: white !important;
        border-color: #30363D !important;
    }
    div[data-baseweb="popover"] {
        background-color: #161B22 !important;
    }
    div[role="option"] {
        color: white !important;
    }
    
    /* --- 6. MESSAGES CHAT (Spécifique) --- */
    /* Bulle utilisateur */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
    }

    /* --- 7. CARTES STATS (METRICS) --- */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 15px;
    }
    div[data-testid="stMetricLabel"] {
        color: #8B949E !important; 
        font-size: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important; 
        font-size: 26px !important;
        font-weight: 700;
    }

    /* --- 8. BOUTONS VERTS --- */
    .stButton > button {
        background-color: #00FFA3;
        color: #000000 !important;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(0, 255, 163, 0.3);
        color: #000000 !important;
    }

    /* --- 9. STYLES SPÉCIAUX (Landing & Cards) --- */
    .landing-title {
        font-size: 72px;
        font-weight: 800;
        color: #00FFA3 !important;
        text-align: center;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: -2px;
    }
    .landing-subtitle {
        font-size: 20px;
        color: #FFFFFF !important;
        text-align: center;
        margin-bottom: 50px;
        font-weight: 500;
    }
    .glass-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        height: 100%;
        transition: transform 0.2s;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: #00FFA3;
    }
    .card-title { color: #FFFFFF !important; font-size: 20px; font-weight: 700; margin-bottom: 10px; }
    .card-text { color: #8B949E !important; font-size: 15px; line-height: 1.6; }
    
    .enter-btn button {
        font-size: 18px !important;
        background: #00FFA3 !important;
        color: black !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# PARTIE A : LANDING PAGE
# ==========================================
if st.session_state.page == 'landing':
    
    st.write(""); st.write(""); st.write("")
    
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        st.markdown('<p class="landing-title">COGNITO</p>', unsafe_allow_html=True)
        st.markdown('<p class="landing-subtitle">The Autonomous Multi-Agent Trading System • Powered by Llama 3</p>', unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            st.markdown('<div class="enter-btn">', unsafe_allow_html=True)
            if st.button("🚀 ENTER TERMINAL", use_container_width=True):
                go_to_app()
            st.markdown('</div>', unsafe_allow_html=True)

    st.write(""); st.write(""); st.write("")

    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size: 40px; margin-bottom: 10px;">🧠</div>
            <div class="card-title">LLM Core Intelligence</div>
            <div class="card-text">
                Powered by a local <b>Llama 3</b> engine. It reads news, interprets volatility, and generates human-like financial reports.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size: 40px; margin-bottom: 10px;">🧬</div>
            <div class="card-title">Multi-Agent Simulation</div>
            <div class="card-text">
                Watch 4 autonomous agents (Tech, News, Risk, Chaos) debate and vote on trade execution in real-time.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size: 40px; margin-bottom: 10px;">🔍</div>
            <div class="card-title">Deep Crypto Audit</div>
            <div class="card-text">
                Connects to CoinGecko API for live data. Visualizes RSI, MACD, and Sentiment Scores via professional dynamic gauges.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write(""); st.divider()
    st.markdown("<div style='text-align:center; color:#8B949E;'>v2.1.0 • Powered by Streamlit & Ollama • Local Privacy First</div>", unsafe_allow_html=True)


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
            gauge = {'axis': {'range': [0, 10], 'tickcolor': "#FFFFFF", 'tickwidth': 2}, 'bar': {'color': color}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 2, 'bordercolor': "#FFFFFF", 'steps': [{'range': [0, 4], 'color': 'rgba(255, 75, 75, 0.1)'}, {'range': [4, 6.5], 'color': 'rgba(255, 165, 0, 0.1)'}]},
            number = {'font': {'color': 'white'}}
        ))
        fig.update_layout(height=160, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        return fig

    def create_clean_chart(df, asset_name, change_24h):
        color = '#00FFA3' if change_24h >= 0 else '#FF4B4B'
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
        fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', line=dict(color=color, width=2), fill='tozeroy'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], marker_color='rgba(255, 255, 255, 0.3)'), row=2, col=1)
        fig.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showgrid=False, color='#FFF'), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#FFF'))
        return fig

   # --- SIDEBAR ---
    with st.sidebar:
        if st.button("🏠 EXIT TERMINAL"): go_to_home()
        st.divider()
        st.header("💬 AI Assistant")
        
        if "msgs" not in st.session_state: st.session_state["msgs"] = []
        
        # AFFICHER L'HISTORIQUE
        for m in st.session_state["msgs"]:
            with st.chat_message(m["role"]):
                # USER : BLEU (#29B6F6) avec !important pour forcer la couleur
                if m["role"] == "user":
                    st.markdown(f'<div style="color: #29B6F6 !important; font-weight: 600;">{m["content"]}</div>', unsafe_allow_html=True)
                # AI : VERT (#00FFA3) avec !important pour forcer la couleur
                else:
                    st.markdown(f'<div style="color: #00FFA3 !important;">{m["content"]}</div>', unsafe_allow_html=True)

        # GÉRER LA NOUVELLE ENTRÉE
        if p := st.chat_input("Ask about crypto..."):
            # 1. Sauvegarder et afficher User (BLEU)
            st.session_state["msgs"].append({"role":"user", "content":p})
            with st.chat_message("user"):
                st.markdown(f'<div style="color: #29B6F6 !important; font-weight: 600;">{p}</div>', unsafe_allow_html=True)

            # 2. Générer, sauvegarder et afficher AI (VERT)
            response = sys["Chat"].respond(p)
            st.session_state["msgs"].append({"role":"assistant", "content":response})
            with st.chat_message("assistant"):
                st.markdown(f'<div style="color: #00FFA3 !important;">{response}</div>', unsafe_allow_html=True)
    # --- HEADER ---
    c_logo, c_title = st.columns([1, 6])
    with c_logo: st.markdown("## 💸")
    with c_title:
        st.title("COGNITO TERMINAL")
        st.caption("<p style='text-align:center; color:#CCCCCC; font-weight:bold;'>INSTITUTIONAL GRADE AI TRADING SYSTEM</p>", unsafe_allow_html=True)


    # --- GLOBAL SCANNER ---
    # MODIFICATION : Titre en vert forcé via HTML
    st.markdown('<h3 style="color: #00FFA3;">🌍 Global Market Overview</h3>', unsafe_allow_html=True)
    
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
        # MODIFICATION : Titre en vert forcé via HTML
        st.markdown('<h3 style="color: #00FFA3;">Real-Time Asset Analysis</h3>', unsafe_allow_html=True)
        
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
                        # MODIFICATION : Titre en vert forcé via HTML
                        st.markdown('<h4 style="color: #00FFA3;">🧠 Intelligence Consensus</h4>', unsafe_allow_html=True)
                        
                        col_gauges, col_summary = st.columns([2, 1])
                        with col_gauges:
                            g1, g2 = st.columns(2)
                            with g1:
                                st.plotly_chart(create_gauge(q['Score'], "Green"), use_container_width=True)
                                st.markdown("<p style='text-align:center; color:#CCCCCC; font-weight:bold;'>Technical Score</p>", unsafe_allow_html=True)
                            with g2:
                                dynamic_social = social_res.get('sentiment_score', 5.0)
                                st.plotly_chart(create_gauge(dynamic_social, "Blue"), use_container_width=True)
                                st.markdown("<p style='text-align:center; color:#CCCCCC; font-weight:bold;'>Sentiment Score</p>", unsafe_allow_html=True)
                        with col_summary:
                            st.info(f"**SIGNAL: {q['Signal']}**")
                            st.markdown(f"Outlook: **{social_res.get('mood', 'Neutral')}**")

                    if not hist.empty:
                        st.write("")
                        # MODIFICATION : Titre en vert forcé via HTML
                        st.markdown('<h4 style="color: #00FFA3;">📉 Price Action (30D)</h4>', unsafe_allow_html=True)
                        with st.container(border=True):
                            st.plotly_chart(create_clean_chart(hist, market['id'], market['change_24h']), use_container_width=True)
                else: st.error(f"Error: {market['error']}")

    # --- TAB 2: DUEL ---
    with tab_duel:
        # MODIFICATION : Titre en vert forcé via HTML
        st.markdown('<h3 style="color: #00FFA3;">Head-to-Head Comparison</h3>', unsafe_allow_html=True)
        
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
        # MODIFICATION : Titre en vert forcé via HTML
        st.markdown('<h3 style="color: #00FFA3;">🧬 Multi-Agent Market Simulation</h3>', unsafe_allow_html=True)
        
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
                        with c1:
                            st.markdown(f"##### 📅 Day {day} / {cfg['days']}")
                            
                            # --- CORRECTION ICI : News en blanc/gris italique ---
                            st.markdown(f"<div style='color: #CCCCCC; font-style: italic; margin-top: -10px;'>📰 NEWS: {s['headline']}</div>", unsafe_allow_html=True)
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
            # MODIFICATION : Titre en vert forcé via HTML
            st.markdown('<h3 style="color: #00FFA3;">🏁 Mission Report</h3>', unsafe_allow_html=True)
            with st.spinner("Compiling Final Analysis..."):
                final_report = engine.generate_final_report(full_logs)
                st.success(final_report)
            
            # SAUVEGARDE HISTORIQUE
            pnl_final = ((history_vals[-1]['Total Value'] - engine.initial_val) / engine.initial_val) * 100
            save_to_history(cfg['asset'], cfg['days'], engine.initial_val, history_vals[-1]['Total Value'], pnl_final, final_report)
            st.toast("Simulation saved to History!", icon="💾")

            # MODIFICATION : Titre en vert forcé via HTML
            st.markdown('<h3 style="color: #00FFA3;">📋 Transaction Log</h3>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(full_table_data), column_config={"AI Summary": st.column_config.TextColumn("AI Logic", width="large")}, use_container_width=True, hide_index=True)
            st.session_state.sim_running = False

    # --- TAB 4: HISTORY ---
    with tab_history:
        # MODIFICATION : Titre en vert forcé via HTML
        st.markdown('<h3 style="color: #00FFA3;">📜 Past Simulations Archive</h3>', unsafe_allow_html=True)
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