import pandas as pd
import plotly.graph_objects as go

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

# Create the plot
fig = go.Figure()

# Add the line for total BTC based on investment day
fig.add_trace(go.Scatter(x=results_df['day'], y=results_df['btc'], mode='lines', name='Total BTC'))

# Customize the layout
fig.update_layout(
    title='Total Bitcoin vs. Day of the Year for Lump Sum Investment',
    xaxis_title='Day of the Year',
    yaxis_title='Total Bitcoin Acquired',
    legend_title='Legend'
)

# Save the plot to an HTML file
fig.write_html("day_of_year_plot.html")

print("Plot has been saved to day_of_year_plot.html")