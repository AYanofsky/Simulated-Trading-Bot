April 3, 2025
I want to make a bot which is capable of analyzing a non-mainstream stock which gained a significant amount of market cap, then (somewhat nebulously) figure out if it will fail or not. If it expects it to fail, I want the bot to enter a short position and sell once a certain percentage of profit has been reached. Otherwise, the bot should leave the stock alone. I will probably program it to see if something is falling first and short if it is falling first.

So far I've realized that the speed of the API's HTTP/S connections is a seriously limiting factor when dealing with large quantities of tickers. I'm going to try to write a web scraper to grab data for me.


April 4, 2025
I was up very late last night trying to get this thing to spit numbers out at me.
I fixed a bunch of bugs, and right now the bot is capable of detecting a breakout based on moving average and a static percentage. It can also detect breakdowns.
Today I implemented a trailing stop-loss.

I branched the repo to refactor the algorithm to focus primarily on backtesting and improving it.

I branched again. Time for theory.


Economic Theory: Enough Time In The Market Will Let The Bot Time The Market
1. Find and track stocks that are stable but undervalued and low price
2. Watch these stocks. If they break out, proceed
3. Hold if the position is good, flip and pivot to a short position
4. Follow through and exit as needed. try to avoid holding a position for long amounts of time after we reach this state

Ideas
1. SQLite database. Pivot to DuckDB if I implement some sort of ML or if speed becomes an issue
2a. Create a script to pre-load and pre-process OHLVC data (from yfinance, for now) into the DB using an API with data integrity validation
2b. Create a script to act as an in-memory analysis engine which pulls from the DB, computes rolling indicators, scores each stock, and returns a time-series based DataFrame with analysis columns. Wrap Pandas DataFrames in a custom class with related methods for calculations?
3. Create a script to wrap the algorithm and utilities in an easy-to-use API (one stock per thread, perhaps, done with multiprocessing parallelism)
4. Create a script to handle backtesting and "live" trading via the above API