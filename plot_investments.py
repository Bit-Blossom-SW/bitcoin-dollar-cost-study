import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the Bitcoin price data, specifying the header rows and index column
df = pd.read_csv('btc_prices.csv', header=[0, 1], skiprows=[2], index_col=0)

# Simplify the column names by dropping the second level of the multi-index
df.columns = df.columns.droplevel(1)

# Convert the index to datetime objects and rename it
df.index = pd.to_datetime(df.index)
df.index.name = 'Date'

# Dollar-cost averaging parameters
investment_amount = 1000  # Dollars

# Calculate cumulative BTC for both strategies
df['btc_lump_sum'] = 0
df['btc_daily'] = 0

btc_lump_sum_total = 0
for year in sorted(df.index.year.unique()):
    investment_date = df[df.index.year == year].index.min()
    price = df.loc[investment_date]['Close']
    btc_purchased = investment_amount / price
    btc_lump_sum_total += btc_purchased
    df.loc[investment_date, 'btc_lump_sum'] = btc_lump_sum_total

df['btc_lump_sum'] = df['btc_lump_sum'].replace(0, pd.NA).ffill()

daily_investment = investment_amount / 365
df['btc_daily'] = (daily_investment / df['Close']).cumsum()

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=df.index, y=df['Close'], name="Bitcoin Price"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df.index, y=df['btc_lump_sum'], name="Lump Sum BTC"),
    secondary_y=True,
)

fig.add_trace(
    go.Scatter(x=df.index, y=df['btc_daily'], name="Daily BTC"),
    secondary_y=True,
)

# Add figure title
fig.update_layout(
    title_text="Bitcoin Investment Strategies"
)

# Set x-axis title
fig.update_xaxes(title_text="Date")

# Set y-axes titles
fig.update_yaxes(title_text="Price (USD)", secondary_y=False)
fig.update_yaxes(title_text="Cumulative BTC", secondary_y=True)

fig.write_html("btc_investment_plot.html")

print("Plot has been saved to btc_investment_plot.html")