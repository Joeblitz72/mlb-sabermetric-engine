import streamlit as st
import pandas as pd
import urllib.request
import json
from totals_engine import generate_totals_leaderboard

st.set_page_config(page_title="MLB Sabermetric Portfolio", layout="wide")
st.title("📊 Quantitative Baseball Edge Engine")
st.markdown("---")

# Portfolio KPI Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric(label="June Control Group Performance", value="20–32", delta="-12 Wins")
col2.metric(label="Liquid Capital Bankroll", value="$959.70", delta="-$40.30")
col3.metric(label="Active Capital at Risk", value="$50.00", delta="5 Units Pending")

st.markdown("### Daily Terminal Outputs")
tab_ml, tab_totals = st.tabs(["🎯 Moneyline Value Board", "📈 Standalone Over/Under Model"])

with tab_ml:
    st.subheader("Current MLB Market Leaderboard (ML Value)")
    st.info("Tracking active mispriced underdogs and short-priced target favorites.")
    
with tab_totals:
    st.subheader("Live MLB Upcoming Totals")

    @st.cache_data(ttl=600)  # Caches for 10 minutes
    def scrape_free_production_lines():
        # Open source public unauthenticated scoreboard feed
        url = "https://site.api.espn.com/sbin/fastcast/v1/sports/baseball/leagues/mlb/events"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                raw_data = json.loads(response.read().decode())
            
            live_feed = []
            events = raw_data.get('events', [])
            
            for event in events:
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                    
                comp = competitions[0]
                competitors = comp.get('competitors', [])
                if len(competitors) < 2:
                    continue
                
                # Identify Home vs Away squads
                if competitors[0].get('homeAway') == 'home':
                    home_team = competitors[0]['team']['displayName']
                    away_team = competitors[1]['team']['displayName']
                else:
                    home_team = competitors[1]['team']['displayName']
                    away_team = competitors[0]['team']['displayName']
                
                live_feed.append({
                    "game": f"{away_team} @ {home_team}",
                    "market_total": 8.5,   # Default line baseline for slate mapping
                    "home_sp_xfip": 4.20,
                    "away_sp_xfip": 4.20,
                    "home_team_wrc": 100,
                    "away_team_wrc": 100,
                    "park_factor": 100
                })
            return live_feed
        except Exception as e:
            return [{"game": f"Pipeline Syncing... ({str(e)})", "market_total": 8.5, "home_sp_xfip": 4.20, "away_sp_xfip": 4.20, "home_team_wrc": 100, "away_team_wrc": 100, "park_factor": 100}]

    with st.spinner("Executing direct scoreboard pipeline..."):
        production_feed = scrape_free_production_lines()
    
    totals_df = generate_totals_leaderboard(production_feed)
    
    if not totals_df.empty:
        st.dataframe(
            totals_df[['game', 'market_total', 'Projected Total', 'Target Bet', 'System Advantage (%)']], 
            use_container_width=True, 
            hide_index=True
        )
        )