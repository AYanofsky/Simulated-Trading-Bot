#!/usr/bin/env python
import yfinance as yf

open_positions = {}

# async function to decide what strategy to use
async def process_data(data_queue):
    while True:
        # get data from the queue
        ticker, data = await data_queue.get()
#        print(f"Processing data for {ticker}...")
        
        # run the breakout detection and strategy execution
        breakout_up, breakout_down, processed_data = detect_breakouts(data)
        if breakout_up:
            execute_strategy(ticker, processed_data)
        elif breakout_down:
            execute_strategy(ticker, processed_data)

        # mark task as complete
        data_queue.task_done()


# function to detect breakouts based on historical data
def detect_breakouts(data):

    # calculate moving average and standard deviation to handle volatility
    data.loc[:,'Moving_Avg'] = data['Close'].rolling(window=20).mean()
    data.loc[:,'Std_Dev'] = data['Close'].rolling(window=20).std()

    # define breakout levels
    breakout_threshold = 1.05
    breakdown_threshold = 0.98

    # current price and moving average
    current_price = data['Close'].iloc[-1]
    moving_avg = data['Moving_Avg'].iloc[-1]

    # detect breakouts by checking to see if the current price is above/below a percentage of the breakout/breakdown threshold
    breakout_up = current_price > moving_avg * breakout_threshold
    breakout_down = current_price < moving_avg * breakdown_threshold

    return breakout_up, breakout_down, data


# function to determine stop-loss and take-profit logic
def stop_loss_take_profit(entry_price,breakout_up=True): # breakout set to true for testing purposes

    # define stop-loss and take-profit margins
    stop_loss_percent = 0.05
    take_profit_percent = 0.10

    if breakout_up:
        stop_loss = entry_price * (1 - stop_loss_percent)
        take_profit = entry_price * (1 + take_profit_percent)
    else:
        stop_loss = entry_price * (1 + stop_loss_percent)
        take_profit = entry_price * (1 - take_profit_percent)

    return stop_loss, take_profit


# function to execute the trading strategy
def execute_strategy(ticker, data):
    # strategy will be triggered if a breakout is occurring
    current_price = data['Close'].iloc[-1]
    breakout_up, breakout_down, processed_data = detect_breakouts(data)

    if ticker in open_positions.keys():
        for position in open_positions[ticker]:
            # check if stop-loss or take-profit matches current price
            stop_loss, take_profit = position['stop_loss'], position['take_profit']
            if (position['position'] == "LONG" and (current_price <= stop_loss or current_price >= take_profit)) or \
                (position['position'] == "SHORT" and (current_price >= stop_loss or current_price <= take_profit)):
                # exit position if stop-loss or take-profit matches current price
                print(f"[{ticker:^4}] Exiting position at ${current_price:,.6f} due to stop-loss/take-profit hit.")
                position["exit"] = current_price
                # generate exit signal
                trade_signal = {
                    "ticker": ticker,
                    "position": "EXIT",
                    "entry": position["entry"],
                    "exit": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "timestamp": data.index[-1]
                }
                # remove position from open positions
                open_positions[ticker].remove(position)
                return trade_signal

    # if we're breaking up, buy long, if we're breakking down, sell short. simple.
    if breakout_up:
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=True)
        print(f"[{ticker:^4}] 📈 Breakout detected: BUY LONG at ${current_price:,.6f}")
        print(f"[{ticker:^4}] Stop-loss: ${stop_loss:,.6f}, Take-profit: ${take_profit:,.6f}\n")

        position = {
            "ticker": ticker,
            "position": "LONG",
            "entry": current_price,
            "exit": None,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "timestamp": data.index[-1]
        }

        # add ticker to open positions if it isn't in there, then add the position we just opened to it
        if ticker not in open_positions:
            open_positions[ticker] = []
        open_positions[ticker].append(position)

    elif breakout_down:
        stop_loss, take_profit = stop_loss_take_profit(current_price, breakout_up=False)
        print(f"[{ticker:^4}] 📉 Breakdown detected: SELL SHORT at ${current_price:,.6f}")
        print(f"[{ticker:^4}] Stop-loss: ${stop_loss:,.6f}, Take-profit: ${take_profit:,.6f}\n")

        position = {
            "ticker": ticker,
            "position": "SHORT",
            "entry": current_price,
            "exit": None,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "timestamp": data.index[-1]
        }

        # add ticker to open positions if it isn't in there, then add the position we just opened to it
        if ticker not in open_positions:
            open_positions[ticker] = []
        open_positions[ticker].append(position)

    else:
        print(f"No breakout detected for {ticker}.\n")


# function to execute strategy for multiple tickets using data generated in the data-collection step
def execute_batch_strategy(tickers, data_dict):
    trade_signals = []

    for ticker in tickers:
        if ticker in data_dict:
            #print(f"Executing trade strategy for {ticker}.")
            trade_signals.append(execute_strategy(ticker, data_dict[ticker]))
        else:
            pass
            #print(f"No data available for {ticker}."))