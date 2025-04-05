import random
import numpy as np
from sklearn.model_selection import ParameterGrid
from tradingbot.backtesting import backtest_multiple_tickers
from tradingbot.utils import calculate_statistics
from tradingbot.algorithm import trades

# create an optimizer class
class BacktestOptimizer:
    # initialization function
    def __init__(self, tickers, period="1y", interval="1h"):
        self.tickers = tickers
        self.period = period
        self.interval = interval

    # run backtest for a single configuration
    def run_backtest(self, config):
        print(f"Running backtest with configuration: {config}")

        # call backtest with config
        backtest_multiple_tickers(self.tickers, self.period, self.interval,
                                   config["breakout_up_threshold"], config["breakout_down_threshold"],
                                   config["stop_loss_percent"], config["take_profit_percent"])

        # calculate performance statistics
        statistics = calculate_statistics(trades)

        return statistics

    # gridsearch to optimize parameters based on profit factor
    def optimize(self, parameter_grid):
        best_profit_factor = -np.inf
        best_config = None

        # generate eall possible combinations
        grid = ParameterGrid(parameter_grid)

        # test every combination
        for config in grid:
            stats = self.run_backtest(config)

            # evaluate based on profit factor
            profit_factor = stats
            print(f"Profit Factor: {profit_factor:.2f}")

            if profit_factor > best_profit_factor:
                best_profit_factor = profit_factor
                best_config = config

        print(f"Best configuration: {best_config}")
        return best_config, best_profit_factor

# define parameter grid for optimization
parameter_grid = {
    "breakout_up_threshold": [1.01, 1.02, 1.03, 1.05],
    "breakout_down_threshold": [0.97, 0.98, 0.99],
    "stop_loss_percent": [0.02, 0.04, 0.05],
    "take_profit_percent": [0.10, 0.15, 0.20]
}


def start_optimizer(tickers):
    optimizer = BacktestOptimizer(tickers)

    # optimize grid search based on Profit Factor
    best_config, best_profit_factor = optimizer.optimize(parameter_grid)

    # output the most successful set of params and profit factor
    print(f"\n\nBest Configuration: {best_config}")
    print(f"Best Profit Factor: {best_profit_factor}")
