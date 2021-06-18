Downloading and Building the Software:
In terminal:
1. Navigate to the folder where you would like to clone the FULLSTACK-APP repo into.
2. Type "git clone https://github.com/ColeMaurer/FULLSTACK-APP.git"
3. Build and populate the database:
*** You may need to install python packages prior to running these scripts ***
*** These are listed at the top of the files, or just trying to run them will result in errors that tell you what is 
   needed. Make sure to install 'newtulipy' as tulipy is not supported for py 3.9.
  - type "python3 Create_db.py"
  - type "python3 Populate_Stocks.py"
  - type "python3 Populate_Prices.py"
4. Next step is to fire up the user interface:
  - Command line to start up app: uvicorn Main:app --reload  --- Remember the capital M!!
  - Then enter this address into a web browser: http://localhost:8000/ to get to the UI.

Navigating the UI:
  Search for stocks by filtering the main list - this is in the top left of the page. They can be sorted
by new closing highs or lows. Not necessary, but it is recommended to search for stocks meeting
one of these criteria before applying a trading strategy.
  Click on stocks of interest and add them to a trading strategy if they look like a good play
based on price action and the Tradingview chart. To add them to a strategy click through the form on the
bottom left of the chart.
After adding a few to the strategy through the UI the database should have the stocks in the stock_strategy table. 
These are used in the opening_range_breakout/down.py scripts.

CRON JOBS to run app: (I believe windows has similar scheduling stuff)
1. This job runs at 10pm daily and updates the stock list in the database. It outputs the print statements to the populate.log file:
0 22 * * * /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/Cole/Documents/Finances/Algo_Trading/FULLSTACK-APP/Populate_Stocks.py >> /Users/Cole/Documents/Finances/Algo_Trading/populate.log 2>&1

2. This job runs at 10pm daily and updates the stock prices in the database. It outputs the print statements to the populate.log file:
0 22 * * * /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/Cole/Documents/Finances/Algo_Trading/FULLSTACK-APP/Populate_Prices.py >> /Users/Cole/Documents/Finances/Algo_Trading/populate.log 2>&1

3. This job runs every minute of every hour between 8am and 4pm during the week Mon-Fri and run the opening_range_breakout script:
*/1 8-16 * * 1-5 /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/Cole/Documents/Finances/Algo_Trading/FULLSTACK-APP/opening_range_breakout.py >> trade.log 2>&1

4. This job runs every minute of every hour between 8am and 4pm during the week Mon-Fri and run the opening_range_breakdown script:
*/1 8-16 * * 1-5 /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/Cole/Documents/Finances/Algo_Trading/FULLSTACK-APP/opening_range_breakdown.py >> trade.log 2>&1

** Resources:
Alpaca Github:
https://github.com/alpacahq/alpaca-trade-api-python
Examples:
https://github.com/alpacahq/alpaca-trade-api-python/tree/master/examples
Long-Short Strategy:
https://github.com/alpacahq/alpaca-trade-api-python/blob/master/examples/long-short.py

Part Time Larry's Youtube Tutorial for full app development:
https://www.youtube.com/playlist?list=PLvzuUVysUFOuoRna8KhschkVVUo2E2g6G
