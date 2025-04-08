#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from tradingbot.scoring import generate_trade_signal
from tradingbot.indicators import calculate_latest_indicators

def process_ticker_data(timestamp, ticker, data, indicators_cache, take_profit_percent, stop_loss_percent, balance, position, position_price, pbar, commission_percent=0.005, slippage_percent=0.002, max_loss_count=3, cooling_off_period=5):
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
    consecutive_losses = 0

    # Track whether cooling-off is active
    if hasattr(process_ticker_data, 'cooling_off_counter'):
        cooling_off_counter = process_ticker_data.cooling_off_counter
    else:
        cooling_off_counter = 0

    if cooling_off_counter > 0:
        # Cooling-off period: skip trading
        cooling_off_counter -= 1
        pbar.set_description(f"[SYSTEM]: Cooling off - {cooling_off_counter} periods remaining.".ljust(40))
        return portfolio_history, position_data, position_price, balance, cooling_off_counter

    if position_data is None and signal == "BUY":
        position_price = ticker_data['Close'].iloc[-1] * (1 + slippage_percent)  # Apply slippage when buying
        max_shares = int(balance / position_price)  # Maximum number of shares we can grab

        if max_shares > 0:
            position_data = max_shares
            balance -= position_data * position_price * (1 + commission_percent)  # Deduct the balance after applying commission
            pbar.set_description(f"[SYSTEM]: BOUT {ticker:<4}".ljust(40))
            consecutive_losses = 0  # Reset consecutive losses after a successful trade

    elif position_data is not None:
        # Check take-profit/stop-loss/sell conditions
        if ticker_data['Close'].iloc[-1] >= position_price + (take_profit_percent * indicators['atr']):
            balance += position_data * ticker_data['Close'].iloc[-1] * (1 - commission_percent)  # Apply commission on sell
            position_data = None
            pbar.set_description(f"[SYSTEM]: TAKING PROFIT FOR {ticker:<4}".ljust(40))
            consecutive_losses = 0  # Reset consecutive losses after taking profit

        elif ticker_data['Close'].iloc[-1] <= position_price - (stop_loss_percent * indicators['atr']):
            balance += position_data * ticker_data['Close'].iloc[-1] * (1 - commission_percent)  # Apply commission on sell
            position_data = None
            pbar.set_description(f"[SYSTEM]: STOPPING LOSS FOR {ticker:<4}".ljust(40))
            consecutive_losses += 1  # Increase consecutive loss counter

            # After a certain number of consecutive losses, enter cooling-off period
            if consecutive_losses >= max_loss_count:
                cooling_off_counter = cooling_off_period
                pbar.set_description(f"[SYSTEM]: Entering cooling-off period after {consecutive_losses} losses.".ljust(40))

        elif signal == "SELL":
            balance += position_data * ticker_data['Close'].iloc[-1] * (1 - commission_percent)  # Apply commission on sell
            position_data = None
            pbar.set_description(f"[SYSTEM]: SOLD {ticker:<4}".ljust(40))

    else:
        pbar.set_description(f"[SYSTEM]: HOLDING".ljust(40))

#    pbar.set_description(f"[SYSTEM]: ${int(balance) if position_data is None else int(position_data * ticker_data['Close'].iloc[-1] + balance):,}".ljust(40))

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

    with tqdm(total=len(data.index), desc="Running backtest", unit=" datapoint") as pbar:
        for looper, (timestamp, ticker) in enumerate(data.index):
            if looper < 50:
                continue

            # Process each ticker data for each timestamp
            result, position, position_price, balance, cooling_off_counter = process_ticker_data(
                timestamp, ticker, data, indicators_cache, take_profit_percent, stop_loss_percent, balance, position, position_price, pbar, commission_percent, slippage_percent, max_loss_count, cooling_off_period
            )

            # Append results to global portfolio history
            portfolio_history.extend(result)
            pbar.update(1)  # Update progress bar

    # At the end of the backtest, liquidate any open positions
    if position is not None:
        balance += position * data['Close'].iloc[-1] * (1 - commission_percent)  # Final balance after selling position with commission
        print(f"[SYSTEM]: End of backtest: Sold remaining position at {data['Close'].iloc[-1]}")

    # Generate final portfolio report
    portfolio_history_df = pd.DataFrame(portfolio_history)
    portfolio_history_df.set_index('timestamp', inplace=True)
    portfolio_history_df['portfolio_value'].plot(title="Portfolio Value Over Time")

    final_value = portfolio_history_df['portfolio_value'].iloc[-1]
    print(f"Final Portfolio Value: ${final_value:,.2f}")
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