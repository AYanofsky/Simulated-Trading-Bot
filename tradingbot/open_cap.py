import pandas as pd
import yfinance as yf
# function to get the day-to-day data of a single stock
def get_daily_data(ticker):
    stock = yf.Ticker(ticker)

    # period and interval will be adjusted as needed, for now a daily basis will work fine
    hist = stock.history(period='1d', interval="1m")

    if hist.empty:
        print(f"{ticker} has no data associated with it.")
        return None

    # today's opening stock price
    opening_share_price = hist.iloc[0]['Open']

    # number of shares held by investors (as compared to treasury stock, which is the number of shares held by the company)
    investor_held_shares = stock.info.get("sharesOutstanding", None)

    if investor_held_shares is None:
        print(f"{ticker} has no data for investor-held shares.")

    market_cap_at_open = opening_share_price * investor_held_shares
    return market_cap_at_open
