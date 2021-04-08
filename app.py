from flask import *
import pandas as pd
from flask_apscheduler import APScheduler
from Screener import StockScreener
from ScreenComparer import ScreenComparer
import sys
from datetime import datetime, timedelta
import pathlib
from flask import send_file, send_from_directory, safe_join, abort
import os

app = Flask(__name__)
date = datetime.now()
filename = 'screener_results'
compare_filename = 'screener_comparison.csv'

@app.route("/rules")
def show_rules():
    return render_template('rules.html')

@app.route("/comparison")
def show_comparison():
    data = pd.read_csv(compare_filename)

    different_cols = [col for col in data.columns if "Different?" in col]
    data = data.drop(['Ticker Entered/Exited Rule?', 'N-Value Rating Entered/Exited Rule?'] + different_cols, axis=1)
    data.set_index(['Unnamed: 0'], inplace=True)
    data.index.name=None
    data =  data.style.apply(color_changing_tests).render()
    fname = pathlib.Path(compare_filename)
    date = datetime.now()
    return render_template('comparison.html',tables=[data], date=date, titles = ['Stock Screener Comparison'])

@app.route("/")
def show_tables():
    date = datetime.now()
    curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
    
    if not os.path.filename(curr_filename):
        run_screener()

    data = pd.read_csv(curr_filename)
    data.set_index(['Unnamed: 0'], inplace=True)
    data.index.name=None

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
    date = datetime.now()
    return render_template('view.html',tables=[data], date=date, titles = ['Stock Screener Results'])

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
    date = datetime.now()
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

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate
    
def run_screener():
    print("Running Screener", file=sys.stdout)
    screener = StockScreener()
    df_final = screener.screen()

    date = datetime.now()
    curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
    df_final.to_csv(curr_filename)

    prev_date = prev_weekday(date)
    prev_filename = "{}_{}_{}_{}.csv".format(filename, prev_date.year, prev_date.month, prev_date.day)

    if not os.path.isfile(prev_filename):
        temp = prev_weekday(prev_date)
        prev_filename = "{}_{}_{}_{}.csv".format(filename, temp.year, temp.month, temp.day)
    
    comparer = ScreenComparer()
    comparer.compare_screen(prev_filename, curr_filename)

scheduler = APScheduler()
scheduler.add_job(func=run_screener, args=None, trigger='cron', id='job', hour='6', minute='0')
scheduler.start()

if __name__ == "__main__":
    app.run()
    