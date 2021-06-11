Command line to start up app: uvicorn Main:app --reload  --- Remember the capital M!!
    python3 -m uvicorn Main:app --reload   --- debugging effort
Then enter this address into a web browser: http://localhost:8000/ to get to the UI.

Strategy Development:
Skim filters on webapp and determine stocks to trade

After coming up with a list, we want to store them in our database
    in new tables.

Alpaca Github:
https://github.com/alpacahq/alpaca-trade-api-python
Examples:
https://github.com/alpacahq/alpaca-trade-api-python/tree/master/examples
Long-Short Strategy:
https://github.com/alpacahq/alpaca-trade-api-python/blob/master/examples/long-short.py

CRON JOBS to run app:
0 22 * * * /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/Cole/Documents/Finances/Algo_Trading/FULLSTACK-APP/Populate_db.py >> /Users/Cole/Documents/Finances/Algo_Trading/populate.log 2>&1

#*/1 * * * * /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/Cole/Documents/Finances/Algo_Trading/FULLSTACK-APP/opening_range_breakout.py >> trade.log 2>&1


Index.html indicators debugging effort: removed the following:

{% if indicator_values[stock.symbol] %}
  <td>{{ indicator_values[stock.symbol].close }}</td>
  {% if indicator_values[stock.symbol].rsi_14 %}
    <td>{{ indicator_values[stock.symbol].rsi_14|round(2) }}</td>
  {% else %}
    <td>N/A</td>
  {% endif %}
  {% if indicator_values[stock.symbol].sma_20 %}
    <td>{{ indicator_values[stock.symbol].sma_20|round(2) }}</td>
  {% else %}
    <td>N/A</td>
  {% endif %}
  {% if indicator_values[stock.symbol].sma_50 %}
    <td>{{ indicator_values[stock.symbol].sma_50|round(2) }}</td>
  {% else %}
    <td>N/A</td>
  {% endif %}
{% endif %}
