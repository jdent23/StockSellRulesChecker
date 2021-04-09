#!/bin/bash

sudo apt install cron
sudo systemctl enable cron

0 3 * * * /home/jonlwowski012/StockSellRulesChecker/upload_data_cron_job.sh