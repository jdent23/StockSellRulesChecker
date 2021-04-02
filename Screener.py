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

class StockScreener:

  @staticmethod
  def initial_screen():
    eps_5year_over0pct = False
    eps_qoq_over0pct = True
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
  def moving_average(yahoo_df, days, delta=0):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max() - datetime.timedelta(days=delta)
      end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
      
      df_days = df[df['Date'] >= end_date]
      df_days = df_days[df_days['Date'] <= curr_date]
      return float(df_days['Close'].mean())

  @staticmethod
  def moving_average_volume(yahoo_df, days, delta=0):
      df = yahoo_df.reset_index()
      curr_date = df['Date'].max() - datetime.timedelta(days=delta)
      end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
      
      df_days = df[df['Date'] >= end_date]
      df_days = df_days[df_days['Date'] <= curr_date]
      return float(df_days['Volume'].mean())

  @staticmethod
  def relative_strength(yahoo_df, sp500_df, days=60, smoothing=2):

    ratios = []
    for i in range(days+1,0, -1):
      curr_price = yahoo_df['Close'].tolist()[i]
      prev_price = yahoo_df['Close'].tolist()[i-1]

      curr_price_sp500 = sp500_df['Close'].tolist()[i]
      prev_price_sp500 = sp500_df['Close'].tolist()[i-1]

      if curr_price != prev_price and curr_price_sp500 != prev_price_sp500:
        ratio = ((curr_price-prev_price)/prev_price) / ((curr_price_sp500-prev_price_sp500)/prev_price_sp500)
        ratios.append(ratio)
    pd_ratios = pd.Series(ratios)
    rs = pd_ratios.ewm(span=60, adjust=False).mean().to_list()[-1]
    return rs

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
      return float(df_days['Close'].max()), float(df_days['Close'].min())

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
  def check_double_bottom_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_doublebottom'], table='Performance', order='price')
    except:
      stocks = []

    print("check_double_bottom_chart_pattern: ", stocks)

    df['Double Bottom Chart Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Double Bottom Chart Pattern'] = True
    return df

  @staticmethod
  def check_inverse_head_and_shoulder_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_headandshouldersinv'], table='Performance', order='price')
    except:
      stocks = []

    print("check_inverse_head_and_shoulder_chart_pattern: ", stocks)

    df['Inverse Head and Shoulder Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Inverse Head and Shoulder Pattern'] = True
    return df

  @staticmethod
  def check_multiple_bottom_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_multiplebottom'], table='Performance', order='price')
    except:
      stocks = []

    print("check_multiple_bottom_chart_pattern: ", stocks)

    df['Multiple Bottom Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Multiple Bottom Pattern'] = True
    return df

  @staticmethod
  def check_channel_up_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_channelup'], table='Performance', order='price')
    except:
      stocks = []

    print("check_channel_up_chart_pattern: ", stocks)

    df['Channel Up Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Channel Up Pattern'] = True
    return df

  @staticmethod
  def check_channel_up_strong_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_channelup2'], table='Performance', order='price')
    except:
      stocks = []

    print("check_channel_up_strong_chart_pattern: ", stocks)

    df['Channel Up Strong Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Channel Up Strong Pattern'] = True
    return df

  @staticmethod
  def check_channel_down_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_channeldown'], table='Performance', order='price')
    except:
      stocks = []

    print("check_channel_down_chart_pattern: ", stocks)

    df['Channel Down Strong Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Channel Down Strong Pattern'] = True
    return df

  @staticmethod
  def check_wedge_down_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_wedgedown'], table='Performance', order='price')
    except:
      stocks = []

    print("check_wedge_down_chart_pattern: ", stocks)

    df['Wedge Down Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Wedge Down Pattern'] = True
    return df

  @staticmethod
  def check_wedge_down_strong_chart_pattern(df):
    tickers = df['Ticker'].unique()
    try:
      stocks = Screener(tickers=tickers, filters=['ta_pattern_wedgedown2'], table='Performance', order='price')
    except:
      stocks = []

    print("check_wedge_down_strong_chart_pattern: ", stocks)

    df['Wedge Down Strong Pattern'] = False
    for stock in stocks:
      df.loc[df.Ticker == stock['Ticker'], 'Wedge Down Strong Pattern'] = True
    return df

  @staticmethod
  def screen_stock(stock):
    try:
      screened_stocks = {}

      if stock["Ticker"] == "":
        return

      finviz_stats = finviz.get_stock(stock['Ticker'])
      prev_close = float(finviz_stats['Prev Close'].replace("$",""))

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

      SMA200_percent = float(finviz_stats['SMA200'].replace("%",""))/100
      SMA50_percent = float(finviz_stats['SMA50'].replace("%",""))/100
      volume = float(finviz_stats['Volume'].replace(",",""))

      try:
        EPS_QoQ_percent = float(finviz_stats['EPS Q/Q'].replace("%",""))/100
      except:
        EPS_QoQ_percent = 0

      try:
        Sales_QoQ_percent = float(finviz_stats['Sales Q/Q'].replace("%",""))/100
      except:
        Sales_QoQ_percent = 0

      try:
        inst_own = float(finviz_stats['Inst Own'].replace("%",""))/100
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
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule_score'] = n_value*score
      screened_stocks[stock['Ticker']]['SMA50_greater_SMA150_rule_nvalue'] = n_value

      # 150d MA greater than 200d MA
      if SMA150_value > SMA200_value:
          SMA150_greater_SMA200_rule = True
          n_value = 2**11
      else:
          SMA150_greater_SMA200_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(SMA150_value,SMA200_value)
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule'] = SMA150_greater_SMA200_rule
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule_score'] = n_value*score
      screened_stocks[stock['Ticker']]['SMA150_greater_SMA200_rule_nvalue'] = n_value

      # 52 week high low span rule
      if 0.75*week52_high > 1.25*week52_low:
          week52_span_rule = True
          n_value = 2**10
      else:
          week52_span_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(0.75*week52_high, 1.25*week52_low)
      screened_stocks[stock['Ticker']]['week52_span_rule'] = week52_span_rule
      screened_stocks[stock['Ticker']]['week52_span_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['week52_span_rule_nvalue'] = n_value

      # RS Value > 1.0 rule:
      if RS_value > 1.0:
        rs_value_rule = True
        n_value = 2**9
      else:
        rs_value_rule = False
        n_value = 0.0
      score = StockScreener.percent_diff(RS_value,1.0)

      screened_stocks[stock['Ticker']]['rs_value_rule'] = rs_value_rule
      screened_stocks[stock['Ticker']]['rs_value_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['rs_value_rule_nvalue'] = n_value

      # Liquidity Rule
      if SMA50_value*SMA50_volume_value <= 20e6:
        liquidity_rule = False
        n_value = 0
      else:
        liquidity_rule = True
        n_value = 2**8
      screened_stocks[stock['Ticker']]['liquidity_rule'] = liquidity_rule
      screened_stocks[stock['Ticker']]['liquidity_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['liquidity_rule_nvalue'] = n_value

      # Close above 52 week high - 25%
      if prev_close > 0.75*week52_high:
          close_above_52weekhigh_rule = True
          n_value = 2**7
      else:
          close_above_52weekhigh_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(prev_close, 0.75*week52_high)
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule'] = close_above_52weekhigh_rule
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['close_above_52weekhigh_rule_nvalue'] = n_value

      # Price greater than $10 rule
      if prev_close < 10:
        prev_close_rule = False
        n_value = 0.0
      else:
        prev_close_rule = True
        n_value = 2**6
      screened_stocks[stock['Ticker']]['prev_close_rule'] = prev_close_rule
      screened_stocks[stock['Ticker']]['prev_close_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['prev_close_rule_nvalue'] = n_value


      # Positive 200d MA
      SMA200_slope_rule, score, n_value = StockScreener.SMA200_slope_positive_rule(yahoo_df, ticker=stock['Ticker'], days=21)
      screened_stocks[stock['Ticker']]['SMA200_slope_rule'] = SMA200_slope_rule
      screened_stocks[stock['Ticker']]['SMA200_slope_rul_score'] = n_value*score
      screened_stocks[stock['Ticker']]['SMA200_slope_rul_nvalue'] = n_value

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
      screened_stocks[stock['Ticker']]['inst_ownership_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['inst_ownership_rule_nvalue'] = n_value


      # Close above 50d MA
      if prev_close > SMA50_value:
          close_greater_SMA50_rule = True
          n_value = 2**3
      else:
          close_greater_SMA50_rule = False
          n_value = 0.0
      score = StockScreener.percent_diff(prev_close,SMA50_value)
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule'] = close_greater_SMA50_rule
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['close_greater_SMA50_rule_nvalue'] = n_value


      # Sales QoQ Yearly > 25% rule
      if Sales_QoQ_percent >= .25:
        sales_QoQ_yearly_rule = True
        n_value = 2**2
      else:
        sales_QoQ_yearly_rule = False
        n_value = 0.0
      score = StockScreener.percent_diff(Sales_QoQ_percent, 0.25)
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule'] = sales_QoQ_yearly_rule
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule_score'] = n_value*score
      screened_stocks[stock['Ticker']]['sales_QoQ_yearly_rule_nvalue'] = n_value


      # EPS QoQ Yearly > 18% rule
      if EPS_QoQ_percent >= .18:
        eps_QoQ_yearly_rule = True
        n_value = 2**1
      else:
        eps_QoQ_yearly_rule = False

      score = StockScreener.percent_diff(EPS_QoQ_percent, 0.18)
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule'] = eps_QoQ_yearly_rule
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule_score'] = score*n_value
      screened_stocks[stock['Ticker']]['eps_QoQ_yearly_rule_nvalue'] = n_value

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

    results = []
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
  def chart_pattern_screen(df_out):
    df_passed = StockScreener.check_double_bottom_chart_pattern(df_out)
    df_passed = StockScreener.check_inverse_head_and_shoulder_chart_pattern(df_passed)
    df_passed = StockScreener.check_multiple_bottom_chart_pattern(df_passed)
    df_passed = StockScreener.check_channel_up_chart_pattern(df_passed)
    df_passed = StockScreener.check_channel_up_strong_chart_pattern(df_passed)
    df_passed = StockScreener.check_wedge_down_chart_pattern(df_passed)
    df_passed = StockScreener.check_wedge_down_strong_chart_pattern(df_passed)
    df_passed = StockScreener.check_channel_down_chart_pattern(df_passed)
    return df_passed

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
    print("Cleanup Screen Done")
    df_clean = StockScreener.chart_pattern_screen(df_out)
    print("Scoring the stocks")
    df_scored = StockScreener.score_stocks(df_clean)
    return df_scored

if __name__ == "__main__":
  screener = StockScreener()
  df_final = screener.screen()
  df_final.to_csv("screener_results.csv")

  
