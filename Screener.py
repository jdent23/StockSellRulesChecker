from finviz.screener import Screener
import nest_asyncio
import finviz

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)

import datetime
import stockquotes
import pandas as pd
import tqdm
nest_asyncio.apply()

import time
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
from shutil import copyfile

class StockScreener:

  @staticmethod
  def initial_screen():
    eps_5year_over0pct = False
    eps_qoq_over0pct = True
    eps_yoy_over0pct = True
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
  def moving_average(yahoo_df, days, delta=0):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max() - datetime.timedelta(days=delta)
      end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
      
      df_days = df[df['Date'] >= end_date]
      df_days = df_days[df_days['Date'] <= curr_date]
      return round(float(df_days['Close'].mean()), 0)

  @staticmethod
  def moving_average_volume(yahoo_df, days, delta=0):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max() - datetime.timedelta(days=delta)
      end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
      
      df_days = df[df['Date'] >= end_date]
      df_days = df_days[df_days['Date'] <= curr_date]
      return round(float(df_days['Volume'].mean()), 0)

  @staticmethod
  def relative_strength(yahoo_df, sp500_df, days=65):
    closes = yahoo_df['Close'].tolist()
    closes.reverse()

    sp_closes = sp500_df['Close'].tolist()
    sp_closes.reverse()

    # Calculate Relative Performance Indicator
    RPs = []
    for i in range(days):
      RPs.append((closes[i]/ sp_closes[i])*100)

    # Calcuate SMA of RPs
    SMA = sum(RPs)/len(RPs)

    # Calculate Mansfield Relative Performance indicator
    MRP = ((RPs[0]/SMA) - 1) * 100
    return round(MRP,0)

  @staticmethod
  def percent_diff(current, ref):
    if current == ref:
        return 1.0
    try:
        return (abs(current - ref) / ref)
    except ZeroDivisionError:
        return 0

  @staticmethod
  def week52_low_high(yahoo_df):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max()
      end_date = curr_date - datetime.timedelta(days=365)
      
      df_days = df[df['Date'] >= end_date]
      return round(float(df_days['Close'].max()),0), round(float(df_days['Close'].min()),0)

  @staticmethod
  def SMA200_slope_positive_rule(yahoo_df, ticker, days=21):
    for day in range(days):
      curr_avg = StockScreener.moving_average(yahoo_df, days=200, delta=day)
      prev_avg = StockScreener.moving_average(yahoo_df, days=200, delta=day+1)
      if curr_avg >= prev_avg:
        continue
      else:
        return False, 0.0, 0.0
    return True, StockScreener.percent_diff(curr_avg,prev_avg), 2**5

  @staticmethod
  def screen_stock(stock):
    try:
      screened_stocks = {}

      if stock["Ticker"] == "":
        return

      finviz_stats = finviz.get_stock(stock['Ticker'])
      prev_close = round(float(finviz_stats['Prev Close'].replace("$","")),0)

      screened_stocks[stock['Ticker']] = {}
      
      try:
        yahoo_df = pdr.get_data_yahoo(stock['Ticker'], interval = "1d", threads= False)
      except:
        return
      try:
        sp500_df = pdr.get_data_yahoo("^GSPC", interval = "1d", threads= False)
      except:
        return

      SMA200_value = StockScreener.moving_average(yahoo_df, days=200)
      SMA150_value = StockScreener.moving_average(yahoo_df, days=150)
      SMA50_value = StockScreener.moving_average(yahoo_df, days=50)
      RS_value = StockScreener.relative_strength(yahoo_df, sp500_df)
      SMA50_volume_value = StockScreener.moving_average_volume(yahoo_df, days=50)

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

      week52_high, week52_low = StockScreener.week52_low_high(yahoo_df)
      
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
      if SMA50_value > SMA150_value:
          SMA50_greater_SMA150_rule = True
          n_value = 2**12
      else:
          SMA50_greater_SMA150_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(SMA50_value,SMA150_value)
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule'] = SMA50_greater_SMA150_rule
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule_nvalue'] = round(n_value,0)

      # 150d MA greater than 200d MA
      if SMA150_value > SMA200_value:
          SMA150_greater_SMA200_rule = True
          n_value = 2**11
      else:
          SMA150_greater_SMA200_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(SMA150_value,SMA200_value)
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule'] = SMA150_greater_SMA200_rule
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule_nvalue'] = round(n_value,0)

      # 52 week high low span rule
      if 0.75*week52_high > 1.25*week52_low:
          week52_span_rule = True
          n_value = 2**10
      else:
          week52_span_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(0.75*week52_high, 1.25*week52_low)
      screened_stocks[stock['Ticker']]['week52_span_rule'] = week52_span_rule
      screened_stocks[stock['Ticker']]['week52_span_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['week52_span_rule_nvalue'] = round(n_value,0)

      # RS Value > 1.0 rule:
      if RS_value > 1.0:
        rs_value_rule = True
        n_value = 2**9
      else:
        rs_value_rule = False
        n_value = 0.0
      score = StockScreener.percent_diff(RS_value,1.0)

      screened_stocks[stock['Ticker']]['rs_value_rule'] = rs_value_rule
      screened_stocks[stock['Ticker']]['rs_value_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['rs_value_rule_nvalue'] = round(n_value,0)

      # Liquidity Rule
      if SMA50_value*SMA50_volume_value <= 20e6:
        liquidity_rule = False
        n_value = 0
      else:
        liquidity_rule = True
        n_value = 2**8
      screened_stocks[stock['Ticker']]['liquidity_rule'] = liquidity_rule
      screened_stocks[stock['Ticker']]['liquidity_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['liquidity_rule_nvalue'] = round(n_value,0)

      # Close above 52 week high - 25%
      if prev_close > 0.75*week52_high:
          close_above_52weekhigh_rule = True
          n_value = 2**7
      else:
          close_above_52weekhigh_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(prev_close, 0.75*week52_high)
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule'] = close_above_52weekhigh_rule
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule_nvalue'] = round(n_value,0)

      # Price greater than $10 rule
      if prev_close < 10:
        prev_close_rule = False
        n_value = 0.0
      else:
        prev_close_rule = True
        n_value = 2**6
      screened_stocks[stock['Ticker']]['prev_close_rule'] = prev_close_rule
      screened_stocks[stock['Ticker']]['prev_close_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['prev_close_rule_nvalue'] = round(n_value,0)


      # Positive 200d MA
      SMA200_slope_rule, score, n_value = StockScreener.SMA200_slope_positive_rule(yahoo_df, ticker=stock['Ticker'], days=21)
      screened_stocks[stock['Ticker']]['SMA200_slope_rule'] = SMA200_slope_rule
      screened_stocks[stock['Ticker']]['SMA200_slope_rul_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['SMA200_slope_rul_nvalue'] = round(n_value,0)

      # Institutional Ownership > 5%
      if 0.05 <= inst_own:
        inst_ownership_rule = True
        score = score = StockScreener.percent_diff(inst_own, 0.05)
        n_value = 2**4
      else:
        inst_ownership_rule = False
        score = 0.0
        n_value = 0.0
      screened_stocks[stock['Ticker']]['inst_ownership_rule'] = inst_ownership_rule
      screened_stocks[stock['Ticker']]['inst_ownership_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['inst_ownership_rule_nvalue'] = round(n_value,0)


      # Close above 50d MA
      if prev_close > SMA50_value:
          close_greater_SMA50_rule = True
          n_value = 2**3
      else:
          close_greater_SMA50_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(prev_close,SMA50_value)
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule'] = close_greater_SMA50_rule
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule_nvalue'] = round(n_value,0)


      # Sales QoQ Yearly > 25% rule
      if Sales_QoQ_percent >= .25:
        sales_QoQ_yearly_rule = True
        n_value = 2**2
      else:
        sales_QoQ_yearly_rule = False
        n_value = 0.0
      score = StockScreener.percent_diff(Sales_QoQ_percent, 0.25)
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule'] = sales_QoQ_yearly_rule
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule_score'] = round(n_value*score,0)
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule_nvalue'] = round(n_value,0)


      # EPS QoQ Yearly > 18% rule
      if EPS_QoQ_percent >= .18:
        eps_QoQ_yearly_rule = True
        n_value = 2**1
      else:
        eps_QoQ_yearly_rule = False
        n_value = 0

      score = StockScreener.percent_diff(EPS_QoQ_percent, 0.18)
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule'] = eps_QoQ_yearly_rule
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule_score'] = round(score*n_value,0)
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule_nvalue'] = round(n_value,0)

      return screened_stocks
    except:
      return {}

  @staticmethod
  def cleanup_screen(df_out):

    primary_rules = ['SMA50_greater_SMA150_rule', 'SMA150_greater_SMA200_rule', 'week52_span_rule', 
                     'rs_value_rule', 'liquidity_rule', 'close_above_52weekhigh_rule', 'prev_close_rule', 
                     'SMA200_slope_rule', 'inst_ownership_rule', 'close_greater_SMA50_rule', 'sales_QoQ_yearly_rule'
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

    df_out = df_out[df_out['Primary Passed Tests']>5]
    return df_out

  @staticmethod
  def main_screen(stock_list):

    # results = []
    # for stock in tqdm(stock_list, total=len(stock_list.data)):
    #   try:
    #     result = StockScreener.screen_stock(stock)
    #     results.append(result)
    #   except:
    #     continue

    # Digital Ocean Does Not Support Multiprocessing
    results = process_map(StockScreener.screen_stock, stock_list, max_workers=8)

    screened_stocks = {}
    for d in results:
      if d is not None:
        screened_stocks.update(d)
      
    output_list = []
    for stock in screened_stocks.keys():
        cols = ["Ticker"] + list(screened_stocks[stock].keys())
        temp_list = []
        temp_list.append(stock)
        for rule in screened_stocks[stock].keys():
            temp_list.append(screened_stocks[stock][rule])
        output_list.append(temp_list)
            
    df_out = pd.DataFrame(output_list,columns=cols)
    return df_out

  @staticmethod
  def score_stocks(df):
    cols = df.columns
    score_cols = [col for col in cols if "score" in col]
    df['Lwowski Rating'] = (df[list(score_cols)]).sum(1)

    nvalue_cols = [col for col in cols if "nvalue" in col]
    df['N-Value Rating'] = (df[list(nvalue_cols)]).sum(1)
    df = df.sort_values(by=['N-Value Rating', 'Lwowski Rating'], ascending=False)

    return df

  def screen(self):
    print("Starting Screener")
    stock_list = StockScreener.initial_screen()
    
    print("Initial Screen Done")
    df_out = StockScreener.main_screen(stock_list)

    print("Main Screen Done")
    df_out = StockScreener.cleanup_screen(df_out)

    print("Scoring the Stocks")
    df_out = StockScreener.score_stocks(df_out)
    return df_out

if __name__ == "__main__":
  screener = StockScreener()
  df_final = screener.screen()
  date = datetime.utcnow()
  filename = 'results/screener_results'
  curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
  df_final.to_csv(curr_filename)

  
