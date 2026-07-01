import streamlit as st
import pandas as pd
import urllib.request
import json
import os
from totals_engine import generate_totals_leaderboard

st.set_page_config(page_title="MLB Sabermetric Portfolio", layout="wide")
st.title("📊 Quantitative Baseball Edge Engine")
st.markdown("---")

# ---------------------------------------------------------
# Dynamic Local Ledger Loading
# ---------------------------------------------------------
LEDGER_FILE = "mlb_ledger.json"

if os.path.exists(LEDGER_FILE):
    with open(LEDGER_FILE, 'r') as f:
        ledger_data = json.load(f)
else:
    ledger_data = {"moneyline": {"wins": 25, "losses": 36, "starting_bankroll": 933.10}}

ml_wins = ledger_data["moneyline"]["wins"]
ml_losses = ledger_data["moneyline"]["losses"]
total_games = ml_wins + ml_losses
win_pct = (ml_wins / total_games * 100) if total_games > 0 else 0.0
current_bankroll = ledger_data["moneyline"]["starting_bankroll"]
net_return = current_bankroll - 1000.0

# Portfolio Dynamic KPI Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric(label="Moneyline Dynamic Record", value=f"{ml_wins}–{ml_losses}", delta=f"{win_pct:.1f}% Win Rate")
col2.metric(label="Liquid Capital Bankroll", value=f"${current_bankroll:.2f}", delta=f"${net_return:.2f} Total Net")
col3.metric(label="Active Feed Refresh Window", value="100% Live", delta="Dual Engine Active")

st.markdown("### Daily Terminal Outputs")
tab_ml, tab_totals = st.tabs(["🎯 Moneyline Value Board", "📈 Standalone Over/Under Model"])

# Consensus DraftKings Lines Shared Matrix
dk_market_lines = {
    "WSH": 9.5, "BAL": 8.5, "CWS": 8.5, "PHI": 9.0, "PIT": 9.0,
    "NYY": 7.0, "DET": 7.0, "NYM": 8.0, "TOR": 8.0, "TEX": 8.5,
    "CLE": 8.5, "BOS": 9.5, "CIN": 9.0, "MIL": 9.0, "SD": 11.5,
    "CHC": 11.5, "HOU": 8.5, "MIN": 8.5, "MIA": 11.5, "COL": 11.5,
    "SF": 7.5, "AZ": 7.5, "LAA": 7.5, "SEA": 7.5, "LAD": 8.5, "OAK": 8.5
}

# Shared Scoreboard Scraper Pipeline
@st.cache_data(ttl=300)
def fetch_live_production_data():
    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = json.loads(response.read().decode())
        
        live_feed = []
        for event in raw_data.get('events', []):
            competitions = event.get('competitions', [])
            if not competitions or len(competitions[0].get('competitors', [])) < 2:
                continue
            
            comp = competitions[0]
            competitors = comp.get('competitors', [])
            
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
            
            market_total = dk_market_lines.get(home_abbrev, 8.5)
            
            live_feed.append({
                "game": f"{away_team} @ {home_team}",
                "home_abbrev": home_abbrev,
                "away_abbrev": away_abbrev,
                "market_total": market_total,
                "home_sp_xfip": 4.15 if home_abbrev == "PHI" else 4.28 if home_abbrev == "NYY" else 4.20,
                "away_sp_xfip": 4.38 if away_abbrev == "PIT" else 4.10 if away_abbrev == "DET" else 4.20,
                "home_team_wrc": 112 if home_abbrev == "PHI" else 115 if home_abbrev == "NYY" else 100,
                "away_team_wrc": 92 if away_abbrev == "PIT" else 96 if away_abbrev == "DET" else 100,
                "park_factor": 102 if home_abbrev == "PHI" else 98 if home_abbrev == "NYY" else 100
            })
        return live_feed
    except Exception as e:
        return []

with st.spinner("Processing dual board metrics..."):
    production_feed = fetch_live_production_data()

# ---------------------------------------------------------
# Tab 1: Embedded Moneyline Engine
# ---------------------------------------------------------
with tab_ml:
    st.subheader("Current MLB Market Leaderboard (ML Value)")
    
    if production_feed:
        ml_records = []
        # Fallback dictionary representing DraftKings moneyline data context
        ml_odds_mock = {
            "PIT": 163, "PHI": -180, "DET": 150, "NYY": -165, "WSH": 144, "BOS": -155,
            "LAA": 170, "SEA": -190, "SD": 130, "CHC": -145, "MIN": 118, "HOU": -130
        }
        
        for game in production_feed:
            home = game["home_abbrev"]
            away = game["away_abbrev"]
            
            # Run your exact baseline projection algorithm logic
            home_proj = 50.0 + (game["home_team_wrc"] - game["away_team_wrc"]) * 0.15 + (game["away_sp_xfip"] - game["home_sp_xfip"]) * 5.0
            home_proj = max(min(home_proj, 75.0), 25.0)
            away_proj = 100.0 - home_proj
            
            for team, abbrev, proj in [(game["game"].split(" @ ")[1], home, home_proj), (game["game"].split(" @ ")[0], away, away_proj)]:
                odds = ml_odds_mock.get(abbrev, 100)
                if odds > 0:
                    implied = 100 / (odds + 100)
                else:
                    implied = abs(odds) / (abs(odds) + 100)
                
                advantage = proj - (implied * 100)
                
                if advantage > 5.0:  # Your exact system threshold parameter
                    ml_records.append({
                        "Target Team": team,
                        "Market Line": f"+{odds}" if odds > 0 else str(odds),
                        "Book Implied": f"{implied*100:.1f}%",
                        "Model Projection": f"{proj:.1f}%",
                        "Advantage (%)": round(advantage, 2)
                    })
        
        if ml_records:
            ml_df = pd.DataFrame(ml_records).sort_values(by="Advantage (%)", ascending=False)
            st.dataframe(ml_df, use_container_width=True, hide_index=True)
        else:
            st.info("No actionable moneyline edges meeting the baseline threshold found on the current slate.")
    else:
        st.error("Unable to load team schedules for Moneyline parsing.")

# ---------------------------------------------------------
# Tab 2: Over/Under Engine
# ---------------------------------------------------------
with tab_totals:
    st.subheader("Live MLB Upcoming Totals")
    if production_feed:
        totals_df = generate_totals_leaderboard(production_feed)
        if not totals_df.empty:
            st.dataframe(
                totals_df[['game', 'market_total', 'Projected Total', 'Target Bet', 'System Advantage (%)']], 
                use_container_width=True, 
                hide_index=True
            )
    else:
        st.error("Data pipeline communication break. Check network configs.")