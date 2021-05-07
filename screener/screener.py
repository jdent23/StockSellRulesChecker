import sys
sys.path.append("/mnt/efs")  # nopep8 # noqa
    
from finviz.screener import Screener

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)

import datetime
import stockquotes
import pandas as pd
import tqdm
import time
from tqdm import tqdm
from shutil import copyfile
import os

import gc
import psutil
import sys 
from importlib import reload  
import finviz
from multiprocessing import Pool
from MarketDirection import MarketDirection
from ScreenComparer import ScreenComparer
from rules import *
from utils import moving_average, relative_strength, week52_low_high, moving_average_volume
from cup_and_handle import CupAndHandleFinder

class StockScreener:

  @staticmethod
  def initial_screen():
    eps_5year_over0pct = False
    eps_qoq_over0pct = False
    eps_yoy_over0pct = False
    sales_5years_over0pct = False
    sales_qoq_over0pct = False

    filters = []
    if eps_5year_over0pct:
      filters.append('fa_eps5years_pos')
    if eps_qoq_over0pct:
      filters.append('fa_epsqoq_pos')
    if eps_yoy_over0pct:
      filters.append('fa_epsyoy_pos')
    if sales_5years_over0pct:
      filters.append('fa_sales5years_pos')
    if sales_qoq_over0pct:
      filters.append('fa_salesqoq_pos')

    stock_list = Screener(filters=filters, table='Performance', order='price')
    return stock_list  

  @staticmethod
  def screen_stock(stock):
    try:
      screened_stocks = {}

      if stock["Ticker"] == "":
        return

      finviz_stats = finviz.get_stock(stock['Ticker'])
      print(finviz_stats)
      prev_close = round(float(finviz_stats['Prev Close'].replace("$","")),2)
      screened_stocks[stock['Ticker']] = {}
      
      try:
        yahoo_df = pdr.get_data_yahoo(stock['Ticker'], interval = "1d", threads= False)
      except:
        return
      try:
        sp500_df = pdr.get_data_yahoo("^GSPC", interval = "1d", threads= False)
      except:
        return

      SMA200_value = moving_average(yahoo_df, days=200)
      SMA150_value = moving_average(yahoo_df, days=150)
      SMA50_value = moving_average(yahoo_df, days=50)
      RS_value = relative_strength(yahoo_df, sp500_df)
      SMA50_volume_value = moving_average_volume(yahoo_df, days=50)

      SMA200_percent = round(float(finviz_stats['SMA200'].replace("%",""))/100,2)
      SMA50_percent = round(float(finviz_stats['SMA50'].replace("%",""))/100,2)
      volume = round(float(finviz_stats['Volume'].replace(",","")),0)

      try:
        EPS_QoQ_percent = round(float(finviz_stats['EPS Q/Q'].replace("%",""))/100,2)
      except:
        EPS_QoQ_percent = 0

      try:
        Sales_QoQ_percent = round(float(finviz_stats['Sales Q/Q'].replace("%",""))/100,2)
      except:
        Sales_QoQ_percent = 0

      try:
        inst_own = round(float(finviz_stats['Inst Own'].replace("%",""))/100,2)
      except:
        inst_own = 0
      
      shares_outstanding = finviz_stats['Shs Outstand']
      if 'M' in shares_outstanding:
        shares_outstanding = float(shares_outstanding.replace("M", ""))*1e6
      elif 'B' in shares_outstanding:
        shares_outstanding = float(shares_outstanding.replace("B", ""))*1e9
      elif 'T' in shares_outstanding:
        shares_outstanding = float(shares_outstanding.replace("T", ""))*1e12
      else:
        shares_outstanding = 0

      week52_high, week52_low = week52_low_high(yahoo_df)
      
      screened_stocks[stock['Ticker']]['SMA200_value'] = SMA200_value
      screened_stocks[stock['Ticker']]['SMA150_value'] = SMA150_value
      screened_stocks[stock['Ticker']]['SMA50_value'] = SMA50_value
      screened_stocks[stock['Ticker']]['SMA200_percent'] = SMA200_percent
      screened_stocks[stock['Ticker']]['SMA50_percent'] = SMA50_percent
      screened_stocks[stock['Ticker']]['EPS_QoQ_percent'] = EPS_QoQ_percent
      screened_stocks[stock['Ticker']]['Sales_QoQ_percent'] = Sales_QoQ_percent
      screened_stocks[stock['Ticker']]['prev_close'] = prev_close
      screened_stocks[stock['Ticker']]['week52_high'] = week52_high
      screened_stocks[stock['Ticker']]['week52_low'] = week52_low
      screened_stocks[stock['Ticker']]['Inst. Ownership'] = inst_own
      screened_stocks[stock['Ticker']]['Shares Outstanding'] = shares_outstanding
      screened_stocks[stock['Ticker']]['volume'] = volume
      screened_stocks[stock['Ticker']]['Relative Strength Value'] = RS_value

      # 50d MA greater than 150d MA
      SMA50_greater_SMA150_rule, n_value, score = MA50gtMA150_rule(SMA50_value, SMA150_value, 12)
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule'] = SMA50_greater_SMA150_rule
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule_nvalue'] = round(n_value,0)

      # 150d MA greater than 200d MA
      SMA150_greater_SMA200_rule, n_value, score = MA150gtMA200_rule(SMA150_value, SMA200_value, 11)
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule'] = SMA150_greater_SMA200_rule
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule_nvalue'] = round(n_value,0)

      # 52 week high low span rule
      week52_span_rule, n_value, score = high_low_span_52_week_rule(week52_high, week52_low, 10)
      screened_stocks[stock['Ticker']]['week52_span_rule'] = week52_span_rule
      screened_stocks[stock['Ticker']]['week52_span_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['week52_span_rule_nvalue'] = round(n_value,0)

      # RS Value > 1.0 rule:
      rs_value_rule_, n_value, score = rs_value_rule(RS_value, 9)
      screened_stocks[stock['Ticker']]['rs_value_rule'] = rs_value_rule_
      screened_stocks[stock['Ticker']]['rs_value_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['rs_value_rule_nvalue'] = round(n_value,0)

      # Liquidity Rule
      liquidity_rule_, n_value, score = liquidity_rule(SMA50_value, SMA50_volume_value, 8)
      screened_stocks[stock['Ticker']]['liquidity_rule'] = liquidity_rule_
      screened_stocks[stock['Ticker']]['liquidity_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['liquidity_rule_nvalue'] = round(n_value,0)

      # Close above 52 week high - 25%
      close_above_52weekhigh_rule_, n_value, score = close_above_52weekhigh_rule(prev_close, week52_high, 7)
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule'] = close_above_52weekhigh_rule_
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule_nvalue'] = round(n_value,0)

      # Price greater than $10 rule
      prev_close_rule_, n_value, score = prev_close_rule(prev_close, 6)
      screened_stocks[stock['Ticker']]['prev_close_rule'] = prev_close_rule_
      screened_stocks[stock['Ticker']]['prev_close_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['prev_close_rule_nvalue'] = round(n_value,0)


      # Positive 200d MA
      SMA200_slope_rule, score, n_value = SMA200_slope_positive_rule(yahoo_df, ticker=stock['Ticker'], days=21, n_value_in=5)
      screened_stocks[stock['Ticker']]['SMA200_slope_rule'] = SMA200_slope_rule
      screened_stocks[stock['Ticker']]['SMA200_slope_rul_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['SMA200_slope_rul_nvalue'] = round(n_value,0)

      # Institutional Ownership > 5%
      inst_ownership_rule_, n_value, score = inst_ownership_rule(inst_own, 4)
      screened_stocks[stock['Ticker']]['inst_ownership_rule'] = inst_ownership_rule_
      screened_stocks[stock['Ticker']]['inst_ownership_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['inst_ownership_rule_nvalue'] = round(n_value,0)


      # Close above 50d MA
      close_greater_SMA50_rule_, n_value, score = close_greater_SMA50_rule(prev_close, SMA50_value, 3)
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule'] = close_greater_SMA50_rule_
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule_nvalue'] = round(n_value,0)


      # Sales QoQ Yearly > 25% rule
      sales_QoQ_yearly_rule_, n_value, score = sales_QoQ_yearly_rule(Sales_QoQ_percent, 2)
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule'] = sales_QoQ_yearly_rule_
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule_nvalue'] = round(n_value,0)


      # EPS QoQ Yearly > 18% rule
      eps_QoQ_yearly_rule_, n_value, score = eps_QoQ_yearly_rule(EPS_QoQ_percent, 1)
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule'] = eps_QoQ_yearly_rule_
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule_nvalue'] = round(n_value,0)

      return screened_stocks
    except:
      return {}

  @staticmethod
  def cleanup_screen(df_out):

    primary_rules = ['SMA50_greater_SMA150_rule', 'SMA150_greater_SMA200_rule', 'week52_span_rule', 
                     'rs_value_rule', 'liquidity_rule', 'close_above_52weekhigh_rule',
                     'prev_close_rule', 'SMA200_slope_rule', 'inst_ownership_rule', 'close_greater_SMA50_rule',
                     'sales_QoQ_yearly_rule'
                     ]

    secondary_rules = ['eps_QoQ_yearly_rule']

    df_out['Primary Passed Tests'] = (df_out[list(primary_rules)]).sum(1)
    df_out['Secondary Passed Tests'] = (df_out[list(secondary_rules)]).sum(1)

    cols = df_out.columns.tolist()

    for rule in primary_rules:
      if rule in cols:
        idx = cols.index(rule)
        cols[idx] = rule + " (1st)"

    for rule in secondary_rules:
      if rule in cols:
        idx = cols.index(rule)
        cols[idx] = rule + " (2nd)"

    df_out.columns = cols

    df_out = df_out[df_out['Primary Passed Tests']>8]
    return df_out

  @staticmethod
  def main_screen(stock):
    try:
      screened_stock = StockScreener.screen_stock(stock)
      ticker = stock["Ticker"]

      if screened_stock == {}:
        return None

      if len(screened_stock[ticker].keys()) == 0:
        return None
        
      output_list = [ticker]
      cols = ["Ticker"] + list(screened_stock[ticker].keys())
      for rule in screened_stock[ticker].keys():
          output_list.append(screened_stock[ticker][rule])     
      df_out = pd.DataFrame([output_list],columns=cols)
      print(df_out)
      return df_out
    except:
      return None

  @staticmethod
  def score_stocks(df):
    cols = df.columns
    score_cols = [col for col in cols if "score" in col]
    df['Lwowski Rating'] = (df[list(score_cols)]).sum(1)

    nvalue_cols = [col for col in cols if "nvalue" in col]
    df['N-Value Rating'] = (df[list(nvalue_cols)]).sum(1)
    df = df.sort_values(by=['N-Value Rating', 'Lwowski Rating'], ascending=False)

    return df

  @staticmethod
  def write_to_s3_csv(df, curr_filename):
    output_file = 's3://elasticbeanstalk-us-east-2-120595873264/{}'.format(curr_filename)
    print("Writing to S3 File: {}".format(output_file))
    df.to_csv(output_file, index=False)

  @staticmethod
  def parallel_screen(stock):
    print("Initial Screen Done")
    df_out = StockScreener.main_screen(stock)
    print(df_out)

    if df_out is not None:
      print("Main Screen Done")
      df_out = StockScreener.cleanup_screen(df_out)

      print("Scoring the Stocks")
      df_out = StockScreener.score_stocks(df_out)
      return df_out
    return None

  def screen(self, curr_filename):
    print("Starting Screener")
    stock_list = StockScreener.initial_screen()

    with Pool(8) as p:
      dfs = list(tqdm(p.imap(StockScreener.parallel_screen, stock_list), total=len(stock_list.data)))

    df_final = pd.concat(dfs, ignore_index = True)
    df_final.reset_index()

    StockScreener.write_to_s3_csv(df_final, curr_filename)

def main():
  # Run Screener
  screener = StockScreener()
  date = datetime.datetime.utcnow()
  filename = 'results/screener_results'
  curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
  #screener.screen(curr_filename)

  # Run Cup and Handle Pattern Recognition
  cup_and_handle_finder = CupAndHandleFinder()
  date = datetime.datetime.utcnow()
  filename = 'results/cup_and_handle'
  curr_cnh_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
  df_out = cup_and_handle_finder.find_cup_and_handles("s3://elasticbeanstalk-us-east-2-120595873264/{}".format(curr_filename))
  StockScreener.write_to_s3_csv(df_out, curr_cnh_filename)

  # Run Market Direction
  market_direction = MarketDirection()
  date = datetime.datetime.utcnow()
  filename = 'results/market_direction'
  curr_md_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
  df_out = market_direction.market_direction(curr_md_filename)

  # Run Screen Comparer
  comparer = ScreenComparer()
  filename = 'results/screener_results'
  date = datetime.datetime.utcnow()
  curr_sc_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
  prev_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
  prev_sc_filename = "{}_{}_{}_{}.csv".format(filename, prev_date.year, prev_date.month, prev_date.day)
  comparer.compare_screen("s3://elasticbeanstalk-us-east-2-120595873264/{}".format(curr_sc_filename),"s3://elasticbeanstalk-us-east-2-120595873264/{}".format(prev_sc_filename))

if __name__ == "__main__":
  main()


  
