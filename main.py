#!/usr/bin/env python

import argparse
from tradingbot.utils import get_tickers
from tradingbot.backtesting import backtest_multiple_tickers

# main handler function
def main(is_backtest=False, period="1y", interval="1h", breakout_up_threshold=1.02, breakout_down_threshold=0.98, 
         stop_loss_percent=0.04, take_profit_percent=0.15):
    tickers = ['NVDA']

    if is_backtest:
        print("Running backtest...")
        backtest_multiple_tickers(tickers,period,interval,breakout_up_threshold,breakout_down_threshold,stop_loss_percent,take_profit_percent)
    else:
        # implement "live" trading logic here
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Bot")

    parser.add_argument('--backtest', action='store_true', help="run backtest instead of live mode.")
    parser.add_argument('--period', type=str, default="1y", help="historical data period for backtest (e.g., '1y', '6mo').")
    parser.add_argument('--interval', type=str, default="1h", help="interval for historical data (e.g., '1h', '1d').")
    parser.add_argument('--breakout_up', type=float, default=1.02, help="breakout threshold for going long.")
    parser.add_argument('--breakout_down', type=float, default=0.98, help="breakdown threshold for going short.")
    parser.add_argument('--stop_loss', type=float, default=0.04, help="stop-loss percentage.")
    parser.add_argument('--take_profit', type=float, default=0.15, help="take-profit percentage.")

    args = parser.parse_args()

    main(
        is_backtest=args.backtest, 
        period=args.period, 
        interval=args.interval,
        breakout_up_threshold=args.breakout_up, 
        breakout_down_threshold=args.breakout_down, 
        stop_loss_percent=args.stop_loss, 
        take_profit_percent=args.take_profit
    )