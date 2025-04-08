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
2. Create a script to pre-load and pre-process OHLVC data (from yfinance, for now) into the DB using an API with data integrity validation
3. Create a script to act as an in-memory analysis engine which pulls from the DB, computes rolling indicators, scores each stock, and returns a time-series based DataFrame with analysis columns. Wrap Pandas DataFrames in a custom class with related methods for calculations?
4. Create a script to wrap the algorithm and utilities in an easy-to-use API (one stock per thread, perhaps, done with multiprocessing parallelism)
5. Create a script to handle backtesting and "live" trading via the above API


### Optimization Methods
The grand spitball.
1. Speed up data retrieval and reduce or eliminate I/O bottlenecks
- DuckDB is faster than SQLite
- Compress OHLCV into .parquet format for storage on disk
- Index data based on `ticker` and `date` to speed up lookups for individual queries
- Split data into chunks (e.g. by year) for better in-memory handling

2. Efficient data loading
- Batch fetching (via yfinance or other api) while still maintaining a polite backoff timer
- Caching libraries like `joblib` or SQLite's cache can help avoid downloads for stocks already in memory
- Periodically update only most recent data (say the last 30d or so, or keep a record of the last time the data was updated) instead of re-fetching everything

3. Efficient rolling calculations
- Minimize computation time by using numpy or cython for large datasets instead of pandas' .rolling()
- Precompute indicators during data loading to avoid recalculating them multiple times
- Use parallel processing for multiple rolling windows as they are expensive to compute

4. Indicator caching
- Cache indicator values for stocks and store them in a seperate table in DB (e.g. `indicators` with precomputed `SMA`, `RSI` values, etc)
- If the calculation is expensive (large rolling windows, custom indicators), store them and use them in the future
- Use in-memory caching (`functools.lru_cache` maybe?) to reduce repeated calculations for small amounts

5. Event detection
- Only recompute signals when needed. Event-driven design is key (e.g. only calculate something when a stock crosses a threshold)
- Optimize the signal threshold to avoid unecessary checks. Focus on stocks that meet specific criteria
- Use a scoring model to rank stocks by metrics such as breakout *strength* to reduce the number of stocks that need to be processed concurrently

6. Portfolio allocation
- Use risk-adjusted metrics (e.g. Sharpe ratio) to decide how much capital to allocate to a stock (like allocating more capital to a riskier stock)
- Use a Monte Carlo simulation to predict outcomes based on historical volatility (not really relevant, but possible)
- Calculate correlations between stocks and avoid simultaneous exposure to highly correlated sources of risk (e.g. if the iron market is crashing, don't invest in steel)

7. Position entry and exit
- Use limit orders to minimize slippage
- Optimize stop-loss and take-profit orders by backtesting different strategies (e.g. trailing stop, ATR, fixed percentage, etc)
- Consider time decay. Don't hold for too long. Test different time limits to optimize maximum holding periods
- Implement multi-threaded/processed trading to monitor multiple stocks or portfolios in parallel

8. Backtesting
- Use multi-processing to run backtests on multiple objects at once
- Group stocks into batches to be tested
- Precompute as much historical data as possible to avoid redundant calculations during backtesting

9. Algorithm and model tuning
- Use random search, not grid search, for hyperparameter optimization (for ML or rule-based thresholds)
- Automate trading parameter optimization for fixed-parameter methods (take-profit percentage, stop-loss distance, etc)

10. Scalability
- Implement a distributed system (or a system that can be distributed), perhaps via docker containers or k8s to scale horizontally and process more at once
- Cloud-based solution in future? Could open up some doors for asynchronous jobs and further distributed workloadsx