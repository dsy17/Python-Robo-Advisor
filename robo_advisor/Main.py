from alpaca.common import APIError
from alpaca.trading import *
from alpaca.trading.client import *
import userDatabase
import tradingStrategy

# --------------------------------- parameters ---------------------------------

endpoint = "https://paper-api.alpaca.markets"
orders = "{}/v2/orders".format(endpoint)

# backup api connection (if not using database)
API_KEY = "PKXYQU6YMZAGH9BSUPXE"
SECRET_KEY = "AnsaUbgN9C3dx9ZeXdh5Z081nhWiArD9vm8pBf4f"
con = {"APCA-API-KEY-ID": API_KEY, "APCA-API_SECRET_KEY": SECRET_KEY}

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

# get watchlist ID for adding/removing symbols
watchlist_id = 0
get_id = trading_client.get_watchlists()
for i in get_id:
    watchlist_id = i.id
get_watchlist = trading_client.get_watchlist_by_id(watchlist_id)

username = "username1"


# -------------------------------------------------------------------------------

# override backup api connection with new user
def connect(user):
    global username
    global API_KEY
    global SECRET_KEY
    global con
    global trading_client

    username = user

    api, secret = userDatabase.api_connect(user)
    if api != 0:
        API_KEY = str(api)
        SECRET_KEY = str(secret)
        con = {"APCA-API-KEY-ID": API_KEY, "APCA-API_SECRET_KEY": SECRET_KEY}

        trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


# gets all information on account linked to API keys
def retrieve_account():
    account = trading_client.get_account()
    for property_name, value in account:
        print(f"\"{property_name}\": {value}")


# opens trade with given parameters
def open_trade(symbol, qty, side, budget, stop_loss, time_in_force="day"):
    is_trail = userDatabase.get_trail(username)
    if is_trail == "y":
        order = TrailingStopOrderRequest(symbol=symbol,
                                         qty=1,
                                         side=side,
                                         stop_loss={'stop_price': budget * (stop_loss / 100)},
                                         time_in_force=time_in_force
                                         )
    else:
        if side == "buy":
            order = MarketOrderRequest(symbol=symbol,
                                       notional=qty,
                                       side=side,
                                       stop_loss={'stop_price': budget * (stop_loss / 100)},
                                       time_in_force=time_in_force
                                       )
        else:
            order = MarketOrderRequest(symbol=symbol,
                                       qty=1,
                                       side=side,
                                       stop_loss={'stop_price': budget * (stop_loss / 100)},
                                       time_in_force=time_in_force
                                       )

    trading_client.submit_order(order_data=order)


# formats trade for making requests with Alpaca
def prepare_trade(symbol, confidence, side):
    budget, stop_loss = userDatabase.get_trade_data(username)
    qty = round(confidence * budget, 2)
    qty = abs(qty)
    symbol = symbol
    side = side

    open_trade(symbol, qty, side, budget, stop_loss)


# find position with given symbol (eg. "AAPL")
def get_order_id(symbol):
    get_positions = trading_client.get_all_positions()
    for a in get_positions:
        if a.symbol == symbol:
            return_id = a.asset_id
            return return_id

    return "No open position found"


# get all current open positions to display on user portfolio (activity overview)
def get_trades():
    trade_info = []
    trade_type = "Buy"
    get_positions = trading_client.get_all_positions()
    for a in get_positions:
        if a.side == "short":
            trade_type = "Sell"
        trade_info.append((a.symbol, trade_type, a.qty, float(a.unrealized_pl)))

    return trade_info


# close trade with given parameter asset_id (id can be retrieved with get_order_id())
def close_trade(asset_id):
    trading_client.close_position(asset_id)


# close all current open trades
def close_all_trades():
    trading_client.close_all_positions(cancel_orders=True)


# get list of all symbols on user's watchlist
def get_symbols():
    symbols = []

    for j in get_watchlist.assets:
        symbols.append(j.symbol)

    return symbols


# add symbols to user's watchlist
def add_symbols(symbol):
    try:
        trading_client.add_asset_to_watchlist_by_id(watchlist_id, symbol)
        return True
    except APIError:
        return False


# remove symbols from user's watchlist
def remove_symbols(symbol):
    trading_client.remove_asset_from_watchlist_by_id(watchlist_id, symbol)


# request data gathering from tradingStrategy.py and sends results to prepare_trade() if trade = True
def get_from_ts():
    symbols = get_symbols()
    symbol_return = []

    get_positions = trading_client.get_all_positions()
    for a in get_positions:
        if a.symbol not in symbols:
            trade, long, confidence = tradingStrategy.check_params(a.symbol)
            if trade:
                if long:
                    # open buy trade
                    prepare_trade(a.symbol, confidence, "buy")
                    symbol_return.append(a.symbol)
                    print(f"Buy trade for {a.symbol} opening...")
                else:
                    # open sell trade
                    prepare_trade(a.symbol, confidence, "sell")
                    symbol_return.append(a.symbol)
                    print(f"Sell trade for {a.symbol} opening...")

    return symbol_return
