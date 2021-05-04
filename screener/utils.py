import datetime

def percent_diff(current, ref):
    if current == ref:
        return 1.0
    try:
        return (abs(current - ref) / ref)
    except ZeroDivisionError:
        return 0

def moving_average(yahoo_df, days, delta=0):
    df = yahoo_df.reset_index()
    curr_date = df['Date'].max() - datetime.timedelta(days=delta)
    end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
    
    df_days = df[df['Date'] >= end_date]
    df_days = df_days[df_days['Date'] <= curr_date]
    return round(float(df_days['Close'].mean()), 2)

def moving_average_volume(yahoo_df, days, delta=0):
    df = yahoo_df.reset_index()
    curr_date = df['Date'].max() - datetime.timedelta(days=delta)
    end_date = curr_date - datetime.timedelta(days=days) - datetime.timedelta(days=delta)
    
    df_days = df[df['Date'] >= end_date]
    df_days = df_days[df_days['Date'] <= curr_date]
    return round(float(df_days['Volume'].mean()), 0)

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

def week52_low_high(yahoo_df):
    df = yahoo_df.reset_index()
    curr_date = df['Date'].max()
    end_date = curr_date - datetime.timedelta(days=365)

    df_days = df[df['Date'] >= end_date]
    return round(float(df_days['Close'].max()),0), round(float(df_days['Close'].min()),2)