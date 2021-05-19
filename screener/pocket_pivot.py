from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)
import datetime
import matplotlib.pyplot as plt 
from tqdm import tqdm
import numpy as np
import pandas as pd
import math
from multiprocessing import Pool
from utils import moving_average, moving_average_volume

class PocketPivotFinder:

    @staticmethod
    def check_prior_vol_rule(df, days=5):
        max_date = df['Date'].max()
        df_days = df[df['Date'] >= max_date-datetime.timedelta(days=days)]
        max_vol = df_days['Volume'].max()
        vol = df_days[df_days['Date'] == max_date]['Volume'].values[0]
        return max_vol == vol
        

    @staticmethod
    def check_pocket_pivot(ticker):
        period = 11 # days
        try:
            yahoo_df = pdr.get_data_yahoo([ticker], interval = '1d', threads= False)
        except:
            return [ticker, False]
        yahoo_df.reset_index(inplace=True)
        max_date = yahoo_df['Date'].max()

        pp_dates = []

        try:
            sma50_vol = moving_average_volume(yahoo_df, 50)
            volume = yahoo_df['Volume'].values[0]
            open_val = yahoo_df['Open'].values[0]
            close = yahoo_df['Close'].values[0]
            prior_vol_rule = PocketPivotFinder.check_prior_vol_rule(yahoo_df, days=5)
        except:
            return [ticker, False]

        if volume > sma50_vol and close > open_val and prior_vol_rule:
            return [ticker, True]
        return [ticker, False]

    def find_pocket_pivots(self, curr_filename):
        df = pd.read_csv(curr_filename)
        df = df[df['N-Value Rating'] > 8178]
        df.index.name=None
        df.reset_index(inplace=True, drop=True)
        df = df.sort_values(by=['N-Value Rating', 'Lwowski Rating'], ascending=False)

        df_out = df['Ticker'].to_frame()
        df_out['Pocket Pivot Pattern'] = False

        # Choose interval "1d" or "1wk"
        with Pool(8) as p:
            tickers = df['Ticker'].values.tolist()
            ticker_check_list = list(tqdm(p.imap(PocketPivotFinder.check_pocket_pivot, tickers), total=len(tickers)))
        
        for ticker_check in ticker_check_list:
            df_out.loc[df_out['Ticker'] == ticker_check[0], 'Pocket Pivot Pattern'] = ticker_check[1]
                
        return df_out

if __name__ == "__main__":
    pocket_pivot_finder = PocketPivotFinder()
    date = datetime.datetime.utcnow()
    filename = 'pocket_pivot'
    curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
    df_out = pocket_pivot_finder.find_pocket_pivots("../frontend/results/screener_results_2021_4_28.csv")
    df_out.to_csv(curr_filename)