import Config
import alpaca_trade_api as tradeapi

api = tradeapi.REST(Config.API_KEY, Config.SECRET_KEY, Config.API_URL, 'v2')

response = api.close_all_positions()

print(response)