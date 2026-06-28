import pandas as pd
import numpy as np

def calculate_projected_total(row):
    """
    Core math engine isolating Starting Pitchers and Team wRC+ 
    Projected Total = Base Total + Pitcher Adjustments + Offense Adjustments
    """
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
    
    # Raw Mathematical Projection
    projected = base_league_total + pitching_adjustment + offense_adjustment + park_factor_adjustment
    return round(projected, 2)

def generate_totals_leaderboard(raw_scraped_data):
    """Processes raw daily market feeds and flags the premium gaps."""
    df = pd.DataFrame(raw_scraped_data)
    
    # Run the core matrix loop
    df['Projected Total'] = df.apply(calculate_projected_total, axis=1)
    
    # Quantify the absolute discrepancy edge vs DraftKings
    df['Discrepancy'] = df['Projected Total'] - df['market_total']
    
    # Generate rules-based clear system recommendations
    df['Target Bet'] = np.where(df['Discrepancy'] > 0.4, 'OVER', 
                       np.where(df['Discrepancy'] < -0.4, 'UNDER', 'PASS'))
    
    # Absolute edge value calculation
    df['System Advantage (%)'] = (df['Discrepancy'].abs() / df['market_total'] * 100).round(2)
    
    # Return sorted by maximum mathematical advantage
    return df[df['Target Bet'] != 'PASS'].sort_values(by='System Advantage (%)', ascending=False)
