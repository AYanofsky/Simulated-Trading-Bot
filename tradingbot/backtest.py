#!/usr/bin/env python

from datetime import datetime
import pandas as pd
from tqdm import tqdm
from tradingbot.scoring import generate_trade_signal
from tradingbot.indicators import calculate_latest_indicators

def backtest(tickers, data, initial_balance=10000, stop_loss_percent=0.03, take_profit_percent=0.05):
    balance = initial_balance
    position = None
    position_price = 0
    portfolio_history = []

    # Precompute indicators for all data once, reducing redundancy in calculations
    indicators_cache = {}

    looper = 0
    with tqdm(total=len(data.index), desc="[SYSTEM]: Running backtest", unit=" datapoint") as pbar:
        for timestamp, ticker in data.index:
            # Ensure we have enough datapoints to do calculations
            if looper <= 50:
                looper += 1
                continue

            # Check if the indicators for this ticker and timestamp are already cached
            if (ticker, timestamp) not in indicators_cache:
                ticker_data = data.xs(ticker, level='Ticker').loc[:timestamp].tail(50)
                indicators_cache[(ticker, timestamp)] = calculate_latest_indicators(ticker_data)

            # Retrieve the latest indicators for this ticker and timestamp
            indicators = indicators_cache[(ticker, timestamp)]

            # get the trade signal
            signal = generate_trade_signal(indicators)
            
            # if we have no position, and we get a "BUY" signal, enter a long position
            if position is None and signal == "BUY":
                position = balance / ticker_data['Close'].iloc[-1]  # ALL IN LET'S GO
                position_price = ticker_data['Close'].iloc[-1]
                balance = 0  # no cash left after buying
            
            # if we have a position, check for sell conditions (take-profit/stop-loss/sell signal)
            elif position is not None:
                # check for take-profit
                if ticker_data['Close'].iloc[-1] >= position_price + (take_profit_percent * indicators['atr']):
                    balance = position * ticker_data['Close'].iloc[-1]
                    position = None
                
                # check for Stop Loss
                elif ticker_data['Close'].iloc[-1] <= position_price - (stop_loss_percent * indicators['atr']):
                    balance = position * ticker_data['Close'].iloc[-1]
                    position = None
                
                # if we get a "SELL" signal, close the position
                elif signal == "SELL":
                    balance = position * ticker_data['Close'].iloc[-1]
                    position = None

            # track portfolio value
            portfolio_history.append({
                'timestamp': timestamp,
                'balance': balance,
                'position': position,
                'portfolio_value': balance if position is None else position * ticker_data['Close'].iloc[-1]
            })

            pbar.update(1)

    # at the end of the backtest, liquidate any open positions
    if position is not None:
        balance = position * ticker_data['Close'].iloc[-1]
        print(f"[SYSTEM]: End of backtest: Sold remaining position at {ticker_data['Close'].iloc[-1]}")
    
    # generate final portfolio report
    portfolio_history_df = pd.DataFrame(portfolio_history)
    portfolio_history_df.set_index('timestamp', inplace=True)
    portfolio_history_df['portfolio_value'].plot(title="Portfolio Value Over Time")

    final_value = portfolio_history_df['portfolio_value'].iloc[-1]
    print(f"Final Portfolio Value: {final_value}")
    print(f"Total Return: {(final_value - initial_balance) / initial_balance * 100:.2f}%")
