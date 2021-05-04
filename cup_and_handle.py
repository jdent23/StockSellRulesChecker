from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)
import datetime
import matplotlib.pyplot as plt 
from tqdm import tqdm
import numpy as np
import pandas as pd
import math

def find_p1_and_b5(yahoo_df, interval, bars=20):
    if interval == "1wk":
        interval_multipler = 7
    else:
        interval_multipler = 1

    curr_time = yahoo_df['Date'].max()
    end_date = curr_time - datetime.timedelta(days=bars*interval_multipler)
    date_df = yahoo_df[yahoo_df['Date'] > end_date]
    p1 = date_df['High_Log'].max()
    b5 = date_df[date_df['High_Log'] == p1]['Date'].values[0]
    return p1, b5

def find_b0(yahoo_df, p1, b5, interval):
    if interval == "1wk":
        interval_multipler = 7
    else:
        interval_multipler = 1

    date_df = yahoo_df[yahoo_df['Date'] < b5]
    date_df = date_df[date_df['High_Log'] > p1]

    b0 = date_df['Date'].max() + datetime.timedelta(days=1*interval_multipler)
    date_df = date_df[date_df['Date'] == date_df['Date'].max()]
    b0 = date_df['Date'].values[0]
    return b0

def find_p0(yahoo_df, b0, b5):
    date_df = yahoo_df[yahoo_df['Date'] > b0]
    date_df = date_df[date_df['Date'] < b5]
    p0 = date_df['High_Log'].min()
    p0_date = date_df[date_df['High_Log'] == p0]['Date'].values[0]
    return p0, p0_date

def find_ls_and_bs(yahoo_df, p0, p1, b0, b5):
    diff_p = p1 - p0
    diff_single_p = diff_p / 5
    l1 = p0 + diff_single_p
    l2 = l1 + diff_single_p
    l3 = l2 + diff_single_p
    l4 = l3 + diff_single_p

    diff_b = b5 - b0
    diff_single_b = diff_b / 5
    b1 = b0 + diff_single_b
    b2 = b1 + diff_single_b
    b3 = b2 + diff_single_b
    b4 = b3 + diff_single_b

    return l1, l2, l3, l4, b1, b2, b3, b4 

def ensure_closing_price_blank(yahoo_df, l2, l3, b1, b2, b3, b4, p1):
        yellow_box_df_1 = yahoo_df[yahoo_df['Date'] > b1]
        yellow_box_df_1 = yellow_box_df_1[yellow_box_df_1['Date'] < b4]
        yellow_box_df_1 = yellow_box_df_1[yellow_box_df_1['Close_Log'] > l3]
        yellow_box_df_1 = yellow_box_df_1[yellow_box_df_1['Close_Log'] < p1]

        if len(yellow_box_df_1['Close_Log'].values.tolist()) > 0:
            return False

        yellow_box_df_2 = yahoo_df[yahoo_df['Date'] > b2]
        yellow_box_df_2 = yellow_box_df_2[yellow_box_df_2['Date'] < b3]
        yellow_box_df_2 = yellow_box_df_2[yellow_box_df_2['Close_Log'] > l2]
        yellow_box_df_2 = yellow_box_df_2[yellow_box_df_2['Close_Log'] < l3]

        if len(yellow_box_df_2['Close_Log'].values.tolist()) > 0:
            return False
        return True

def ensure_lows_in_boxes(yahoo_df, l1, l2, b0, b1, b2, b3, b4, b5, p0):
    # Check Yellow Boxes
    diff = (l2-l1)*(2./3.)
    yellow_box_df_1 = yahoo_df[yahoo_df['Date'] > b0]
    yellow_box_df_1 = yellow_box_df_1[yellow_box_df_1['Date'] < b1]
    yellow_box_df_1 = yellow_box_df_1[yellow_box_df_1['Low_Log'] > l1]
    yellow_box_df_1 = yellow_box_df_1[yellow_box_df_1['Low_Log'] < l1+diff]

    diff = (l2-l1)*(2./3.)
    yellow_box_df_2 = yahoo_df[yahoo_df['Date'] < b5]
    yellow_box_df_2 = yellow_box_df_2[yellow_box_df_2['Date'] > b4]
    yellow_box_df_2 = yellow_box_df_2[yellow_box_df_2['Low_Log'] > l1]
    yellow_box_df_2 = yellow_box_df_2[yellow_box_df_2['Low_Log'] < l1+diff]

    print(len(yellow_box_df_1['Low_Log'].values.tolist()), len(yellow_box_df_2['Low_Log'].values.tolist()))
    if len(yellow_box_df_1['Low_Log'].values.tolist()) > 0 and len(yellow_box_df_2['Low_Log'].values.tolist()) > 0:
        return True

    # Check Cyan Boxes
    diff = (l1-p0)*(2./3.)
    cyan_box_df_1 = yahoo_df[yahoo_df['Date'] > b1]
    cyan_box_df_1 = cyan_box_df_1[cyan_box_df_1['Date'] < b2]
    cyan_box_df_1 = cyan_box_df_1[cyan_box_df_1['Low_Log'] > p0]
    cyan_box_df_1 = cyan_box_df_1[cyan_box_df_1['Low_Log'] < p0+diff]

    diff = (l1-p0)*(2./3.)
    cyan_box_df_2 = yahoo_df[yahoo_df['Date'] > b3]
    cyan_box_df_2 = cyan_box_df_2[cyan_box_df_2['Date'] < b4]
    cyan_box_df_2 = cyan_box_df_2[cyan_box_df_2['Low_Log'] > p0]
    cyan_box_df_2 = cyan_box_df_2[cyan_box_df_2['Low_Log'] < p0+diff]

    if len(cyan_box_df_1['Low_Log'].values.tolist()) > 0 and len(cyan_box_df_2['Low_Log'].values.tolist()) > 0:
        return True
    
    # If Not in Boxes False
    return False

