
import pandas as pd
import numpy as np
import plotly.express as px

# Load the Bitcoin price data, specifying the header rows and index column
df = pd.read_csv('btc_prices.csv', header=[0, 1], skiprows=[2], index_col=0)

# Simplify the column names by dropping the second level of the multi-index
df.columns = df.columns.droplevel(1)

# Convert the index to datetime objects and rename it
df.index = pd.to_datetime(df.index)
df.index.name = 'Date'

# Dollar-cost averaging parameters
investment_amount = 1000  # Dollars

# Monte Carlo Simulation Parameters
num_simulations = 1000
window_years = 5

all_simulation_results = []

# Determine possible start dates for 5-year windows
# A window must have at least `window_years` of data
min_start_date = df.index.min()
max_start_date = df.index.max() - pd.DateOffset(years=window_years)

possible_start_dates = df[(df.index >= min_start_date) & (df.index <= max_start_date)].index.unique()

if len(possible_start_dates) == 0:
    print("Not enough data to run 5-year simulations. Please ensure you have at least 5 years of data.")
else:
    for _ in range(num_simulations):
        # Randomly select a start date for the 5-year window
        start_date_idx = np.random.randint(0, len(possible_start_dates))
        window_start_date = possible_start_dates[start_date_idx]
        window_end_date = window_start_date + pd.DateOffset(years=window_years)

        # Filter data for the current 5-year window
        window_df = df[(df.index >= window_start_date) & (df.index < window_end_date)].copy()

        if window_df.empty:
            continue

        # --- Calculate BTC for each strategy within this window ---

        # Lump Sum (Jan 1st)
        btc_lump_sum_jan1 = 0
        for year in sorted(window_df.index.year.unique()):
            investment_date = window_df[(window_df.index.year == year) & (window_df.index.dayofyear >= 1)].index.min()
            if pd.notna(investment_date):
                price = window_df.loc[investment_date]['Close']
                btc_lump_sum_jan1 += investment_amount / price

        # Lump Sum (June 1st)
        btc_lump_sum_june1 = 0
        for year in sorted(window_df.index.year.unique()):
            # June 1st is day 152 in a non-leap year
            investment_date = window_df[(window_df.index.year == year) & (window_df.index.dayofyear >= 152)].index.min()
            if pd.notna(investment_date):
                price = window_df.loc[investment_date]['Close']
                btc_lump_sum_june1 += investment_amount / price

        # Daily Investment
        daily_investment_amount = investment_amount / 365
        btc_daily = (daily_investment_amount / window_df['Close']).sum()

        # Bi-Weekly Investment
        bi_weekly_investment_amount = investment_amount / 26
        btc_bi_weekly = 0
        bi_weekly_dates_in_window = pd.to_datetime(pd.date_range(start=window_start_date, end=window_end_date, freq='14D'))

        for date in bi_weekly_dates_in_window:
            investment_date = window_df[window_df.index >= date].index.min()
            if pd.notna(investment_date):
                price = window_df.loc[investment_date]['Close']
                btc_bi_weekly += bi_weekly_investment_amount / price

        all_simulation_results.append({
            'Strategy': 'Lump Sum (Jan 1st)', 'BTC': btc_lump_sum_jan1
        })
        all_simulation_results.append({
            'Strategy': 'Lump Sum (June 1st)', 'BTC': btc_lump_sum_june1
        })
        all_simulation_results.append({
            'Strategy': 'Daily DCA', 'BTC': btc_daily
        })
        all_simulation_results.append({
            'Strategy': 'Bi-Weekly DCA', 'BTC': btc_bi_weekly
        })

    results_df = pd.DataFrame(all_simulation_results)

    # Create the box plot
    fig = px.box(results_df, x="Strategy", y="BTC",
                 title="Monte Carlo Simulation of Bitcoin Investment Strategies (5-Year Windows)",
                 labels={'BTC': 'Total Bitcoin Acquired'},
                 color="Strategy")

    fig.update_layout(showlegend=False)
    fig.write_html("monte_carlo_simulation_plot.html")

    print("Monte Carlo simulation plot has been saved to monte_carlo_simulation_plot.html")
