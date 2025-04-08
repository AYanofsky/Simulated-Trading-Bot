#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from tradingbot.scoring import generate_trade_signal
from tradingbot.indicators import calculate_latest_indicators
from tradingbot.utils import calculate_position_size

def process_ticker_data(timestamp, ticker, data, indicators_cache, take_profit_percent, stop_loss_percent, balance, position, position_price, pbar, commission_percent, slippage_percent, max_loss_count, cooling_off_period, cooling_off_counter):
    ticker_data = data.xs(ticker, level='Ticker').loc[:timestamp].tail(50)

    # Check if the indicators for this ticker and timestamp are already cached
    if (ticker, timestamp) not in indicators_cache:
        indicators_cache[(ticker, timestamp)] = calculate_latest_indicators(ticker_data)

    indicators = indicators_cache[(ticker, timestamp)]

    # Generate trade signal
    signal = generate_trade_signal(indicators)

    # Process trading logic for each tick
    position_data = position
    portfolio_history = []

    # Cooling off period logic (no trades if cooling off is active)
    if cooling_off_counter > 0:
        cooling_off_counter -= 1
        return portfolio_history, position_data, position_price, balance, cooling_off_counter

    # Buying logic: if no position and signal is "BUY"
    if position_data is None and signal == "BUY":
        position_price = ticker_data['Close'].iloc[-1]

        # Apply slippage and commission to the position price
        position_price *= (1 + slippage_percent / 100)
        position_price = position_price * (1 + commission_percent / 100)

        # Calculate ATR for stop loss distance
        atr = indicators['atr']
        
        # Calculate position size based on risk management (1% of balance risk per trade)
        max_shares = calculate_position_size(balance, position_price, atr, risk_percent=0.01)  # 1% risk per trade
        
        # Update position and balance
        position_data = max_shares
        balance -= position_data * position_price  # Subtract cost of purchase from balance

        # Set cooling off period after buying
        cooling_off_counter = cooling_off_period

        pbar.set_description(f"[SYSTEM]: {position_data} SHARES OF {ticker}")


    # Selling logic: if position is open and the signal is "SELL"
    elif position_data is not None:
        # Check take-profit/stop-loss conditions
        atr = indicators['atr']
        if ticker_data['Close'].iloc[-1] >= position_price + (take_profit_percent * atr):
            balance += position_data * ticker_data['Close'].iloc[-1]
            position_data = None

        elif ticker_data['Close'].iloc[-1] <= position_price - (stop_loss_percent * atr):
            balance += position_data * ticker_data['Close'].iloc[-1]
            position_data = None

        elif signal == "SELL":
            balance += position_data * ticker_data['Close'].iloc[-1]
            position_data = None

    # Track portfolio value
    portfolio_history.append({
        'timestamp': timestamp,
        'balance': balance,
        'position': position_data,
        'portfolio_value': balance if position_data is None else position_data * ticker_data['Close'].iloc[-1] + balance
    })

    return portfolio_history, position_data, position_price, balance, cooling_off_counter


def backtest(tickers, data, initial_balance=10000, stop_loss_percent=0.03, take_profit_percent=0.05, commission_percent=0.005, slippage_percent=0.002, max_loss_count=3, cooling_off_period=5):
    balance = initial_balance
    position = None
    position_price = 0
    portfolio_history = []
    indicators_cache = {}
    cooling_off_counter = 0

    with tqdm(total=len(data.index), desc="RUNNING BACKTEST", unit=" datapoint") as pbar:
        for looper, (timestamp, ticker) in enumerate(data.index):
            if looper < 50:
                continue

            # Process each ticker data for each timestamp
            result, position, position_price, balance, cooling_off_counter = process_ticker_data(
                timestamp, ticker, data, indicators_cache, take_profit_percent, stop_loss_percent, balance, position, position_price, pbar, commission_percent, slippage_percent, max_loss_count, cooling_off_period, cooling_off_counter
            )

            # Append results to global portfolio history
            portfolio_history.extend(result)
            pbar.update(1)  # Update progress bar

    # At the end of the backtest, liquidate any open positions
    if position is not None:
        balance += position * data['Close'].iloc[-1] * (1 - commission_percent)  # Final balance after selling position with commission
        print(f"[SYSTEM]: END OF BACKTEST: SOLD REMAINING POSITION AT {data['Close'].iloc[-1]}")

    # Generate final portfolio report
    portfolio_history_df = pd.DataFrame(portfolio_history)
    portfolio_history_df.set_index('timestamp', inplace=True)
    portfolio_history_df['portfolio_value'].plot(title="Portfolio Value Over Time")

    final_value = portfolio_history_df['portfolio_value'].iloc[-1]
    print(f"FINAL PORTFOLIO VALUE: ${final_value:,.2f}")
    print(f"TOTAL RETURN: {(final_value - initial_balance) / initial_balance * 100:.2f}%")

    plt.figure(figsize=(10, 6))
    plt.plot(portfolio_history_df.index, portfolio_history_df['portfolio_value'], label="Portfolio Value", color='green')
    plt.title("Portfolio Value Over Time", fontsize=16)
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Portfolio Value ($)', fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("portfolio-value.png")