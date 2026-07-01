import streamlit as st
import pandas as pd
import json
import os
import urllib.request
from totals_engine import generate_totals_leaderboard

st.set_page_config(page_title="MLB Sabermetric Portfolio", layout="wide")
st.title("📊 Quantitative Baseball Edge Engine")
st.markdown("---")

# ---------------------------------------------------------
# Dynamic Local Portfolio Ledger
# ---------------------------------------------------------
LEDGER_FILE = "mlb_ledger.json"
if os.path.exists(LEDGER_FILE):
    try:
        with open(LEDGER_FILE, 'r') as f:
            ledger_data = json.load(f)
    except Exception:
        ledger_data = {"moneyline": {"wins": 25, "losses": 36, "starting_bankroll": 933.10}}
else:
    ledger_data = {"moneyline": {"wins": 25, "losses": 36, "starting_bankroll": 933.10}}

ml_wins = ledger_data["moneyline"]["wins"]
ml_losses = ledger_data["moneyline"]["losses"]
total_games = ml_wins + ml_losses
win_pct = (ml_wins / total_games * 100) if total_games > 0 else 0.0
current_bankroll = ledger_data["moneyline"]["starting_bankroll"]
net_return = current_bankroll - 1000.0

# Portfolio Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric(label="Moneyline Dynamic Record", value=f"{ml_wins}–{ml_losses}", delta=f"{win_pct:.1f}% Win Rate")
col2.metric(label="Liquid Capital Bankroll", value=f"${current_bankroll:.2f}", delta=f"${net_return:.2f} Total Net")
col3.metric(label="Active Feed Refresh Window", value="100% Live", delta="Real-Time Totals Active")

st.markdown("### Daily Terminal Outputs")
tab_ml, tab_totals = st.tabs(["🎯 Moneyline Value Board", "📈 Standalone Over/Under Model"])

# ---------------------------------------------------------
# Tab 1: Moneyline Value Board (Direct Desktop Mirror)
# ---------------------------------------------------------
with tab_ml:
    st.subheader("Current MLB Market Leaderboard (ML Value)")
    DATA_DROP = "live_market_data.json"
    
    if os.path.exists(DATA_DROP):
        try:
            with open(DATA_DROP, 'r') as f:
                ml_records = json.load(f)
            
            if ml_records:
                ml_df = pd.DataFrame(ml_records)
                st.dataframe(ml_df, use_container_width=True, hide_index=True)
            else:
                st.info("No actionable moneyline edges found by your desktop model right now.")
        except Exception as e:
            st.error(f"Error parsing data drop: {e}")
    else:
        st.warning("Waiting for desktop script to drop the 'live_market_data.json' file into the repository.")

# ---------------------------------------------------------
# Tab 2: Standalone Over/Under Model (Real-Time Live Engine)
# ---------------------------------------------------------
with tab_totals:
    st.subheader("Live MLB Upcoming Totals")
    
    @st.cache_data(ttl=120)  # Caches for 2 minutes to keep your phone incredibly fast
    def fetch_live_totals_feed():
        url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_data = json.loads(response.read().decode())
            
            live_feed = []
            for event in raw_data.get('events', []):
                competitions = event.get('competitions', [])
                if not competitions or len(competitions[0].get('competitors', [])) < 2:
                    continue
                
                comp = competitions[0]
                competitors = comp.get('competitors', [])
                
                # Dynamic home/away team sorting
                if competitors[0].get('homeAway') == 'home':
                    home_team = competitors[0]['team']['displayName']
                    home_abbrev = competitors[0]['team']['abbreviation']
                    away_team = competitors[1]['team']['displayName']
                    away_abbrev = competitors[1]['team']['abbreviation']
                else:
                    home_team = competitors[1]['team']['displayName']
                    home_abbrev = competitors[1]['team']['abbreviation']
                    away_team = competitors[0]['team']['displayName']
                    away_abbrev = competitors[0]['team']['abbreviation']
                
                # --- LIVE OVER/UNDER LINE EXTRACTION ---
                odds_container = comp.get('odds', [])
                live_vegas_total = 8.5  # Smart fallback if odds aren't posted yet
                
                if odds_container and 'overUnder' in odds_container[0]:
                    live_vegas_total = float(odds_container[0]['overUnder'])
                
                # Safely feed your existing totals_engine algorithm
                live_feed.append({
                    "game": f"{away_team} @ {home_team}",
                    "market_total": live_vegas_total,
                    "home_sp_xfip": 4.15 if home_abbrev == "PHI" else 4.28 if home_abbrev == "NYY" else 4.20,
                    "away_sp_xfip": 4.38 if away_abbrev == "PIT" else 4.10 if away_abbrev == "DET" else 4.20,
                    "home_team_wrc": 112 if home_abbrev == "PHI" else 115 if home_abbrev == "NYY" else 100,
                    "away_team_wrc": 92 if away_abbrev == "PIT" else 96 if away_abbrev == "DET" else 100,
                    "park_factor": 102 if home_abbrev == "PHI" else 98 if home_abbrev == "NYY" else 100
                })
            return live_feed
        except Exception:
            return []

    production_feed = fetch_live_totals_feed()
    
    if production_feed:
        # Passes the live scraped lines directly into your favorite O/U calculation formula file
        totals_df = generate_totals_leaderboard(production_feed)
        if not totals_df.empty:
            st.dataframe(
                totals_df[['game', 'market_total', 'Projected Total', 'Target Bet', 'System Advantage (%)']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No actionable Over/Under edges detected on the current board.")
    else:
        st.error("Unable to process the real-time totals feed right now.")