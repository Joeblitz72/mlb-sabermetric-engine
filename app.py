import streamlit as st
import pandas as pd
import requests
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

    # Automated Live Schedule Pipeline Function
    @st.cache_data(ttl=3600)  # Caches data for 1 hour so it runs fast
    def load_live_schedule():
        url = "https://bcl-api-production.up.railway.app/mlb/schedule" # Live free MLB slate feed
        try:
            response = requests.get(url, timeout=10)
            games_list = response.json()
            
            live_feed = []
            for game in games_list:
                # Map real upcoming games and inject baseline defaults for metrics
                live_feed.append({
                    "game": f"{game['away_team']} @ {game['home_team']}",
                    "market_total": float(game.get('over_under', 8.5)), # Live market line or default fallback
                    "home_sp_xfip": 4.20,  # Baseline default (July 1 we connect live FanGraphs)
                    "away_sp_xfip": 4.20,  # Baseline default
                    "home_team_wrc": 100,  # Baseline default
                    "away_team_wrc": 100,  # Baseline default
                    "park_factor": 100     # Baseline default
                })
            return live_feed
        except Exception as e:
            # Fallback data if the live API is timed out
            return [{"game": "Data Fetch Timeout", "market_total": 8.5, "home_sp_xfip": 4.20, "away_sp_xfip": 4.20, "home_team_wrc": 100, "away_team_wrc": 100, "park_factor": 100}]

    with st.spinner("Fetching upcoming MLB slate from live data servers..."):
        real_api_feed = load_live_schedule()
    
    # Process through your decoupled mathematical formulas
    totals_df = generate_totals_leaderboard(real_api_feed)
    
    if not totals_df.empty:
        st.dataframe(
            totals_df[['game', 'market_total', 'Projected Total', 'Target Bet', 'System Advantage (%)']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.write("All upcoming games match the market lines perfectly. No system edges detected yet.")