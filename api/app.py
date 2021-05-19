from flask import Flask, render_template
import pandas as pd
from flask_apscheduler import APScheduler
import sys
from datetime import datetime, timedelta
import pathlib
from flask import send_file, send_from_directory, safe_join, abort
import os
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

app = Flask(__name__)
application = app # For beanstalk

date = datetime.utcnow()
filename = 'results/screener_results'
compare_filename = 'results/screener_comparison.csv'
market_direction_filename = 'results/market_direction'
cnh_pattern_filename = 'results/cup_and_handle'
pp_pattern_filename = 'results/pocket_pivot'

def read_from_s3_csv(curr_filename):
    output_file = 's3://elasticbeanstalk-us-east-2-120595873264/{}'.format(curr_filename)
    df = pd.read_csv(output_file)
    return df

@app.route("/chart_patterns")
def show_chart_patterns():
    date = datetime.utcnow()
    curr_filename = "{}_{}_{}_{}.csv".format(cnh_pattern_filename, date.year, date.month, date.day)
    try:
        data_cnh = read_from_s3_csv(curr_filename)
    except:
        date = datetime.utcnow() - timedelta(days=1)
        curr_filename = "{}_{}_{}_{}.csv".format(cnh_pattern_filename, date.year, date.month, date.day)
        data_cnh = read_from_s3_csv(curr_filename)
    data_cnh = data_cnh[data_cnh['Cup and Handle Pattern'] == True]

    curr_filename = "{}_{}_{}_{}.csv".format(pp_pattern_filename, date.year, date.month, date.day)
    try:
        data_pp = read_from_s3_csv(curr_filename)
    except:
        date = datetime.utcnow() - timedelta(days=1)
        curr_filename = "{}_{}_{}_{}.csv".format(pp_pattern_filename, date.year, date.month, date.day)
        data_pp = read_from_s3_csv(curr_filename)
    data_pp = data_pp.drop(['Unnamed: 0'], axis=1)
    data_pp = data_pp[data_pp['Pocket Pivot Pattern'] == True]

    data = pd.merge(data_cnh, data_pp, on='Ticker', how='outer')
    data = data.fillna(False)
    print(data)
    
    data =  data.style.apply(color_passing_tests).render()
    return render_template('chart_patterns.html',tables=[data], date=date, titles = ['Chart Patterns'])

@app.route("/rules")
def show_rules():
    return render_template('rules.html')

@app.route("/comparison")
def show_comparison():
    date = datetime.utcnow()
    data = read_from_s3_csv(compare_filename)
    data = data.drop_duplicates()
    different_cols = [col for col in data.columns if "Different?" in col]
    data = data.drop(['Ticker Entered/Exited Rule?', 'N-Value Rating Entered/Exited Rule?'] + different_cols, axis=1)
    #data.set_index(['Unnamed: 0'], inplace=True)
    data.index.name=None
    data =  data.style.apply(color_changing_tests).render()
    fname = pathlib.Path(compare_filename)
    date = datetime.utcnow()
    return render_template('comparison.html',tables=[data], date=date, titles = ['Stock Screener Comparison'])

@app.route("/")
def show_tables():
    date = datetime.utcnow()
    curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)

    try:
        data = read_from_s3_csv(curr_filename)
    except:
        date = datetime.utcnow() - timedelta(days=1)
        curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
        data = read_from_s3_csv(curr_filename)

    data = data.drop_duplicates(subset='Ticker', keep="last")
    data = data[data['N-Value Rating'] > 8178.]
    #data.set_index(['Unnamed: 0'], inplace=True)
    data.index.name=None
    data.reset_index(inplace=True, drop=True)

    cols = data.columns
    cols_first_rules = [col for col in cols if "(1st)" in col]
    cols_second_rules = [col for col in cols if "(2nd)" in col]
    cols_patterns = [col for col in cols if "Pattern" in col]
    cols_nvalue = [col for col in cols if "nvalue" in col]
    cols_score = [col for col in cols if "score" in col]
    cols_order = ['Ticker', 'N-Value Rating', 'Lwowski Rating', 'Primary Passed Tests', 'Secondary Passed Tests'] + cols_first_rules + cols_second_rules + cols_patterns
    remaining_cols = list(set(cols) - set(cols_order) -set(cols_nvalue) - set(cols_score))
    data = data[cols_order+remaining_cols+cols_nvalue+cols_score]
    data = data.sort_values(by=['N-Value Rating', 'Lwowski Rating'], ascending=False)
    data.to_csv(curr_filename)
    data =  data.style.apply(color_passing_tests).render()

    fname = pathlib.Path(curr_filename)
    try:
        date = datetime.utcnow()
        curr_filename = "{}_{}_{}_{}.csv".format(market_direction_filename, date.year, date.month, date.day)
        market_direction_data = read_from_s3_csv(curr_filename)
    except:
        date = datetime.utcnow() - timedelta(days=1)
        curr_filename = "{}_{}_{}_{}.csv".format(market_direction_filename, date.year, date.month, date.day)
        market_direction_data = read_from_s3_csv(curr_filename)
    
    num_true_sma21 = market_direction_data['SMA21_Greater_SMA50_Rule'].values.sum()
    num_true_slope = market_direction_data['SMA50_Positive_Slope_Rule'].values.sum()
    
    if num_true_sma21 < 2:
        market_direction = "Downward"
        color = "red"
    elif num_true_slope == 1:
        market_direction = "Mixed"
        color = "orange"
    elif num_true_slope == 0:
        market_direction = "Downward"
        color = "red"
    else:
        market_direction = "Upward"
        color = "green"

    #market_direction_data.set_index(['Unnamed: 0'], inplace=True)
    market_direction_data.index.name=None
    market_direction_data.reset_index(inplace=True, drop=True)
    market_direction_data =  market_direction_data.style.apply(color_passing_tests).render()

    return render_template('view.html',tables=[market_direction_data, data], date=date, titles = ['Market Direction', 'Stock Screener Results'], market_direction=market_direction, color=color)

def color_changing_tests(s):
    out = []
    for idx,v in enumerate(s):
        if v == "Entered Rule":
            out.append('background-color: #77dd77')
        elif v == "Exited Rule":
            out.append('background-color: #ff5252')
        else:
            if idx % 2 == 0:
                out.append('background-color: #eee')
            else:
                out.append('background-color: #fff')
    return out

def color_passing_tests(s):
    out = []
    for idx,v in enumerate(s):
        if type(v) == bool and v:
            out.append('background-color: #77dd77')
        else:
            if idx % 2 == 0:
                out.append('background-color: #eee')
            else:
                out.append('background-color: #fff')
    return out

#background process happening without any refreshing
@app.route('/export_table')
def export_table():
    date = datetime.utcnow()
    curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
    print("Sending CSV: ", curr_filename)
    safe_path = safe_join(curr_filename)
    try:
        return send_file(safe_path, as_attachment=True)
    except FileNotFoundError:
        abort(404)

#background process happening without any refreshing
@app.route('/export_comparison_table')
def export_comparison_table():
    print("Sending CSV: ", compare_filename)
    safe_path = safe_join(compare_filename)
    try:
        return send_file(compare_filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

#background process happening without any refreshing
@app.route('/export_chart_patterns_table')
def export_chart_patterns_table():
    print("Sending CSV: ", cnh_pattern_filename)
    safe_path = safe_join(cnh_pattern_filename)
    try:
        return send_file(cnh_pattern_filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

    print("Sending CSV: ", pp_pattern_filename)
    safe_path = safe_join(pp_pattern_filename)
    try:
        return send_file(pp_pattern_filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == "__main__":
    app.run(threaded=True)
    