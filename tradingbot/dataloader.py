#!/usr/bin/env python

import sqlite3 as sq3
import pandas as pd
import yfinance as yf
import os
from pandas.tseries.holiday import USFederalHolidayCalendar
from tqdm import tqdm

DB_PATH = "databases/tradingbot.db"

# function to get timestamps during trading hours with format "y-m-d h"
def get_trading_hours(start,end):
    # generate hourly timestamps
    all_hours = pd.date_range(start=start, end=end, freq='h')

    # filter: only include weekdays and business hours (9 am to 4 pm inclusive)
    trading_hours = all_hours[(all_hours.weekday < 5) & (all_hours.hour >= 9) & (all_hours.hour <= 16)]

    # remove federal holidays
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start=start, end=end)
    trading_hours = trading_hours[~trading_hours.normalize().isin(holidays)]

    return trading_hours.strftime('%Y-%m-%d %H:00:00').tolist()

# function to fetch all data for given list of tickers
def fetch_data(tickers):
    print("[SYSTEM]: Fetching data.")
    data = yf.download(tickers, period='1y', interval='1h', group_by='ticker', auto_adjust=True, progress=False)
    return data

# function to insert data into database
def insert_data(ticker, df):
    # ensure timestamp is in pseudo-ISO format
    df.index = df.index.strftime('%Y-%m-%d %H:00:00')

    # set up tuple
    rows = [
        (ticker, idx, row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])
        for idx, row in df.iterrows()
    ]

    # pythonic!
    with sq3.connect(DB_PATH) as con:
        cur = con.cursor()
        # insert data into sql database
        cur.executemany("""

        INSERT INTO dataloader (Ticker, Timestamp, Open, High, Low, Close, Volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, rows)
        con.commit()

# function to preprocess data
def preprocessor(ticker, data, expected_timestamps):

    try:
        # create copy of dataframe to prevent copy error
        data = data.copy()

        # convert timestamps in data to datetime and normalize (strip timezone)
        data.index = pd.to_datetime(data.index).tz_localize(None)

        # change the timestamps to ISO format and keep only the date + hour part
        data.index = data.index.strftime('%Y-%m-%d %H:00:00')

        # convert back to datetime after formatting
        data.index = pd.to_datetime(data.index)

        # sort data by timestamp
        data.sort_index(inplace=True)

        # drop invalid data points (NaN, Infinity, None)
        data.replace([None, float('inf'), -float('inf')], pd.NA, inplace=True)
        data.dropna(how='any', inplace=True)

        # make sure the expected_timestamps is in the same format and reindex to the expected range
        expected_timestamps = pd.to_datetime(expected_timestamps)

        # reindex to expected timestamps
        data = data.reindex(expected_timestamps)

        # fill missing data points: 
        # if the first row is NaN, fill with the next available row
        if data.iloc[0].isna().any():
            next_valid_index = data.dropna().index.min()
            if pd.notna(next_valid_index):
                data.iloc[0] = data.loc[next_valid_index]

        # interpolate missing data using fifth-order polynomial interpolation
        data.interpolate(method='polynomial', order=5, limit_direction='both', inplace=True)


#        print(data)
        # return the processed data
        return data

    except Exception as ex:
        print(f"[{ticker:<4}]: Error during preprocessing. {ex}")
        return None

def dataloader(tickers, expected_timestamps):
    data = fetch_data(tickers)

    with tqdm(total=len(tickers), desc="[SYSTEM]: Inserting data",unit=" ticker") as pbar:
        # preprocess data for each ticker
        for ticker in tickers:
            # for every ticker's data in the list, run the preprocessor on it
            df = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
            preprocessed_df = preprocessor(ticker, df, expected_timestamps)

            if preprocessed_df is not None:
            # after the data is preprocessed, insert it into the database
                insert_data(ticker, preprocessed_df)
        #            print(f"[{ticker:<4}]: Loaded preprocessed data into the database.")
        #        else:
        #            print(f"[{ticker:<4}]: Failed to preprocess data.")
        # return data, where data is a multi-index dataframe
            pbar.update(1)
    print(f"[SYSTEM]: All data loaded.")
    return data

def bootstrap_dataloader(tickers, start_date, end_date):
    # if tickers is a string, turn it into a list
    if isinstance(tickers, str):
        tickers = [tickers]
    
    # ensure database exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sq3.connect(DB_PATH)
    cur = con.cursor()

    # check if table exists
    cur.execute("""
    SELECT name FROM sqlite_master WHERE type='table' AND name='dataloader';
    """)

    table_exists = cur.fetchone() is not None
    expected_timestamps = get_trading_hours(start_date, end_date)

    # if we have a table, check to see if it's complete
    if table_exists:
        all_data_present = True

        for ticker in tickers:
            cur.execute("""
            SELECT COUNT(DISTINCT Timestamp) FROM dataloader
            WHERE Ticker = ? and Timestamp between ? and ?;
            """, (ticker, start_date, end_date))
            count = cur.fetchone()[0]
            if count < len(expected_timestamps):
                all_data_present = False
                print(f"[{ticker:<4}]: {count}/{len(expected_timestamps)}")
                # we can break here because we don't care how many dates are 
                break

    # if the table doesn't exist or we don't have all our data, rebuild
    if not table_exists or not all_data_present:
        print("[SYSTEM]: Missing or incomplete data. Rebuilding table.")
        cur.execute("DROP TABLE IF EXISTS dataloader;")
        cur.execute("""
        CREATE TABLE dataloader (
            Ticker TEXT,
            Timestamp TEXT,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume INTEGER
        );
        """)
        con.commit()
        # download, preprocess, insert
        data = dataloader(tickers, expected_timestamps)

    print("[SYSTEM]: All data present. Reading from database.")
    data = pd.read_sql_query("SELECT * FROM dataloader;", con, parse_dates=["Timestamp"])
    con.close()
    data.set_index(['Timestamp', 'Ticker'], inplace=True)
    data.sort_index(inplace=True)

    return data