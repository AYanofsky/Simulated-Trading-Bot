import yfinance as yf
import asyncio

# function to fetch historical data asynchronously
async def get_history(ticker):
    stock = yf.Ticker(ticker)
    data = await asyncio.to_thread(stock.history, period="30d")
    return ticker, data

# collect data for all tickers
async def collect_data(tickers, data_queue):
    tasks = [asyncio.create_task(get_history(ticker)) for ticker in tickers]
    for task in asyncio.as_completed(tasks):
        ticker, data = await task
        if not data.empty:
            await data_queue.put((ticker, data))

# start data collection
async def start_collecting(tickers, data_queue):
    await collect_data(tickers, data_queue)