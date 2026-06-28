import pandas as pd
import numpy as np

def calculate_projected_total(row):
    """Core math engine isolating Starting Pitchers and Team wRC+"""
    # 1. Establish league baseline constant
    base_league_total = 8.5
    
    # 2. Starting Pitcher Sabermetric Deviations (xFIP vs League Mean of ~4.20)
    home_sp_deviation = row['home_sp_xfip'] - 4.20
    away_sp_deviation = row['away_sp_xfip'] - 4.20
    pitching_adjustment = (home_sp_deviation + away_sp_deviation) * 0.85
    
    # 3. Lineup Weighted Offense Deviations (wRC+ vs League Mean of 100)
    home_off_deviation = (row['home_team_wrc'] - 100) / 100
    away_off_deviation = (row['away_team_wrc'] - 100) / 100
    offense_adjustment = (home_off_deviation + away_off_deviation) * 1.2
    
    # 4. Specific Stadium Infrastructure Modifier
    park_factor_adjustment = (row['park_factor'] - 100) / 100 * 0.5
    
    # 5. Compile Final Decoupled Projection Matrix
    projected_total = base_league_total + pitching_adjustment + offense_adjustment + park_factor_adjustment
    return round(projected_total, 2)

def generate_totals_leaderboard(api_games_list):
    """Processes the live API feed through the matrix and forces all games to display"""
    if not api_games_list:
        return pd.DataFrame()
        
    df = pd.DataFrame(api_games_list)
    
    # Run the math engine
    df['Projected Total'] = df.apply(calculate_projected_total, axis=1)
    df['Discrepancy'] = df['Projected Total'] - df['market_total']
    
    # CRITICAL FIX: Changed the threshold to 0.00 so EVERY game displays on your web screen
    df['Target Bet'] = np.where(df['Discrepancy'] > 0.00, 'OVER', 
                       np.where(df['Discrepancy'] < 0.00, 'UNDER', 'PASS'))
    
    # Calculate edge percentage
    df['System Advantage (%)'] = round((df['Discrepancy'].abs() / df['market_total']) * 100, 2)
    
    # Sort by the highest statistical advantage
    df = df.sort_values(by='System Advantage (%)', ascending=False)
    return df