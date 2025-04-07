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

# database path var
DB_PATH = "databases/tradingbot.db"


# function that creates an sqlite table via sqlite3
def create_table():
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

# gets yfinance data for a given list of tickers. returns multi-index dataframe
def fetch_data(tickers):
    data = yf.download(tickers,period='1y',interval='1h',group_by='ticker', auto_adjust=True)
    data = data.dropna()
    return data

# inserts ticker data into sqlite3 db
def insert_data(ticker, df):
    con = sq3.connect(DB_PATH)
    cur = con.cursor()

    for index, row in df.iterrows():
        cur.execute("""
        INSERT OR IGNORE INTO dataloader (ticker, timestamp, open, high, low, close, volume)
        VALUES (?,?,?,?,?,?,?)
        """, (ticker, index.isoformat(), row['Open'], row['High'], row['Low'], row['Close'], int(row['Volume']))
        )

    con.commit()
    con.close()

# takes a list of tickers and populates sqlite3 db with their information
def dataloader(tickers):
    create_table()
    data = fetch_data(tickers)

    if isinstance(tickers, str):
        tickers = [ticker]

    for ticker in tickers:
        try:
            df = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
            insert_data(ticker, df)
            print(f"[{ticker:^4}]: Loaded data.")

        except Exception as ex:
            print(f"[{ticker:^4}]: Failed to load data. {ex}")