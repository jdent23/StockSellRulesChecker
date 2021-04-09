source ~/.venvs/flask/bin/activate
cd /home/jonlwowski012/StockSellRulesChecker
python generate_results.py
git add screener_results*.csv
git add screener_comparison.csv
git commit -m "Auto Uploading CSV files"
git push