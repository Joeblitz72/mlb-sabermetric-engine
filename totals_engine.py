import pandas as pd
import numpy as np

def calculate_projected_total(row):
    base_league_total = 8.5
    home_sp_deviation = row['home_sp_xfip'] - 4.20
    away_sp_deviation = row['away_sp_xfip'] - 4.20
    pitching_adjustment = (home_sp_deviation + away_sp_deviation) * 0.85
    
    home_off_deviation = (row['home_team_wrc'] - 100) / 100
    away_off_deviation = (row['away_team_wrc'] - 100) / 100
    offense_adjustment = (home_off_deviation + away_off_deviation) * 1.2
    
    park_factor_adjustment = (row['park_factor'] - 100) / 100 * 0.5
    return round(base_league_total + pitching_adjustment + offense_adjustment + park_factor_adjustment, 2)

def generate_totals_leaderboard(raw_scraped_data):
    df = pd.DataFrame(raw_scraped_data)
    df['Projected Total'] = df.apply(calculate_projected_total, axis=1)
    df['Discrepancy'] = df['Projected Total'] - df['market_total']
    df['Target Bet'] = np.where(df['Discrepancy'] > 0.4, 'OVER', 
                       np.where(df['Discrepancy'] < -0.4, 'UNDER', 'PASS'))
    df['System Advantage (%)'] = (df['Discrepancy'].abs() / df['market_total'] * 100).round(2)
    return df[df['Target Bet'] != 'PASS'].sort_values(by='System Advantage (%)', ascending=False)