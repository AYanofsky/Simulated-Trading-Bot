from datetime import datetime, timedelta
from skopt import gp_minimize
from skopt.space import Real, Integer
from tradingbot.utils import get_tickers_from_file
from tradingbot.backtest import backtest
from tradingbot.dataloader import bootstrap_dataloader

# define the search space for hyperparameters
search_space = [
    Real(0.01, 0.2, name='stop_loss_percent'),
    Real(0.01, 0.2, name='take_profit_percent'),
    Integer(1, 10, name='cooling_off_period'),
    Integer(0, 10, name='max_loss_count')
    ]

tickers = get_tickers_from_file()


# get dates. this will be a variable that can be changed later
end_date = datetime.today()
start_date = end_date - timedelta(days=365)
end_date = end_date.isoformat()
start_date = start_date.isoformat()
    

# define the objective function that evaluates your trading strategy
def objective(params):
    stop_loss, take_profit, cooling_off_period, max_loss_count= params

    # returns multindex dataframe
    data = bootstrap_dataloader(tickers, start_date, end_date)

    # backtesting function that returns performance
    performance = backtest(tickers, data, stop_loss_percent=stop_loss, take_profit_percent=take_profit, cooling_off_period=cooling_off_period, max_loss_count=max_loss_count)
    
    # return a negative value because `gp_minimize` minimizes the objective function
    return -performance  # assuming higher performance is better

# perform Bayesian Optimization
result = gp_minimize(objective, search_space, n_calls=50, random_state=2, n_jobs=-1)

# print the best parameters and the corresponding performance
print(f"Best parameters: {result.x}")
print(f"Best performance: {-result.fun}")
