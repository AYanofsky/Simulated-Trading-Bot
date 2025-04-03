from tradingbot.open_cap import get_daily_data

ticker = "UEC"
data = get_daily_data(ticker)
print(f"Market cap at open for {ticker} was {data}")