def ensure_handle_above_l2(yahoo_df, l2, b5):
    date_df = yahoo_df[yahoo_df['Date'] >= b5]
    if date_df['Low_Log'].min() > l2:
        return True
    else:
        return False

def ensure_cup_period_long_enough(b0,b5):
    difference = (b5 - b0)
    days = difference.astype('timedelta64[D]')
    days / np.timedelta64(1, 'D')
    if days >= 30:
        return True
    return False

def daterange(start_date, end_date):
    print(end_date, start_date)
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

df = pd.read_csv('frontend/results/screener_results_2021_4_28.csv')
df = df[df['N-Value Rating'] > 7990]
df.set_index(['Unnamed: 0'], inplace=True)
df.index.name=None
df.reset_index(inplace=True, drop=True)
df = df.sort_values(by=['N-Value Rating', 'Lwowski Rating'], ascending=False)

# Choose interval "1d" or "1wk"
interval = "1d"
tickers = df['Ticker'].values.tolist()
max_weeks = 30
#tickers = ['CMD']
end_date = datetime.datetime.now() #datetime.datetime.strptime("2021-03-15", '%Y-%m-%d') 

for ticker in tqdm(tickers):
    try:
        print(ticker)
        yahoo_df = pdr.get_data_yahoo([ticker], interval = interval, threads= False)
        yahoo_df.reset_index(inplace=True)
        start_date = end_date - datetime.timedelta(days=(max_weeks)*7)

        yahoo_df = yahoo_df[yahoo_df['Date'] > start_date]
        yahoo_df = yahoo_df[yahoo_df['Date'] < end_date]

        # Calculate Logs (Step 1)
        yahoo_df['High_Log'] = np.log(yahoo_df['High'])
        yahoo_df['Low_Log'] = np.log(yahoo_df['Low'])
        yahoo_df['Close_Log'] = np.log(yahoo_df['Close'])

        # Find P1 and B5 (Step 2)
        p1, b5 = find_p1_and_b5(yahoo_df, interval=interval)

        # Find B0 (Step 3)
        b0 = find_b0(yahoo_df, p1, b5, interval=interval)

        # Find P0 (Step 4)
        p0, p0_date = find_p0(yahoo_df, b0, b5)

        # Define L1, L2, L3, L4 and B1, B2, B3, B4 (Step 5)
        l1, l2, l3, l4, b1, b2, b3, b4 = find_ls_and_bs(yahoo_df, p0, p1, b0, b5)
        
        # Ensure Closing Price Blank (Step 6)
        closing_price_blank = ensure_closing_price_blank(yahoo_df, l2, l3, b1, b2, b3, b4, p1)
        if not closing_price_blank:
            print("Failed Closing Price Blank: ", ticker)
            continue

        # Ensure low is in both cyan or both yellow boxes (Step 7)
        lows_in_boxes = ensure_lows_in_boxes(yahoo_df, l1, l2, b0, b1, b2, b3, b4, b5, p0)
        if not lows_in_boxes:
            print("Failed Lows in Boxes: ", ticker)
            continue

        # Ensure handle is above l2 (Step 8)
        handle_above_l2 = ensure_handle_above_l2(yahoo_df, l2, b5)
        if not handle_above_l2:
            print("Failed Handle above l2: ", ticker)
            continue

        # Ensure Cup Period Greater than 30 bars (Step 9)
        cup_period_long_enough = ensure_cup_period_long_enough(b0,b5)
        if not cup_period_long_enough:
            print("Failed cup period length: ", ticker)
            continue

        b0_dt = (b0 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        b2_dt = (b2 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        b3_dt = (b3 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        b5_dt = (b5 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        t0 = (b2_dt+b3_dt)/2
        a = (math.exp(p1) - math.exp(p0))/((b0_dt-t0)**6)
        
        y = []
        x = []
        for t in range(int(b0_dt), int(b5_dt), 60*60*24):
            date_x = datetime.datetime.utcfromtimestamp(t)
            date_y = min(math.exp(p1), a*((t-t0)**6)+0.99*(math.exp(p0)))
            x.append(date_x)
            y.append(date_y)
            
        plt.figure()
        plt.plot(yahoo_df['Date'], yahoo_df['Close'])
        plt.plot(x,y)
        plt.savefig("{}_CnH.png".format(ticker))
        # plt.plot(yahoo_df['Date'], yahoo_df['Close_Log'])
        # plt.scatter(b5, p1)
        # plt.scatter(b0, p1)
        # plt.scatter(p0_date, p0)
        # plt.scatter([b1, b2, b3, b4], [p0,p0,p0,p0])
        # plt.scatter([b0, b0, b0, b0], [l1, l2, l3, l4])
        #plt.show()
    except:
       continue

