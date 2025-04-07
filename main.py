#!/usr/bin/env python

from datetime import datetime, timedelta
from tradingbot.utils import get_tickers_from_file
from tradingbot.dataloader import bootstrap_dataloader
from tradingbot.indicators import generate_indicator_dict

def main():
    # get tickers from a file
    tickers = get_tickers_from_file()

    # get dates. this will be a variable that can be changed later
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    end_date = end_date.isoformat()
    start_date = start_date.isoformat()
    
    # returns multindex dataframe
    data = bootstrap_dataloader(tickers, start_date, end_date)

    # returns nested dict of form {ticker{indicator:value}...}
    indicators = generate_indicator_dict(tickers, data)

if __name__ == '__main__':
    main()