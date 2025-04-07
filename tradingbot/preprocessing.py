#!/usr/bin/env python

import pandas as pd
import yfinance as yf


# fetch current ratios and add to in-mem dataframe
def preprocess_data(ticker, df):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        pe = info.get('trailingPE')
        pb = info.get('priceToBook')

        if pe is None or pb is None or not (pd.notna(pe) and pd.notna(pb)) or not (pd.api.types.is_number(pe) and pd.api.types.is_number(pb)) or not (abs(pe) < float('inf') and abs(pb) < float('inf')):
            raise ValueError

        df['P/E'] = pe
        df['P/B'] = pb


        print(f"[{ticker:<4}]: Financials fetched: {pe} {pb}")

    except Exception as e:
        return None

    return df

# preprocess all data
def preprocess_all_data(tickers, data):
    processed = {}

    for ticker in tickers:
        df = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
        processed[ticker] = preprocess_data(ticker, df.copy())
        if processed[ticker] is None:
            processed.pop(ticker)
            print(f"[{ticker:<4}]: Removed due to bad data.")

    return processed