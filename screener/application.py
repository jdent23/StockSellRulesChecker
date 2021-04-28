from flask import Flask, render_template, Response
import pandas as pd
import sys
from datetime import datetime, timedelta
import pathlib
import os
from pytz import utc
from Screener import StockScreener
import logging
logging.basicConfig(filename='/opt/python/log/screener.log', level=logging.DEBUG)

application = Flask(__name__)

date = datetime.utcnow()

@application.route('/worker/screen/', methods = ['POST'])
def run_screener():
    print("Running Screener")
    logging.info("Running Screener")
    screener = StockScreener()
    date = datetime.utcnow()
    filename = 'results/screener_results'
    curr_filename = "{}_{}_{}_{}.csv".format(filename, date.year, date.month, date.day)
    screener.screen(curr_filename)
    logging.info("Screener Done")
    return "Screener Done"

@application.route("/")
def main():
    logging.info("Main")
    return "Main"

if __name__ == "__main__":
    application.run(debug=True)
    