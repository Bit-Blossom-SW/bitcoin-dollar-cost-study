import yfinance as yf
import datetime

# Define the ticker symbol for Bitcoin
ticker = "BTC-USD"

# Define the start and end dates for the data
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=10*365)

# Download the data from Yahoo Finance
btc_data = yf.download(ticker, start=start_date, end=end_date)

# Save the data to a CSV file
btc_data.to_csv("btc_prices.csv")

print("Bitcoin price data for the last 10 years has been downloaded and saved to btc_prices.csv")
