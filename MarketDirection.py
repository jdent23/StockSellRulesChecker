from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)
import datetime
import pandas as pd
import tqdm
import time
import os

class MarketDirection:
    @staticmethod
    def moving_average(yahoo_df, days, delta=0):
        df = yahoo_df.reset_index()
        curr_date = df['Date'].max() - datetime.timedelta(days=delta)
        end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)

        df_days = df[df['Date'] >= end_date]
        df_days = df_days[df_days['Date'] <= curr_date]
        return round(float(df_days['Close'].mean()), 2)

    @staticmethod
    def SMA50_slope_positive_rule(yahoo_df, ticker, days=21):
        for day in range(days):
            curr_avg = MarketDirection.moving_average(yahoo_df, days=50, delta=day)
            prev_avg = MarketDirection.moving_average(yahoo_df, days=50, delta=day+1)
            if curr_avg >= prev_avg:
                continue
            else:
                return False
        return True
        
    def market_direction(self, curr_filename):

        print("Starting Market Direction")
        market_direction = {}

        print("Getting S&P 500 Indictator")
        market_direction["S&P500"] = {}
        ticker = "^GSPC"
        yahoo_df = pdr.get_data_yahoo(ticker, interval = "1d", threads= False)
        SP500_SMA21_value = MarketDirection.moving_average(yahoo_df, days=21)
        SP500_SMA50_value = MarketDirection.moving_average(yahoo_df, days=50)
        SP500_Slope = MarketDirection.SMA50_slope_positive_rule(yahoo_df, ticker, days=21)
        market_direction["S&P500"]['SMA21_Greater_SMA50_Rule'] = bool(SP500_SMA21_value > SP500_SMA50_value)
        market_direction["S&P500"]['SMA50_Positive_Slope_Rule'] = SP500_Slope
        market_direction["S&P500"]['SMA21'] = SP500_SMA21_value
        market_direction["S&P500"]['SMA50'] = SP500_SMA50_value

        print("Getting NASDAQ Indictator")
        market_direction["NASDAQ"] = {}
        ticker = "^IXIC"
        yahoo_df = pdr.get_data_yahoo(ticker, interval = "1d", threads= False)
        SP500_SMA21_value = MarketDirection.moving_average(yahoo_df, days=21)
        SP500_SMA50_value = MarketDirection.moving_average(yahoo_df, days=50)
        SP500_Slope = MarketDirection.SMA50_slope_positive_rule(yahoo_df, ticker, days=21)
        market_direction["NASDAQ"]['SMA21_Greater_SMA50_Rule'] = bool(SP500_SMA21_value > SP500_SMA50_value)
        market_direction["NASDAQ"]['SMA50_Positive_Slope_Rule'] = SP500_Slope
        market_direction["NASDAQ"]['SMA21'] = SP500_SMA21_value
        market_direction["NASDAQ"]['SMA50'] = SP500_SMA50_value


        output_list = []
        cols = None
        for stock in market_direction.keys():
            cols = ["Ticker"] + list(market_direction[stock].keys())
            temp_list = []
            temp_list.append(stock)
            for rule in market_direction[stock].keys():
                temp_list.append(market_direction[stock][rule])
            output_list.append(temp_list)
        df_out = pd.DataFrame(output_list,columns=cols)
        return df_out


if __name__ == "__main__":
  market_direction = MarketDirection()
  date = datetime.datetime.utcnow()
  filename = 'results/market_direction'
  curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
  df_out = market_direction.market_direction(curr_filename)
  df_out.to_csv(curr_filename)
  

  
