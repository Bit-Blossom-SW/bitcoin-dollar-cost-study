import pandas as pd

# Load the Bitcoin price data, specifying the header rows and index column
df = pd.read_csv('btc_prices.csv', header=[0, 1], skiprows=[2], index_col=0)

# Simplify the column names by dropping the second level of the multi-index
df.columns = df.columns.droplevel(1)

# Convert the index to datetime objects and rename it
df.index = pd.to_datetime(df.index)
df.index.name = 'Date'

# Dollar-cost averaging parameters
investment_amount = 1000  # Dollars
years = sorted(df.index.year.unique())

# --- Day of Year Analysis ---
day_of_year_results = []

# Loop through each possible day of the year (1-365)
for day in range(1, 366):
    total_btc = 0
    # Loop through each year in the dataset
    for year in years:
        # Find the first available trading day on or after the target day of the year
        investment_date = df[(df.index.year == year) & (df.index.dayofyear >= day)].index.min()

        # If a valid investment date is found for that year
        if pd.notna(investment_date):
            price = df.loc[investment_date]['Close']
            total_btc += investment_amount / price
    
    if total_btc > 0:
        day_of_year_results.append({'day': day, 'btc': total_btc})

# Create a DataFrame from the results
results_df = pd.DataFrame(day_of_year_results)

# Find the best and worst days
best_day = results_df.loc[results_df['btc'].idxmax()]
worst_day = results_df.loc[results_df['btc'].idxmin()]

print("--- Lump Sum Day-of-Year Comparison (1-365) ---")
print(f"Best day of the year to invest: Day {int(best_day['day'])}")
print(f"  -> Total Bitcoin acquired: {best_day['btc']:.8f}")
print(f"Worst day of the year to invest: Day {int(worst_day['day'])}")
print(f"  -> Total Bitcoin acquired: {worst_day['btc']:.8f}")

# --- Strategy Comparison ---
# Scenario 1a: Buying $1000 worth of Bitcoin on Jan 1st each year
btc_lump_sum_jan1 = results_df[results_df['day'] == 1]['btc'].iloc[0]

# Scenario 1b: Buying $1000 worth of Bitcoin on June 1st each year
# June 1st is the 152nd day of a non-leap year.
btc_lump_sum_june1 = results_df[results_df['day'] == 152]['btc'].iloc[0]

# Scenario 2: Buying $1000/365 worth of Bitcoin every day
daily_investment = investment_amount / 365
btc_daily = (daily_investment / df['Close']).sum()

# Scenario 3: Buying $1000/26 worth of Bitcoin every 2 weeks
bi_weekly_investment = investment_amount / 26
btc_bi_weekly = 0
# Create a date range for bi-weekly investments
bi_weekly_dates = pd.to_datetime(pd.date_range(start=df.index.min(), end=df.index.max(), freq='14D'))

for date in bi_weekly_dates:
    # Find the first available trading day on or after the investment date
    investment_date = df[df.index >= date].index.min()
    if pd.notna(investment_date):
        price = df.loc[investment_date]['Close']
        btc_bi_weekly += bi_weekly_investment / price

print("\n--- Investment Strategy Comparison ---")
print(f"Total Bitcoin with lump sum investment (Jan 1st): {btc_lump_sum_jan1:.8f}")
print(f"Total Bitcoin with lump sum investment (June 1st): {btc_lump_sum_june1:.8f}")
print(f"Total Bitcoin with daily investment: {btc_daily:.8f}")
print(f"Total Bitcoin with bi-weekly investment: {btc_bi_weekly:.8f}")

# Find the best strategy
strategies = {
    "Lump Sum (Jan 1st)": btc_lump_sum_jan1,
    "Lump Sum (June 1st)": btc_lump_sum_june1,
    "Daily": btc_daily,
    "Bi-Weekly": btc_bi_weekly
}

best_strategy = max(strategies, key=strategies.get)
print(f"\nThe best performing strategy is: {best_strategy}")