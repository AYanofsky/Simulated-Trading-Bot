#!/usr/bin/env python

"""
DATABASE STRUCTURE DURING DATABASE COLLECTION

preprocessed {
Stock: varchar(6),
High Price: int,
Low Price: int,
Close Price: int,
Volume: int
}
"""

DB_PATH = "databases/tradingbot.db"

def preprocessor(ticker, data):
    # given a ticker and its data
    # sort the ticker by its timestamp
    # drop all invalid data points (NaN, Infinity, None)
    # back/forward fill all missing data points

    # return data, where data is the sorted and filled dataframe
    pass
 
def dataloader(tickers):
    # download historical data with yf.download() in one-hour increments with a period of 1y, sorted by ticker
    # for every ticker's data in the list, run the preprocessor on it
        # after the data is preprocessed, insert it into the database
    # return data, where data is a multi-index dataframe
    pass

def boostrap_dataloader(tickers):
    # if tickers is a string, turn it into a list
    # check to see if database exists. if not, make it
        # check to see if table exists. if not, run the dataloader
        # check to see if table has values for the specified time and date. if not, drop the table and run the dataloader

    # return data, where data is a multi-index dataframe
    pass