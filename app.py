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

    @st.cache_data(ttl=1800)  # Caches for 30 minutes to stay nimble
    def scrape_production_lines():
        # High-stability backup endpoint parsing the direct market board
        url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey=7ea9e6f3643d9b4b0e5bc5d11b33b708&regions=us&markets=totals&oddsFormat=decimal"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                raw_data = json.loads(response.read().decode())
            
            live_feed = []
            for match in raw_data:
                # Extract clean team definitions
                home_team = match.get('home_team')
                away_team = match.get('away_team')
                
                # Dig down into the bookmaker matrix to locate the Over/Under line
                market_total = 8.5 # High-safety baseline fallback
                bookmakers = match.get('bookmakers', [])
                if bookmakers:
                    markets = bookmakers[0].get('markets', [])
                    if markets:
                        outcomes = markets[0].get('outcomes', [])
                        if outcomes:
                            market_total = float(outcomes[0].get('point', 8.5))
                
                live_feed.append({
                    "game": f"{away_team} @ {home_team}",
                    "market_total": market_total,
                    "home_sp_xfip": 4.20,  # Baseline Constant
                    "away_sp_xfip": 4.20,  # Baseline Constant
                    "home_team_wrc": 100,  # Baseline Constant
                    "away_team_wrc": 100,  # Baseline Constant
                    "park_factor": 100     # Baseline Constant
                })
            return live_feed
        except Exception as e:
            return [{"game": f"Pipeline Initializing... ({str(e)})", "market_total": 8.5, "home_sp_xfip": 4.20, "away_sp_xfip": 4.20, "home_team_wrc": 100, "away_team_wrc": 100, "park_factor": 100}]

    with st.spinner("Executing live sportsbook scraping engine..."):
        production_feed = scrape_production_lines()
    
    # Send our fresh scraped live lines into the mathematical calculator
    totals_df = generate_totals_leaderboard(production_feed)
    
    if not totals_df.empty:
        st.dataframe(
            totals_df[['game', 'market_total', 'Projected Total', 'Target Bet', 'System Advantage (%)']], 
            use_container_width=True, 
            hide_index=True
        )