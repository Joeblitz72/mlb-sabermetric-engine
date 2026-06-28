import streamlit as st
import pandas as pd
from totals_engine import generate_totals_leaderboard

st.set_page_config(page_title="MLB Sabermetric Portfolio", layout="wide")
st.title("📊 Quantitative Baseball Edge Engine")
st.markdown("---")

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
    st.subheader("Current MLB Market Leaderboard (Totals Edge)")
    mock_api_feed = [
        {"game": "Cubs @ Brewers", "market_total": 8.5, "home_sp_xfip": 4.65, "away_sp_xfip": 4.80, "home_team_wrc": 112, "away_team_wrc": 105, "park_factor": 102},
        {"game": "Diamondbacks @ Rays", "market_total": 7.5, "home_sp_xfip": 3.10, "away_sp_xfip": 3.35, "home_team_wrc": 92, "away_team_wrc": 98, "park_factor": 94},
        {"game": "Yankees @ Red Sox", "market_total": 9.0, "home_sp_xfip": 4.10, "away_sp_xfip": 4.15, "home_team_wrc": 122, "away_team_wrc": 118, "park_factor": 106}
    ]
    totals_df = generate_totals_leaderboard(mock_api_feed)
    st.dataframe(totals_df[['game', 'market_total', 'Projected Total', 'Target Bet', 'System Advantage (%)']], use_container_width=True, hide_index=True)