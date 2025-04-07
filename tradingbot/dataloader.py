#!/usr/bin/env python

"""
DATABASE STRUCTURE DURING DATABASE COLLECTION

data {
Stock: varchar(6),
High Price: int,
Low Price: int,
Close Price: int,
Volume: int
}


DATABASE STRUCTURE AFTER PRE-PROCESSING

processed data {
Stock: varchar(6),
High Price: int,
Low Price: int,
Close Price: int,
Volume: int,
P/E: int,
P/B: int
}
"""

import yfinance as yf
import sqlite3 as sq3
import pandas as pd
import os
from preprocessing import preprocess_data

# database path var
DB_PATH = "databases/tradingbot.db"


# gets yfinance data for a given list of tickers. returns multi-index dataframe
def fetch_data(tickers):
    data = yf.download(tickers,period='1y',interval='1d', group_by='ticker', auto_adjust=True)
    data = data.dropna()

    data = data.sort_index(axis=1, level=1)
    data = data.sort_index()

    return data

# function that creates an sqlite table via sqlite3
def create_table():
    # ensure db and dirs exist before connecting
    os.makedirs(os.path.dirname(DB_PATH), exist_ok = True)
    con = sq3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dataloader (
        ticker TEXT,
        timestamp TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        PRIMARY KEY (ticker, timestamp)
        )
        """)

    con.commit()
    con.close()

# inserts ticker data into sqlite3 db
def insert_data(ticker, df):
    con = sq3.connect(DB_PATH)
    cur = con.cursor()

    # using INSERT OR IGNORE to ensure we aren't overwriting data we've already written
    for index, row in df.iterrows():
        cur.execute("""
        INSERT OR IGNORE INTO dataloader (ticker, timestamp, open, high, low, close, volume)
        VALUES (?,?,?,?,?,?,?)
        """, (ticker, index.isoformat(), row['Open'], row['High'], row['Low'], row['Close'], int(row['Volume']))
        )

#        print(f"[{ticker:<4}]: Loaded: {row['Open']}, {row['High']}, {row['Low']}, {row['Close']}, {int(row['Volume'])}")

    con.commit()
    con.close()


# takes a list of tickers and populates sqlite3 db with their information
def dataloader(tickers):
    create_table()

    # if passed one ticker, turn it into a one-ticker list
    if isinstance(tickers, str):
        tickers = [ticker]

    # sort alphabetically
    tickers.sort()

    data = fetch_data(tickers)

    for ticker in tickers:
        try:
            # get a dataframe from a multiindex, or if it's already a dataframe (in the case that we have one ticker), just use that one
            df = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data

            # add data for missing datapoints via backfilling
            df.index = pd.to_datetime(df.index)
            full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='h')
            df = df.reindex(full_range, method=None)
            df.ffill(inplace=True)
            df.bfill(inplace=True)

            # insert data to sqlite
            insert_data(ticker, df)

            print(f"[{ticker:<4}]: Loaded data into SQLite.")

        except Exception as ex:
            print(f"[{ticker:<4}]: Failed to load data into SQLite. {ex}")
            return None
            
    return data