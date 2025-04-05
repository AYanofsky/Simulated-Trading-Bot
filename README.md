# DO NOT USE THIS BOT AS FINANCIAL ADVICE. HOOKING IT UP TO A TRADING API IS *NOT* A GOOD IDEA. THIS BOT IS A PERSONAL PROJECT. 
## An algorithmic, short-term trading bot.
This project will be written in Python.
Due to this project's nature I will likely not be deploying it to an environment where it has access to actual funds. It is intended to be used for educational purposes (subject to change) in a controlled, simulated environment.

I used @rreichel3's list of tickers to test this thing with a large data set. You can find it [here](https://github.com/rreichel3/US-Stock-Symbols).

Currently, this bot is capable of detecting breakouts and suggesting take-profit and stop-loss orders.

## THE PLAN
Economic Theory: Enough Time In The Market Will Let The Bot Time The Market
1. Find and track stocks that are stable but undervalued and low price
- requires OHLCV data via yfinance; basic fundamentals like P/E, P/B, volume, market cap
- must be able to filter by price of stock, a stability metric (e.g. low standard deviation of moving average over a long period), and valuation filters like low P/E or a sudden high earnings yield.
- must be able to store a watchlist table in the database, as well as a candidate stock table in memory
- IMPLEMENTATION: scoring script, dataloader script
- OUTPUT: MULTIPLE TABLES IN CHOSEN MEMORY WITH COMPUTED VALUES

2. Watch these stocks. If they break out, proceed
- requires indicators: moving averages, bollinger bands/donchian channels, relative volume (to industry)
- requires breakout detection logic (price surges above recent high and a volume surge is present)
- optional: RSI/MACD confirmation
- IMPLEMENTATION: in-memory data analysis engine
- OUTPUT: TRADE SIGNALS, CONFIDENCE SCORE

3. Hold if the position is good, flip and pivot to a short position
- performance tracking: price/indicator after breakout entry, entry price vs stop-loss or drawdown
- decision logic: implement trailing stop or moving average crossover, flip to short once stock moves into previous range or completely devalues
- track active stocks (ticker, directional trend, entry price, etc) and position status (watchlist, breakout, long, short, neutral, exited)
- IMPLEMENTATION: semi-stateful(?) strategy evaluation in an API wrapper
- OUTPUT: ACTIONS (HOLD, FLIP-TO-SHORT, EXIT)

4. Follow through and exit as needed. try to avoid holding a position for long amounts of time after we reach this state
- don't hold too long, exit once matured
- exit logic: profit target reached, stop-loss triggered, or time-based exit
- trailing indicators: ATR or moving trailing stop, drop in volume or movement should produce an exit signal
- state cleanup: mark position as closed and store the results, probably via asyncio or some other collision-proof method
- IMPLEMENTATION: further strategy evaluation logic in the same wrapper. may necessitate seperate code for asynchronicity
- OUTPUT: POSITION METRICS, EQUITY CURVE


Ideas
1. SQLite database. Pivot to DuckDB if I implement some sort of ML or if speed becomes an issue
2a. Create a script to pre-load and pre-process OHLVC data (from yfinance, for now) into the DB using an API with data integrity validation
2b. Create a script to act as an in-memory analysis engine which pulls from the DB, computes rolling indicators, scores each stock, and returns a time-series based DataFrame with analysis columns. Wrap Pandas DataFrames in a custom class with related methods for calculations?
3. Create a script to wrap the algorithm and utilities in an easy-to-use API (one stock per thread, perhaps, done with multiprocessing parallelism)
4. Create a script to handle backtesting and "live" trading via the above API