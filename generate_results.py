from Screener import StockScreener
from ScreenComparer import ScreenComparer
from datetime import datetime, timedelta

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate

filename = 'results/screener_results'
compare_filename = 'results/screener_comparison.csv'

print("Running Screener")
screener = StockScreener()
df_final = screener.screen()

date = datetime.now()
curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
df_final.to_csv(curr_filename)

prev_date = prev_weekday(date)
prev_filename = "{}_{}_{}_{}.csv".format(filename, prev_date.year, prev_date.month, prev_date.day)

comparer = ScreenComparer()
comparer.compare_screen(prev_filename, curr_filename)