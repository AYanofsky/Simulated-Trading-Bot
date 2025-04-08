#!/usr/bin/env python

from datetime import datetime
import pandas as pd
from tqdm import tqdm
from tradingbot.scoring import generate_trade_signal
from tradingbot.indicators import calculate_all_indicators

def backtest(tickers, data, initial_balance=10000, stop_loss_percent=0.03, take_profit_percent=0.05):
    balance = initial_balance
    position = None
    position_price = 0
    portfolio_history = []


    looper = 0
    with tqdm(total=len(data.index),desc="[SYSTEM]: Running backtest", unit=" datapoint") as pbar:
        for timestamp, ticker in data.index:
            

            ticker_data = data.xs(ticker, level='Ticker').loc[:timestamp]

            if looper <= 20:
                looper += 1
                continue

    #        print(ticker_data)

            # get the latest indicators for the stock
            indicators = calculate_all_indicators(ticker, ticker_data)

            # get the trade signal
            signal = generate_trade_signal(indicators)
            
            # if we have no position, and we get a "BUY" signal, enter a long position
            if position is None and signal == "BUY":
                position = balance / ticker_data['Close'].iloc[-1]  # ALL IN LET'S GO
                position_price = ticker_data['Close'].iloc[-1]
                balance = 0  # no cash left after buying
                print(f"[{timestamp}]: Bought {ticker} at {position_price}")
            
            # if we have a position, check for sell conditions (take-profit/stop-loss/sell signal)
            elif position is not None:
                # check for take-profit
                if ticker_data['Close'].iloc[-1] >= position_price * (1 + take_profit_percent):
                    balance = position * ticker_data['Close'].iloc[-1]
                    position = None
                    print(f"[{timestamp}]: Sold {ticker} for a profit at {ticker_data['Close'].iloc[-1]}")
                
                # check for Stop Loss
                elif ticker_data['Close'].iloc[-1] <= position_price * (1 - stop_loss_percent):
                    balance = position * ticker_data['Close'].iloc[-1]
                    position = None
                    print(f"[{timestamp}]: Sold {ticker} for a loss at {ticker_data['Close'].iloc[-1]}")
                
                # if we get a "SELL" signal, close the position
                elif signal == "SELL":
                    balance = position * ticker_data['Close'].iloc[-1]
                    position = None
                    print(f"[{timestamp}]: Sold {ticker} based on signal at {ticker_data['Close'].iloc[-1]}")

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
