source ~/.venvs/flask/bin/activate
cd /home/jonlwowski012/StockSellRulesChecker
python generate_results.py
git add results/screener_results*.csv
git add results/screener_comparison.csv
git add results/market_direction*.csv
git commit -m "Auto Uploading CSV files"
git push