#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from tradingbot.scoring import generate_trade_signal
from tradingbot.indicators import calculate_latest_indicators

def process_ticker_data(timestamp, ticker, data, indicators_cache, take_profit_percent, stop_loss_percent, initial_balance, position, position_price, pbar):
    ticker_data = data.xs(ticker, level='Ticker').loc[:timestamp].tail(50)

    # Check if the indicators for this ticker and timestamp are already cached
    if (ticker, timestamp) not in indicators_cache:
        indicators_cache[(ticker, timestamp)] = calculate_latest_indicators(ticker_data)

    indicators = indicators_cache[(ticker, timestamp)]

    # Generate trade signal
    signal = generate_trade_signal(indicators)

    # Process trading logic for each tick
    balance = initial_balance
    position_data = position
    position_price_data = position_price
    portfolio_history = []

    if position_data is None and signal == "BUY":
        position_price_data = ticker_data['Close'].iloc[-1]
        position_data = balance / position_price_data  # ALL IN LET'S GO
        balance = 0  # no cash left after buying
#        pbar.set_description(f"[SYSTEM]: BOUT {ticker:<4}".ljust(40))

    elif position_data is not None:
        # Check take-profit/stop-loss/sell conditions
        if ticker_data['Close'].iloc[-1] >= position_price_data + (take_profit_percent * indicators['atr']):
            balance = position_data * ticker_data['Close'].iloc[-1]
            position_data = None
#            pbar.set_description(f"[SYSTEM]: SOLD {ticker:<4}".ljust(40))

        elif ticker_data['Close'].iloc[-1] <= position_price_data - (stop_loss_percent * indicators['atr']):
            balance = position_data * ticker_data['Close'].iloc[-1]
            position_data = None
#            pbar.set_description(f"[SYSTEM]: SOLD {ticker:<4}".ljust(40))

        elif signal == "SELL":
            balance = position_data * ticker_data['Close'].iloc[-1]
            position_data = None
#            pbar.set_description(f"[SYSTEM]: SOLD {ticker:<4}".ljust(40))

    # Track portfolio value
    portfolio_history.append({
        'timestamp': timestamp,
        'balance': balance,
        'position': position_data,
        'portfolio_value': balance if position_data is None else position_data * ticker_data['Close'].iloc[-1]
    })

    return portfolio_history, position_data, position_price_data

def backtest(tickers, data, initial_balance=10000, stop_loss_percent=0.03, take_profit_percent=0.05):
    balance = initial_balance
    position = None
    position_price = 0
    portfolio_history = []

    # Precompute indicators for all data once, reducing redundancy in calculations
    indicators_cache = {}

    with tqdm(total=len(data.index), desc="Running backtest", unit=" datapoint") as pbar:
        for looper, (timestamp, ticker) in enumerate(data.index):
            if looper < 50:
                continue

            # Process each ticker data for each timestamp
            result, position, position_price = process_ticker_data(
                timestamp, ticker, data, indicators_cache, take_profit_percent, stop_loss_percent, initial_balance, position, position_price, pbar
            )

            # Append results to global portfolio history
            portfolio_history.extend(result)
            pbar.set_description(f"[SYSTEM]: ${portfolio_history[-1].get('balance'):,.2f}")
            pbar.update(1)  # Update progress bar

    # At the end of the backtest, liquidate any open positions
    if position is not None:
        balance = position * data['Close'].iloc[-1]  # Final balance after selling position
        print(f"[SYSTEM]: End of backtest: Sold remaining position at {data['Close'].iloc[-1]}")

    # Generate final portfolio report
    portfolio_history_df = pd.DataFrame(portfolio_history)
    portfolio_history_df.set_index('timestamp', inplace=True)
    portfolio_history_df['portfolio_value'].plot(title="Portfolio Value Over Time")

    final_value = portfolio_history_df['portfolio_value'].iloc[-1]
    print(f"Final Portfolio Value: {final_value}")
    print(f"Total Return: {(final_value - initial_balance) / initial_balance * 100:.2f}%")

    plt.figure(figsize=(10, 6))
    plt.plot(portfolio_history_df.index, portfolio_history_df['portfolio_value'], label="Portfolio Value", color='blue')
    plt.title("Portfolio Value Over Time", fontsize=16)
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Portfolio Value ($)', fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("portfolio-value.png")